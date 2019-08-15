#include <WiFi.h> //Connect to WiFi Network
#include <SPI.h>
#include <TFT_eSPI.h>
#include <mpu9255_esp32.h>
#include<math.h>
#include<string.h>

float scaled_reading_1;
float scaled_reading_2;
float scaled_reading_3;
float scaled_reading_4;
float scaled_reading_5;
float scaled_reading_6;

int player_num = 1;


float threshold = 0.75;

const int game_timer = 300000;
const int round_timer = 2000;

int shooting_state = 0;
int target_location; //GET from server
int hit_tracker = 0;
int old_hit_tracker = 100;
int hit_miss = 0;

int sensor_1_hit = 0;
int sensor_2_hit = 0;
int sensor_3_hit = 0;
int sensor_4_hit = 0;
int sensor_5_hit = 0;
int sensor_6_hit = 0;


uint32_t timer;

char network[] = "iPhone";  //SSID for 6.08 Lab
char password[] = "608watchtime"; //Password for 6.08 Lab 
char host[] = "608dev.net";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response

void setup() {
  // put your setup code here, to run once:
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
    Serial.println("Failed to Connect :/  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }
  
}

void loop() {
  // put your main code here, to run repeatedly:
  scaled_reading_1 = analogRead(A0)*(3.3/4096);
  scaled_reading_2 = analogRead(A3)*(3.3/4096);
  scaled_reading_3 = analogRead(A6)*(3.3/4096);
  scaled_reading_4 = analogRead(A7)*(3.3/4096);
  scaled_reading_5 = analogRead(A4)*(3.3/4096);
  scaled_reading_6 = analogRead(A5)*(3.3/4096);
  
  //Threshold <0.75V

  //Game over if statement, check timer
  
  
  switch(shooting_state){
    case 0:
      hit_tracker = 100;
      //get target location from server      
      hit_miss = 0;
      shooting_state = 1;
    case 1:
      //where sensors will be read
      //first sensor to be hit is what counts
      if (scaled_reading_1 < threshold){
        hit_tracker = 1;
        shooting_state = 2;
      }
      else if (scaled_reading_2 < threshold){
        hit_tracker = 2;
        shooting_state = 2;
      }
      else if (scaled_reading_3 < threshold){
        hit_tracker = 3;
        shooting_state = 2;
      }
      else if (scaled_reading_4 < threshold){
        hit_tracker = 4;
        shooting_state = 2;
      }
      else if (scaled_reading_5 < threshold){
        hit_tracker = 5;
        shooting_state = 2;
      }  
      else if (scaled_reading_6 < threshold){
        hit_tracker = 6;
        shooting_state = 2;
      }  
    case 2:
      Serial.println(hit_tracker);
      char hit_tracker_char[200];
      
      if (hit_tracker != 100 && old_hit_tracker != hit_tracker)  {
        if (player_num ==2) hit_tracker+=6;
        sprintf(hit_tracker_char,"current_game=gallery&game_over=0&target=%d",hit_tracker);
        post_hit(hit_tracker_char); 
        old_hit_tracker = hit_tracker;
      }
      shooting_state = 0;
  
  } 
}



void get_request() { //current_game=gallery&game_over=0&target=(sensor_hit)&player_num=(player_num)
  //formulate GET request...first line:
  sprintf(request_buffer,"GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?current_game=gallery HTTP/1.1\r\n");
  strcat(request_buffer,"Host: 608dev.net\r\n"); //add more to the end
  strcat(request_buffer,"\r\n"); //add blank line!
  //submit to function that performs GET.  It will return output using response_buffer char array
  do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,false);
  char * pch;
  int vals[2];
  char delimiters[] = " ";
  int i = 0;
  pch = strtok(response_buffer, delimiters);
  while(pch != NULL) {
    vals[i] = atoi(pch);
    pch = strtok(NULL, delimiters);
    i++;
  }
  target_location = vals[0];
}

/*----------------------------------
  char_append Function:
  Arguments:
     char* buff: pointer to character array which we will append a
     char c:
     uint16_t buff_size: size of buffer buff

  Return value:
     boolean: True if character appended, False if not appended (indicating buffer full)
*/
uint8_t char_append(char* buff, char c, uint16_t buff_size) {
  int len = strlen(buff);
  if (len > buff_size) return false;
  buff[len] = c;
  buff[len + 1] = '\0';
  return true;
}

/*----------------------------------
   do_http_request Function:
   Arguments:
      char* host: null-terminated char-array containing host to connect to
      char* request: null-terminated char-arry containing properly formatted HTTP request
      char* response: char-array used as output for function to contain response
      uint16_t response_size: size of response buffer (in bytes)
      uint16_t response_timeout: duration we'll wait (in ms) for a response from server
      uint8_t serial: used for printing debug information to terminal (true prints, false doesn't)
   Return value:
      void (none)
*/

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
    if (serial) Serial.println("connection failed :/");
    if (serial) Serial.println("wait 0.5 sec...");
    client.stop();
  }
}
void post_hit(char body[200]) { 
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?current_game=gallery HTTP/1.1\r\n");
  strcat(request_buffer,"Host: 608dev.net\r\n");
  strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer,"\r\n"); //new line from header to body
  strcat(request_buffer,body); //body
  strcat(request_buffer,"\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
}

//void get_request() {
//  sprintf(request_buffer,"GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?current_game=gallery HTTP/1.1\r\n");
//  strcat(request_buffer,"Host: 608dev.net\r\n");
//  do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
//}
