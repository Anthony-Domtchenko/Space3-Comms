#include <WiFi.h>
#include <WiFiAP.h>
#include <vector>
#include "transmission.hpp"
#include "ax25.hpp"
#include "uart.h"
#include "beacon.hpp"

#define GROUND_STATION_IP "192.168.1.2"
#define SAT_IP            "192.168.1.1"
#define SAT_PORT 4210

#define TX_PIN 47
#define RX_PIN 48
#define COMMS_BAUDRATE 3000000

// Set these to your desired credentials.
const char *ssid = "DOCKER-1";
const char *password = "Bingus123";

IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WiFiServer satServer(SAT_PORT); // TCP Server


enum TaskRequest {
    WOD_DOWNLINK,
    SCI_DOWNLINK,
    CLEAR_WOD,
    SEND_PARAMS
  };


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

    while (client.connected()) {
      if (client.available()) {
        // Start by recieving the request packet from the ground station
        std::vector<char> packet = recieveAx25Packet(&client);
        RxAx25 requestP(packet);
        if (requestP.fcsCompare()) {
          Serial.println("Request packet recieved: FCS is okay");
        }
        else {
          Serial.println("WARNING: FCS of incoming packet does not match calculated");
        }


        if (requestP.getData().size() > 1) {
          Serial.println("Client Request was not valid");
        }

        else if (requestP.getData()[0] == WOD_DOWNLINK) {
          Serial.println("Sending WOD Data");
          std::vector<char> sampleData = {1, 0, 0, 0, 1, 1, 0, 0, 0, 1};
          for (int i = 1; i <= 24; i++) {
            sampleData.front() = static_cast<char>(i);
            sampleData.back() = static_cast<char>(i);
            std::vector<char> txPacket = ax25encode(sampleData, true);
            sendAx25Packet(&client, txPacket);
            Serial.printf("Sending Packet %d\n", i);
          }
        }

        else if (requestP.getData()[0] == SCI_DOWNLINK) {

        }

        else if (requestP.getData()[0] == CLEAR_WOD) {

        }

        else if (requestP.getData()[0] == SEND_PARAMS) {

        }

        else {
          Serial.println("Client Request was not valid");
        }

        client.stop();
      }
    }

    Serial.println("Client Disconnected");
  }
}






