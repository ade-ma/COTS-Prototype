#include<stdlib.h>
#include <SoftwareSerial.h>
#define SSID "ADEMA"
#define PASS ""
#define IP "184.106.153.149" // thingspeak.com
String GET = "GET /update?key=DQFCKSS2BAMAYFNE&field1=";
SoftwareSerial monitor(10, 11); // RX, TX

#include "DHT.h"
#define DHTPIN 2     // what pin we're connected to
#define DHTTYPE DHT11   // DHT 11 
DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  monitor.begin(9600);
  Serial.begin(9600);
  dht.begin();
  sendDebug("AT");
  delay(5000);
  if(monitor.find("OK")){
    Serial.println("RECEIVED: OK");
    connectWiFi();
  }
}

void loop(){
  float tempC = 32.2;
  float t = dht.readTemperature(true);
  float h = dht.readHumidity();
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  char buffer[10];
  String temp = dtostrf(t, 4, 1, buffer); //F
  String hum = dtostrf(h, 4, 1, buffer);
  update(temp, hum);
  delay(5000);
}

void update(String temp, String hum){
  String cmd = "AT+CIPSTART=\"TCP\",\"";
  cmd += IP;
  cmd += "\",80";
  sendDebug(cmd);
  delay(20000);
  if(monitor.find("Error")){
    Serial.print("RECEIVED: Error");
    return;
  }
  cmd = GET;
  cmd += temp;
  cmd += "&field2=";
  cmd += hum;
  cmd += "\r\n";
  monitor.print("AT+CIPSEND=");
  monitor.println(cmd.length());
  if(monitor.find(">")){
    Serial.print(">");
    Serial.print(cmd);
    monitor.print(cmd);
  }else{
    sendDebug("AT+CIPCLOSE");
  }
  if(monitor.find("OK")){
    Serial.println("RECEIVED: OK");
  }else{
    Serial.println("RECEIVED: Error");
  }
}

void sendDebug(String cmd){
  Serial.print("SEND: ");
  Serial.println(cmd);
  monitor.println(cmd);
} 
 
boolean connectWiFi(){
  monitor.println("AT+CWMODE=1");
  delay(2000);
  String cmd="AT+CWJAP=\"";
  cmd+=SSID;
  cmd+="\",\"";
  cmd+=PASS;
  cmd+="\"";
  sendDebug(cmd);
  delay(5000);
  if(monitor.find("OK")){
    Serial.println("RECEIVED: OK");
    return true;
  }else{
    Serial.println("RECEIVED: Error");
    return false;
  }
}
