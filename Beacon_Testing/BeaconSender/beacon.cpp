#include "beacon.hpp"

static RadioEvents_t RadioEvents;
bool loraIdle = true;

void initLoRa(void) {
  RadioEvents.TxDone = OnTxDone;
  RadioEvents.TxTimeout = OnTxTimeout;
  
  Radio.Init( &RadioEvents );
  Radio.SetChannel( RF_FREQUENCY );
  Radio.SetTxConfig( MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
                                  LORA_SPREADING_FACTOR, LORA_CODINGRATE,
                                  LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                                  true, 0, 0, LORA_IQ_INVERSION_ON, 3000 );
}



bool handleOBCBeacon(void) {
  UART_msg_t msg;
  if (UART_receive(&Serial2, &msg)) {
    Serial.println("Recieved beacon message from OBC");

    if (!checkMessage(&msg)) {
      return false;
    }

    // Convert beacon data to vector and ax25 encode
    std::vector<char> beaconData(msg.payload, msg.payload + msg.length);
    std::vector<char> beaconPacket = ax25encode(beaconData, true);

    // Send Packet over LoRa
    sendLoRa(beaconPacket);
  }
  return true;
}



bool checkMessage(UART_msg_t* msg) {
  if (msg->id != BEACON_MSG_ID) {
    Serial.println("Beacon ID Invalid");
    return false;
  }
  if (msg->length != BEACON_TIME_STRING_BYTES + CUBESAT_IDENTIFIER_BYTES + BEACON_MSG_DATA_BYTES) {
    Serial.println("Beacon Length Invalid");
    return false;
  }
  return true;
}



void sendLoRa(std::vector<char>& packet) {
  uint8_t* packetPtr = reinterpret_cast<uint8_t*>(packet.data());
  uint8_t length = packet.size();
  Radio.Send(packetPtr, length);
  loraIdle = false;
  while (loraIdle == false) {
    Radio.IrqProcess();
  }
}



void OnTxDone(void) {
  Radio.Sleep();
  Serial.println("LoRa Tx Done......");
	loraIdle = true;
}



void OnTxTimeout(void) {
  Radio.Sleep();
  Serial.println("LoRa Tx Timeout......");
	loraIdle = true;
}


