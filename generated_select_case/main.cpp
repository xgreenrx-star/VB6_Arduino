#include <Arduino.h> // L0001
void TestGrade(int score); // L0002
void TestDayType(int day); // L0003
// L0004
// L0005
// L0006
void TestGrade(int score) { // L0007
// __VB_LINE__:25 // L0008
String grade = ""; // L0009
// __VB_LINE__:27 // L0010
switch (score) { // L0011
// __VB_LINE__:28 // L0012
case 90: // L0013
case 91: // L0014
case 92: // L0015
case 93: // L0016
case 94: // L0017
case 95: // L0018
case 96: // L0019
case 97: // L0020
case 98: // L0021
case 99: // L0022
case 100: // L0023
// __VB_LINE__:29 // L0024
grade = "A"; // L0025
// __VB_LINE__:30 // L0026
break; // L0027
case 80: // L0028
case 81: // L0029
case 82: // L0030
case 83: // L0031
case 84: // L0032
case 85: // L0033
case 86: // L0034
case 87: // L0035
case 88: // L0036
case 89: // L0037
// __VB_LINE__:31 // L0038
grade = "B"; // L0039
// __VB_LINE__:32 // L0040
break; // L0041
case 70: // L0042
case 71: // L0043
case 72: // L0044
case 73: // L0045
case 74: // L0046
case 75: // L0047
case 76: // L0048
case 77: // L0049
case 78: // L0050
case 79: // L0051
// __VB_LINE__:33 // L0052
grade = "C"; // L0053
// __VB_LINE__:34 // L0054
break; // L0055
case 60: // L0056
case 61: // L0057
case 62: // L0058
case 63: // L0059
case 64: // L0060
case 65: // L0061
case 66: // L0062
case 67: // L0063
case 68: // L0064
case 69: // L0065
// __VB_LINE__:35 // L0066
grade = "D"; // L0067
// __VB_LINE__:36 // L0068
break; // L0069
default: // L0070
// __VB_LINE__:37 // L0071
grade = "F"; // L0072
// __VB_LINE__:38 // L0073
break; // L0074
} // L0075
// __VB_LINE__:40 // L0076
Serial.println("Score " + score + " = Grade " + grade); // L0077
} // L0078
void TestDayType(int day) { // L0079
// __VB_LINE__:44 // L0080
String dayType = ""; // L0081
// __VB_LINE__:46 // L0082
switch (day) { // L0083
// __VB_LINE__:47 // L0084
case 1: // L0085
case 7: // L0086
// __VB_LINE__:48 // L0087
dayType = "Weekend"; // L0088
// __VB_LINE__:49 // L0089
break; // L0090
case 2: // L0091
case 3: // L0092
case 4: // L0093
case 5: // L0094
case 6: // L0095
// __VB_LINE__:50 // L0096
dayType = "Weekday"; // L0097
// __VB_LINE__:51 // L0098
break; // L0099
default: // L0100
// __VB_LINE__:52 // L0101
dayType = "Invalid"; // L0102
// __VB_LINE__:53 // L0103
break; // L0104
} // L0105
// __VB_LINE__:55 // L0106
Serial.println("Day " + day + " is a " + dayType); // L0107
} // L0108
void setup() { // L0109
    delay(1000); // L0110
    // __VB_LINE__:5 // L0111
    Serial.begin(115200); // L0112
    Serial.setRxBufferSize(1024); // L0113
    Serial.setTxBufferSize(1024); // L0114
    // __VB_LINE__:6 // L0115
    Serial.println("Select Case Enhanced Demo" + "\r\n"); // L0116
    // __VB_LINE__:9 // L0117
    TestGrade(95); // L0118
    // __VB_LINE__:10 // L0119
    TestGrade(85); // L0120
    // __VB_LINE__:11 // L0121
    TestGrade(75); // L0122
    // __VB_LINE__:12 // L0123
    TestGrade(65); // L0124
    // __VB_LINE__:13 // L0125
    TestGrade(50); // L0126
    // __VB_LINE__:15 // L0127
    Serial.println("\r\n"); // L0128
    // __VB_LINE__:18 // L0129
    TestDayType(1); // L0130
    // __VB_LINE__:19 // L0131
    TestDayType(3); // L0132
    // __VB_LINE__:20 // L0133
    TestDayType(6); // L0134
    // __VB_LINE__:21 // L0135
    TestDayType(7); // L0136
} // L0137
// L0138
void loop() { // L0139
    // __VB_LINE__:59 // L0140
    delay(5000); // L0141
} // L0142
