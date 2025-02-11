
#Importamos librerías
from guizero import * #interfaz gráfica
import os 
from socket import * #para configurar sockets
import numpy as np
import pandas #para leer excel
import matplotlib.pyplot as plt #para representar las gráficas
from scipy.ndimage import uniform_filter1d #para suavizar
from scipy.integrate import cumtrapz #para hacer integrales numéricas
from statistics import mean #función para calcular la media

#APP---------------

app = App(bg = "#289687",
          title ="LOGIN",
          height = 400,
          width = 450)

#FUNCTIONS---------

#FISICA--------------------------------------------------------------------------------------------------------------#

#1. Lectura del fichero
def lectura():
    global fich1
    fichero = fich1 + '.xlsx'
    df = pandas.read_excel(fichero)
    #datos del fichero
    t = df.values[:,0].astype(float) #tiempo: 1ª columna
    mod_a = (df.values[:,1].astype(float)) #módulo de la aceleracion: 2ª columna
    ay = (df.values[:,3].astype(float)) #componente vertical de la aceleración: 4ª columna
    av = mod_a * np.sign(ay) #aceleracion con signo
    return t, mod_a, ay, av

#Gráficas aceleración
def graf_acel():
    global t, mod_a, ay, av
    
    #Módulo de la aceleración
    plt.figure()
    plt.title('Módulo aceleración')
    plt.xlabel('t (s)')
    plt.ylabel(r'$a (m/s^2)$')

    plt.plot(t, mod_a,'g' ,label='Módulo aceleración')
    plt.grid()
    plt.xlim([0, 3]) #limite eje x
    plt.legend()
    
    plt.savefig("Módulo aceleración.png") #guarda la imagen
    
    #Aceleración con signo y suavizada
    plt.figure()
    plt.title('Aceleración')
    plt.xlabel('t (s)')
    plt.ylabel(r'$a (m/s^2)$')

    plt.plot(t, av, label='Aceleración')
    
    am = suavizar()
    plt.plot(t, am, 'g',label='Aceleración suavizada')
    
    plt.legend()
    plt.grid()
    plt.xlim([0, 5]) #limite eje x
    plt.savefig("Aceleración suavizada.png") #guarda la imagen

    plt.show()

#------------------#

#2. Suavizar la aceleración

def suavizar():
    global av
    
    #Suavizado con media movil: funcion sacada de la práctica de mates
    am = uniform_filter1d(av, 15) #aceleración suavizada
    
    return am
#------------------#

#3. Calcular el valor de g
    
def grav():
    global t, av
    
    am = suavizar()
    
    #g = media desde el principio hasta el momento en el que empieza el impulso

    #vemos en la grafica de la aceleracion que el impulso empieza aproximadamente en t = 0.3
    #cogemos los valores de aceleracion desde t=0 a t=0.3
    a_reposo= am[0:list(t).index(0.3)]

    #hacemos la media de los valores para conseguir g
    g = mean(a_reposo)
    
    return g

#------------------#

#4. Calcula F(t)

def fuerza():
    global t, peso1
    am = suavizar()
    m = int(peso1)
    f = m*am # F = m*a
    return f

def graf_f():
    f = fuerza()
    global t
    f = fuerza()
    indice = list(t).index(1)
    f2 = f[:indice]
    f_piernas = max(f2)
    return round(f_piernas,2)

def graf_f2():
    f = fuerza()
    global t
    f = fuerza()
    indice = list(t).index(1)
    f2 = f[:indice]
    f_piernas = max(f2)
    
    
    #Representacion
    plt.figure()
    plt.title('Fuerza')
    plt.xlabel('t (s)')
    plt.ylabel('F (N)')

    plt.plot(t, f, 'g', label='F')

    plt.xlim([0, 3]) #limites del eje x
    plt.grid()
    plt.legend()
    plt.savefig("Fuerza.png") #guarda la imagen
    
    plt.show()
    
#------------------#

#5. Calcula la velocidad v(t)

def vel():
    global t
    g = grav()
    am = suavizar()
    
    #funcion para calcular integrales: sacada de la práctica 13 de matemáticas
    def primitivaNumerica(variable, tiempo, y0):
        return cumtrapz(variable,x=tiempo,initial=y0)

    v = primitivaNumerica(am-g, t, 0) #calcula v usando la funcion **IMPORTANTE: integramos acel_medida-g, NO acel_medida
    
    return v

def graf_v():
    v = vel()
    
    #representacion
    plt.figure()
    plt.title('Velocidad')
    plt.xlabel('t (s)')
    plt.ylabel('v (m/s)')

    plt.plot(t, v, 'g', label='v')

    plt.xlim([0, 3]) #limite eje x
    plt.grid()
    plt.legend()
    plt.savefig("Velocidad.png") #guarda la imagen
    plt.show()
    
#------------------#

#6. Identifica el final del impulso y el final del vuelo
    
def vuelo():
    global t
    v = vel()
    am = suavizar()
    
    v0 = max(v) #v max: v final del impulso/inicio del vuelo
    vf = min(v) #v min: v final del vuelo

    t0 = t[list(v).index(v0)] #instante del final del impulso
    tf = t[list(v).index(vf)] #instante del final del vuelo

    T = tf - t0 #tiempo de vuelo
    
    return v0, T

#------------------#

#7. Cálculo de la potencia
    
def pot():
    f = fuerza()
    v = vel()
    am = suavizar()
    P = f*v
    p_max = max(P)
    return round(p_max,2)

def pot2():
    f = fuerza()
    v = vel()
    am = suavizar()
    P = f*v
    p_max = max(P)

    #representacion
    plt.figure()
    plt.title('Potencia')
    plt.xlabel('t (s)')
    plt.ylabel('P (W)')

    plt.plot(t, P, 'g', label='P')
    plt.legend()
    plt.xlim([0, 3]) #limite eje x
    plt.grid()
    
    plt.savefig("Potencia_grafica.png") #guarda la imagen
    plt.show()
#------------------#

#8. Altura del salto

def altura2():
    g = grav()
    v0, T = vuelo()
    
    #a partir de la velocidad de despegue
    h_v = (v0**2) / (2*g)
    

    #a partir del tiempo de vuelo
    h_T = g*T**2 / 8
    
    
    
    return round(h_v, 3)

#ARQRED---------------------------------------------------------------------------------------------
#1. Setup del servidor y cliente

#servidor
serverName = '158.42.188.200'
serverPort = 64010
TCPserverAddr=(serverName, serverPort)
#cliente
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(TCPserverAddr)

#------------------#
#2. Inicio de sesión

#GUIZERO------------------------------------------------------------------------------------
def PC():
    import socket
    pc = socket.gethostname()
    IP = socket.gethostbyname(pc)
    return IP

#2.1. Comando HELLO
def hello():
    IP = PC()
    mensaje = 'HELLO ' + IP + ' \n'
    print(mensaje)
    clientSocket.send(mensaje.encode())
    mensaje_rx = clientSocket.recv(2048)
    print(mensaje_rx)
    if mensaje_rx.decode()[0:3] == '400':
        print('Error en el formato de la IP')
        global U1, C1
        user_textbox.clear()
        U1 = ""
        passw.clear()
        C1 = ""
        app.error('ERROR','La IP es incorrecta;(!!!')
        return 'ERROR'
        
    else:
        return 'Todo ha ido correctamente'

#--------#

#2.2. Comando USER
        
def user(ident):
    mensaje = 'USER ' + ident + '\n'
    clientSocket.send(mensaje.encode())
    mensaje_rx = clientSocket.recv(2048)
    print(mensaje)
    print(mensaje_rx)
    if mensaje_rx.decode()[0:3] == '400': #control de errores: el programa no continúa hasta que USER no se reciba correctamente
        print('Usuario no registrado')
        global U1, C1
        user_textbox.clear()
        U1 = ""
        passw.clear()
        C1 = ""
        app.error('ERROR','El usuario es incorrecto;(!!!')
        return 'ERROR'
    else:
        return 'Todo ha ido correctamente'
    
#--------#

#2.3. Comando PASS
def password(cod):
    mensaje = 'PASS ' + cod + ' \n'
    clientSocket.send(mensaje.encode())
    mensaje_rx = clientSocket.recv(2048)
    print(mensaje)
    print(mensaje_rx)
    if mensaje_rx.decode()[0] == '4':
        print('Contraseña incorrecta')
        global U1, C1
        U1 = ""
        passw.clear()
        C1 = ""
        return app.error('ERROR','La contraseña es incorrecta;(!!!')
    else:
        return 'Todo ha ido correctamente'
        
#GUIZERO------------------------------------------------------------------------------------------------#
    
#BOTONES
def acceder():
    hello()
    global U1, C1
    error1 = user(U1)
    error2 = password(C1)
    if error1 != 'ERROR' and error2 != 'ERROR':
        app.hide()
        window_inicio.show()

def enviar():
    window_inicio.hide()
    window_enviar_datos.show()

def obtener():
    window_inicio.hide()
    window_fichero.show()

t = []
mod_a = []
ay = []
av = []

def continuar_fich():
    global t, mod_a, ay, av
    window_fichero.hide()
    window_peso.show()
    t, mod_a, ay, av = lectura()

def continuar_peso():
    window_peso.hide()
    window_obtener_datos.show()
    graf_f()

def close1():
    a =window_enviar_datos.yesno('SALIR','Está seguro de que quiere salir del programa?')
    if a == True:
        app.destroy()
        QUIT()
    else:
        window_enviar_datos.focus()
def close2():
    a = window_fichero.yesno('SALIR','Está seguro de que quiere salir del programa?')
    if a == True:
        app.destroy()
        QUIT()
    else:
        window_fichero.focus()        
def close3():
    a = window_obtener_datos.yesno('SALIR','Está seguro de que quiere salir del programa?')
    if a == True:
        app.destroy()
        QUIT()
    else:
        window_obtener_datos.focus()
def close4():
    a = window_ranking.yesno('SALIR','Está seguro de que quiere salir del programa?')
    if a == True:
        app.destroy()
        QUIT()
    else:
        window_ranking.focus()
def close5():
    a = window_datos.yesno('SALIR','Está seguro de que quiere salir del programa?')
    if a == True:
        app.destroy()
        QUIT()
    else:
        window_datos.focus()  

def info_frogup():
    app.info('QUE HACE FROGUP?', 'FrogUp es una aplicación dedicada a la medida y comparación de saltos, donde podrá obtener datos y gráficas. \rGRACIAS POR UTILIZAR FrogUp!!! ')
      
def info_medidas():
    app.info('MEDIDAS', 'Recuerde que las medidas han de estar en milímetros ;)')
def inicio1():
    window_enviar_datos.hide()
    window_inicio.show()
    
def inicio2():
    window_obtener_datos.hide()
    plot.hide()
    window_inicio.show()
    
def inicio3():
    window_datos.hide()
    window_inicio.show()
    
def volver1():
    window_fichero.hide()
    window_inicio.show()
    
def volver2():
    window_ranking.hide()
    window_obtener_datos.show()
    
#DEF LOGIN()
U1 = ""
def usuario(u):
    global U1
    if u.isalpha():
        U1 += u
    else:
        U1 = U1[:-1]
    
C1 = "" 
def contraseña(c):
    global C1
    if c.isdigit():
        C1 += c
    else:
        C1 = C1[:-1]         

#ENVIAR DATOS--------------------------------------------#

def send_data(nom, grupo, num, h, d, m , a):
    grupo = grupo + '-' + num
    fecha = d + '-' + m + '-' + a
    datos = '{"nombre":'+nom+',"grupo_ProMu":'+grupo+',"altura":'+h+',"fecha":'+fecha+'}'
    mensaje = 'SEND_DATA ' + datos + '\n'
    
    print(mensaje)
    
    clientSocket.send(mensaje.encode())
    
    mensaje_rx = clientSocket.recv(2048)
    print(mensaje_rx)
    
    if mensaje_rx.decode()[0:3] == '201':
        return window_enviar_datos.info('DATO','Oh no!!!\n El salto no entró en el top 10 \n Suerte para la próxima vez')
    elif mensaje_rx.decode()[0:3] == '200':
        return window_enviar_datos.info('DATO','ENHORABUENA!!!\n El salto entró en el top 10 \n ;)')
    
nombre = ""           
def name(n):
    global nombre
    if n.isalpha()==False and n.isdigit()==False:
        nombre = nombre[:-1]
    else:
        nombre += n
    
altura = ""
def alt(h):
    global altura
    if h.isdigit():
        altura += h
    else:
        altura = altura[:-1]

grupo = ""
def group(g):
    global grupo
    grupo += g
    
numero = ""
def number(n):
    global numero
    numero += n
dia = ""
def day(d):
    global dia
    dia += d
  
mes = ""
def month(m):
    global mes
    mes += m

año = ""
def year(a):
    global año
    año += a
    
def enviar2():
    global nombre, grupo, numero, altura, dia, mes, año
    send_data(nombre, grupo, numero, altura, dia, mes, año)
    
#OBTENER-------------------------------------------------------------------------------------#

#FICHERO
fich1 = ""
def name_fich(fich):
    global fich1
    fich1 += fich 

#PESO
peso1 = ""
def peso(p):
    global peso1
    if p.isdigit():
        peso1 += p
    else:
        peso1 = peso1[:-1]
    if p == '\r':
        peso_text.append(str(p))

    
#RANKING + GET_LEADERBOARD(arqred)----------------------------------------------------------------------------------#

def get_leaderboard():
    mensaje = 'GET_LEADERBOARD\n'
    clientSocket.send(mensaje.encode())
    mensaje_rx = clientSocket.recv(2048)
    
    print(mensaje_rx.decode())
    
    if mensaje_rx[0:3] == '400':
        print('La tabla está vacía')
    else:
        rank = []
        
        while True:
            persona = clientSocket.recv(2048)
            persona = persona.decode()
            
            if persona[0:3] != '202':
                persona = persona.split(',')
                nom = persona[1].split(':')[1].strip('"')
                grupo = persona[2].split(':')[1].strip('"')
                altura = persona[3].split(':')[1].strip('"')
                
                persona = [nom, grupo, altura]
                rank.append(persona)
                
            else:
                break
        return rank

def leader():
    get_leaderboard()
    rang()
    window_obtener_datos.hide()
    window_ranking.show()

ran1 = ""
ran2 = ""
ran3 = ""
ran4 = ""
ran5 = ""
ran6 = ""
ran7 = ""
ran8 = ""
ran9 = ""
ran10 = ""
def rang():
    global ran1, ran2, ran3, ran4, ran5, ran6, ran7, ran8, ran9, ran10
    rank = get_leaderboard()
    r1 = rank[0]
    r2 = rank[1]
    r3 = rank[2]
    r4 = rank[3]
    r5 = rank[4]
    r6 = rank[5]
    r7 = rank[6]
    r8 = rank[7]
    r9 = rank[8]
    r10 = rank[9]
    for i in r1:
        ran1 += i + '\t'
    print(ran1)
    text_rank1.append(str(ran1))
    for i in r2:
        ran2 += i + '\t'
    print(ran2)
    text_rank2.append(str(ran2))
    for i in r3:
        ran3 += i + '\t'
    print(ran3)
    text_rank3.append(str(ran3))
    for i in r4:
        ran4 += i + '\t'
    print(ran4)
    text_rank4.append(str(ran4))
    for i in r5:
        ran5+= i + '\t'
    print(ran5)
    text_rank5.append(str(ran5))
    for i in r6:
        ran6 += i + '\t'
    print(ran6)
    text_rank6.append(str(ran6))
    for i in r7:
        ran7 += i + '\t'
    print(ran7)
    text_rank7.append(str(ran7))
    for i in r8:
        ran8 += i + '\t'
    print(ran8)
    text_rank8.append(str(ran8))
    for i in r9:
        ran9 += i + '\t'
    print(ran9)
    text_rank9.append(str(ran9))
    for i in r10:
        ran10 += i + '\t'
    print(ran10)
    text_rank10.append(str(ran10))  

#GRÁFICAS-------------------------------------------------------------------------------------------------#

def grafica_potencia():
    window_obtener_datos.hide()
    window_datos.show()
    fuerza_gui()
    potencia_gui()
    altura_gui()
    pot2()
       
def grafica_fuerza():
    window_obtener_datos.hide()
    window_datos.show()
    fuerza_gui()
    potencia_gui()
    altura_gui()
    graf_f2()
    
def grafica_velocidad():
    window_obtener_datos.hide()
    window_datos.show()
    fuerza_gui()
    potencia_gui()
    altura_gui()
    graf_v()
    
def grafica_aceleracion():
    window_obtener_datos.hide()
    window_datos.show()
    fuerza_gui()
    potencia_gui()
    altura_gui()
    graf_acel()

fuerza1 = ""
cont_f = 0
def fuerza_gui():
    global fuerza1, cont_f
    fuerza1 = graf_f()
    cont_f += 1
    if cont_f==1:
        text_f.append(str(fuerza1))
    
altura1 = ""
cont_a = 0
def altura_gui():
    global altura1, cont_a
    altura1 = altura2()
    cont_a += 1
    if cont_a==1:
        text_a.append(str(altura1))
    
potencia1 = ""
cont_p = 0
def potencia_gui():
    global potencia1, cont_p
    potencia1 = pot()
    cont_p += 1
    if cont_p==1:
        text_p.append(str(potencia1))
    
#QUIT: salir del programa------------------------------------------------------#

def QUIT():
    mensaje = 'QUIT ' + '\n'
    clientSocket.send(mensaje.encode())
    print('\nFIN DEL PROGRAMA')
    clientSocket.close()
    
 
#WIDGETS-----------
    
#LOGIN
box_bienvenida = Box(app, width= 325 , height = 100 )
text_bienvenida = Text(box_bienvenida, text = 'BIENVENID@   A  ', align = 'left')
text_bienvenida.font = 'Abolition'
text_bienvenida.text_size = 17
logo = Picture(box_bienvenida,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'right')

llave = Picture(app , image = 'llave.gif', width = 100, height = 100)

#USUARIO---------------------------
input_asked = 'usuario'
box_user = Box(app, width = 150, height = 50)
text_user = Text(box_user, text = 'USUARIO', align = 'left')
text_user.font = 'Abolition'
user_textbox = TextBox(box_user, align = 'left', command = usuario)
user_textbox.bg = '#9ccac1'

#CONTRASEÑA------------------------------
spacef = Box(app, align = 'top', height = 5)
box_passw = Box(app, width = 200, height = 50)
text_passw = Text(box_passw, text = 'CONTRASEÑA' , align = 'left')
text_passw.font = 'Abolition'
passw = TextBox(box_passw, align = 'left', command = contraseña, hide_text=True)
passw.bg = '#9ccac1'

spacef = Box(app, align = 'top', height = 5)
acceder_button = PushButton(app, text = 'ACCEDER', pady = 15, padx = 15, command = acceder)
acceder_button.font = 'Abolition'
acceder_button.text_size = 15
acceder_button.bg = '#91bb6e'

#PANTALLA INICIO

window_inicio = Window(app, bg = "#289687",
          title ="FrogUp",
          height = 890,
          width = 550)
window_inicio.hide()
logo = Picture(window_inicio,
               image = 'Logo_definitivo.gif',
               width = 450,
               height = 300)

enviar_datos = PushButton(window_inicio, text ='ENVIAR DATOS', pady=40,
    padx=90, align = 'top', command = enviar)
enviar_datos.font = 'Abolition'
enviar_datos.text_size = 18
enviar_datos.bg = '#91bb6e'

obtener_datos = PushButton(window_inicio, text =  'OBTENER DATOS', pady=40,
    padx=84, align = 'top', command = obtener)
obtener_datos.font = 'Abolition'
obtener_datos.text_size = 18
obtener_datos.bg = '#91bb6e'

ranita_salta  = Picture(window_inicio, image = 'ran5.gif', width = 270, height = 225)

info = PushButton(window_inicio, image = 'info4.gif', align = 'right', width = 50, height = 50, command = info_frogup)

#ENVIAR DATOS-----------------------------------------------------------------------------------------------------------


window_enviar_datos = Window(app, bg = "#289687",
                             title = 'ENVIAR DATOS',
                             height = 750,
                             width = 550)
window_enviar_datos.hide()
space = Box(window_enviar_datos, align = 'top', height = 20)
logo = Picture(window_enviar_datos,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

space1 = Box(window_enviar_datos, align = 'top', height = 5)
box = Box(window_enviar_datos , align = 'top', border = False)
introduzca = Text(box, text = 'INTRODUZCA LOS DATOS DE SU SALTO:', align = 'left')
introduzca.font = 'Abolition'
introduzca.text_size = 17

spacen = Box(window_enviar_datos, align = 'top', height = 5)
box_nombre = Box(window_enviar_datos , align = 'top', border = False)
nombre_text = Text(box_nombre, text = 'NOMBRE:', align = 'left')
nombre_text.font = 'Abolition'
nombre_text.text_size = 15
nombre_textbox = TextBox(box_nombre, align = 'left', command = name)
nombre_textbox.bg = '#9ccac1'

spaceg = Box(window_enviar_datos, align = 'top', height = 5)
box_grupo = Box(window_enviar_datos , align = 'top', border = False)
grupo_text = Text(box_grupo, text = 'GRUPO:', align = 'left')
grupo_text.font = 'Abolition'
grupo_text.text_size = 15
grupo_combo = Combo(box_grupo, options = ['A1', 'A2', 'A3'], selected = None, align = 'left', command = group)
grupo_combo.bg = '#9ccac1'
numero_combo = Combo(box_grupo, options = ['1','2','3', '4', '5', '6', '7' ], selected = None, align = 'left', command = number)
numero_combo.bg = '#9ccac1'

spacea = Box(window_enviar_datos, align = 'top', height = 5)
box_altura = Box(window_enviar_datos, align = 'top', border = False )
recordatorio_altura = PushButton(box_altura, image = 'Infonom.gif', width = 50, height = 50, align = 'left', command = info_medidas)
altura_text = Text(box_altura, text = 'ALTURA:', align = 'left')
altura_text.font = 'Abolition'
altura_text.text_size = 15
altura_textbox = TextBox(box_altura, align = 'left', command = alt)
altura_textbox.bg = '#9ccac1'
mm = Text(box_altura, text = 'mm', align = 'left')
mm.text_size = 10

spacef = Box(window_enviar_datos, align = 'top', height = 5)
box_fecha= Box(window_enviar_datos , align = 'top', border = False)
fecha_text = Text(box_fecha, text = 'FECHA:', align = 'left')
fecha_text.font = 'Abolition'
fecha_text.text_size = 15
dia_combo = Combo(box_fecha, options = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                                        '21', '22', '23', '24', '25', '26', '27', '28', '29',
                                        '30', '31'], align = 'left', command = day)
dia_combo.bg = '#9ccac1'
mes_combo = Combo(box_fecha, options = ['Enero','Febrero','Marzo', 'Abril', 'Mayo', 'Junio',
                                        'Julio', 'Agosto', 'Septiembre', 'Noviembre', 'Diciembre'],
                                        selected = None, align = 'left', command = month)
mes_combo.bg = '#9ccac1'
año_combo = Combo(box_fecha, options = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012',
                    '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022'],
                    selected = None, align = 'left', command = year)
año_combo.bg = '#9ccac1'


space2 = Box(window_enviar_datos, align = 'top', height = 70)
enviar_datos = PushButton(window_enviar_datos, text ='ENVIAR DATOS', pady=40,
    padx=90, command = enviar2)
enviar_datos.font = 'Abolition'
enviar_datos.text_size = 18
enviar_datos.bg = '#91bb6e'

box_fin = Box(window_enviar_datos, width = 550, height = 50, align = 'bottom')
inicio = PushButton(box_fin, text = 'INICIO', align = 'left', command = inicio1 )
inicio.font = 'Abolition'
inicio.bg = '#77995b'
salir = PushButton(box_fin, image = 'salir.gif', align = 'right',width = 50, height = 50, command = close1)    


#OBTENER_DATOS-----------------------------------------------------------------------------------------------
#FICHERO
window_fichero = Window(app, bg = "#289687",
                             title = 'FICHERO',
                             height = 450,
                             width = 550)
window_fichero.hide()

space = Box(window_fichero, align = 'top', height = 20)
logo = Picture(window_fichero,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

introduce_fichero = Text(window_fichero, text = 'INTRODUZCA EL NOMBRE\n DE SU FICHERO', align = 'top')
introduce_fichero.font = 'Abolition'
introduce_fichero.text_size = 17

fichero_box = Box(window_fichero, align = 'top', width = 450 , height = 100)
fichero_picture = Picture(fichero_box, image = 'Fichero.gif', width = 100 , height = 100, align = 'left')
nombre_fichero = TextBox(fichero_box, align = 'left', width = 30, command = name_fich)
nombre_fichero.bg = '#9ccac1'

space1 = Box(window_fichero, align = 'top', height = 10)
continuar_button = PushButton(window_fichero, text ='CONTINUAR', pady=20,
    padx=20, command = continuar_fich)
continuar_button.font = 'Abolition'
continuar_button.text_size = 15
continuar_button.bg = '#91bb6e'

box_fin = Box(window_fichero, width = 550, height = 50, align = 'bottom')
atras = PushButton(box_fin, text = 'VOLVER', align = 'left', command = volver1 )
atras.font = 'Abolition'
atras.bg = '#77995b'
salir = PushButton(box_fin, image = 'salir.gif', align = 'right',width = 30, height = 30, command = close2)

#PESO
window_peso = Window(app, bg = "#289687",
                             title = 'PESO',
                             height = 350,
                             width = 450)
window_peso.hide()

space = Box(window_peso, align = 'top', height = 20)
logo = Picture(window_peso,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

introduce_peso = Text(window_peso, text = 'INTRODUZCA SU PESO', align = 'top')
introduce_peso.font = 'Abolition'
introduce_peso.text_size = 17

space1 = Box(window_peso, align = 'top', height = 3)
peso_box = Box(window_peso)
peso_picture = Picture(peso_box, image = 'Peso.gif', width = 100, height = 100, align = 'left')
peso_textbox = TextBox(peso_box, width = 100, height = 50, command = peso, align = 'left')
peso_textbox.font = 'Abolition'
peso_textbox.text_size = 15
peso_textbox.bg = '#9ccac1'


space2 = Box(window_peso, align = 'top', height = 5)
peso_box2 = Box(window_peso)
peso_text = Text(peso_box2, text = 'Su peso es :' + str(peso1), align = 'left')
peso_text.font = 'Abolition'
kg_text = Text(peso_box2, text = 'KG', align = 'right')
kg_text.font = 'Abolition'

box_fin = Box(window_peso, width = 450, height = 50, align = 'bottom')
continuar = PushButton(box_fin, text = 'CONTINUAR', align = 'right' , command = continuar_peso)
continuar.font = 'Abolition'
continuar.bg = '#77995b'

#PRINCIPAL-------------------------------------------------------------------------------------------------#
window_obtener_datos = Window(app, bg = "#289687",
                             title = 'OBTENER DATOS',
                             height = 750,
                             width = 550)
window_obtener_datos.hide()

space = Box(window_obtener_datos, align = 'top', height = 20)
logo = Picture(window_obtener_datos,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

space1 = Box(window_obtener_datos, align = 'top', height = 20)
text_obtener = Text(window_obtener_datos, text = 'OBTENER:')
text_obtener.font = 'Abolition'
text_obtener.text_size = 17

space2 = Box(window_obtener_datos, align = 'top', height = 10)
leaderboard = PushButton(window_obtener_datos, text = 'LEADERBOARD', command = leader)
leaderboard.font = 'Abolition'
leaderboard.text_size = 15
leaderboard.bg = '#91bb6e'

space3 = Box(window_obtener_datos, align = 'top', height = 10)
text_graficas = Text(window_obtener_datos, text = 'GRÁFICAS')
text_graficas.font = 'Abolition'
text_graficas.text_size = 10

graficas_box = Box(window_obtener_datos, align = 'top', layout = 'grid')
potencia_button = PushButton(graficas_box, image = 'Potencia.gif' , width = 150 , height = 150, grid = [0,0], command = grafica_potencia)
potencia_button.bg = '#91bb6e'
fuerza_button = PushButton(graficas_box, image = 'Fuerza.gif', width = 150 , height = 150, grid = [0,2], command = grafica_fuerza )
fuerza_button.bg = '#54706d'
aceleracion_button = PushButton(graficas_box, image = 'Aceleración.gif' , width = 150 , height = 150, grid = [2,0], command = grafica_aceleracion )
aceleracion_button.bg = '#8eb327'
velocidad_button = PushButton(graficas_box, image = 'Velocidad.gif', width = 150 , height = 150, grid = [2,2], command = grafica_velocidad )
velocidad_button.bg = '#069766'

box_fin = Box(window_obtener_datos, width = 550, height = 50, align = 'bottom')
inicio = PushButton(box_fin, text = 'INICIO', align = 'left' , command = inicio2)
inicio.font = 'Abolition'
inicio.bg = '#77995b'
salir = PushButton(box_fin, image = 'salir.gif', align = 'right',width = 50, height = 50, command = close3)

#RANKING

window_ranking = Window(app, bg = "#289687",
                             title = 'RANKING',
                             height = 750,
                             width = 650)
window_ranking.hide()

space = Box(window_ranking, align = 'top', height = 20)
logo = Picture(window_ranking,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

ranking = Text(window_ranking, text = 'RANKING')
ranking.font = 'Abolition'
ranking.text_size = 20
ranking_box = Box(window_ranking)

rank1_box = Box(ranking_box, width = 550, height =50)
gold = Picture(rank1_box, image = 'Gold.gif', height = 50, width = 50, align = 'left')
text_rank1 = Text(rank1_box, text = '1.-\t' + str(ran1) , align = 'left')
text_rank1.font = 'Abolition'
text_rank1.text_size = 10
text_mm = Text(rank1_box, text = 'mm', align = 'left')

rank2_box = Box(ranking_box, width = 550, height =50)
silver = Picture(rank2_box, image = 'Silver.gif', height = 50, width = 50, align = 'left')
text_rank2 = Text(rank2_box, text = '2.-\t' + str(ran2), align = 'left')
text_rank2.font = 'Abolition'
text_rank2.text_size = 10
text_mm = Text(rank2_box, text = 'mm', align = 'left')

rank3_box = Box(ranking_box, width = 550, height =50)
bronze = Picture(rank3_box, image = 'Bronze.gif', height = 50, width = 50, align = 'left')
text_rank3 = Text(rank3_box, text = '3.-\t' + str(ran3), align = 'left')
text_rank3.font = 'Abolition'
text_rank3.text_size = 10
text_mm = Text(rank3_box, text = 'mm', align = 'left')

rank4_box = Box(ranking_box, width = 450, height =50)
text_rank4 = Text(rank4_box, text = '4.-\t' + str(ran4) , align = 'left')
text_rank4.font = 'Abolition'
text_rank4.text_size = 10
text_mm = Text(rank4_box, text = 'mm', align = 'left')

rank5_box = Box(ranking_box, width = 450, height =50)
text_rank5 = Text(rank5_box, text = '5.-\t' + str(ran5), align = 'left')
text_rank5.font = 'Abolition'
text_rank5.text_size = 10
text_mm = Text(rank5_box, text = 'mm', align = 'left')

rank6_box = Box(ranking_box, width = 450, height =50)
text_rank6 = Text(rank6_box, text = '6.-\t' + str(ran6), align = 'left')
text_rank6.font = 'Abolition'
text_rank6.text_size = 10
text_mm = Text(rank6_box, text = 'mm', align = 'left')

rank7_box = Box(ranking_box, width = 450, height =50)
text_rank7 = Text(rank7_box, text = '7.-\t' + str(ran7) , align = 'left')
text_rank7.font = 'Abolition'
text_rank7.text_size = 10
text_mm = Text(rank7_box, text = 'mm', align = 'left')

rank8_box = Box(ranking_box, width = 450, height =50)
text_rank8 = Text(rank8_box, text = '8.-\t' + str(ran8), align = 'left')
text_rank8.font = 'Abolition'
text_rank8.text_size = 10
text_mm = Text(rank8_box, text = 'mm', align = 'left')

rank9_box = Box(ranking_box, width = 450, height =50)
text_rank9 = Text(rank9_box, text = '9.-\t' + str(ran9) , align = 'left')
text_rank9.font = 'Abolition'
text_rank9.text_size = 10
text_mm = Text(rank9_box, text = 'mm', align = 'left')


rank10_box = Box(ranking_box, width = 450, height =50)
text_rank10 = Text(rank10_box, text = '10.-\t' + str(ran10), align = 'left')
text_rank10.font = 'Abolition'
text_rank10.text_size = 10
text_mm = Text(rank10_box, text = 'mm', align = 'left')


box_fin = Box(window_ranking, width = 650, height = 50, align = 'bottom')
atras = PushButton(box_fin, text = 'VOLVER', align = 'left', command = volver2 )
atras.font = 'Abolition'
atras.bg = '#77995b'
salir = PushButton(box_fin, image = 'salir.gif', align = 'right',width = 50, height = 50, command = close4)

#GRÁFICAS
window_datos = Window(app, bg = "#289687",
                             title = 'DATOS + GRÁFICAS',
                             height = 400,
                             width = 450)
window_datos.hide()
space = Box(window_datos, align = 'top', height = 20)
logo = Picture(window_datos,
               image = 'Logo_definitivo.gif',
               width = 150,
               height = 100, align = 'top')

datos_text = Text(window_datos, text = 'DATOS:')
datos_text.font = 'Abolition'
datos_text.text_size = 17

box_fuerza =  Box(window_datos)
text_f = Text(box_fuerza, text="Fuerza de tu salto:" + str(fuerza1), align = 'left') #+f
text_f.font = 'Abolition'
text_n = Text(box_fuerza, text = 'N', align = 'left')
text_n.font = 'Abolition'

box_altura = Box(window_datos)
text_a = Text(box_altura, text="Altura de tu salto:" + str(altura1), align = 'left')
text_a.font = 'Abolition'
text_m = Text(box_altura, text = 'm', align = 'left')
text_m.font = 'Abolition'

box_potencia = Box(window_datos)
text_p = Text(box_potencia, text="Potencia de tu salto:" + str(potencia1), align = 'left') 
text_p.font = 'Abolition'
text_w = Text(box_potencia, text = 'w', align = 'left')
text_w.font = 'Abolition'

box_fin = Box(window_datos, width = 450, height = 50, align = 'bottom')
inicio = PushButton(box_fin, text = 'INICIO', align = 'left', command = inicio3)
inicio.font = 'Abolition'
inicio.bg = '#77995b'
salir = PushButton(box_fin, image = 'salir.gif', align = 'right',width = 50, height = 50, command = close5)



#DISPLAY---------------------------------
app.display()