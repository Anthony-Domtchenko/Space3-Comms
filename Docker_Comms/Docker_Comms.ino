#include <WiFi.h>
#include <WiFiAP.h>
#include <vector>
#include "transmission.hpp"
#include "ax25.hpp"
#include "uart.h"
#include "beacon.hpp"
#include "link.hpp"

#define GROUND_STATION_IP "192.168.1.2"
#define SAT_IP            "192.168.1.1"
#define SAT_PORT 4210

#define TX_PIN 48
#define RX_PIN 47
#define COMMS_BAUDRATE 3000000

// Set these to your desired credentials.
const char *ssid = "DOCKER-1";
const char *password = "Bingus123";

IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WiFiServer satServer(SAT_PORT); // TCP Server


void setup() {
  Serial.begin(115200);
  Serial2.begin(COMMS_BAUDRATE, SERIAL_8N1, RX_PIN, TX_PIN); // OBC UART Connection
  Mcu.begin(HELTEC_BOARD,SLOW_CLK_TPYE);

  Serial.println();
  Serial.println("Configuring access point...");

  // You can remove the password parameter if you want the AP to be open.
  // a valid password must have more than 7 characters
  if (!WiFi.softAP(ssid, password)) {
    log_e("Soft AP creation failed.");
    while (1);
  }
  WiFi.softAPConfig(local_ip, gateway, subnet);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);

  satServer.begin();

  Serial.println();
  Serial.println("Configuring LoRa...");
  initLoRa();
}


void loop() {
  // SATELLITE BEACON
  if (handleOBCBeacon()) {
    Serial.println("OBC Beacon Successful");
  }

  // SATELLITE LINK
  WiFiClient client = satServer.available(); // Check for a client
  if (client) {
    Serial.println("New Client Connected");
    handleLink(&client);
  }
}






