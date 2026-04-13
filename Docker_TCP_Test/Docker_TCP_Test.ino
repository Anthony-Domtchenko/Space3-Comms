#include <WiFi.h>
#include <WiFiAP.h>


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
        String data = client.readStringUntil('\n'); // Read incoming data (blocking)
        Serial.println("Received: " + data);
        client.println("Message Received Slug"); // Send response
      }
    }
    client.stop(); // Close the connection
    Serial.println("Client Disconnected");
  }
}
