//===========================================================
//--------------------Libraries--------------------
#include <SoftwareSerial.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h> 

//===========================================================
//--------------------Hardware Mapping--------------------
//LCD
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);

//keyboard
#define bt4 17
#define bt3 16
#define bt2 15
#define bt1 14

//buzzer
#define buz 13

//encoder
#define encoder 12

//motor
#define in1 11
#define in2 10
#define in3 9
#define in4 8
#define inm 7

//illumination
#define lgt_top 6
#define lgt_r 5
#define lgt_l 4

//bluetooth
SoftwareSerial bth(2, 3);

//===========================================================
//--------------------Global Variables--------------------

bool bt1_f = 0;
bool bt2_f = 0;
bool bt3_f = 0;
bool bt4_f = 0;

int bt_tag = 1; //1 - home; 2 - rotation test; 3 - illumination; 4 - start
int bt1_code = 0;
int bt2_code = 0;
int bt3_code = 0;
int bt4_code = 0;

int step_number = 0;

int count = 0;

//===========================================================
//--------------------Setup--------------------
void setup() {
  
  //Setting pins

  pinMode(bt1, INPUT);
  pinMode(bt2, INPUT);
  pinMode(bt3, INPUT);
  pinMode(bt4, INPUT);

  pinMode(buz, OUTPUT);
  pinMode(encoder, INPUT);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(inm, OUTPUT);
  
  pinMode(lgt_top, OUTPUT);
  pinMode(lgt_r, OUTPUT);
  pinMode(lgt_l, OUTPUT);

  //Starting pins as LOW
  digitalWrite(buz, LOW);

  digitalWrite(in1, HIGH);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, HIGH);
  digitalWrite(inm, HIGH);
  
  digitalWrite(lgt_top, HIGH);
  digitalWrite(lgt_r, HIGH);
  digitalWrite(lgt_l, HIGH);

  //Starting LCD
  lcd.begin(20, 4);
  home_screen();

  //Starting Bluetooth
  bth.begin(9600);

  Serial.begin(9600);
  Serial.println("Começou");

  
    
}

//===========================================================
//--------------------Listening Buttons and Bluetooth--------------------
void loop(){

  if(!digitalRead(bt1)) bt1_f = 1;
  if(digitalRead(bt1) && bt1_f){
    bt1_f = 0;
    buzzer(50, 50, 1);
    bt1_click();
  }
  
  if(!digitalRead(bt2)) bt2_f = 1;
  if(digitalRead(bt2) && bt2_f){
    bt2_f = 0;
    buzzer(50, 50, 1);
    bt2_click();
  }
  
  if(!digitalRead(bt3)) bt3_f = 1;
  if(digitalRead(bt3) && bt3_f){
    bt3_f = 0;
    buzzer(50, 50, 1);
    bt3_click();
  }
  
  if(!digitalRead(bt4)) bt4_f = 1;
  if(digitalRead(bt4) && bt4_f){
    bt4_f = 0;
    buzzer(50, 50, 1);
    bt4_click();
  }

}

//===========================================================
//--------------------Programming--------------------
void bt1_click(){

  if(bt_tag == 1){
  }else if(bt_tag == 2){
    bt_tag = 1;
    home_screen();    
  }else if(bt_tag == 3){
    bt_tag = 1;
    home_screen();
  }else if(bt_tag == 4){
    bt_tag = 1;
    home_screen();
  }
  
  Serial.println(bt_tag);
}

void bt2_click(){
  
  if(bt_tag == 1){
    bt_tag = 2;
    r_test_screen(); 

  }else if(bt_tag == 2){
    digitalWrite(inm, LOW);
    unsigned long t0 = millis();
    unsigned long t1 = millis();
    while (t1 - t0 <= 2000) {
      oneStep(1);
      delay(10);
      t1 = millis();
    }
    digitalWrite(inm, HIGH);

  }else if(bt_tag == 3){
    digitalWrite(lgt_l, !digitalRead(lgt_l));

  }else if(bt_tag == 4){
    bt_tag = 41;
    loading();
    String bthTest = bth_test();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(bthTest);
    lcd.setCursor(0, 1);
    lcd.print("4. Come Back");
  }
  
  Serial.println(bt_tag);
}

void bt3_click(){
  
  if(bt_tag == 1){
    bt_tag = 3;
    illum_screen();
    
  }else if(bt_tag == 2){
    digitalWrite(inm, LOW);
    unsigned long t0 = millis();
    unsigned long t1 = millis();
    while (t1 - t0 <= 2000) {
      oneStep(0);
      delay(10);
      t1 = millis();
    }
    digitalWrite(inm, HIGH);

  }else if(bt_tag == 3){
      digitalWrite(lgt_r, !digitalRead(lgt_r));
      
  }else if(bt_tag == 4){
    if (bth_test().equals("Connected")) {
      start_motor();
    }else{
      buzzer(100, 100, 3);
    }
    
  }
  
  Serial.println(bt_tag);
}

void bt4_click(){
  
  if(bt_tag == 1){
    bt_tag = 4;
    scan_screen();

  }else if(bt_tag == 2){

  }else if(bt_tag == 3){
    digitalWrite(lgt_top, !digitalRead(lgt_top));

  }else if(bt_tag == 4){

  }else if(bt_tag == 41){
    bt_tag = 4;
    scan_screen();    
  }
  
  Serial.println(bt_tag);
}

void home_screen(){

  lcd.clear();
  lcd.setCursor(1, 0);
  lcd.print("AGGREGATE SCAN 2.0");
  lcd.setCursor(0, 1);
  lcd.print("2. Rotation Test");
  lcd.setCursor(0, 2);
  lcd.print("3. Illumination");
  lcd.setCursor(0, 3);
  lcd.print("4. Start Scan");
}

void r_test_screen(){
  lcd.clear();
  lcd.setCursor(1, 0);
  lcd.print("TESTING ROTATION");
  lcd.setCursor(0, 1);
  lcd.print("1. Home");
  lcd.setCursor(0, 2);
  lcd.print("2. Clockwise");
  lcd.setCursor(0, 3);
  lcd.print("3. Anticlockwise");
}

void illum_screen(){
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("ILLUMINATION");
  lcd.setCursor(0, 1);
  lcd.print("1. Home");
  lcd.setCursor(0, 2);
  lcd.print("2. Left | 3. Right");
  lcd.setCursor(0, 3);
  lcd.print("4. Top Light");
}

void scan_screen(){
  lcd.clear();
  lcd.setCursor(2, 0);
  lcd.print("START SCANNING");
  lcd.setCursor(0, 1);
  lcd.print("1. Home");
  lcd.setCursor(0, 2);
  lcd.print("2. Bluetooth Status");
  lcd.setCursor(0, 3);
  lcd.print("3. Start");
}

void loading(){
  lcd.clear();
  lcd.setCursor(6, 1);
  lcd.print("wait...");
}

void start_motor(){

  digitalWrite(inm, LOW);

  while(1){ 
    Serial.println("No while 1");
  
    if(digitalRead(encoder)){
      Serial.println("Encoder lido");
      picture();   
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(count);   
      count++;

      if(count > 50){
        Serial.println("Terminou");
        digitalWrite(in1, HIGH);
        digitalWrite(in2, HIGH);
        digitalWrite(in3, HIGH);
        digitalWrite(in4, HIGH);
        digitalWrite(inm, HIGH);

        bt_tag = 1;
        home_screen();
        buzzer(1000, 1000, 2);
        break;
      }

      while(1){
        oneStep(1);
        delay(10);
        if(!digitalRead(encoder)){
          break;
        }
      }
      //security steps for LOW state
      oneStep(1);
      delay(10);
      oneStep(1);
      delay(10);
      oneStep(1);
      delay(10);      
    }else{
      Serial.println("Encoder não lido");
      oneStep(1);
      delay(10); 
    }
    
  }

  count = 0;
  
}

void picture(){

  if(count != 0){
    digitalWrite(inm, HIGH);
    delay(1000);
    bth.println("{xis}");
    delay(100);
    Serial.println("Tirou foto");
    String camera = "";
    while(1){
      if(bth.available()){
        for(int i = 0; i < bth.available(); i++){
          camera += bth.readString();
        }
        if(camera.equals("taken")){
          Serial.println("Retorno do celular - seguir para proxima foto");
          break;
        }
      }
    }
    digitalWrite(inm, LOW);    
    delay(1000);
  }

}

String bth_test(){

  String status = "Error";
  unsigned long before = millis();
  unsigned long after = millis();

  bth.print("{status}");

  while (1) {
    if(bth.available()){
      status = "";
      for(int i = 0; i < bth.available(); i++){
        status += bth.readString();
      }
      break;
    }

    after = millis();
    if(after - before >= 5000){
      status = "Disconnected";
      break;
    }

    delay(1);

  }

  Serial.print(status);

  return status;
}

void buzzer(unsigned long t_on, unsigned long t_off, int amount){

  for(int i = 0; i < amount; i++){
    digitalWrite(buz, 1);
    delay(t_on);
    digitalWrite(buz, 0);
    delay(t_off);
  }
  
}

void oneStep(bool dir){
  if(dir){
    switch(step_number){
      case 0:
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, HIGH);
      break;
      case 1:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, HIGH);
      break;
      case 2:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, LOW);
      digitalWrite(in4, HIGH);
      break;
      case 3:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      break;
    } 
  }else{
    switch(step_number){
      case 0:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      break;
      case 1:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, LOW);
      digitalWrite(in4, HIGH);
      break;
      case 2:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, HIGH);
      break;
      case 3:
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, HIGH);

    } 
  }
  step_number++;
  if(step_number > 3){
    step_number = 0;
  }
}

void delay_(unsigned long t){
  unsigned long before = millis();
  unsigned long after = before;

  while(1){
    if(after - before >= t){
      break;
    }
  }
  
}