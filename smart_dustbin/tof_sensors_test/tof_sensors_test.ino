#include "Adafruit_VL53L0X.h"

// address we will assign if dual sensor is present
#define sensor1_ADDRESS 0x30
#define sensor2_ADDRESS 0x31
#define sensor3_ADDRESS 0x32

// set the pins to shutdown
#define sensor1_xshut 32  // GPIO32 // P19
#define sensor2_xshut 33  // GPIO33 // P20
#define sensor3_xshut 26  // GPIO26 // P21
//#define sensor3_xshut 22  // GPIO22 // P11


// objects for the vl53l0x
Adafruit_VL53L0X sensor1 = Adafruit_VL53L0X();
Adafruit_VL53L0X sensor2 = Adafruit_VL53L0X();
Adafruit_VL53L0X sensor3 = Adafruit_VL53L0X();

// this holds the measurement
VL53L0X_RangingMeasurementData_t Abstand1;
VL53L0X_RangingMeasurementData_t Abstand2;
VL53L0X_RangingMeasurementData_t Abstand3;

/*
    Reset all sensors by setting all of their XSHUT pins low for delay(10), then set all XSHUT high to bring out of reset
    Keep sensor #1 awake by keeping XSHUT pin high
    Put all other sensors into shutdown by pulling XSHUT pins low
    Initialize sensor #1 with lox.begin(new_i2c_address) Pick any number but 0x29 and it must be under 0x7F. Going with 0x30 to 0x3F is probably OK.
    Keep sensor #1 awake, and now bring sensor #2 out of reset by setting its XSHUT pin high.
    Initialize sensor #2 with lox.begin(new_i2c_address) Pick any number but 0x29 and whatever you set the first sensor to
 */


  
void init_lasers() {
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

void read_dual_sensors() {
  
  sensor1.rangingTest(&Abstand1, false); // pass in 'true' to get debug data printout!
  sensor2.rangingTest(&Abstand2, false); // pass in 'true' to get debug data printout!
  sensor3.rangingTest(&Abstand3, false); // pass in 'true' to get debug data printout!

  // print sensor one reading
  Serial.print(F("Sensor 1: "));
  if(Abstand1.RangeStatus != 4) {     // if not out of range
    Serial.print(Abstand1.RangeMilliMeter);
  } else {
    Serial.print(F("Out of range"));
  }
  
  Serial.print(F("  "));

  // print sensor two reading
  Serial.print(F("Sensor 2: "));
  if(Abstand2.RangeStatus != 4) {
    Serial.print(Abstand2.RangeMilliMeter);
  } else {
    Serial.print(F("Out of range"));
  }
  Serial.print(F("  "));
    // print sensor three reading
  Serial.print(F("Sensor 3: "));
  if(Abstand3.RangeStatus != 4) {
    Serial.print(Abstand3.RangeMilliMeter);
  } else {
    Serial.print(F("Out of range"));
  }
  
  Serial.println();
}

void setup() {
  Serial.begin(9600);

  // wait until serial port opens for native USB devices
  while (! Serial) { delay(1); }


  

  init_lasers();
 
}

void loop() {
   
  read_dual_sensors();
  delay(100);
}
