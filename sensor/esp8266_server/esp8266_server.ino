#include<stdlib.h>
#include <SoftwareSerial.h>
//esp8266 settings
#define SSID "ADEMA"
#define PASS ""
#define IP "192.168.1.103"
#define ID "001"

//setup software serial to talk to esp8266
SoftwareSerial espComm(10, 11); // RX->pin 10 Tx->pin 11

//sensor DHT11 setup
#include "DHT.h" //make sure the library is properly installed!!
#define DHTPIN 2      //DHT11 data pin 
#define DHTTYPE DHT11   // using DHT11 sensor
DHT dht(DHTPIN, DHTTYPE);

#define RESET 5 //esp harware reset
#definte LED 13
float i = 0.0;

void setup()
{
  espComm.begin(9600);//talks to esp8266
  Serial.begin(9600);//talks to serial monitor on computer, if connected
  dht.begin();//initialize sensor
  sendDebug("AT");//initialize esp8266
  delay(5000);
  if(espComm.find("OK")){
    Serial.println("RECEIVED: OK esp8266 initialization");
    for(int i=0;i<5;i++){
      if(connectWiFi()){
        Serial.println("Wifi Connection attempt success");
        break;
      }
    }
    Serial.println("Wifi Connection failed 5X");
  }
}

void loop(){
  reset();
  delay(5000);
  float tempC = 32.2;
  float t = dht.readTemperature(true);//Fahrenheit
  //float t = i;//debug
  float h = dht.readHumidity();//Percent
  if (isnan(h) || isnan(t)) {
    Serial.println("Error failed to read from DHT sensor");
    return;
  }
  char buffer[10];
  String temp = dtostrf(t, 4, 1, buffer); //F
  String hum = dtostrf(h, 4, 1, buffer);
  String type = "temp";
  updateSense(temp, type);//send temp data to server
  type = "humidity";
  reset();
  delay(6000);
  updateSense(hum, type);//send humidity data to server
  delay(5000);
}

void updateSense(String value, String type){
  String cmd = "AT+CIPSTART=\"TCP\",\"";//connect to IP address cmd
  cmd += IP;
  cmd += "\",5000";
  sendDebug(cmd);
  delay(20000);
  if(espComm.find("Error")){
    Serial.print("RECEIVED: Error connecting to IP address");
    return;
  }
  //build send data command
  cmd = "GET /";
  cmd += type;
  cmd += "Sense?ID=";
  cmd += ID;
  cmd += "&value=";
  cmd += value;
  cmd += " HTTP/1.1\r\n\r\n";
  Serial.print("val=");
  Serial.println(value);
  espComm.print("AT+CIPSEND=");
  espComm.println(cmd.length());
  if(espComm.find(">")){
    Serial.print(">");
    Serial.print(cmd);
    espComm.print(cmd);
  }else{
    sendDebug("AT+CIPCLOSE");
  }
  if(espComm.find("OK")){
    Serial.println("RECEIVED: OK update data");
    sendDebug("AT+CIPCLOSE");
  }else{
    Serial.println("RECEIVED: Error update data");
  }
}

void sendDebug(String cmd){
  Serial.print("SEND: ");
  Serial.println(cmd);
  espComm.println(cmd);
} 
 
boolean connectWiFi(){
  espComm.println("AT+CWMODE=1");
  delay(2000);
  String cmd="AT+CWJAP=\"";
  cmd+=SSID;
  cmd+="\",\"";
  cmd+=PASS;
  cmd+="\"";
  sendDebug(cmd);
  delay(7000);
  if(espComm.find("OK")){
    Serial.println("RECEIVED: OK wifi connect");
    return true;
  }else{
    Serial.println("RECEIVED: Error wifi connect");
    return false;
  }
  
}

void reset(){
  digitalWrite(RESET,LOW);
  digitalWrite(LED,HIGH);
  delay(100);
  digitalWrite(RESET,HIGH);
  digitalWrite(LED,LOW);
}
