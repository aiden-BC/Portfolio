//LIBRERÍAS-----------------------------------------------------------------------
#include <MD_MAX72xx.h>
#include <SPI.h>
#include <Wire.h>

//CONSTANTES----------------------------------------------------------------------
//LCD-------------------------------
#define LCD_I2C_ADDR        0x3E

#define LCD_MODE_COMMAND    0x00
#define LCD_MODE_DATA       0x40

#define LCD_CLEARDISPLAY    0x01
#define LCD_RETURNHOME      0x02
#define LCD_ENTRYMODESET    0x04
#define LCD_DISPLAYCONTROL  0x08
#define LCD_CURSORSHIFT     0x10
#define LCD_FUNCTIONSET     0x20
#define LCD_SETCGRAMADDR    0x40
#define LCD_SETDDRAMADDR    0x80

#define LCD_8BITMODE        0x10
#define LCD_4BITMODE        0x00
#define LCD_2LINE           0x08
#define LCD_1LINE           0x00
#define LCD_5x10DOTS        0x04
#define LCD_5x8DOTS         0x00

#define LCD_DISPLAYON       0x04
#define LCD_DISPLAYOFF      0x00
#define LCD_CURSORON        0x02
#define LCD_CURSOROFF       0x00
#define LCD_BLINKON         0x01
#define LCD_BLINKOFF        0x00

#define LCD_ENTRYRIGHT      0x00
#define LCD_ENTRYLEFT       0x02
#define LCD_ENTRYSHIFTINC   0x01
#define LCD_ENTRYSHIFTDEC   0x00

//Pines-------------------------------
#define CLK_PIN   13  // or SCK
#define DATA_PIN  11  // or MOSI
#define CS_PIN    10  // or SS

const int Xin= A0; // X Input Pin -- pin analógico 0
const int Yin = A1; // Y Input Pin -- pin analógico 1

//Matriz de LEDs----------------------
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4 //nº de matrices de led
MD_MAX72XX mx = MD_MAX72XX(HARDWARE_TYPE, DATA_PIN, CLK_PIN, CS_PIN, MAX_DEVICES);

//Scrolling parameters----------------
#define CHAR_SPACING  1 // pixels between characters
bool termina=false;

//Global message buffers shared by Serial and Scrolling functions
#define BUF_SIZE  75
uint8_t mensaje[BUF_SIZE] = { "SNAKE            " };
uint16_t  scrollDelay = 50;  // in milliseconds

//Juego-------------------------------
const short longInicial = 4;

//Constantes de direccion
const short arriba = 1;
const short abajo = 3;
const short derecha = 2;
const short izquierda = 4;

int matriz[8][32] = {}; //matriz que guarda los leds encendidos de la placa

//VARIABLES-----------------------------------------------------------------------
int xVal, yVal; //valores del joystick
bool gameOver = false;
int puntos = 0;
String texto;
String pt = "";

//Constructor
struct Punto{
  int fil = 0;
  int col = 0;
  Punto(int fil=0, int col=0): fil(fil), col(col){}
};

//Serpiente---------------------------
struct Punto snake; //crea la serpiente
int longitud = longInicial; //longitud
int direccion = 3; //dirección inicial -- derecha

//Comida
struct Punto manzana(-1, -1); //creamos la manzana pero la ponemos fuera del tablero

//FUNCIONES-----------------------------------------------------------------------
//Joystick----------------------------
int joystickReadX(){
  return analogRead(Xin);
}

int joystickReadY(){
  return analogRead(Yin);
}

//LCD---------------------------------
void lcdSend(unsigned char value, unsigned char mode){
  Wire.beginTransmission(LCD_I2C_ADDR);
  Wire.write(mode);
  Wire.write(value);
  Wire.endTransmission();
  delayMicroseconds(50);
}

void lcdSetup(){
  Wire.begin();
  delay(50);

  lcdSend(LCD_FUNCTIONSET | LCD_8BITMODE | LCD_2LINE | LCD_5x8DOTS, LCD_MODE_COMMAND);
  lcdSend(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF, LCD_MODE_COMMAND);
  lcdSend(LCD_CLEARDISPLAY, LCD_MODE_COMMAND);
  delayMicroseconds(2000);
  lcdSend(LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDEC, LCD_MODE_COMMAND);
}

void lcdClear(){
  lcdSend(LCD_CLEARDISPLAY, LCD_MODE_COMMAND);
  delayMicroseconds(2000);
}

void lcdSetCursor(int x, int y){
  unsigned char value = 0;

  if (y>0){
    value = 0x40;
  }
  value += x;

  lcdSend(LCD_SETDDRAMADDR | value, LCD_MODE_COMMAND);
}

void lcdPrint(const char *str){
  while (*str != 0){
    lcdSend(*str, LCD_MODE_DATA);
    str++;
  }
}

//Juego-------------------------------
void joystickDirection(){
  int previousDir = direccion;
  long tiempo = millis();
  xVal = joystickReadX();
  yVal = joystickReadY();

  if (xVal > 550){
    direccion = derecha;
  }

  if (xVal < 450){
    direccion = izquierda;
  }

  if (yVal > 550){
    direccion = arriba; 
  }

  if (yVal < 450){
    direccion = abajo;
  }

  //ignora los cambios de dirección de 180 grados
  if (previousDir == direccion-2 || previousDir == direccion+2){
    direccion = previousDir;
  }


}

void movimiento(){
  switch(direccion){
    case arriba:
      snake.fil--;
      limites();
      mx.setPoint(snake.fil, snake.col, true);
      break;
    case abajo:
      snake.fil++;
      limites();
      mx.setPoint(snake.fil, snake.col, true);
      break;
    case derecha:
      snake.col++;
      limites();
      mx.setPoint(snake.fil, snake.col, true);
      break;
    case izquierda:
      snake.col--;
      limites();
      mx.setPoint(snake.fil, snake.col, true);
      break;
    default:
      return;
  }

  //si te chocas con la serpiente mueres
  if (matriz[snake.fil][snake.col] > 0){
    Serial.println("chocó");
    reinicio();
    return;
  }

  matriz[snake.fil][snake.col] = longitud + 1;

  //enciende y apaga los LEDS segun se mueve la serpiente
  for (int fil=0; fil<8;fil++){
    for (int col=0; col<32; col++){
      if (matriz[fil][col] > 0){
        matriz[fil][col]--;
      }
      if (matriz[fil][col] == 0){
        mx.setPoint(fil, col, false);
      }else{
        mx.setPoint(fil, col, true);
      }

    }
  }
}

void limites(){
  if(snake.col<0){
    snake.col += 32;
  }
  if(snake.col>31){
    snake.col -=32;
  }
  if(snake.fil<0){
    snake.fil +=8;
  }
  if(snake.fil>7){
    snake.fil -=8;
  }
}

void manzanas(){
  if (manzana.fil == -1 || manzana.col == -1){ //si no hay manzana en el tablero
    do{
      manzana.fil = random(8);
      manzana.col = random(32);
    }while(matriz[manzana.fil][manzana.col] > 0);//para que no genere la manzana encima de la serpiente
  }
  mx.setPoint(manzana.fil, manzana.col, true); //enciende el LED donde se ha generado la comida
}

void comer(){
  if (snake.fil == manzana.fil && snake.col == manzana.col){
    //resetea la comida
    manzana.fil = -1;
    manzana.col = -1;

    longitud++; //aumenta la longitud de la serpiente
    puntos++; //suma 1 punto

    //recorre la matriz de leds
    for (int fil=0;fil<8;fil++){
      for (int col=0;col<32;col++){
        //si un led está encendido, incrementa su valor a 2
        //así cuando se ejecute la función de movimiento se pondrá a 1 y quedará encendido
        if(matriz[fil][col]>0){ 
          matriz[fil][col]++;
        }
      }
    }
  }
}

void puntuacion(){
  pt = String(puntos);
  texto = "Puntuacion: " + pt;
  lcdSetCursor(0,0);
  lcdPrint(texto.c_str());
}

void inicio(){
  lcdClear();
  lcdSetCursor(0,0);
  lcdPrint("Bienvenid@! :D");

  strcpy(mensaje, "SNAKE            ");
  do{
    scrollText();
  }while(termina==false);


  lcdClear();
  lcdSetCursor(0,0);
}

void reinicio(){
  //reinicia el juego
  puntos = 0;
  longitud = longInicial;
  termina = false;

  for (int fil=0;fil<8;fil++){
    for (int col=0;col<32;col++){
      matriz[fil][col] = 0;
    }
  }
  delay(500);
  mx.clear();

  lcdSetCursor(0,0);
  lcdPrint("HAS PERDIDO :(");

  strcpy(mensaje, "GAME OVER           ");
  do{
    scrollText();
  }while(termina==false);

  delay(2000);
  lcdClear();

  snake.fil = random(8);
  snake.col = random(32);
  manzana.fil = -1;
  manzana.col = -1;
	termina = false;

  inicio(); 
  
}

//Animaciones-------------------------
uint8_t scrollDataSource(uint8_t dev, MD_MAX72XX::transformType_t t){
  // Callback function for data that is required for scrolling into the display

  static uint8_t* p = mensaje;
  static enum {LOAD_CHAR, SHOW_CHAR, BETWEEN_CHAR } state = LOAD_CHAR;
  static uint8_t  curLen, showLen;
  static uint8_t  cBuf[15];
  uint8_t colData = 0;    // blank column is the default

  // finite state machine to control what we do on the callback
  switch(state)
  {
    case LOAD_CHAR: // Load the next character from the font table
      showLen = mx.getChar(*p++, sizeof(cBuf)/sizeof(cBuf[0]), cBuf);
      curLen = 0;
      state = SHOW_CHAR;

      // if we reached end of message, opportunity to load the next
      if (*p == '\0')
      {
        p = mensaje;     // reset the pointer to start of message
        termina=true;
      }
      // !! deliberately fall through to next state to start displaying

    case SHOW_CHAR: // display the next part of the character
      colData = cBuf[curLen++];
      if (curLen == showLen)
      {
        showLen = CHAR_SPACING;
        curLen = 0;
        state = BETWEEN_CHAR;
      }
      break;

    case BETWEEN_CHAR: // display inter-character spacing (blank columns)
      colData = 0;
      curLen++;
      if (curLen == showLen)
        state = LOAD_CHAR;
      break;

    default:
      state = LOAD_CHAR;
  }

  return(colData);
}

void scrollText(void){
  static uint32_t	prevTime = 0;

  // Is it time to scroll the text?
  if (millis()-prevTime >= scrollDelay)
  {
    mx.transform(MD_MAX72XX::TSL);  // scroll along - the callback will load all the data
    prevTime = millis();      // starting point for next time
  }
}

//PROGRAMA------------------------------------------------------------------------
void setup() {
  // put your setup code here, to run once:
  lcdSetup();
  lcdSetCursor(0,0);

  mx.begin();
  mx.control(MD_MAX72XX::INTENSITY, 2);
  mx.control(MD_MAX72XX::UPDATE, MD_MAX72XX::ON);
  mx.clear();
  mx.control(MD_MAX72XX::UPDATE, MD_MAX72XX::ON);

  snake.fil = random(8);
  snake.col = random(32);

  Serial.begin(115200);

	mx.setShiftDataInCallback(scrollDataSource);
  inicio();

}

void loop() {
  // put your main code here, to run repeatedly:
  joystickDirection();
  manzanas();
  movimiento();
  comer();
  puntuacion();
}