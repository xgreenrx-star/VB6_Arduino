#include <Arduino.h> // L0001
// L0002
// L0003
void setup() { // L0004
    delay(1000); // L0005
    // __VB_LINE__:5 // L0006
    Serial.begin(115200); // L0007
    Serial.setRxBufferSize(1024); // L0008
    Serial.setTxBufferSize(1024); // L0009
    // __VB_LINE__:6 // L0010
    Serial.println("VB6 Enhancements Demo" + "\r\n"); // L0011
    // __VB_LINE__:9 // L0012
    int age = 0; // L0013
    // __VB_LINE__:10 // L0014
    age = 25; // L0015
    // __VB_LINE__:11 // L0016
    String status = ""; // L0017
    // __VB_LINE__:12 // L0018
    status = (age >= 18 ? "Adult" : "Minor"); // L0019
    // __VB_LINE__:13 // L0020
    Serial.println("Age: " + age + " is " + status); // L0021
    // __VB_LINE__:15 // L0022
    int score = 0; // L0023
    // __VB_LINE__:16 // L0024
    score = 85; // L0025
    // __VB_LINE__:17 // L0026
    Serial.println("Grade: " + (score >= 90 ? "A" : IIf(score >= 80, "B", "C"))); // L0027
    // __VB_LINE__:20 // L0028
    Serial.println("\r\n" + "Type Conversions:"); // L0029
    // __VB_LINE__:22 // L0030
    int num = 0; // L0031
    // __VB_LINE__:23 // L0032
    num = 42; // L0033
    // __VB_LINE__:24 // L0034
    String s = ""; // L0035
    // __VB_LINE__:25 // L0036
    s = String(num); // L0037
    // __VB_LINE__:26 // L0038
    Serial.println("String(42) = " + s); // L0039
    // __VB_LINE__:28 // L0040
    String str = ""; // L0041
    // __VB_LINE__:29 // L0042
    str = "123"; // L0043
    // __VB_LINE__:30 // L0044
    int i = 0; // L0045
    // __VB_LINE__:31 // L0046
    i = atoi(String(str).c_str()); // L0047
    // __VB_LINE__:32 // L0048
    Serial.println("atoi(String(" + Chr(34).c_str()) + "123" + Chr(34) + ") = " + i); // L0049
    // __VB_LINE__:34 // L0050
    float d = 0; // L0051
    // __VB_LINE__:35 // L0052
    d = atof(String("3.14159").c_str()); // L0053
    // __VB_LINE__:36 // L0054
    Serial.println("atof(String(3.14159).c_str()) = " + d); // L0055
    // __VB_LINE__:38 // L0056
    uint8_t b = 0; // L0057
    // __VB_LINE__:39 // L0058
    b = (byte)(255); // L0059
    // __VB_LINE__:40 // L0060
    Serial.println("(byte)(255) = " + b); // L0061
    // __VB_LINE__:43 // L0062
    Serial.println("\r\n" + "String Functions:"); // L0063
    // __VB_LINE__:45 // L0064
    String spaces = ""; // L0065
    // __VB_LINE__:46 // L0066
    spaces = String(' ', 5); // L0067
    // __VB_LINE__:47 // L0068
    Serial.println("String(' ', 5) = [" + spaces + "]"); // L0069
    // __VB_LINE__:49 // L0070
    String stars = ""; // L0071
    // __VB_LINE__:50 // L0072
    stars = String('*', 10); // L0073
    // __VB_LINE__:51 // L0074
    Serial.println("String(*, 10) = " + stars); // L0075
    // __VB_LINE__:54 // L0076
    Serial.println("\r\n" + "Type Checking:"); // L0077
    // __VB_LINE__:56 // L0078
    String test1 = ""; // L0079
    // __VB_LINE__:57 // L0080
    test1 = "456"; // L0081
    // __VB_LINE__:58 // L0082
    if ((String(test1).toInt() != 0 || String(test1) == \"0\")) { // L0083
    // __VB_LINE__:59 // L0084
    Serial.println(test1 + " is numeric"); // L0085
    // __VB_LINE__:60 // L0086
    } // L0087
    // __VB_LINE__:62 // L0088
    String test2 = ""; // L0089
    // __VB_LINE__:63 // L0090
    test2 = "abc"; // L0091
    // __VB_LINE__:64 // L0092
    if (! (String(test2).toInt() != 0 || String(test2) == \"0\")) { // L0093
    // __VB_LINE__:65 // L0094
    Serial.println(test2 + " is ! numeric"); // L0095
    // __VB_LINE__:66 // L0096
    } // L0097
    // __VB_LINE__:68 // L0098
    String empty = ""; // L0099
    // __VB_LINE__:69 // L0100
    empty = ""; // L0101
    // __VB_LINE__:70 // L0102
    if ((String(empty).length() == 0)) { // L0103
    // __VB_LINE__:71 // L0104
    Serial.println("String is empty"); // L0105
    // __VB_LINE__:72 // L0106
    } // L0107
    // __VB_LINE__:75 // L0108
    Serial.println("\r\n" + "Free RAM: " + ESP.getFreeHeap() + " bytes"); // L0109
    // __VB_LINE__:77 // L0110
    Serial.println("\r\n" + "Setup complete!"); // L0111
} // L0112
// L0113
void loop() { // L0114
    // __VB_LINE__:81 // L0115
    int i = 0; // L0116
    // __VB_LINE__:82 // L0117
    for (int i = 1; ((1) >= 0 ? i <= 5 : i >= 5); i += (1)) { // L0118
    // __VB_LINE__:83 // L0119
    Serial.print("Processing " + i + "..."); // L0120
    // __VB_LINE__:84 // L0121
    delay(0); // L0122
    // __VB_LINE__:85 // L0123
    delay(100); // L0124
    // __VB_LINE__:86 // L0125
    Serial.println("done"); // L0126
    // __VB_LINE__:87 // L0127
    } // L0128
    // __VB_LINE__:89 // L0129
    delay(2000); // L0130
} // L0131
