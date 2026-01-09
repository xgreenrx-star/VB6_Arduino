#include <Arduino.h> // L0001
#include <ESP32Servo.h> // L0002
// L0003
// __VB_LINE__:6 // L0004
Servo myServo; // L0005
// L0006
void setup() { // L0007
    delay(1000); // L0008
    // __VB_LINE__:9 // L0009
    Serial.begin(115200); // L0010
    Serial.setRxBufferSize(1024); // L0011
    Serial.setTxBufferSize(1024); // L0012
    // __VB_LINE__:10 // L0013
    Serial.println("Servo Library Demo" + "\r\n"); // L0014
    // __VB_LINE__:13 // L0015
    myServo.attach(18); // L0016
} // L0017
// L0018
void loop() { // L0019
    // __VB_LINE__:17 // L0020
    int angle = 0; // L0021
    // __VB_LINE__:20 // L0022
    for (int angle = 0; ((10) >= 0 ? angle <= 180 : angle >= 180); angle += (10)) { // L0023
    // __VB_LINE__:21 // L0024
    int us = 0; // L0025
    // __VB_LINE__:22 // L0026
    us = (int)(1000 + (((int)min(180, max(0, (int)(angle)))) * (1000.0/180.0))); // L0027
    // __VB_LINE__:23 // L0028
    myServo.writeMicroseconds(us); // L0029
    // __VB_LINE__:24 // L0030
    Serial.println("Angle=" + angle + ", us=" + us); // L0031
    // __VB_LINE__:25 // L0032
    delay(150); // L0033
    // __VB_LINE__:26 // L0034
    } // L0035
    // __VB_LINE__:29 // L0036
    for (int angle = 180; ((-10) >= 0 ? angle <= 0 : angle >= 0); angle += (-10)) { // L0037
    // __VB_LINE__:30 // L0038
    int us2 = 0; // L0039
    // __VB_LINE__:31 // L0040
    us2 = (int)((500) + ((2500)-(500)) * (((int)min(180, max(0, (int)(angle)))) / 180.0)); // L0041
    // __VB_LINE__:32 // L0042
    myServo.writeMicroseconds(us2); // L0043
    // __VB_LINE__:33 // L0044
    Serial.println("Angle=" + angle + ", us2=" + us2); // L0045
    // __VB_LINE__:34 // L0046
    delay(150); // L0047
    // __VB_LINE__:35 // L0048
    } // L0049
    // __VB_LINE__:37 // L0050
    delay(1000); // L0051
} // L0052
