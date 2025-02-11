######################################
#                                    #
#         SERVIDOR LICENCIAS         #
#                                    #
######################################

#LIBRERIAS----------------------------------------------------------------------
import os
from socket import *
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

#FUNCIONES----------------------------------------------------------------------
from funciones import rsa_server, send, recv

#CONFIGURACION SOCKETS----------------------------------------------------------
serverPort = 60001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print('Server ready to receive connections')
connectionSocket, clientAdress = serverSocket.accept()

#CONFIGURACION CIFRADO----------------------------------------------------------
intercambio = False
KEY = os.urandom(16)
IV = os.urandom(16)

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
        
        #Recibe mensaje firmado por CDM y su kpub
        msj = recv(connectionSocket, KEY, IV)
        
        if msj == b"quit": #si el mensaje es quit --> para el programa
            break
    
        signature = msj.split(b"-----")[0] #recibe la firma
        print("\n***Firma recibida")

        pemCDM = recv(connectionSocket, KEY, IV) #recibe clave publica del CDM
        kpubCDM = serialization.load_pem_public_key(pemCDM)
        print("***Clave pública CDM recibida")
        
        #Recibe mensaje del cliente
        mensaje_b = msj.split(b"-----")[1]
        mensaje = mensaje_b.decode()
        print("***Mensaje recibido del cliente:",mensaje)
        
        #Verificar la firma del mensaje
        try:
            kpubCDM.verify(
                signature,
                mensaje_b,
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                    
                ),
                hashes.SHA256()
            )
            print("***Signature is valid")
        
        except Exception as e:
            print("ERROR\n***Signature is invalid")
            send("ERROR", connectionSocket, KEY, IV)
            break
        
        if "." in mensaje:
            message = mensaje.split('.')[0][:-2]
        else:
            message = mensaje

        print("***Licencia solicitada:",message)

        #Abrimos clave de claves y obtenemos las credenciales
        fhand = open('temp/clave_de_claves.txt','rb')
        for i,line in enumerate(fhand):
            if i==0:
                clave_de_clave = line[:16]
            if i==1:
                iv_de_clave = line[:16]
        fhand.close()
        
        #Cifrador para descifrar txt de claves
        aesCipher_CTR_KEY = Cipher(algorithms.AES(clave_de_clave),modes.CTR(iv_de_clave))
        aesDecryptor_CTR_KEY = aesCipher_CTR_KEY.decryptor()
        
        #Desciframos txt de claves
        fhand = open("temp/claves.txt",'rb')
        data = fhand.read()
        f_decrypt = aesDecryptor_CTR_KEY.update(data)+ aesDecryptor_CTR_KEY.finalize()
        fhand.close()
        
        os.remove("temp/claves.txt") #borramos el txt cifrado
        
        f = open('temp/claves.txt', 'wb') #guardamos txt descifrado
        f.write(f_decrypt)
        f.close()
        
        f = open('temp/claves.txt', 'rb')
        
        for line in f: #buscamos clave del fichero en el txt
            nombre_ext = str(line).split("---")[0]
            nombre = nombre_ext.split(".")[0]
            l = len(nombre_ext)
            
            if nombre[2:] == message:
                clave = line[l+1:l+17]
                iv = line[l+20:l+36]
        
        f.close()
        
        if iv==b'' or clave==b'':
            send(b"ERROR", connectionSocket, KEY, IV)
        else:
            msg = clave+iv
            send(msg, connectionSocket, KEY, IV)
            print("---Clave enviada:",clave)
            print("---IV enviado:",iv)
        f.close()
        
        #Eliminamos el fichero de claves descifrado-------------
        os.remove("temp/claves.txt")
        os.remove("temp/clave_de_claves.txt")

        #Eliminamos el fichero cifrado de la carpeta temporal---
        os.remove("ficheros_server/temp/"+mensaje)
        
    except Exception as e:
        print('\nERROR')
        print(e)
        aesEncryptor_CTR = aesCipher_CTR.encryptor()
        msg_enc = aesEncryptor_CTR.update(b"ERROR") + aesEncryptor_CTR.finalize()
        connectionSocket.send(msg_enc)
        
        #borra contenido de temp
        if ("claves.txt" or "clave_de_claves.txt") in os.listdir("temp/"):
            os.remove("temp/claves.txt")
            os.remove("temp/clave_de_claves.txt")

print("\nServer has finished its work")
connectionSocket.close()
serverSocket.close()