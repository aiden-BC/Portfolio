import os
from socket import *
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

#Cifrador CTR para ficheros----------------------------------------------------
def cifra_CTR(nombre):
    #clave y vector de inicializacion
    KEY = os.urandom(16)
    IV = os.urandom(16)

    #para que no haya retornos de carro en KEY o IV
    while (b"\n" in KEY):
        KEY = os.urandom(16)
    while (b"\n" in IV):
        IV = os.urandom(16)

    #cifrador CTR
    aesCipher_CTR = Cipher(algorithms.AES(KEY),modes.CTR(IV))
    aesEncryptor_CTR = aesCipher_CTR.encryptor()

    #saber si vamos a cifrar un fichero o el txt de claves
    if nombre[-3:]!='txt':
        #datos
        nombre_l = nombre.split('.')
        img = open('ficheros_server/temp/'+nombre, 'rb')
        data = img.read()
        img.close()

        #encriptamos en modo CTR
        data_encrypt = aesEncryptor_CTR.update(data)

        #guardamos el fichero encriptado
        fhand = open('ficheros_server/temp/'+nombre_l[0]+'_e.'+nombre_l[1], 'wb')
        fhand.write(data_encrypt)
        fhand.close()

        #escribimos KEY e IV en el fichero de claves
        fhand = open('temp/claves.txt', 'ab+')
        fhand.write(nombre.encode('utf-8')+b'---'+KEY+b'---'+IV)
        fhand.close()
    else:
        #leemos el txt
        f = open('temp/claves.txt','rb')
        data = f.read()
        f.close()

        #encriptamos el contenido y borramos el fichero original
        aesEncryptor_CTR = aesCipher_CTR.encryptor()
        data_encrypt = aesEncryptor_CTR.update(data)+ aesEncryptor_CTR.finalize()
        os.remove("temp/claves.txt")
        
        #guardamos el fichero encriptado
        fhand = open('temp/claves.txt', 'wb')
        fhand.write(data_encrypt)
        fhand.close()
        
        #guardamos la clave en otro txt
        fhand = open('temp/clave_de_claves.txt','wb')
        fhand.write(KEY+b'\n')
        fhand.write(IV)
        fhand.close()

#Conversion bytes <--> int-----------------------------------------------------
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

def int_to_bytes(i):
    return i.to_bytes((i.bit_length()+7)//8, byteorder='big')

#Funciones para cifrado asimetrico RSA-----------------------------------------
def rsa_cliente(pem, clientSocket, d, n):
    #envia la clave publica
    clientSocket.send(pem)

    #recibe KEY
    key_cifrada = clientSocket.recv(2048)
    
    #recibe IV
    iv_cifrado = clientSocket.recv(2048)

    #descifra KEY con clave privada
    key_dec_int = pow(bytes_to_int(key_cifrada), d, n)
    KEY = int_to_bytes(key_dec_int)
    
    #descifra IV con clave privada
    iv_dec_int = pow(bytes_to_int(iv_cifrado), d, n)
    IV = int_to_bytes(iv_dec_int)
    
    print("***Clave simétrica recibida")

    return KEY, IV

def rsa_server(KEY, IV, connectionSocket):
    #recibe clave publica
    pem = connectionSocket.recv(2048)
    kpub_cliente = serialization.load_pem_public_key(pem)
    print("***Clave pública recibida")
    
    #parametros de la clave publica
    e = kpub_cliente.public_numbers().e
    n = kpub_cliente.public_numbers().n

    #cifra KEY con la clave publica
    KEY_int = bytes_to_int(KEY)
    key_cifrada = int_to_bytes(pow(KEY_int, e, n))
    
    #cifra IV con la clave pública
    IV_int = bytes_to_int(IV)
    iv_cifrado = int_to_bytes(pow(IV_int, e, n))

    #envia KEY+IV cifrados
    connectionSocket.send(key_cifrada)
    connectionSocket.send(iv_cifrado)
    print('---Clave simétrica enviada')

#Firma digital-----------------------------------------------------------------
def sign_message(private_key, message):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

#Funcion para encriptar y enviar mensajes--------------------------------------
def send(msg, clientSocket, KEY="", IV=""):
    #comprueba si el mensaje a enviar se quiere encriptar
    if msg == b"quit":
        msg_enc = msg
    else:
        #crea cifrador
        aesCipher_CTR = Cipher(algorithms.AES(KEY),modes.CTR(IV))
        aesEncryptor_CTR = aesCipher_CTR.encryptor()
        
        #si el mensaje es string lo convierte a bytes
        if type(msg)==str:
            msg = msg.encode()
        
        #encripta el mensaje
        msg_enc = aesEncryptor_CTR.update(msg) + aesEncryptor_CTR.finalize()
    
    #envia el mensaje
    clientSocket.send(msg_enc)

#Funcion para recibir y desencriptar mensajes----------------------------------
def recv(connectionSocket, KEY="", IV=""):
    #recibe el mensaje
    msg_enc = connectionSocket.recv(2048)

    #comprueba si el mensaje es quit
    if msg_enc == b"quit":
        print(msg_enc)
        return msg_enc

    #crea el descifrador
    aesCipher_CTR = Cipher(algorithms.AES(KEY),modes.CTR(IV))
    aesDecryptor_CTR = aesCipher_CTR.encryptor()

    #desencripta el mensaje
    msj = aesDecryptor_CTR.update(msg_enc) + aesDecryptor_CTR.finalize()
    return msj
