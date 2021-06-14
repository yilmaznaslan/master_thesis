
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <VL53L0X.h>
#include <ArduinoJson.h>


int laser_three = 32;  // P19 = GPIO32 (ESP32)
int laser_two = 33;    // P20 = GPIO33 (ESP32)
int laser_one = 26;    // P21 = GPIO26 (ESP32)
TwoWire I2CBME = TwoWire(0);

VL53L0X sensor1;
VL53L0X sensor2;
VL53L0X sensor3;
StaticJsonDocument<200> doc;

float maxhight = 71.8;

float Abstand1;

float Abstand2;

float Abstand3;

float Mittelwert1;

float Abstand4;

float Abstand5;

float Abstand6;

float Mittelwert2;

float Abstand7;

float Abstand8;

float Abstand9;

float Mittelwert3;

float Abstand10;

float Abstand11;

float Abstand12;

float Mittelwert4;

float fuellstand;

float Abstand;

// Benoetigte Variablen werden definiert

int counter = 0;
bool gesendet;
bool hochfrequent = true;
bool i = true;




#define PIN 0
int timer = 0;
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(1, PIN, NEO_GRB + NEO_KHZ800);

static const u1_t PROGMEM APPEUI[8] = { 0x74, 0x38, 0x03, 0xD0, 0x7E, 0xD5, 0xB3, 0X70};
static const u1_t PROGMEM DEVEUI[8] = {0x53, 0x7F, 0x51, 0x0B, 0x47, 0xE5, 0x49, 0x00};
static const u1_t PROGMEM APPKEY[16] = {0xD0, 0x23, 0x08, 0x87, 0xCD, 0x46, 0x9D, 0x25, 0xDF, 0xD5, 0xDB, 0x73, 0xF0, 0xFE, 0x62, 0x9D};

void os_getArtEui (u1_t* buf) {
  memcpy_P(buf, APPEUI, 8);
}
void os_getDevEui (u1_t* buf) {
  memcpy_P(buf, DEVEUI, 8);
}
void os_getDevKey (u1_t* buf) {
  memcpy_P(buf, APPKEY, 16);
}


static osjob_t txjob;
bool is_joined = false;

// Pin mapping
const lmic_pinmap lmic_pins = {
  .nss = 18,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = LMIC_UNUSED_PIN,
  .dio = {23, 23, 23},
};

void onEvent (ev_t ev) {
  Serial.print(os_getTime());
  Serial.print(": ");
  switch (ev) {
    case EV_SCAN_TIMEOUT:
      Serial.println(F("EV_SCAN_TIMEOUT"));
      break;
    case EV_BEACON_FOUND:
      Serial.println(F("EV_BEACON_FOUND"));
      break;
    case EV_BEACON_MISSED:
      Serial.println(F("EV_BEACON_MISSED"));
      break;
    case EV_BEACON_TRACKED:
      Serial.println(F("EV_BEACON_TRACKED"));
      break;
    case EV_JOINING:
      Serial.println(F("EV_JOINING"));
      break;
    case EV_JOINED:
      Serial.println(F("EV_JOINED"));
      is_joined = true;
      // Disable link check validation (automatically enabled
      // during join, but not supported by TTN at this time).
      LMIC_setLinkCheckMode(0);
      pixels.setPixelColor(0, pixels.Color(0, 128, 0));
      pixels.show();
      delay(1000);
      pixels.setPixelColor(0, pixels.Color(0, 0, 0));
      pixels.show();
      break;
    case EV_RFU1:
      Serial.println(F("EV_RFU1"));
      break;
    case EV_JOIN_FAILED:
      Serial.println(F("EV_JOIN_FAILED"));
      break;
    case EV_REJOIN_FAILED:
      Serial.println(F("EV_REJOIN_FAILED"));
      break;
      break;
    case EV_TXCOMPLETE:
      Serial.println(F("EV_TXCOMPLETE (includes waiting for RX windows)"));
      if (LMIC.txrxFlags & TXRX_ACK)
        Serial.println(F("Received ack"));
      if (LMIC.dataLen) {
        Serial.println(F("Received "));
        Serial.println(LMIC.dataLen);
        Serial.println(F(" bytes of payload"));
      }
      // Schedule next transmission
      //os_setTimedCallback(&txjob, os_getTime()+sec2osticks(TX_INTERVAL), add_tx_queue);
      pixels.setPixelColor(0, pixels.Color(0, 128, 0));
      pixels.show();
      delay(1000);
            //os_setTimedCallback(&txjob, os_getTime()+sec2osticks(TX_INTERVAL), add_tx_queue);
      pixels.setPixelColor(0, pixels.Color(0, 0, 0));
      pixels.show();
      break;
    case EV_LOST_TSYNC:
      Serial.println(F("EV_LOST_TSYNC"));
      break;
    case EV_RESET:
      Serial.println(F("EV_RESET"));
      break;
    case EV_RXCOMPLETE:
      // data received in ping slot
      Serial.println(F("EV_RXCOMPLETE"));
      break;
    case EV_LINK_DEAD:
      Serial.println(F("EV_LINK_DEAD"));
      break;
    case EV_LINK_ALIVE:
      Serial.println(F("EV_LINK_ALIVE"));
      break;
    default:
      Serial.println(F("Unknown event"));
      break;
  }
}

void add_tx_queue(osjob_t* j, int val = 50) {
  // Check if there is not a current TX/RX job running
  
  byte tx_byte = val;

  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println(F("OP_TXRXPEND, not sending"));
  } else {
    // Prepare upstream data transmission at the next possible time.
    LMIC_setTxData2(1,&tx_byte , sizeof(tx_byte), 0);
    Serial.print("Tx Packet queued, Data: ");
    Serial.println(tx_byte);
  }

}


void init_lasers() {
  int sda = 25; // P22
  int scl = 14; // P23
  
  pinMode(laser_three, OUTPUT);
  pinMode(laser_two, OUTPUT);
  pinMode(laser_one, OUTPUT);

  digitalWrite(laser_three, HIGH);
  digitalWrite(laser_two, HIGH);
  digitalWrite(laser_one, HIGH);
  delay(500);

  Wire.begin(sda,scl);
  //I2CBME.begin(sda,scl, 100000);

  // Init laser sensor1 address 1
  digitalWrite(laser_one, HIGH);
  delay(150);
  sensor1.init(true);
  delay(100);
  sensor1.setAddress((uint8_t)01);


  // Init laser sensor1 address 2
  digitalWrite(laser_two, HIGH);
  delay(150);
  sensor2.init(true);
  delay(100);
  sensor2.setAddress((uint8_t)02);


  // Init laser sensor1 address 3
  digitalWrite(laser_three, HIGH);
  delay(150);
  sensor3.init(true);
  delay(100);
  sensor3.setAddress((uint8_t)03);



  sensor1.startContinuous();
  sensor2.startContinuous();
  sensor3.startContinuous();

}
void setup() {
  init_lasers();
   
  pixels.begin();
  Serial.begin(9600);
  Serial.print("\nStarting\n");
  
  // LMIC init
  os_init();

  // Reset the MAC state. Session and pending data transfers will be discarded.
  LMIC_reset();

  // Start job (sending automatically starts OTAA too)
  //add_tx_queue(&txjob);

  // Start OTAA and add the initial job to upstream data transmission at the next possible time.
  add_tx_queue(&txjob, 100);

  // Set initial Color to Red
  pixels.setPixelColor(0, pixels.Color(128, 0, 0));
  pixels.show();



  // Wait until LoRa Connection to TTN is established
  while (is_joined) {
    os_runloop_once();
  }



}

void loop() {
  // This must be run continously
  os_runloop_once();

  // Only run to send TX Packet
  // add_tx_queue(&txjob, random(0,100) );
  // delay(10000);
  marco();


}

void marco(){
  switch (hochfrequent) {
    case true:
      if (counter == 4 ) {
        counter -= 4;
      } else if (gesendet == true) {
        counter = 0;
        gesendet = false;
      }
      if (i == true) {
        Serial.println("Standort wird überprüft...");
        delay(2000);
        Serial.println("hochfrequenter Standort --> Berlin Alexanderplatz");
        i = false;
        Serial.println("-----------------------------");
      }
      delay(3000);
      Abstand1 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand1 beträgt:");
      Serial.print(Abstand1 / 10);
      Serial.println("cm");

      delay(2000);


      Abstand2 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand2 beträgt:");
      Serial.print(Abstand2 / 10);
      Serial.println("cm");

      delay(2000);


      Abstand3 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand3 beträgt:");
      Serial.print(Abstand3 / 10);
      Serial.println("cm");

      Mittelwert1 = (((Abstand1 + Abstand2 + Abstand3) / 3) / 10);


      Serial.print("der gemittelte Abstand der ersten Messung beträgt:");
      Serial.print(Mittelwert1);
      Serial.println("cm");

      delay(10000);

      Abstand4 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand4 beträgt:");
      Serial.print(Abstand4 / 10);
      Serial.println("cm");

      delay(2000);

      Abstand5 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand5 beträgt:");
      Serial.print(Abstand5 / 10);
      Serial.println("cm");

      delay(2000);


      Abstand6 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand6 beträgt:");
      Serial.print(Abstand6 / 10);
      Serial.println("cm");


      Mittelwert2 = (((Abstand4 + Abstand5 + Abstand6) / 3) / 10);

      Serial.print("der gemittelte Abstand der zweiten Messung beträgt:");
      Serial.print(Mittelwert2);
      Serial.println("cm");


      delay(10000);

      Abstand7 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand7 beträgt:");
      Serial.print(Abstand7 / 10);
      Serial.println("cm");


      delay(2000);
      Abstand8 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand8 beträgt:");
      Serial.print(Abstand8 / 10);
      Serial.println("cm");

      delay(2000);


      Abstand9 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand9 beträgt:");
      Serial.print(Abstand9 / 10);
      Serial.println("cm");

      Mittelwert3 = (((Abstand7 + Abstand8 + Abstand9) / 3) / 10);


      Serial.print("der gemittelte Abstand der dritten Messung beträgt:");
      Serial.print(Mittelwert3);
      Serial.println("cm");

      delay(10000);

      Abstand10 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand10 beträgt:");
      Serial.print(Abstand10 / 10);
      Serial.println("cm");

      delay(2000);

      Abstand11 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand11 beträgt:");
      Serial.print(Abstand11 / 10);
      Serial.println("cm");


      delay(2000);

      Abstand12 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand12 beträgt:");
      Serial.print(Abstand12 / 10);
      Serial.println("cm");

      Mittelwert4 = (((Abstand10 + Abstand11 + Abstand12) / 3) / 10);


      Serial.print("der gemittelte Abstand der vierten Messung beträgt:");
      Serial.print(Mittelwert4);
      Serial.println("cm");

      delay(10000);

      Abstand = (Mittelwert1 + Mittelwert2 + Mittelwert3 + Mittelwert4) / 4;
      fuellstand = 100 - ((Abstand * 100) / maxhight);

      delay(3000);

      Serial.print("der finale Abstand beträgt:");
      Serial.print(Abstand);
      Serial.println("cm");



      if (Abstand > maxhight ) {                     // Falls der gemessene Abstand höher ist als die max. Höhe des Mülleimers wird ein Fehler ausgegeben

        Serial.println ("nicht funktionsfähig");

      }

      else {

        Serial.print ("Füllstand beträgt:");
        Serial.print (fuellstand);
        Serial.println ("%");
      }
      // Für hochfrequente Standorte gilt: Der Füllstand wird sofort geschickt falls dieser >=90% ist oder zwischen 75% und 90% liegt.
      // Ansosnten wird der Füllstand nach 12 Stunden oder 3 Schleifendurchläufen geschickt.


      if (fuellstand > 90) {                            //wird geprüft ob Füllstand über 90% ist , falls ja wird dieser direkt geschickt
        Serial.println("Füllstand wird geschickt");
        add_tx_queue(&txjob, fuellstand);
        Serial.println("nächste Messung in 4h");
        Serial.println("-----------------------------");
        counter++;
        gesendet = true;
        delay(10000); //4h Warten
      }

      else if (fuellstand >= 75 && fuellstand <= 90) { // für hochfrequenten Standort wird der Füllstand geschickt falls er zwischen 75 und 90 Prozent liegt
        Serial.println("Füllstand wird geschickt");
        add_tx_queue(&txjob, fuellstand);
        Serial.println("nächste Messung in 4h");
        Serial.println("-----------------------------");
        counter++;
        gesendet = true;
        delay(10000); //4 h Warten
      }

      else if (counter >= 3 ) {                          //beim dritten Durchlauf bzw. nach 12 Stunden wird der Füllstand geschickt egal wie hoch dieser ist
        Serial.println("Füllstand wird geschickt");
        add_tx_queue(&txjob, fuellstand);
        Serial.println("nächste Messung in 4h");
        Serial.println("-----------------------------");
        counter++;
        delay(10000); // 4 h warten
      }
      else {
        Serial.println("nächste Messung in 4h");  //falls nichts zutrifft wird die schleife einfach wiederholt --> Schleifen Counter eins nach oben gesetzt--> neue 4 Stunden
        Serial.println("-----------------------------");
        counter++;
        delay(10000); //4 h warten
      }
      break;
    case false:
      if (counter == 4 ) {
        counter -= 4;
      } else if (gesendet == true) {
        counter = 0;
        gesendet = false;
      }

      if (i == true) {
        Serial.println("Standort wird überprüft...");
        delay(2000);
        Serial.println("nicht hochfrequenter Standort --> Berlin Marzahn");
        i = false;
        Serial.println("-----------------------------");
      }
      delay(10000);

      Abstand1 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand1 beträgt:");
      Serial.print(Abstand1 / 10);
      Serial.println("cm");



      Abstand2 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand2 beträgt:");
      Serial.print(Abstand2 / 10);
      Serial.println("cm");




      Abstand3 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand3 beträgt:");
      Serial.print(Abstand3 / 10);
      Serial.println("cm");

      Mittelwert1 = (((Abstand1 + Abstand2 + Abstand3) / 3) / 10);


      Serial.print("der gemittelte Abstand der ersten Messung beträgt:");
      Serial.print(Mittelwert1);
      Serial.println("cm");

      delay(10000);

      Abstand4 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand4 beträgt:");
      Serial.print(Abstand4 / 10);
      Serial.println("cm");



      Abstand5 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand5 beträgt:");
      Serial.print(Abstand5 / 10);
      Serial.println("cm");




      Abstand6 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand6 beträgt:");
      Serial.print(Abstand6 / 10);
      Serial.println("cm");


      Mittelwert2 = (((Abstand4 + Abstand5 + Abstand6) / 3) / 10);

      Serial.print("der gemittelte Abstand der zweiten Messung beträgt:");
      Serial.print(Mittelwert2);
      Serial.println("cm");


      delay(10000);

      Abstand7 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand7 beträgt:");
      Serial.print(Abstand7 / 10);
      Serial.println("cm");



      Abstand8 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand8 beträgt:");
      Serial.print(Abstand8 / 10);
      Serial.println("cm");




      Abstand9 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand9 beträgt:");
      Serial.print(Abstand9 / 10);
      Serial.println("cm");

      Mittelwert3 = (((Abstand7 + Abstand8 + Abstand9) / 3) / 10);


      Serial.print("der gemittelte Abstand der dritten Messung beträgt:");
      Serial.print(Mittelwert3);
      Serial.println("cm");

      delay(10000);

      Abstand10 = sensor1.readRangeContinuousMillimeters();

      Serial.print("Abstand10 beträgt:");
      Serial.print(Abstand10 / 10);
      Serial.println("cm");



      Abstand11 = sensor2.readRangeContinuousMillimeters();

      Serial.print("Abstand11 beträgt:");
      Serial.print(Abstand11 / 10);
      Serial.println("cm");




      Abstand12 = sensor3.readRangeContinuousMillimeters();

      Serial.print("Abstand12 beträgt:");
      Serial.print(Abstand12 / 10);
      Serial.println("cm");

      Mittelwert4 = (((Abstand10 + Abstand11 + Abstand12) / 3) / 10);


      Serial.print("der gemittelte Abstand der vierten Messung beträgt:");
      Serial.print(Mittelwert4);
      Serial.println("cm");

      delay(10000);

      Abstand = (Mittelwert1 + Mittelwert2 + Mittelwert3 + Mittelwert4) / 4;
      fuellstand = 100 - ((Abstand * 100) / maxhight);

      delay(3000);

      Serial.print("der finale Abstand beträgt:");
      Serial.print(Abstand);
      Serial.println("cm");


      if (Abstand > maxhight ) {                         // auch für nicht hochfrequente Standorte wird ein Fehler ausgegeben falls der gemessene Absatnd höher ist als die max. Höhe des Mülleimers

        Serial.println ("nicht funktionsfähig");

      }

      else {

        Serial.print ("Füllstand beträgt:");
        Serial.print (fuellstand);
        Serial.println ("%");
      }
      // Für nicht hochfrequente Standorte gilt: der Füllstand wird sofort geschickt sobald er bei über 90% liegt.
      //Falls er zwischen 75% und 90% liegt wird der Füllstand nicht geschickt und die Messung nach 4 Stunden wiederholt.
      // Nach 12 Stunden oder drei Schleifendurchläufen wird der Füllstand geschickt


      if (fuellstand > 90) {                            //wird geprüft ob Füllstand über 90% ist, falls ja wird dieser auch für nicht hochfrequente Standorte sofort geschickt
        Serial.println("Füllstand wird geschickt");
        add_tx_queue(&txjob, fuellstand);
        Serial.println("nächste Messung in 4h");
        Serial.println("-----------------------------");
        counter++;
        gesendet = true;
        delay(10000); //warten 4h
      }

      else if (counter >= 3 ) {                          // nach 12 Stunden, oder nach dem dritten Durchlauf wird der Füllstand geschickt unabhängig wie hoch dieser ist.
        Serial.println("Füllstand wird geschickt");
        add_tx_queue(&txjob, fuellstand);
        Serial.println("nächste Messung in 4h");
        Serial.println("-----------------------------");
        counter++;
        delay(10000); // warten 4 h
      }
      else {
        Serial.println("nächste Messung in 4h");         //falls nichts zutrifft wird die schleife einfach wiederholt --> Schleifen Counter wird eins nach oben gesetzt--> neue 4 Stunden
        Serial.println("-----------------------------");
        counter++;
        delay(10000);// warten 4 h
      }
      break;
  }

}
