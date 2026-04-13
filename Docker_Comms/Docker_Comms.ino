#include <WiFi.h>
#include <WiFiAP.h>
#include <vector>
#include "transmission.hpp"
#include "ax25.hpp"


#define SAT_IP "192.168.1.1"
#define SAT_PORT 4210
#define GROUND_STATION_IP "192.168.1.2"

#define BUFFER_SIZE 276

// Set these to your desired credentials.
const char *ssid = "Dockers";
const char *password = "Bingus123";

IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WiFiServer satServer(SAT_PORT); // TCP Server

// Functions
std::vector<char> getAx25Data(WiFiClient* client);


void setup() {
  Serial.begin(115200);
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
}


void loop() {
  WiFiClient client = satServer.available(); // Check for a client

  if (client) {
    Serial.println("New Client Connected");
    while (client.connected()) {
      if (client.available()) {
        //std::vector<char> data = getAx25Data(&client);
        std::vector<char> packet = recieveAx25Packet(&client);
        //std::vector<char> data(packet.begin() + 17, packet.end() - 3);
        for (const auto& val : packet) {
          int num = val; // this line is just so numbers are pritned in readable ascii
          Serial.print(num);
          Serial.print(" ");
        }
        Serial.print("\n");

        RxAx25 recievedPacket(packet);

        Serial.print("Destination Address: ");
        for (const auto& val : recievedPacket.getDestAddr()) {
          Serial.print(val);
        }
        Serial.print("\n");

        Serial.print("Destination SSID: ");
        Serial.println(recievedPacket.getDestSSID());

        Serial.print("Source Address: ");
        for (const auto& val : recievedPacket.getSourAddr()) {
          Serial.print(val);
        }
        Serial.print("\n");

        Serial.print("Source SSID: ");
        Serial.println(recievedPacket.getSourSSID());

        Serial.print("Data: ");
        for (const auto& val : recievedPacket.getData()) {
          int num = val; // this line is just so numbers are pritned in readable ascii
          Serial.print(num);
        }
        Serial.print("\n");

        Serial.print("FCS: ");
        for (const auto& val : recievedPacket.getFcs()) {
          int num = val; // this line is just so numbers are pritned in readable ascii
          Serial.print(num);
        }
        Serial.print("\n");
      }
    }
    client.stop(); // Close the connection
    Serial.println("Client Disconnected");
  }
}


std::vector<char> getAx25Data(WiFiClient* client) {
  std::vector<char> rawData;
  char byte = client->read();
  char escapeFlag = 0;

  // Check that packet reading is synchronise (first byte should be a flag)
  if (byte == FLAG) {
    // Make sure to append that first flag
    rawData.push_back(byte);
    while(true) {
      char prevByte = byte;
      byte = client->read();

      if (escapeFlag == 0 && byte == ESCAPE) {
        escapeFlag = 1;
        continue;
      }
      else if (escapeFlag == 0 && byte == FLAG) {
        rawData.push_back(byte);
        break;
      }
      else if (escapeFlag == 1) {
        rawData.push_back(byte);
        escapeFlag = 0;
      }
      else {
        // (escapeFlag == 0 && byte is something random)
        rawData.push_back(byte);
      }
    }
  }
  else {
    Serial.println("ERROR: Recieved packet is out of sync!!");
  }
  std::vector<char> data(rawData.begin() + 17, rawData.end() - 3);

  return data;
}






