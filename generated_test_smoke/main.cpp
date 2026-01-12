#include <Arduino.h> // L0001
#include <vector> // L0002
#include <TFT_eSPI.h> // L0003
// L0004
void DrawBackground(); // L0005
void DrawBall(); // L0006
// L0007
// L0008
TFT_eSPI tft; // L0009
// __VB_LINE__:6 // L0010
const auto SCREEN_W = 240; // L0011
// __VB_LINE__:7 // L0012
const auto SCREEN_H = 240; // L0013
// __VB_LINE__:8 // L0014
const auto BALL_RADIUS = 40; // L0015
// __VB_LINE__:9 // L0016
const auto BALL_TILES = 8; // L0017
// __VB_LINE__:10 // L0018
const auto BALL_SPEED_X = 3.2; // L0019
// __VB_LINE__:11 // L0020
const auto BALL_SPEED_Y = 0.09; // L0021
// __VB_LINE__:12 // L0022
const auto FLOOR_GRID = 8; // L0023
// __VB_LINE__:13 // L0024
const auto COLOR_BG = TFT_DARKGREY; // L0025
// __VB_LINE__:14 // L0026
const auto COLOR_GRID = TFT_MAGENTA; // L0027
// __VB_LINE__:15 // L0028
const auto COLOR_SHADOW = TFT_DARKGREY; // L0029
// __VB_LINE__:16 // L0030
const auto COLOR_RED = TFT_RED; // L0031
// __VB_LINE__:17 // L0032
const auto COLOR_WHITE = TFT_WHITE; // L0033
// __VB_LINE__:19 // L0034
float ballX = 0; // L0035
// __VB_LINE__:20 // L0036
float ballY = 0; // L0037
// __VB_LINE__:21 // L0038
float ballVX = 0; // L0039
// __VB_LINE__:22 // L0040
float ballVY = 0; // L0041
// __VB_LINE__:23 // L0042
float phase = 0; // L0043
// __VB_LINE__:24 // L0044
float shadowY = 0; // L0045
// __VB_LINE__:25 // L0046
float amplitude = 0; // L0047
// __VB_LINE__:26 // L0048
float centerY = 0; // L0049
// __VB_LINE__:27 // L0050
float bounceMargin = 0; // L0051
// __VB_LINE__:28 // L0052
float leftBound = 0; // L0053
// __VB_LINE__:29 // L0054
float rightBound = 0; // L0055
// __VB_LINE__:30 // L0056
bool isMovingRight = false; // L0057
// __VB_LINE__:31 // L0058
bool isMovingUp = false; // L0059
// L0060
void DrawBackground() { // L0061
// __VB_LINE__:53 // L0062
tft.fillRect(0, 0, SCREEN_W, SCREEN_H, COLOR_BG); // L0063
// __VB_LINE__:54 // L0064
int i = 0; // L0065
// __VB_LINE__:55 // L0066
float x1v = 0; // L0067
// __VB_LINE__:55 // L0068
float y1v = 0; // L0069
// __VB_LINE__:55 // L0070
float x2v = 0; // L0071
// __VB_LINE__:55 // L0072
float y2v = 0; // L0073
// __VB_LINE__:57 // L0074
float vanishingX = 0; // L0075
// __VB_LINE__:57 // L0076
float vanishingY = 0; // L0077
// __VB_LINE__:58 // L0078
vanishingX = SCREEN_W / 2; // L0079
// __VB_LINE__:59 // L0080
vanishingY = SCREEN_H * 0.85; // L0081
// __VB_LINE__:61 // L0082
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0083
// __VB_LINE__:62 // L0084
x1v = vanishingX; // L0085
// __VB_LINE__:63 // L0086
y1v = vanishingY; // L0087
// __VB_LINE__:64 // L0088
x2v = i * (SCREEN_W / FLOOR_GRID); // L0089
// __VB_LINE__:65 // L0090
y2v = SCREEN_H; // L0091
// __VB_LINE__:66 // L0092
tft.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0093
// __VB_LINE__:67 // L0094
} // L0095
// __VB_LINE__:69 // L0096
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0097
// __VB_LINE__:70 // L0098
y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0099
// __VB_LINE__:71 // L0100
tft.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0101
// __VB_LINE__:72 // L0102
} // L0103
} // L0104
void DrawBall() { // L0105
// __VB_LINE__:77 // L0106
int t = 0; // L0107
// __VB_LINE__:77 // L0108
int s = 0; // L0109
// __VB_LINE__:78 // L0110
float angle1v = 0; // L0111
// __VB_LINE__:79 // L0112
float angle2v = 0; // L0113
// __VB_LINE__:80 // L0114
float x1v = 0; // L0115
// __VB_LINE__:81 // L0116
float y1v = 0; // L0117
// __VB_LINE__:82 // L0118
float x2v = 0; // L0119
// __VB_LINE__:83 // L0120
float y2v = 0; // L0121
// __VB_LINE__:84 // L0122
float x3v = 0; // L0123
// __VB_LINE__:85 // L0124
float y3v = 0; // L0125
// __VB_LINE__:86 // L0126
int colorTile = 0; // L0127
// __VB_LINE__:88 // L0128
tft.fillCircle(ballX, shadowY, BALL_RADIUS * 0.7, COLOR_SHADOW); // L0129
// __VB_LINE__:90 // L0130
for (int t = 0; ((1) >= 0 ? t <= BALL_TILES : t >= BALL_TILES); t += (1)) { // L0131
// __VB_LINE__:91 // L0132
angle1v = phase + t * (3.14159 * 2 / BALL_TILES); // L0133
// __VB_LINE__:92 // L0134
angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES); // L0135
// __VB_LINE__:93 // L0136
for (int s = 0; ((1) >= 0 ? s <= 1 : s >= 1); s += (1)) { // L0137
// __VB_LINE__:94 // L0138
x1v = ballX; // L0139
// __VB_LINE__:95 // L0140
y1v = ballY; // L0141
// __VB_LINE__:96 // L0142
x2v = ballX + cos(angle1v) * BALL_RADIUS * (1 - s * 0.5); // L0143
// __VB_LINE__:97 // L0144
y2v = ballY + sin(angle1v) * BALL_RADIUS * (1 - s * 0.5); // L0145
// __VB_LINE__:98 // L0146
x3v = ballX + cos(angle2v) * BALL_RADIUS * (1 - s * 0.5); // L0147
// __VB_LINE__:99 // L0148
y3v = ballY + sin(angle2v) * BALL_RADIUS * (1 - s * 0.5); // L0149
// __VB_LINE__:100 // L0150
if (((t + s) % 2) == 0) { // L0151
// __VB_LINE__:101 // L0152
colorTile = TFT_RED; // L0153
// __VB_LINE__:102 // L0154
} else { // L0155
// __VB_LINE__:103 // L0156
colorTile = TFT_WHITE; // L0157
// __VB_LINE__:104 // L0158
} // L0159
// __VB_LINE__:105 // L0160
tft.fillTriangle(x1v, y1v, x2v, y2v, x3v, y3v, colorTile); // L0161
// __VB_LINE__:106 // L0162
} // L0163
// __VB_LINE__:107 // L0164
} // L0165
// __VB_LINE__:109 // L0166
tft.drawCircle(ballX, ballY, BALL_RADIUS, TFT_WHITE); // L0167
} // L0168
void setup() { // L0169
    delay(1000); // L0170
    tft.begin(); // L0171
    // __VB_LINE__:35 // L0172
    ballX = SCREEN_W / 2; // L0173
    // __VB_LINE__:36 // L0174
    centerY = SCREEN_H * 0.75; // L0175
    // __VB_LINE__:37 // L0176
    amplitude = SCREEN_H * 0.25 - BALL_RADIUS; // L0177
    // __VB_LINE__:38 // L0178
    ballY = centerY; // L0179
    // __VB_LINE__:39 // L0180
    ballVX = BALL_SPEED_X; // L0181
    // __VB_LINE__:40 // L0182
    ballVY = BALL_SPEED_Y; // L0183
    // __VB_LINE__:41 // L0184
    phase = 0; // L0185
    // __VB_LINE__:42 // L0186
    bounceMargin = BALL_RADIUS + 4; // L0187
    // __VB_LINE__:43 // L0188
    leftBound = bounceMargin; // L0189
    // __VB_LINE__:44 // L0190
    rightBound = SCREEN_W - bounceMargin; // L0191
    // __VB_LINE__:45 // L0192
    isMovingRight = true; // L0193
    // __VB_LINE__:46 // L0194
    isMovingUp = false; // L0195
    // __VB_LINE__:47 // L0196
    shadowY = centerY + BALL_RADIUS + 12; // L0197
    // __VB_LINE__:48 // L0198
    DrawBackground(); // L0199
} // L0200
// L0201
void loop() { // L0202
    // __VB_LINE__:113 // L0203
    DrawBackground(); // L0204
    // __VB_LINE__:115 // L0205
    if (isMovingRight) { // L0206
    // __VB_LINE__:116 // L0207
    ballX = ballX + ballVX; // L0208
    // __VB_LINE__:117 // L0209
    phase = phase + 0.18; // L0210
    // __VB_LINE__:118 // L0211
    if (ballX >= rightBound) { // L0212
    // __VB_LINE__:119 // L0213
    isMovingRight = false; // L0214
    // __VB_LINE__:120 // L0215
    } // L0216
    // __VB_LINE__:121 // L0217
    } else { // L0218
    // __VB_LINE__:122 // L0219
    ballX = ballX - ballVX; // L0220
    // __VB_LINE__:123 // L0221
    phase = phase - 0.18; // L0222
    // __VB_LINE__:124 // L0223
    if (ballX <= leftBound) { // L0224
    // __VB_LINE__:125 // L0225
    isMovingRight = true; // L0226
    // __VB_LINE__:126 // L0227
    } // L0228
    // __VB_LINE__:127 // L0229
    } // L0230
    // __VB_LINE__:128 // L0231
    ballY = centerY - amplitude * abs(cos(phase * ballVY)); // L0232
    // __VB_LINE__:129 // L0233
    if (ballY < centerY) { // L0234
    // __VB_LINE__:130 // L0235
    isMovingUp = true; // L0236
    // __VB_LINE__:131 // L0237
    } else { // L0238
    // __VB_LINE__:132 // L0239
    isMovingUp = false; // L0240
    // __VB_LINE__:133 // L0241
    } // L0242
    // __VB_LINE__:134 // L0243
    DrawBall(); // L0244
} // L0245
