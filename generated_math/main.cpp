#include <Arduino.h> // L0001
int InitializeSensor(); // L0002
int ReadData(); // L0003
// L0004
// L0005
// L0006
int InitializeSensor() { // L0007
// __VB_LINE__:105 // L0008
delay(100); // L0009
// __VB_LINE__:106 // L0010
return 0; // L0011
} // L0012
int ReadData() { // L0013
// __VB_LINE__:111 // L0014
if (Random[0][10] > 2) { // L0015
// __VB_LINE__:112 // L0016
return 0; // L0017
// __VB_LINE__:113 // L0018
} else { // L0019
// __VB_LINE__:114 // L0020
return -1; // L0021
// __VB_LINE__:115 // L0022
} // L0023
} // L0024
void setup() { // L0025
    delay(1000); // L0026
    // __VB_LINE__:5 // L0027
    Serial.begin(115200); // L0028
    Serial.setRxBufferSize(1024); // L0029
    Serial.setTxBufferSize(1024); // L0030
    // __VB_LINE__:6 // L0031
    Serial.println("Math Constants Demo" + "\r\n"); // L0032
    // __VB_LINE__:11 // L0033
    float radius = 0; // L0034
    // __VB_LINE__:12 // L0035
    radius = 5.0; // L0036
    // __VB_LINE__:15 // L0037
    float circumference1 = 0; // L0038
    // __VB_LINE__:16 // L0039
    circumference1 = 2 * PI * radius; // L0040
    // __VB_LINE__:17 // L0041
    Serial.print("Circumference (2*PI*r): "); // L0042
    // __VB_LINE__:18 // L0043
    Serial.println(circumference1); // L0044
    // __VB_LINE__:21 // L0045
    float circumference2 = 0; // L0046
    // __VB_LINE__:22 // L0047
    circumference2 = (2.0 * PI) * radius; // L0048
    // __VB_LINE__:23 // L0049
    Serial.print("Circumference ((2.0 * PI)*r): "); // L0050
    // __VB_LINE__:24 // L0051
    Serial.println(circumference2); // L0052
    // __VB_LINE__:27 // L0053
    float area = 0; // L0054
    // __VB_LINE__:28 // L0055
    area = PI * radius * radius; // L0056
    // __VB_LINE__:29 // L0057
    Serial.print("Area (PI*r^2): "); // L0058
    // __VB_LINE__:30 // L0059
    Serial.println(area); // L0060
    // __VB_LINE__:32 // L0061
    Serial.println("\r\n" + "Angle Conversions:"); // L0062
    // __VB_LINE__:35 // L0063
    float degrees = 0; // L0064
    // __VB_LINE__:36 // L0065
    degrees = 90; // L0066
    // __VB_LINE__:37 // L0067
    float radians = 0; // L0068
    // __VB_LINE__:38 // L0069
    radians = degrees * (PI / 180.0); // L0070
    // __VB_LINE__:39 // L0071
    Serial.print("90 degrees = "); // L0072
    // __VB_LINE__:40 // L0073
    Serial.print(radians); // L0074
    // __VB_LINE__:41 // L0075
    Serial.println(" radians"); // L0076
    // __VB_LINE__:44 // L0077
    float rad2deg = 0; // L0078
    // __VB_LINE__:45 // L0079
    rad2deg = radians * (180.0 / PI); // L0080
    // __VB_LINE__:46 // L0081
    Serial.print("Back to degrees: "); // L0082
    // __VB_LINE__:47 // L0083
    Serial.println((180.0 / PI)); // L0084
    // __VB_LINE__:50 // L0085
    Serial.print("Full circle: (2.0 * PI) = "); // L0086
    // __VB_LINE__:51 // L0087
    Serial.println((2.0 * PI)); // L0088
    // __VB_LINE__:54 // L0089
    Serial.println("\r\n" + "Trigonometry:"); // L0090
    // __VB_LINE__:56 // L0091
    float angle = 0; // L0092
    // __VB_LINE__:57 // L0093
    angle = PI / 4; // L0094
    // __VB_LINE__:59 // L0095
    Serial.print("sin(PI/4) = "); // L0096
    // __VB_LINE__:60 // L0097
    Serial.println(sin(angle)); // L0098
    // __VB_LINE__:62 // L0099
    Serial.print("cos(PI/4) = "); // L0100
    // __VB_LINE__:63 // L0101
    Serial.println(cos(angle)); // L0102
    // __VB_LINE__:65 // L0103
    Serial.print("tan(PI/4) = "); // L0104
    // __VB_LINE__:66 // L0105
    Serial.println(tan(angle)); // L0106
    // __VB_LINE__:69 // L0107
    Serial.println("\r\n" + "Special Values:"); // L0108
    // __VB_LINE__:71 // L0109
    float infinite = 0; // L0110
    // __VB_LINE__:72 // L0111
    infinite = INFINITY; // L0112
    // __VB_LINE__:73 // L0113
    Serial.print("Infinity: "); // L0114
    // __VB_LINE__:74 // L0115
    Serial.println(infinite); // L0116
    // __VB_LINE__:76 // L0117
    float notANumber = 0; // L0118
    // __VB_LINE__:77 // L0119
    notANumber = NAN; // L0120
    // __VB_LINE__:78 // L0121
    Serial.print("! a Number: "); // L0122
    // __VB_LINE__:79 // L0123
    Serial.println(notANumber); // L0124
    // __VB_LINE__:82 // L0125
    Serial.println("\r\n" + "Function Return Values:"); // L0126
    // __VB_LINE__:84 // L0127
    int result = 0; // L0128
    // __VB_LINE__:85 // L0129
    result = InitializeSensor(); // L0130
    // __VB_LINE__:87 // L0131
    if (result == 0) { // L0132
    // __VB_LINE__:88 // L0133
    Serial.println("Sensor initialized successfully!"); // L0134
    // __VB_LINE__:89 // L0135
    } else if (result == -1) { // L0136
    // __VB_LINE__:90 // L0137
    Serial.println("Sensor initialization -1!"); // L0138
    // __VB_LINE__:91 // L0139
    } // L0140
    // __VB_LINE__:93 // L0141
    result = ReadData(); // L0142
    // __VB_LINE__:94 // L0143
    if (result == 0) { // L0144
    // __VB_LINE__:95 // L0145
    Serial.println("Data read successfully!"); // L0146
    // __VB_LINE__:96 // L0147
    } else { // L0148
    // __VB_LINE__:97 // L0149
    Serial.println("Data read -1!"); // L0150
    // __VB_LINE__:98 // L0151
    } // L0152
    // __VB_LINE__:100 // L0153
    Serial.println("\r\n" + "Setup complete!"); // L0154
} // L0155
// L0156
void loop() { // L0157
    // __VB_LINE__:120 // L0158
    float angle = 0; // L0159
    // __VB_LINE__:121 // L0160
    int servoPos = 0; // L0161
    // __VB_LINE__:123 // L0162
    long t = 0; // L0163
    // __VB_LINE__:124 // L0164
    t = millis() / 1000.0; // L0165
    // __VB_LINE__:127 // L0166
    angle = sin((t * (2.0 * PI)) / 4.0); // L0167
    // __VB_LINE__:128 // L0168
    servoPos = 90 + (angle * 45); // L0169
    // __VB_LINE__:130 // L0170
    Serial.print("Servo angle: "); // L0171
    // __VB_LINE__:131 // L0172
    Serial.println(servoPos); // L0173
    // __VB_LINE__:133 // L0174
    delay(50); // L0175
} // L0176
