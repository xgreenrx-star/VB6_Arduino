#include <Arduino.h> // L0001
#include <TFT_eSPI.h> // L0002
// L0003
// __VB_LINE__:6 // L0004
TFT_eSPI tft; // L0005
// L0006
void setup() { // L0007
    delay(1000); // L0008
    // __VB_LINE__:9 // L0009
    Serial.begin(115200); // L0010
    Serial.setRxBufferSize(1024); // L0011
    Serial.setTxBufferSize(1024); // L0012
    // __VB_LINE__:10 // L0013
    Serial.println("RGB Color Demo"); // L0014
    // __VB_LINE__:12 // L0015
    // TODO: tft.init // L0016
    // __VB_LINE__:13 // L0017
    tft.setRotation(1); // L0018
    // __VB_LINE__:16 // L0019
    tft.fillScreen(tft.color565(0, 0, 0)); // L0020
    // __VB_LINE__:17 // L0021
    delay(500); // L0022
    // __VB_LINE__:20 // L0023
    tft.fillRect(10, 10, 100, 80, tft.color565(255, 0, 0)); // L0024
    // __VB_LINE__:21 // L0025
    tft.fillRect(120, 10, 100, 80, tft.color565(0, 255, 0)); // L0026
    // __VB_LINE__:22 // L0027
    tft.fillRect(230, 10, 80, 80, tft.color565(0, 0, 255)); // L0028
    // __VB_LINE__:24 // L0029
    tft.fillRect(10, 100, 100, 80, tft.color565(255, 255, 0)); // L0030
    // __VB_LINE__:25 // L0031
    tft.fillRect(120, 100, 100, 80, tft.color565(0, 255, 255)); // L0032
    // __VB_LINE__:26 // L0033
    tft.fillRect(230, 100, 80, 80, tft.color565(255, 0, 255)); // L0034
    // __VB_LINE__:29 // L0035
    tft.setTextColor(tft.color565(255, 255, 255), tft.color565(0, 0, 0)); // L0036
    // __VB_LINE__:30 // L0037
    tft.setTextSize(2); // L0038
    // __VB_LINE__:31 // L0039
    tft.setCursor(50, 200); // L0040
    // __VB_LINE__:32 // L0041
    tft.print("RGB Colors!"); // L0042
    // __VB_LINE__:34 // L0043
    Serial.println("Drawing complete"); // L0044
} // L0045
// L0046
void loop() { // L0047
    // __VB_LINE__:39 // L0048
    int hue = 0; // L0049
    // __VB_LINE__:40 // L0050
    for (int hue = 0; ((10) >= 0 ? hue <= 360 : hue >= 360); hue += (10)) { // L0051
    // __VB_LINE__:41 // L0052
    int r = 0; // L0053
    // __VB_LINE__:44 // L0054
    if (hue < 60) { // L0055
    // __VB_LINE__:45 // L0056
    r = 255; // L0057
    // __VB_LINE__:46 // L0058
    g = hue * 4; // L0059
    // __VB_LINE__:47 // L0060
    b = 0; // L0061
    // __VB_LINE__:48 // L0062
    } else if (hue < 120) { // L0063
    // __VB_LINE__:49 // L0064
    r = 255 - ((hue - 60) * 4); // L0065
    // __VB_LINE__:50 // L0066
    g = 255; // L0067
    // __VB_LINE__:51 // L0068
    b = 0; // L0069
    // __VB_LINE__:52 // L0070
    } else if (hue < 180) { // L0071
    // __VB_LINE__:53 // L0072
    r = 0; // L0073
    // __VB_LINE__:54 // L0074
    g = 255; // L0075
    // __VB_LINE__:55 // L0076
    b = (hue - 120) * 4; // L0077
    // __VB_LINE__:56 // L0078
    } else if (hue < 240) { // L0079
    // __VB_LINE__:57 // L0080
    r = 0; // L0081
    // __VB_LINE__:58 // L0082
    g = 255 - ((hue - 180) * 4); // L0083
    // __VB_LINE__:59 // L0084
    b = 255; // L0085
    // __VB_LINE__:60 // L0086
    } else if (hue < 300) { // L0087
    // __VB_LINE__:61 // L0088
    r = (hue - 240) * 4; // L0089
    // __VB_LINE__:62 // L0090
    g = 0; // L0091
    // __VB_LINE__:63 // L0092
    b = 255; // L0093
    // __VB_LINE__:64 // L0094
    } else { // L0095
    // __VB_LINE__:65 // L0096
    r = 255; // L0097
    // __VB_LINE__:66 // L0098
    g = 0; // L0099
    // __VB_LINE__:67 // L0100
    b = 255 - ((hue - 300) * 4); // L0101
    // __VB_LINE__:68 // L0102
    } // L0103
    // __VB_LINE__:70 // L0104
    tft.fillCircle(160, 120, 50, tft.color565(r, g, b)); // L0105
    // __VB_LINE__:71 // L0106
    delay(50); // L0107
    // __VB_LINE__:72 // L0108
    } // L0109
} // L0110
