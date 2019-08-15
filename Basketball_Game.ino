#include <WiFi.h> //Connect to WiFi Network
#include <SPI.h>
#include <TFT_eSPI.h>
#include <mpu9255_esp32.h>
#include<math.h>
#include<string.h>

#define BACKGROUND TFT_BLACK
#define BALL_COLOR TFT_WHITE

#define IDLE 0
#define PLAY 1
#define UPDATE 2

#define BOP 0
#define SHOUT 1
#define TILT 2
#define SPIN 3
#define WAIT 4


MPU9255 imu; //imu object called, appropriately, imu
TFT_eSPI tft = TFT_eSPI();
// Set up the TFT object

const int LOOP_PERIOD = 10;
unsigned long primary_timer; //main loop timer

const int BUTTON_PIN = 5;
int button_flag = 0;

float x,y,z;

float x_acc_total = 0;
int x_counter = 0;
float x_avg = 0;

float y_acc_total = 0;
int y_counter = 0;
float y_avg = 0;

float z_acc_total = 0;
int z_counter = 0;
float z_avg = 0;

uint32_t button_press_time;

float x_ang,y_ang,z_ang;

char network[] = "6s08";  //SSID for 6.08 Lab
char password[] = "iesc6s08"; //Password for 6.08 Lab
char kerberos[] = "cjoshea";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[OUT_BUFFER_SIZE];
char response_buffer[OUT_BUFFER_SIZE];

class Button{
  public:
  uint32_t t_of_state_2;
  uint32_t t_of_button_change;    
  uint32_t debounce_time;
  uint32_t long_press_time;
  uint8_t pin;
  uint8_t flag;
  bool button_pressed;
  uint8_t state; // This is public for the sake of convenience
  Button(int p) {
  flag = 0;  
    state = 0;
    pin = p;
    t_of_state_2 = millis(); //init
    t_of_button_change = millis(); //init
    debounce_time = 10;
    long_press_time = 1000;
    button_pressed = 0;
  }
  void read() {
    uint8_t button_state = digitalRead(pin);  
    button_pressed = !button_state;
  }
  int update() {
    read();
  flag = 0;
  if (state==0) { //Rest state
    flag = 0;
    if (button_pressed) {
      state = 1;
    }
  } else if (state==1) { //Button is pressed
      flag = 1;
      if(!button_pressed){
        state = 2;
      }
  } else if (state==2) { //Button just released
      state = 3;
  } else if (state==3) { //Button starts its rest state
      flag = 2;
      state = 0;
  }
  return flag;
  }
};
 

void setup() {
  Serial.begin(115200); //for debugging if needed.
  WiFi.begin(network, password); //attempt to connect to wifi
  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  Serial.println(network);
  while (WiFi.status() != WL_CONNECTED && count < 12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.println(WiFi.localIP().toString() + " (" + WiFi.macAddress() + ") (" + WiFi.SSID() + ")");
    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect 😕  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }
  if (imu.setupIMU(1)) {
    Serial.println("IMU Connected!");
  } else {
    Serial.println("IMU Not Connected 😕");
    Serial.println("Restarting");
    ESP.restart(); // restart the ESP (proper way)
  }
  tft.init();
  tft.setRotation(3);
  tft.setTextSize(1);
  tft.fillScreen(BACKGROUND);
  tft.setTextColor(TFT_WHITE, TFT_BLACK); //set color of font to green foreground, black background

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  analogSetAttenuation(ADC_6db); //set to 6dB attenuation for 3.3V full scale reading.
  delay(20); //wait 20 milliseconds

}

Button button(BUTTON_PIN);

void loop() {
  imu.readAccelData(imu.accelCount);
  x = imu.accelCount[0] * imu.aRes;
  y = imu.accelCount[1] * imu.aRes;
  z = imu.accelCount[2] * imu.aRes;

  button_flag = button.update();
  if(button_flag == 1){
    x_acc_total += x;
    x_counter++;
    
    y_acc_total += y;
    y_counter++;
    
    z_acc_total += z;
    z_counter++;

    button_press_time = millis();
  }else if(button_flag == 2){
    x_avg = (x_acc_total / x_counter) * 40;
    Serial.println(x_avg);
    x_acc_total = 0;
    x_counter = 0;
    
    y_avg = (y_acc_total / y_counter) * 40;
    Serial.println(y_avg);
    y_acc_total = 0;
    y_counter = 0;

    z_avg = -(z_acc_total / z_counter) * 15;
    Serial.println(z_avg);
    z_acc_total = 0;
    z_counter = 0;

    char body[100];
    sprintf(body,"y_acc=%f&z_acc=%f&x_acc=%f&player_num=%d&current_game=%s&game_over=0", x_avg, z_avg, y_avg, 1, "basketball"); //remove y_acc
    int body_len = strlen(body);
    
    sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/cjoshea/carnival_server.py HTTP/1.1\r\n");
    strcat(request_buffer,"Host: 608dev.net\r\n");
    strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len);
    strcat(request_buffer,"\r\n"); //new line from header to body
    strcat(request_buffer,body);
    strcat(request_buffer,"\r\n"); //header

    Serial.println(request_buffer);
    
    do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
    
    x_avg = 0;
    y_avg = 0;
    z_avg = 0;
    
  }
  /*
  while (millis() - primary_timer < LOOP_PERIOD); //wait for primary timer to increment
  primary_timer = millis();*/

  
}

/*
void post_request(char body[200]) {
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/cjoshea/bop_it.py HTTP/1.1\r\n");
  strcat(request_buffer,"Host: 608dev.net\r\n");
  strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer,"\r\n"); //new line from header to body
  strcat(request_buffer,body); //body
  strcat(request_buffer,"\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
}
*/
uint8_t char_append(char* buff, char c, uint16_t buff_size) {
        int len = strlen(buff);
        if (len>buff_size) return false;
        buff[len] = c;
        buff[len+1] = '\0';
        return true;
}

void do_http_request(char* host, char* request, char* response, uint16_t response_size, uint16_t response_timeout, uint8_t serial){
  WiFiClient client; //instantiate a client object
  if (client.connect(host, 80)) { //try to connect to host on port 80
    if (serial) Serial.print(request);//Can do one-line if statements in C without curly braces
    client.print(request);
    memset(response, 0, response_size); //Null out (0 is the value of the null terminator '\0') entire buffer
    uint32_t count = millis();
    while (client.connected()) { //while we remain connected read out data coming back
      client.readBytesUntil('\n',response,response_size);
      if (serial) Serial.println(response);
      if (strcmp(response,"\r")==0) { //found a blank line!
        break;
      }
      memset(response, 0, response_size);
      if (millis()-count>response_timeout) break;
    }
    memset(response, 0, response_size);  
    count = millis();
    while (client.available()) { //read out remaining text (body of response)
      char_append(response,client.read(),OUT_BUFFER_SIZE);
    }
    if (serial) Serial.println(response);
    client.stop();
    if (serial) Serial.println("-----------");  
  }else{
    if (serial) Serial.println("connection failed 😕");
    if (serial) Serial.println("wait 0.5 sec...");
    client.stop();
  }
}
