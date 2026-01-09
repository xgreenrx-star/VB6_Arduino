#include <Arduino.h> // L0001
// L0002
// L0003
void setup() { // L0004
    delay(1000); // L0005
    // __VB_LINE__:9 // L0006
    Serial.begin(115200); // L0007
    Serial.setRxBufferSize(1024); // L0008
    Serial.setTxBufferSize(1024); // L0009
    // __VB_LINE__:10 // L0010
    Serial.println("Servo DEG2PULSE Demo" + " // L0011
"); // L0012
} // L0013
// L0014
void loop() { // L0015
    // __VB_LINE__:17 // L0016
    int angle = 0; // L0017
    // __VB_LINE__:20 // L0018
    for (int angle = 0; ((15) >= 0 ? angle <= 180 : angle >= 180); angle += (15)) { // L0019
    // __VB_LINE__:21 // L0020
    int us = 0; // L0021
    // __VB_LINE__:22 // L0022
    us = (int)(1000 + ((angle) * (1000.0/180.0))); // L0023
    // __VB_LINE__:23 // L0024
    Serial.print("Angle=" + angle + " deg, Pulse=" + us + " us" + " // L0025
"); // L0026
    // __VB_LINE__:25 // L0027
    delay(150); // L0028
    // __VB_LINE__:26 // L0029
    } // L0030
    // __VB_LINE__:29 // L0031
    for (int angle = 180; ((-15) >= 0 ? angle <= 0 : angle >= 0); angle += (-15)) { // L0032
    // __VB_LINE__:30 // L0033
    int us2 = 0; // L0034
    // __VB_LINE__:31 // L0035
    us2 = (int)((500) + ((2500)-(500)) * ((angle) / 180.0)); // L0036
    // __VB_LINE__:32 // L0037
    Serial.print("Angle=" + angle + " deg, Pulse=" + us2 + " us (custom)" + " // L0038
"); // L0039
    // __VB_LINE__:34 // L0040
    delay(150); // L0041
    // __VB_LINE__:35 // L0042
    } // L0043
    // __VB_LINE__:37 // L0044
    delay(1000); // L0045
} // L0046
