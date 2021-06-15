// LoRaWAN Libraries
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <Adafruit_NeoPixel.h>

// Other Libraries
#include <ArduinoJson.h>

// Sensor library build for ESP32
#include "Adafruit_VL53L0X.h"

// Defining the xshut pins of sensors
int sensor1_xshut = 32;  // GPIO32(ESP32) & P19(Lopy4) 
int sensor2_xshut = 33;  // GPIO33(ESP32) & P20(Lopy4) 
int sensor3_xshut = 26;  // GPIO26(ESP32) & P21(Lopy4)

// Defining I2C Slave address we will assign if dual sensor is present
#define sensor1_ADDRESS 0x30
#define sensor2_ADDRESS 0x31
#define sensor3_ADDRESS 0x32


// Defining objects for the vl53l0x sesnors
Adafruit_VL53L0X sensor1 = Adafruit_VL53L0X();
Adafruit_VL53L0X sensor2 = Adafruit_VL53L0X();
Adafruit_VL53L0X sensor3 = Adafruit_VL53L0X();
StaticJsonDocument<200> doc;

// this holds the measurement
VL53L0X_RangingMeasurementData_t sensor1_data;
VL53L0X_RangingMeasurementData_t sensor2_data;
VL53L0X_RangingMeasurementData_t sensor3_data;

float Abstand1;
float Abstand2;
float Abstand3;
float Abstand4;
float Abstand5;
float Abstand6;
float Abstand7;
float Abstand8;
float Abstand9;
float Abstand10;
float Abstand11;
float Abstand12;


float maxhight = 71.8;

float Mittelwert1;

float Mittelwert2;

float Mittelwert3;

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


void init_sensors() {
  Serial.println(F("Shutdown pins inited..."));
  pinMode(sensor1_xshut,OUTPUT);
  pinMode(sensor2_xshut,OUTPUT);
  pinMode(sensor3_xshut,OUTPUT);
  
  // all reset
  digitalWrite(sensor1_xshut, LOW);    
  digitalWrite(sensor2_xshut, LOW);
  digitalWrite(sensor3_xshut, LOW);
  delay(100);

  
  // all unreset
  digitalWrite(sensor1_xshut, HIGH);
  digitalWrite(sensor2_xshut, HIGH);
  digitalWrite(sensor3_xshut, HIGH);
  delay(100);

  // all reset again
  digitalWrite(sensor1_xshut, LOW);
  digitalWrite(sensor2_xshut, LOW);
  digitalWrite(sensor3_xshut, LOW);
  delay(100);

  // Initialize sensor1
  digitalWrite(sensor1_xshut, HIGH);
  if(!sensor1.begin(sensor1_ADDRESS)) {
    Serial.println(F("Failed to boot first VL53L0X"));
    while(1);
  }
   Serial.println(F("Successfull to boot first VL53L0X"));
  

  // Initialize sensor2
  digitalWrite(sensor2_xshut, HIGH);
  delay(100);
  if(!sensor2.begin(sensor2_ADDRESS)) {
    Serial.println(F("Failed to boot second VL53L0X"));
    while(1);
  }
Serial.println(F("Successfull to boot second VL53L0X"));
  
  // activating sensor3
  digitalWrite(sensor3_xshut, HIGH);
  delay(100);
  if(!sensor3.begin(sensor3_ADDRESS)) {
    Serial.println(F("Failed to boot third VL53L0X"));
    while(1);
  }
Serial.println(F("Successfull to boot third VL53L0X"));



    Serial.println(F("Starting..."));
}
void setup() {
  init_sensors();
   
  pixels.begin();
  Serial.begin(9600);
  Serial.print("\nStarting\n");
  
  // LMIC init
  os_init();

  // Reset the MAC state. Session and pending data transfers will be discarded.
  LMIC_reset();


  // Start OTAA and add the initial job to upstream data transmission at the next possible time.
  add_tx_queue(&txjob, 100);

  // Set initial Color to Red
  pixels.setPixelColor(0, pixels.Color(128, 0, 0));
  pixels.show();



  // Wait until LoRa Connection to TTN is established
  while (not is_joined) {
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
        sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand1  =sensor1_data.RangeMilliMeter;
  os_runloop_once();
      Serial.print("Abstand1 beträgt:");
      Serial.print(Abstand1 / 10);
      Serial.println("cm");

      delay(2000);


      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand2  =sensor2_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand2 beträgt:");
      Serial.print(Abstand2 / 10);
      Serial.println("cm");

      delay(2000);


      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand3  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand3 beträgt:");
      Serial.print(Abstand3 / 10);
      Serial.println("cm");

      Mittelwert1 = (((Abstand1 + Abstand2 + Abstand3) / 3) / 10);


      Serial.print("der gemittelte Abstand der ersten Messung beträgt:");
      Serial.print(Mittelwert1);
      Serial.println("cm");

      delay(10000);

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand4  =sensor1_data.RangeMilliMeter;
os_runloop_once();
      Serial.print("Abstand4 beträgt:");
      Serial.print(Abstand4 / 10);
      Serial.println("cm");

      delay(2000);

      
      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand5  =sensor2_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand5 beträgt:");
      Serial.print(Abstand5 / 10);
      Serial.println("cm");

      delay(2000);


      
      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand6  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand6 beträgt:");
      Serial.print(Abstand6 / 10);
      Serial.println("cm");


      Mittelwert2 = (((Abstand4 + Abstand5 + Abstand6) / 3) / 10);

      Serial.print("der gemittelte Abstand der zweiten Messung beträgt:");
      Serial.print(Mittelwert2);
      Serial.println("cm");


      delay(10000);

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand7  =sensor1_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand7 beträgt:");
      Serial.print(Abstand7 / 10);
      Serial.println("cm");


      delay(2000);
      
      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand8  =sensor2_data.RangeMilliMeter;

os_runloop_once();
      Serial.print("Abstand8 beträgt:");
      Serial.print(Abstand8 / 10);
      Serial.println("cm");

      delay(2000);


      
      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand9  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand9 beträgt:");
      Serial.print(Abstand9 / 10);
      Serial.println("cm");

      Mittelwert3 = (((Abstand7 + Abstand8 + Abstand9) / 3) / 10);


      Serial.print("der gemittelte Abstand der dritten Messung beträgt:");
      Serial.print(Mittelwert3);
      Serial.println("cm");

      delay(10000);

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand10  =sensor1_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand10 beträgt:");
      Serial.print(Abstand10 / 10);
      Serial.println("cm");

      delay(2000);

      
      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand11  =sensor2_data.RangeMilliMeter;

os_runloop_once();
      Serial.print("Abstand11 beträgt:");
      Serial.print(Abstand11 / 10);
      Serial.println("cm");


      delay(2000);

      
      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand12  =sensor3_data.RangeMilliMeter;
os_runloop_once();

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
os_runloop_once();
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

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand1  =sensor1_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand1 beträgt:");
      Serial.print(Abstand1 / 10);
      Serial.println("cm");



     
      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand2  =sensor2_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand2 beträgt:");
      Serial.print(Abstand2 / 10);
      Serial.println("cm");

      
      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand3  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand3 beträgt:");
      Serial.print(Abstand3 / 10);
      Serial.println("cm");

      Mittelwert1 = (((Abstand1 + Abstand2 + Abstand3) / 3) / 10);


      Serial.print("der gemittelte Abstand der ersten Messung beträgt:");
      Serial.print(Mittelwert1);
      Serial.println("cm");

      delay(10000);

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand4  =sensor1_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand4 beträgt:");
      Serial.print(Abstand4 / 10);
      Serial.println("cm");



      
      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand5  =sensor2_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand5 beträgt:");
      Serial.print(Abstand5 / 10);
      Serial.println("cm");




    
      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand6  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand6 beträgt:");
      Serial.print(Abstand6 / 10);
      Serial.println("cm");


      Mittelwert2 = (((Abstand4 + Abstand5 + Abstand6) / 3) / 10);

      Serial.print("der gemittelte Abstand der zweiten Messung beträgt:");
      Serial.print(Mittelwert2);
      Serial.println("cm");


      delay(10000);

      
      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand7  =sensor1_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand7 beträgt:");
      Serial.print(Abstand7 / 10);
      Serial.println("cm");




      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand8  =sensor2_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand8 beträgt:");
      Serial.print(Abstand8 / 10);
      Serial.println("cm");




      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand9  =sensor3_data.RangeMilliMeter;
os_runloop_once();

      Serial.print("Abstand9 beträgt:");
      Serial.print(Abstand9 / 10);
      Serial.println("cm");

      Mittelwert3 = (((Abstand7 + Abstand8 + Abstand9) / 3) / 10);


      Serial.print("der gemittelte Abstand der dritten Messung beträgt:");
      Serial.print(Mittelwert3);
      Serial.println("cm");

      delay(10000);


      sensor1.rangingTest(&sensor1_data, false); // pass in 'true' to get debug data printout!
      Abstand10  =sensor1_data.RangeMilliMeter;
os_runloop_once();
      Serial.print("Abstand10 beträgt:");
      Serial.print(Abstand10 / 10);
      Serial.println("cm");



      sensor2.rangingTest(&sensor2_data, false); // pass in 'true' to get debug data printout!
      Abstand11  =sensor2_data.RangeMilliMeter;


      Serial.print("Abstand11 beträgt:");
      Serial.print(Abstand11 / 10);
      Serial.println("cm");




      sensor3.rangingTest(&sensor3_data, false); // pass in 'true' to get debug data printout!
      Abstand12  =sensor3_data.RangeMilliMeter;

os_runloop_once();
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
os_runloop_once();
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

os_runloop_once();
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
