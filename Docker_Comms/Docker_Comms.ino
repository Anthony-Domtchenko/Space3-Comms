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
        // Start by recieving the request packet from the ground station
        std::vector<char> packet = recieveAx25Packet(&client);
        RxAx25 recievedPacket(packet);

        // Print the recieved data
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


        // Send back a packet with information 'A B C ~ }'
        std::vector<char> responseData = {'A', 'B', 'C', 0x7E, 0x7D};
        std::vector<char> txPacket = ax25encode(responseData, true);
        if (sendAx25Packet(&client, txPacket)) {
          Serial.println("Tx Packet Sent!");
          client.stop();
        }
      }
    }
    //client.stop(); // Close the connection
    Serial.println("Client Disconnected");
  }
}






