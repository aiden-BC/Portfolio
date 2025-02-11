##############################
#                            #
#          SERVIDOR          #
#                            #
##############################

#LIBRERIAS----------------------------------------------------------------------
import os
from socket import *
from PIL import Image, ImageDraw, ImageFont

#FUNCIONES----------------------------------------------------------------------
from funciones import cifra_CTR

#CONFIGURACION SOCKETS----------------------------------------------------------
serverPort = 60000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen()

print('Server ready to receive connections')

connectionSocket, clientAdress = serverSocket.accept()

cifrado = " "

#NOMBRE USUARIO-----------------------------------------------------------------
nombre_usuario = connectionSocket.recv(2048).decode()

#PROGRAMA-----------------------------------------------------------------------
while True:
    try:
        #Recibe e imprime el comando
        message = connectionSocket.recv(2048).decode()
        print("\n***Comando recibido:",message.lower())
        lista = message.split()
        
        #Comando LIST--------------------
        #Enumera los ficheros disponibles
        if lista[0] == 'LIST':
            #comprueba si se ha pedido una extension
            if lista[1] == 'ALL':
                extension = ''
            else:
                extension = '.' + lista[1].lower()
            
            #directorio
            directorio = 'ficheros_server/'
            contenido = os.listdir(directorio)
            fich = []
            
            #crea lista con los ficheros
            for fichero in contenido:
                if os.path.isfile(os.path.join(directorio, fichero)) and fichero.endswith(extension):
                    fich.append(fichero)
            
            #si no hay ficheros
            if len(fich) == 0:
                resp = '201 NO HAY FICHEROS'
                print('\n',resp)
                connectionSocket.sendall(resp.encode())       
            
            #hay ficheros: envia el listado
            else:
                resp = '200 INICIO ENVIO LISTADO\n'
                print(resp[:-1])
                
                for fichero in fich:
                    resp += '\t-'+fichero+'\n'
                    print('\t- ',fichero)
                connectionSocket.sendall(resp.encode())
        
        #Comando GET-------------------------------------
        #Envia un fichero
        elif lista[0] == 'GET':
            try:
                extension = lista[1].split('.')[1].lower()
                nombre = lista[1].lower()
                carpeta = "ficheros_server/"
                
                if extension!='mp4':
                    #crea fichero con marca------------------
                    #Opening Image
                    img = Image.open(carpeta + nombre) 

                    #Creating draw object
                    draw = ImageDraw.Draw(img) 
                    #Creating text and font object
                    text = nombre_usuario
                    width, height = img.size
                    font = ImageFont.truetype('arial.ttf', int(height/20))

                    #Positioning Text
                    x=int(height/40)
                    y=height-int(height/20)-20

                    #Applying text on image via draw object
                    draw.text((x, y), text, font=font) 

                    #Saving the new image
                    img.save("ficheros_server/temp/"+ nombre.lower())
                    
                    #cifra la imagen marcada-------------
                    cifra_CTR(nombre.lower())
                    print("***Imagen ", nombre.lower() ,"cifrada")
                    
                    cifra_CTR("claves.txt")
                    
                    #elimina el fichero marcado sin cifrar
                    os.remove("ficheros_server/temp/"+nombre.lower())
                
                    #mandar fichero cifrado------------------
                    nombre = nombre.lower().split('.')
                    nombre_nuevo = nombre[0]+"_e."+nombre[1]
                    fichero = "ficheros_server/temp/"+nombre_nuevo
                    
                    cifrado = "T"
                
                else:
                    fichero = "ficheros_server/"+nombre.lower()
                    cifrado = "F"
                
                f = open(fichero,'rb')           
                long = 0

                #calcula longitud del fichero
                for line in f:
                    long += len(line)
                f.close()
                
                message = cifrado + ' 200 LONGITUD CONTENIDO: ' + str(long) + '\n'
                connectionSocket.send(message.encode())
                
                f2 = open(fichero,'rb')
                
                #manda el fichero cifrado
                for line in f2:
                    connectionSocket.sendall(line)
                    
                f2.close()
                print("---Imagen marcada y cifrada enviada") if cifrado=='T' else print("---Fichero enviado")
                    
            except FileNotFoundError:
                message = '\n 401 FICHERO NO ENCONTRADO'
                print(message)
                connectionSocket.sendall(message.encode())
        
        #Comando HELP--------------------
        elif lista[0] == 'HELP':
            print('***Imprimiendo listado de comandos')
        
        #Comando QUIT--------------------
        elif lista[0] == 'QUIT':
            print('\nServer has finished its work')
            break
        
        #Comando no reconocido-----------
        else:
            resp = '400 ERROR. MENSAJE NO IDENTIFICADO'
            print(resp)
    
    except Exception as e:
        print('\nERROR')
        print(e)
        connectionSocket.send("ERROR".encode())
        
    
connectionSocket.close()
serverSocket.close()   