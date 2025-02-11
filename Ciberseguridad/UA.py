##############################
#                            #
#             UA             #
#                            #
##############################

#LIBRERIAS----------------------------------------------------------------------
import os
from socket import *
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers, RSAPrivateNumbers

#FUNCIONES----------------------------------------------------------------------
from funciones import rsa_cliente, sign_message, send, recv

#CONFIGURACION SOCKETS----------------------------------------------------------
serverName = '127.0.0.1'
serverPort = 60000
serverPortLic = 60001
serverPortCDM = 60002

TCPserverAddr=(serverName, serverPort)
TCPserverAddrLIC=(serverName, serverPortLic)
TCPserverAddrCDM=(serverName, serverPortCDM)

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocketLIC = socket(AF_INET, SOCK_STREAM)
clientSocketCDM = socket(AF_INET, SOCK_STREAM)

clientSocket.connect(TCPserverAddr)
print("Conectado al servidor")

#CONFIGURACION CIFRADO RSA -----------------------------------------------------
intercambio_CDM = False
intercambio_LIC = False

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

n = public_key.public_numbers().n
d = private_key.private_numbers().d

pem = public_key.public_bytes(
   encoding=serialization.Encoding.PEM,
   format=serialization.PublicFormat.SubjectPublicKeyInfo
)

firmado=False

#PROGRAMA-----------------------------------------------------------------------
#Nombre de usuario----------------------------------------
nombre_usuario = input("Por favor, introduce tu nombre: ")
clientSocket.send(nombre_usuario.encode())

while True:
    try:
        #Input y envío de comandos
        print('\nIntroduzca un comando (help para ayuda)\n')
        comando = input ('>')
        comando = comando.upper()
        comando_l = comando.split(' ')
        clientSocket.send(comando.encode())
        print('---Mensaje enviado\n')
        
        #Comando HELP------------------
        #Imprime por pantalla la lista de comandos posibles
        if comando_l[0] == 'HELP':
            print("""LISTA DE COMANDOS:
            - LIST ALL: lista de todos los ficheros
            - LIST <extension>: lista los ficheros de una extensión
            - GET <fichero>: pide un fichero
            - QUIT: sale del programa
            - HELP: lista de comandos\n""")
        
        #Comando LIST------------------
        #Devuelve la lista de ficheros disponibles
        elif comando_l[0] == 'LIST':
            resp = clientSocket.recv(2048).decode()
            resp = resp.split('\n')
            
            #recorre la lista de ficheros y los imprime
            for el in resp:
                print(el)
        
        #Comando GET-------------------
        #Pide un archivo al servidor de contenidos
        elif comando_l[0] == 'GET':
            resp = clientSocket.recv(2048) #respuesta inicial del servidor

            if resp == b"ERROR":
                print("ERROR \nNombre del archivo en formato incorrecto\n(recuerde poner la extension)")
                continue
            
            print(resp.decode()[2:])
            
            l_resp = resp.split(b' ')
            long2 = 0
            
            #Recibe el archivo
            if l_resp[1] == b'200': #200: todo correcto, se procede a enviar el archivo
                #Fichero encriptado --> añadimos _e al nombre
                if l_resp[0] == b"T": #respuesta del servidor empieza por T si el archivo esta encriptado
                    print("***Fichero encriptado")
                    nombre_nuevo = comando[4:].lower().split('.')
                    nombre_nuevo = nombre_nuevo[0]+'_e.'+nombre_nuevo[1]
                    nuevo_f = open('ficheros_recibidos/'+nombre_nuevo,'wb')
                
                #Fichero no encriptado --> mismo nombre
                else:
                    print("***Fichero no encriptado")
                    nombre_nuevo = comando[4:].lower()
                    nuevo_f = open('ficheros_recibidos/'+nombre_nuevo,'wb')
                
                long = int(l_resp[-1].split(b':')[-1]) #longitud del fichero
                
                #Recibe fichero linea a linea y lo guarda
                while long2 < long:
                    linea = clientSocket.recv(2048)
                    long2 += len(linea)
                    nuevo_f.write(linea)
                
                nuevo_f.close()
                nombre = nombre_nuevo.split('.')
                
                #Si está encriptado --> desencripta
                if nombre[0][-2:]=='_e':
                    #Ciframos comunicación entre CDM y UA
                    if intercambio_CDM == False:
                        clientSocketCDM.connect(TCPserverAddrCDM)
                        print('***Conectado al CDM')
                        KEY_CDM, IV_CDM = rsa_cliente(pem, clientSocketCDM, d, n)
                        intercambio_CDM = True
                    
                    #Pedimos al CDM la solicitud de licencia firmada
                    send(nombre_nuevo, clientSocketCDM, KEY_CDM, IV_CDM)
                    
                    #Recibimos pem del CDM para poder verificar la firma con el serv_lic
                    pemCDM = recv(clientSocketCDM, KEY_CDM, IV_CDM)
                    print("***Clave pública del CDM recibida")
                    
                    #Preparamos conexión con serv_lic para enviarle solicitud de descifrar
                    #Intercambio de claves
                    if intercambio_LIC==False:
                        clientSocketLIC.connect(TCPserverAddrLIC)
                        print('***Conectado al servidor de licencias')
                        
                        KEY_LIC, IV_LIC = rsa_cliente(pem, clientSocketLIC, d, n)
                        intercambio_LIC = True
                    
                    #recibimos la solicitud de descifrado por parte del CDM
                    signature = recv(clientSocketCDM, KEY_CDM, IV_CDM)
                    print("***Mensaje firmado recibido")
                    
                    #reenviamos a serv_lic el mensaje creado por CDM, su kpub y la solicitud
                    msj = signature+b"-----"+nombre_nuevo.encode()
                    send(msj, clientSocketLIC, KEY_LIC, IV_LIC)
                    print("---Solicitud de licencia firmada enviada")
                    
                    send(pemCDM, clientSocketLIC, KEY_LIC, IV_LIC)
                    print("---Clave pública CDM enviada")
                    resp = recv(clientSocketLIC, KEY_LIC, IV_LIC)
                    
                    if resp==b"ERROR":
                        print("***ERROR en la obtencion de la licencia")
                    else:
                        print("***Licencia recibida")
                        #enviamos las credenciales de acceso
                        send(resp, clientSocketCDM, KEY_CDM, IV_CDM)
                        print("---Licencia enviada a CDM")
                    
        #Comando QUIT------------------
        elif comando_l[0] == 'QUIT':
            #Intercambio de clave simetrica-----------------------
            if intercambio_CDM==False:
                clientSocketCDM.connect(TCPserverAddrCDM)
                rsa_cliente(pem, clientSocketCDM, d, n)
                intercambio_CDM = True
                
            if intercambio_LIC==False:
                clientSocketLIC.connect(TCPserverAddrLIC)
                rsa_cliente(pem, clientSocketLIC, d, n)
                intercambio_LIC = True
            
            send(b"quit", clientSocketCDM)
            send(b"quit", clientSocketLIC)
            break
        
        else:
            print("400 ERROR. MENSAJE NO IDENTIFICADO")
     
    except Exception as e:
        print('\nERROR')
        print(e)
        
        #borra contenido de temp
        if ("claves.txt" or "clave_de_claves.txt") in os.listdir("temp/"):
            os.remove("temp/claves.txt")
            os.remove("temp/clave_de_claves.txt")

print("Client has finished its work")
clientSocket.close()