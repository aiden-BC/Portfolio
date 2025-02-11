#############################
#                           #
#            CDM            #
#                           #
#############################

#LIBRERIAS----------------------------------------------------------------------
import os
from socket import *
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

#FUNCIONES----------------------------------------------------------------------
from funciones import rsa_server, sign_message, send, recv

#CONFIGURACION SOCKETS----------------------------------------------------------
serverPort = 60002
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print('CDM ready to receive connections')
connectionSocket, clientAdress = serverSocket.accept()

conectado = False

#CONFIGURACION CIFRADO RSA -----------------------------------------------------
intercambio = False
KEY = os.urandom(16)
IV = os.urandom(16)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

pem = public_key.public_bytes(
   encoding=serialization.Encoding.PEM,
   format=serialization.PublicFormat.SubjectPublicKeyInfo
)

firmado=False

#cifrador CTR
aesCipher_CTR = Cipher(algorithms.AES(KEY),modes.CTR(IV))

#PROGRAMA-----------------------------------------------------------------------
while True:
    try:
        #Intercambio de clave simetrica-----------------------
        if intercambio==False:
            rsa_server(KEY, IV, connectionSocket)
            intercambio = True
        
        #Comunicacion con cliente-----------------------------      
        #recibimos mensaje del cliente con el nombre del fichero
        msj = recv(connectionSocket, KEY, IV)
        print(msj)
        
        #si el mensaje es quit --> para el programa
        if msj == b"quit":
            break
        
        nombre_nuevo = msj.decode() #decodifica el mensaje
        print("\n***Mensaje recibido:",nombre_nuevo)
        
        send(pem, connectionSocket, KEY, IV) #envia al cliente su clave publica
        
        #guarda datos de fichero cifrado
        f = open('ficheros_recibidos/'+nombre_nuevo, 'rb')
        data = f.read()
        f.close()
        
        #firmamos la solicitud y se la enviamos al cliente
        try:
            message_to_sign = msj
            signature = sign_message(private_key, message_to_sign)
            send(signature, connectionSocket, KEY, IV)
            print("---Mensaje firmado enviado")

        except Exception as e:
            print("\nERROR. Mensaje firmado NO enviado")
            print(e)
            break
        
        #recibimos las credenciales de acceso al contenido multimedia
        resp = recv(connectionSocket, KEY, IV)
        
        if resp!=b"ERROR": #comprobamos que no haya dado error
            print("***Licencia recibida")
            
            #sacamos KEY e IV de la respuesta del servidor
            KEY2 = resp[:16]
            IV2 = resp[16:]
            
            print("***Clave del fichero recibida:",KEY2)
            print("***IV del fichero recibido:",IV2)
            
            #creamos descifrador para desencriptar el fichero
            aesCipher_CTR2 = Cipher(algorithms.AES(KEY2),modes.CTR(IV2))
            aesDecryptor_CTR2 = aesCipher_CTR2.decryptor()
            
            #desencriptamos el fichero y lo guardamos
            data_decrypt = aesDecryptor_CTR2.update(data) + aesDecryptor_CTR2.finalize()
            
            nombre = nombre_nuevo.split('.')
            nom = nombre[0][:-2]+"."+nombre[1]
            f_decrypt = open('ficheros_recibidos/'+nom, "wb")
            f_decrypt.write(data_decrypt)
            f_decrypt.close()
        
            os.remove('ficheros_recibidos/'+nombre_nuevo) #borramos el fichero encriptado
            print("***Fichero desencriptado")
        else:
            print("\nERROR al desencriptar")
            break
        
    except Exception as e: #en caso de error: lo imprimimos y notificamos al cliente
        print('\nERROR')
        print(e)
        aesEncryptor_CTR = aesCipher_CTR.encryptor()
        msg_enc = aesEncryptor_CTR.update(b"ERROR") + aesEncryptor_CTR.finalize()
        send(msg_enc, connectionSocket, KEY, IV)

print("\nServer has finished its work")
connectionSocket.close()
serverSocket.close()