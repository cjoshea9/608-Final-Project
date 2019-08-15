#include <WiFi.h> //Connect to WiFi Network
#include <SPI.h>
#include <TFT_eSPI.h>
#include <mpu9255_esp32.h>
#include<math.h>
#include<string.h>

#define BACKGROUND TFT_BLACK

#define CONTROLLER_SELECTION 0
#define GAME_SELECTION 1
#define GAME_PLAY 2
#define GAME_OVER 3

#define USER_ONE 1
#define USER_TWO 2

#define BASKETBALL 0
#define SHOOTING_GALLERY 1

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */
#define HIGH_SCORE_SLEEP 5

RTC_DATA_ATTR int state = CONTROLLER_SELECTION;
RTC_DATA_ATTR int controller = 0; //which user this esp is

MPU9255 imu; //imu object called, appropriately, imu
TFT_eSPI tft = TFT_eSPI();
// Set up the TFT object

const int LOOP_PERIOD = 10;
unsigned long primary_timer; //timer for get requests
unsigned long no_response_timer; //timer for no response from user
unsigned long GAME_TIME = 30000;
unsigned long BUFFER = 3000;
unsigned long HIGH_SCORE_TIME = 8000;

const int LEFT_BUTTON_PIN = 16;
const int RIGHT_BUTTON_PIN = 5;
int left_button_flag = 0;
int right_button_flag = 0;

float x,z;

float x_acc_total = 0;
int x_counter = 0;
float x_avg = 0;

float z_acc_total = 0;
int z_counter = 0;
float z_avg = 0;

uint32_t button_press_time;

char network[] = "6s08";  //SSID for 6.08 Lab
char password[] = "iesc6s08"; //Password for 6.08 Lab

char basketball[] = "basketball";
char shooting_gallery[] = "gallery";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[OUT_BUFFER_SIZE];
char response_buffer[OUT_BUFFER_SIZE];

//For the shooting game:
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
  tft.setRotation(2);
  tft.setTextSize(1);
  tft.fillScreen(BACKGROUND);
  tft.setTextColor(TFT_WHITE, TFT_BLACK); //set color of font to green foreground, black background
  tft.println("Use left/right buttons to select controller.");

  pinMode(LEFT_BUTTON_PIN, INPUT_PULLUP);
  pinMode(RIGHT_BUTTON_PIN, INPUT_PULLUP);
  analogSetAttenuation(ADC_6db); //set to 6dB attenuation for 3.3V full scale reading.
  
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

  primary_timer = millis();
  no_response_timer = millis();
  
  delay(20); //wait 20 milliseconds
}

Button leftButton(LEFT_BUTTON_PIN);
Button rightButton(RIGHT_BUTTON_PIN);
RTC_DATA_ATTR boolean both_controllers = false; //True when both controllers have been selected
RTC_DATA_ATTR boolean first_controller = false; //True when this esp is the first one to select a user
RTC_DATA_ATTR boolean selected = false; //When this is true, the esp cannot select a user until this becomes false again
RTC_DATA_ATTR boolean one_selected = false; //True when there is already an entry in the controller database before this esp sends its selected user
RTC_DATA_ATTR int game = -1; //0 if basketball, 1 if shooting gallery
RTC_DATA_ATTR boolean just_entered_game = true; //True when the player just enters a game. Used for timing purposes
RTC_DATA_ATTR boolean just_entered_game_selection = false; //True when the player enters the game selection state from the high-score state
RTC_DATA_ATTR boolean first_sleep = true; //True when the esp hasn't gone to sleep for the first time in the game selection state

void loop() {
  left_button_flag = leftButton.update();
  right_button_flag = rightButton.update();
  switch(state){
    case CONTROLLER_SELECTION:
      //If this esp hasn't selected a user yet
      if(!selected){
        //If either button has been pressed and released, enter this
        if(left_button_flag == 2 || right_button_flag == 2){
          //Get request to see if there's a user already in the controller database
          memset(request_buffer, 0, sizeof(request_buffer));
          memset(response_buffer, 0, sizeof(response_buffer));
          sprintf(request_buffer, "GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?game_over=0&current_game=controller_selection  HTTP/1.1\r\n");
          strcat(request_buffer, "Host: 608dev.net \r\n");
          strcat(request_buffer, "\r\n"); //new line from header to body
          do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);

          //Response from the get request
          char get_controller_db_response[10];
          strcpy(get_controller_db_response, response_buffer);

          //This means there is already an entry in the controller database so set one_selected to true to indicate that
          if(atoi(get_controller_db_response) == 1){
            one_selected = true;
          }

          //Controller is USER_ONE if left button is pressed and released, USER_TWO if right button is pressed and released
          if(left_button_flag == 2){
            controller = USER_ONE;
          } else{
            controller = USER_TWO;
          }

          //Post the selected user to the controller database
          char body[100];
          sprintf(body,"game_over=0&player_num=%d&current_game=controller_selection", controller);
          int body_len = strlen(body);
          memset(request_buffer, 0, sizeof(request_buffer));
          memset(response_buffer, 0, sizeof(response_buffer));
          sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py HTTP/1.1\r\n");
          strcat(request_buffer,"Host: 608dev.net\r\n");
          strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
          sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len);
          strcat(request_buffer,"\r\n"); //new line from header to body
          strcat(request_buffer,body);
          strcat(request_buffer,"\r\n"); //header
          do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);

          //Response from post request
          char post_controller_db_response[10];
          strcpy(post_controller_db_response, response_buffer);
          
          //If the size of the database didn't change, that means this esp 
          //selected the same user as the user already in the controller database
          if(!one_selected && atoi(post_controller_db_response) == 1){
            first_controller = true;
            selected = true;
          }
          //Otherwise, there are two unique users in the database so continue on
          else if(atoi(post_controller_db_response) == 2){
            selected = true;
            first_controller = false;
            both_controllers = true;
          }
        }
      }

      //If this esp was the first to select a user
      //Now, we want to keep sending get requests until the database returns 2, 
      //which would indicate that there are two users playing
      if(first_controller){
        //Get request to see the size of the database
        memset(request_buffer, 0, sizeof(request_buffer));
        memset(response_buffer, 0, sizeof(response_buffer));
        sprintf(request_buffer, "GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?game_over=0&current_game=controller_selection  HTTP/1.1\r\n");
        strcat(request_buffer, "Host: 608dev.net \r\n");
        strcat(request_buffer, "\r\n"); //new line from header to body
        do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
        
        char controller_db_response[10];
        strcpy(controller_db_response, response_buffer);

        //Set both_controllers to true to indicate that both players have picked different users and are ready to select a game
        if(atoi(controller_db_response) == 2){
          first_controller = false;
          both_controllers = true;
        }
        
      }

      //Users 1 and 2 have been selected and now we just display to the client
      //and change the state to the game_selection state
      if(controller == USER_ONE && both_controllers){
        tft.fillScreen(BACKGROUND);
        tft.drawString("You are user one", 0, 0, 1);
        state = GAME_SELECTION;
        primary_timer = millis();
        no_response_timer = millis();
      } else if(controller == USER_TWO && both_controllers){
        tft.fillScreen(BACKGROUND);
        tft.drawString("You are user two", 0, 0, 1);
        state = GAME_SELECTION;
        primary_timer = millis();
        no_response_timer = millis();
      }
      
      break;
    
    case GAME_SELECTION:
      //Enters this block if coming from the high-score state, otherwise the screen displays which user the player is
      if(just_entered_game_selection){
        tft.fillScreen(BACKGROUND);
        tft.drawString("Select a game", 0, 0, 1);
        just_entered_game_selection = false;
        first_sleep = true;
        primary_timer = millis();
        no_response_timer = millis();
      }

      //If the user hasn't selected a game in 20 seconds, put the esp to sleep for a couple seconds
      if(first_sleep){
        if(millis() - no_response_timer > 20000){
          first_sleep = false;
          just_entered_game_selection = true;
          esp_deep_sleep_start();
        }
      }
      //After the first time the esp is put to sleep, sleep for two seconds after 5 seconds of no response instead of 20
      else{
        if(millis() - no_response_timer > 6000){
          just_entered_game_selection = true;
          esp_deep_sleep_start();
        }
      }

      //Send a get request every half a second to see if the user has selected a game yet
      if(millis() - primary_timer > 500){
        //Get request to see which game is selected
        memset(request_buffer, 0, sizeof(request_buffer));
        memset(response_buffer, 0, sizeof(response_buffer));
        sprintf(request_buffer, "GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?current_game=current_game  HTTP/1.1\r\n");
        strcat(request_buffer, "Host: 608dev.net \r\n");
        strcat(request_buffer, "\r\n"); //new line from header to body
        do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);

        //store the server's response
        char game_db_response[20];
        strcpy(game_db_response, response_buffer);

        //game_name is the "current_game"
        //game_over needs to be 0 in order to enter a new game
        char* game_name = strtok(game_db_response, " ");
        int game_over = atoi(strtok(NULL, " "));

        if(!game_over){
          if(strcmp(game_name, basketball) == 0){
            game = BASKETBALL;
            state = GAME_PLAY;
            just_entered_game = true;
          }else if(strcmp(game_name, shooting_gallery) == 0){
            game = SHOOTING_GALLERY;
            state = GAME_PLAY;
            just_entered_game = true;
          }
        }

        //Send a get request for game selection every 500ms
        primary_timer = millis();
      }

      break;
      
    case GAME_PLAY:
      if(just_entered_game){
        tft.fillScreen(BACKGROUND);
        primary_timer = millis();
        just_entered_game = false;

        if(game == BASKETBALL){
          tft.drawString("Basketball", 0, 0, 1);
          tft.drawString("Shoot by holding down", 0, 20, 1);
          tft.drawString("on your selected but-", 0, 30, 1);
          tft.drawString("ton, then releasing  ", 0, 40, 1);
          tft.drawString("during your shooting ", 0, 50, 1);
          tft.drawString("arc", 0, 60, 1);
        }else{
          tft.drawString("Shooting Gallery", 0, 0, 1);
          tft.drawString("Press down on right  ", 0, 20, 1);
          tft.drawString("button to shoot. Aim ", 0, 30, 1);
          tft.drawString("at the targets on yo-", 0, 40, 1);
          tft.drawString("ur side of the screen", 0, 50, 1);
        }
      }
 
      if(millis() - primary_timer < GAME_TIME){
        //basketball game
        if(game == BASKETBALL){
          basketball_game();
        }
        //shooting gallery game
        else{
          shooting_game();
        }
      }

      if(millis() - primary_timer > GAME_TIME + BUFFER){
        memset(request_buffer, 0, sizeof(request_buffer));
        memset(response_buffer, 0, sizeof(response_buffer));
        sprintf(request_buffer, "GET http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?game_over=0&current_game=current_game  HTTP/1.1\r\n");
        strcat(request_buffer, "Host: 608dev.net \r\n");
        strcat(request_buffer, "\r\n"); //new line from header to body
        do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
        
        char game_db_response[20];
        strcpy(game_db_response, response_buffer);

        strtok(game_db_response, " ");
        int game_over = atoi(strtok(NULL, " "));

        if(game_over){
          state = GAME_OVER;
          just_entered_game = true;
          primary_timer = millis();
        }
      }
      
      break;

    
    case GAME_OVER:

      //Reset all the controller booleans
      both_controllers = false;
      first_controller = false;
      selected = false;
      one_selected = false;
      just_entered_game_selection = true;
      state = GAME_SELECTION;

      esp_sleep_enable_timer_wakeup(HIGH_SCORE_SLEEP * uS_TO_S_FACTOR);
      esp_deep_sleep_start();
  }

}

void basketball_game(){
  imu.readAccelData(imu.accelCount);
  x = imu.accelCount[1] * imu.aRes;
  z = imu.accelCount[2] * imu.aRes;
  int button_flag;
  
  if(controller == USER_ONE){
    button_flag = leftButton.update();
  }else{
    button_flag = rightButton.update();
  }

  if(button_flag == 1){
    x_acc_total += x;
    x_counter++;
    
    z_acc_total += z;
    z_counter++;

    button_press_time = millis();
  }else if(button_flag == 2){ 
    x_avg = (x_acc_total / x_counter) * 40;
    Serial.println(x_avg);
    x_acc_total = 0;
    x_counter = 0;

    z_avg = -(z_acc_total / z_counter) * 35;
    Serial.println(z_avg);
    z_acc_total = 0;
    z_counter = 0;

    char body[100];
    sprintf(body,"z_acc=%f&x_acc=%f&player_num=%d&current_game=%s&game_over=0", z_avg, x_avg, controller, "basketball");
    int body_len = strlen(body);
    
    sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py HTTP/1.1\r\n");
    strcat(request_buffer,"Host: 608dev.net\r\n");
    strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len);
    strcat(request_buffer,"\r\n"); //new line from header to body
    strcat(request_buffer,body);
    strcat(request_buffer,"\r\n"); //header

    Serial.println(request_buffer);
    
    do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);

    x_avg = 0;
    z_avg = 0;
  }
}

void shooting_game(){
  
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

void post_hit(char post_body[200]) { 
  int body_len = strlen(post_body); //calculate body length (for header reporting)
  sprintf(request_buffer,"POST http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py?current_game=gallery HTTP/1.1\r\n");
  strcat(request_buffer,"Host: 608dev.net\r\n");
  strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer,"\r\n"); //new line from header to body
  strcat(request_buffer,post_body); //body
  strcat(request_buffer,"\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
  memset(request_buffer, 0, sizeof(request_buffer));
  memset(response_buffer, 0, sizeof(response_buffer));
}
