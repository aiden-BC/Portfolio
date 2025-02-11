##############################################################
#                 PROYECTO INTERA: Theremin                  #
#                                                            #
#   Aiden Bugarín Carreira                                   #
#   Adrián Martínez Quivén                                   #
##############################################################


#LIBRERIAS------------------------------------------
import math
import machine
import utime
import wifiCfg
import imu
from m5stack import lcd, rgb
from uosc.client import Client

#CONFIGURACION--------------------------------------------
print("Conectando...")
wifiCfg.connect("GTDM", "12345678", 30000, True)

if wifiCfg.wlan_sta.isconnected():
    wifi_ip = ""
    wifi_config = wifiCfg.wlan_sta.ifconfig()
    if wifi_config is not None:
        wifi_ip = wifi_config[0]
        print("Conectado con IP:", wifi_ip)
else:
    print("No conectado")

#configuramos pines
trig_pin_B = machine.Pin(26, machine.Pin.OUT)
echo_pin_B = machine.Pin(36, machine.Pin.IN)
#trig_pin_C = machine.Pin(17, machine.Pin.OUT)
#echo_pin_C = machine.Pin(16, machine.Pin.IN)
print("bloque A")

#CONSTANTES-----------------------------------------------
mpu = imu.IMU() # creo el objeto mpu con acceso al MPU6886
server_ip = "192.168.0.108" # IP del ordenador con TouchOSC
tx_port = 22201 #puerto recepción TouchOSC
osc = Client(server_ip, tx_port)
print("Bloque B")

#velocidad del sonido para T=20º
c = 331.59 * math.sqrt(1 + 20/273.15)

#mapeo distancias y notas musicales
mapeo_notas = {
    (-1, 5): {"frecuencia": 131, "nota": "C3", "color":lcd.RED},
    (5, 10): {"frecuencia": 147, "nota": "D3", "color":lcd.ORANGE},
    (10, 15): {"frecuencia": 165, "nota": "E3", "color":lcd.YELLOW},
    (15, 20): {"frecuencia": 175, "nota": "F3", "color":lcd.GREEN},
    (20, 25): {"frecuencia": 196, "nota": "G3", "color":lcd.CYAN},
    (25, 30): {"frecuencia": 220, "nota": "A3", "color":lcd.BLUE},
    (30, 35): {"frecuencia": 247, "nota": "B3", "color":lcd.PURPLE},
    (35, 40): {"frecuencia": 261, "nota": "C4", "color":lcd.RED},
    (40, 45): {"frecuencia": 294, "nota": "D4", "color":lcd.ORANGE},
    (45, 50): {"frecuencia": 330, "nota": "E4", "color":lcd.YELLOW},
    (50, 55): {"frecuencia": 349, "nota": "F4", "color":lcd.GREEN},
    (55, 60): {"frecuencia": 392, "nota": "G4", "color":lcd.CYAN},
    (60, 65): {"frecuencia": 440, "nota": "A4", "color":lcd.BLUE},
    (65, 70): {"frecuencia": 494, "nota": "B4", "color":lcd.PURPLE},
    (70, 100): {"frecuencia": 523, "nota": "C5", "color":lcd.RED},
}
print("Bloque C")

#VARIABLES------------------------------------------------
f = 440
vol = 1

#FUNCIONES------------------------------------------------
start = utime.ticks_ms()

#funcion que calcula la distancia a la que esta el objeto
def distancia():
    trig_pin_B.on()
    utime.sleep_us(10)
    trig_pin_B.off()

    #trig_pin_C.on()
    utime.sleep_us(10)
    #trig_pin_C.off()

    pulse_time_B = machine.time_pulse_us(echo_pin_B, 1, 30000)
    #pulse_time_C = machine.time_pulse_us(echo_pin_C, 1, 30000)

    d_B = pulse_time_B*10**(-4) * c / 2
    #d_C = pulse_time_C*10**(-4) * c / 2

    return d_B#, d_C

def display(nota, color):
    lcd.circle(160,120,200,lcd.BLACK,lcd.BLACK)
    lcd.print(nota, 120, 90, color)
    rgb.setColorAll(color)

while True:
    lcd.font(lcd.FONT_DejaVu72, transparent=False) #cambio el tamaño de la letra

    if utime.ticks_diff(utime.ticks_ms(), start)>50:
        distB = distancia()
        #print(distB)
        #print(distC)
        start = utime.ticks_ms()

        # if (distC>20):
        #     vol = 1
        # else:
        #     vol = distC/20

        # Calcular la frecuencia y la nota según la distancia
        for rango, info_nota in mapeo_notas.items():
            if rango[0] < distB <= rango[1]:
                f = info_nota["frecuencia"]
                nota = info_nota["nota"]
                color = info_nota["color"]
                break
        else:
            # Si no se cumple ninguna condición, establecer valores predeterminados
            f = 1
            nota = ""
            color = lcd.BLACK

        display(nota, color)
        x = math.log(f/20)/6.6
        osc.send(b"/1/fader1", x)
        osc.send(b"/1/fader3", vol)
   