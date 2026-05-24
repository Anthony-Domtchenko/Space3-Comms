#include "LoRaWan_APP.h"
#include "Arduino.h"
#include "ax25.hpp"


#define RF_FREQUENCY                                915000000 // Hz
#define TX_OUTPUT_POWER                             14        // dBm
#define LORA_BANDWIDTH                              0         // [0: 125 kHz,
                                                              //  1: 250 kHz,
                                                              //  2: 500 kHz,
                                                              //  3: Reserved]
#define LORA_SPREADING_FACTOR                       7         // [SF7..SF12]
#define LORA_CODINGRATE                             1         // [1: 4/5,
                                                              //  2: 4/6,
                                                              //  3: 4/7,
                                                              //  4: 4/8]
#define LORA_PREAMBLE_LENGTH                        8         // Same for Tx and Rx
#define LORA_SYMBOL_TIMEOUT                         0         // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON                  false
#define LORA_IQ_INVERSION_ON                        false
#define RX_TIMEOUT_VALUE                            1000


static RadioEvents_t RadioEvents;
int16_t rssi,rxSize;
bool loraIdle = true;

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD,SLOW_CLK_TPYE);

    rssi=0;
  
    RadioEvents.RxDone = OnRxDone;
    Radio.Init( &RadioEvents );
    Radio.SetChannel( RF_FREQUENCY );
    Radio.SetRxConfig( MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
                               LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
                               LORA_SYMBOL_TIMEOUT, LORA_FIX_LENGTH_PAYLOAD_ON,
                               0, true, 0, 0, LORA_IQ_INVERSION_ON, true );


  Serial.println();
  Serial.println("Configuring LoRa Transmitter...");
}

void loop() {
  if(loraIdle)
  {
    loraIdle = false;
    Serial.println("into RX mode");
    Radio.Rx(0);
  }
  Radio.IrqProcess();
}


void OnRxDone( uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr )
{
    rssi=rssi;
    rxSize=size;
    std::vector<char> ax25Packet(payload, payload + size);
    Radio.Sleep();

    RxAx25 decodedPacket(ax25Packet);
    Serial.printf("\r\nReceived Packet with rssi %d , length %d\r\n",rssi,rxSize);

    Serial.print("Destination Address: ");
    for (char c : decodedPacket.getDestAddr()) {
    Serial.print(c);
    }
    Serial.println();

    Serial.printf("Desitanation SSID: %d\r\n", decodedPacket.getDestSSID());

    Serial.print("Source Address: ");
    for (char c : decodedPacket.getSourAddr()) {
    Serial.print(c);
    }
    Serial.println();

    Serial.printf("Source SSID: %d\r\n", decodedPacket.getSourSSID());
    Serial.println();

    Serial.print("Data: ");
    for (char c : decodedPacket.getData()) {
    Serial.printf("%d", c);
    }
    Serial.println();

    if (decodedPacket.fcsCompare()) {
      Serial.println("FCS is intact");
    }
    else {
      Serial.println("FCS is fucked");
    }


    loraIdle = true;
}


