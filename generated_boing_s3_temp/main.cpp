#include <Arduino.h> // L0001
#include <vector> // L0002
#include <TFT_eSPI.h> // L0003
// L0004
void DrawBackground(); // L0005
void DrawBall(); // L0006
// L0007
// L0008
TFT_eSPI tft; // L0009
TFT_eSprite shadow = TFT_eSprite(&tft); // L0010
TFT_eSprite ball = TFT_eSprite(&tft); // L0011
// __VB_LINE__:8 // L0012
const auto SCREEN_W = 172; // L0013
// __VB_LINE__:9 // L0014
const auto SCREEN_H = 320; // L0015
// __VB_LINE__:10 // L0016
const auto BALL_RADIUS = 30; // L0017
// __VB_LINE__:11 // L0018
const auto BALL_TILES = 8; // L0019
// __VB_LINE__:12 // L0020
const auto BALL_SPEED_X = 4.5; // L0021
// __VB_LINE__:13 // L0022
const auto BALL_SPEED_Y = 0.12; // L0023
// __VB_LINE__:14 // L0024
const auto PHASE_STEP = 0.25; // L0025
// __VB_LINE__:15 // L0026
const auto FLOOR_GRID = 8; // L0027
// __VB_LINE__:16 // L0028
const auto COLOR_BG = TFT_DARKGREY; // L0029
// __VB_LINE__:17 // L0030
const auto COLOR_GRID = TFT_MAGENTA; // L0031
// __VB_LINE__:18 // L0032
const auto COLOR_SHADOW = TFT_DARKGREY; // L0033
// __VB_LINE__:19 // L0034
const auto COLOR_RED = TFT_RED; // L0035
// __VB_LINE__:20 // L0036
const auto COLOR_WHITE = TFT_WHITE; // L0037
// __VB_LINE__:22 // L0038
float ballX = 0; // L0039
// __VB_LINE__:23 // L0040
float ballY = 0; // L0041
// __VB_LINE__:24 // L0042
float ballVX = 0; // L0043
// __VB_LINE__:25 // L0044
float ballVY = 0; // L0045
// __VB_LINE__:26 // L0046
float phase = 0; // L0047
// __VB_LINE__:27 // L0048
float shadowY = 0; // L0049
// __VB_LINE__:28 // L0050
float amplitude = 0; // L0051
// __VB_LINE__:29 // L0052
float centerY = 0; // L0053
// __VB_LINE__:30 // L0054
float bounceMargin = 0; // L0055
// __VB_LINE__:31 // L0056
float leftBound = 0; // L0057
// __VB_LINE__:32 // L0058
float rightBound = 0; // L0059
// __VB_LINE__:33 // L0060
float prevBallX = 0; // L0061
// __VB_LINE__:34 // L0062
float prevBallY = 0; // L0063
// __VB_LINE__:35 // L0064
bool isMovingRight = false; // L0065
// __VB_LINE__:36 // L0066
bool isMovingUp = false; // L0067
// L0068
void DrawBackground() { // L0069
// __VB_LINE__:69 // L0070
tft.fillRect(0, 0, SCREEN_W, SCREEN_H, COLOR_BG); // L0071
// __VB_LINE__:70 // L0072
int i = 0; // L0073
// __VB_LINE__:71 // L0074
float x1v = 0; // L0075
// __VB_LINE__:71 // L0076
float y1v = 0; // L0077
// __VB_LINE__:71 // L0078
float x2v = 0; // L0079
// __VB_LINE__:71 // L0080
float y2v = 0; // L0081
// __VB_LINE__:72 // L0082
float vanishingX = 0; // L0083
// __VB_LINE__:72 // L0084
float vanishingY = 0; // L0085
// __VB_LINE__:73 // L0086
vanishingX = SCREEN_W / 2; // L0087
// __VB_LINE__:74 // L0088
vanishingY = SCREEN_H * 0.85; // L0089
// __VB_LINE__:77 // L0090
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0091
// __VB_LINE__:78 // L0092
x1v = vanishingX; // L0093
// __VB_LINE__:79 // L0094
y1v = vanishingY; // L0095
// __VB_LINE__:80 // L0096
x2v = i * (SCREEN_W / FLOOR_GRID); // L0097
// __VB_LINE__:81 // L0098
y2v = SCREEN_H; // L0099
// __VB_LINE__:82 // L0100
tft.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0101
// __VB_LINE__:83 // L0102
} // L0103
// __VB_LINE__:86 // L0104
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0105
// __VB_LINE__:87 // L0106
y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0107
// __VB_LINE__:88 // L0108
tft.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0109
// __VB_LINE__:89 // L0110
} // L0111
} // L0112
void DrawBall() { // L0113
// __VB_LINE__:93 // L0114
int t = 0; // L0115
// __VB_LINE__:93 // L0116
int s = 0; // L0117
// __VB_LINE__:94 // L0118
float angle1v = 0; // L0119
// __VB_LINE__:94 // L0120
float angle2v = 0; // L0121
// __VB_LINE__:95 // L0122
float x1v = 0; // L0123
// __VB_LINE__:95 // L0124
float y1v = 0; // L0125
// __VB_LINE__:95 // L0126
float x2v = 0; // L0127
// __VB_LINE__:95 // L0128
float y2v = 0; // L0129
// __VB_LINE__:95 // L0130
float x3v = 0; // L0131
// __VB_LINE__:95 // L0132
float y3v = 0; // L0133
// __VB_LINE__:96 // L0134
int colorTile = 0; // L0135
// __VB_LINE__:97 // L0136
float spriteCX = 0; // L0137
// __VB_LINE__:98 // L0138
float spriteCY = 0; // L0139
// __VB_LINE__:99 // L0140
spriteCX = BALL_RADIUS; // L0141
// __VB_LINE__:100 // L0142
spriteCY = BALL_RADIUS; // L0143
// __VB_LINE__:103 // L0144
ball.fillSprite(COLOR_BG); // L0145
// __VB_LINE__:105 // L0146
for (int t = 0; ((1) >= 0 ? t <= BALL_TILES : t >= BALL_TILES); t += (1)) { // L0147
// __VB_LINE__:106 // L0148
angle1v = phase + t * (3.14159 * 2 / BALL_TILES); // L0149
// __VB_LINE__:107 // L0150
angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES); // L0151
// __VB_LINE__:108 // L0152
for (int s = 0; ((1) >= 0 ? s <= 1 : s >= 1); s += (1)) { // L0153
// __VB_LINE__:110 // L0154
x1v = ballX; // L0155
// __VB_LINE__:111 // L0156
y1v = ballY; // L0157
// __VB_LINE__:112 // L0158
x2v = ballX + cos(angle1v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0159
// __VB_LINE__:113 // L0160
y2v = ballY + sin(angle1v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0161
// __VB_LINE__:114 // L0162
x3v = ballX + cos(angle2v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0163
// __VB_LINE__:115 // L0164
y3v = ballY + sin(angle2v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0165
// __VB_LINE__:117 // L0166
if (((t + s) % 2) == 0) { // L0167
// __VB_LINE__:118 // L0168
colorTile = TFT_RED; // L0169
// __VB_LINE__:119 // L0170
} else { // L0171
// __VB_LINE__:120 // L0172
colorTile = TFT_WHITE; // L0173
// __VB_LINE__:121 // L0174
} // L0175
// __VB_LINE__:124 // L0176
ball.fillTriangle(spriteCX, spriteCY, x2v - (ballX - spriteCX), y2v - (ballY - spriteCY), x3v - (ballX - spriteCX), y3v - (ballY - spriteCY), colorTile); // L0177
// __VB_LINE__:125 // L0178
} // L0179
// __VB_LINE__:126 // L0180
} // L0181
// __VB_LINE__:129 // L0182
float shadowScale = 0; // L0183
// __VB_LINE__:130 // L0184
shadowScale = 0.6 + 0.4 * (1 - ((ballY - (centerY - amplitude)) / (2 * amplitude))); // L0185
// __VB_LINE__:131 // L0186
shadow.fillSprite(COLOR_BG); // L0187
// __VB_LINE__:132 // L0188
shadow.fillEllipse(BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * shadowScale, BALL_RADIUS * 0.4 * shadowScale, COLOR_SHADOW); // L0189
// __VB_LINE__:135 // L0190
int pushX = 0; // L0191
// __VB_LINE__:136 // L0192
int pushY = 0; // L0193
// __VB_LINE__:137 // L0194
pushX = ballX - BALL_RADIUS; // L0195
// __VB_LINE__:138 // L0196
pushY = ballY - spriteCY; // L0197
// __VB_LINE__:141 // L0198
shadow.pushSprite(pushX, shadowY - BALL_RADIUS/2); // L0199
// __VB_LINE__:142 // L0200
ball.pushSprite(pushX, pushY); // L0201
} // L0202
void setup() { // L0203
    delay(1000); // L0204
    tft.begin(); // L0205
    shadow.createSprite(spriteW, BALL_RADIUS); // L0206
    ball.createSprite(spriteW, spriteH); // L0207
    // __VB_LINE__:40 // L0208
    ballX = SCREEN_W / 2; // L0209
    // __VB_LINE__:41 // L0210
    centerY = SCREEN_H * 0.75; // L0211
    // __VB_LINE__:42 // L0212
    amplitude = SCREEN_H * 0.20 - BALL_RADIUS; // L0213
    // __VB_LINE__:43 // L0214
    ballY = centerY; // L0215
    // __VB_LINE__:44 // L0216
    ballVX = BALL_SPEED_X; // L0217
    // __VB_LINE__:45 // L0218
    ballVY = -2.0; // L0219
    // __VB_LINE__:46 // L0220
    phase = 0; // L0221
    // __VB_LINE__:47 // L0222
    bounceMargin = BALL_RADIUS + 8; // L0223
    // __VB_LINE__:48 // L0224
    leftBound = bounceMargin; // L0225
    // __VB_LINE__:49 // L0226
    rightBound = SCREEN_W - bounceMargin; // L0227
    // __VB_LINE__:50 // L0228
    isMovingRight = true; // L0229
    // __VB_LINE__:51 // L0230
    isMovingUp = false; // L0231
    // __VB_LINE__:52 // L0232
    shadowY = centerY + BALL_RADIUS + 8; // L0233
    // __VB_LINE__:53 // L0234
    prevBallX = ballX; // L0235
    // __VB_LINE__:54 // L0236
    prevBallY = ballY; // L0237
    // __VB_LINE__:56 // L0238
    DrawBackground(); // L0239
    // __VB_LINE__:59 // L0240
    int spriteW = 0; // L0241
    // __VB_LINE__:60 // L0242
    spriteW = BALL_RADIUS * 2; // L0243
    // __VB_LINE__:61 // L0244
    int spriteH = 0; // L0245
    // __VB_LINE__:62 // L0246
    spriteH = BALL_RADIUS * 2; // L0247
    // __VB_LINE__:63 // L0248
    // CREATE_SPRITE ball spriteW spriteH // L0249
    // __VB_LINE__:64 // L0250
    // CREATE_SPRITE shadow spriteW BALL_RADIUS // L0251
} // L0252
// L0253
void loop() { // L0254
    // __VB_LINE__:147 // L0255
    tft.fillCircle(prevBallX, prevBallY, BALL_RADIUS + 2, COLOR_BG); // L0256
    // __VB_LINE__:149 // L0257
    if (isMovingRight) { // L0258
    // __VB_LINE__:150 // L0259
    ballX = ballX + ballVX; // L0260
    // __VB_LINE__:151 // L0261
    phase = phase + PHASE_STEP; // L0262
    // __VB_LINE__:152 // L0263
    if (ballX >= rightBound) { // L0264
    // __VB_LINE__:153 // L0265
    isMovingRight = false; // L0266
    // __VB_LINE__:154 // L0267
    } // L0268
    // __VB_LINE__:155 // L0269
    } else { // L0270
    // __VB_LINE__:156 // L0271
    ballX = ballX - ballVX; // L0272
    // __VB_LINE__:157 // L0273
    phase = phase - PHASE_STEP; // L0274
    // __VB_LINE__:158 // L0275
    if (ballX <= leftBound) { // L0276
    // __VB_LINE__:159 // L0277
    isMovingRight = true; // L0278
    // __VB_LINE__:160 // L0279
    } // L0280
    // __VB_LINE__:161 // L0281
    } // L0282
    // __VB_LINE__:164 // L0283
    ballY = ballY + ballVY; // L0284
    // __VB_LINE__:165 // L0285
    ballVY = ballVY + 0.6; // L0286
    // __VB_LINE__:166 // L0287
    if (ballY >= centerY + amplitude) { // L0288
    // __VB_LINE__:167 // L0289
    ballY = centerY + amplitude; // L0290
    // __VB_LINE__:168 // L0291
    ballVY = -abs(ballVY) * 0.75; // L0292
    // __VB_LINE__:169 // L0293
    isMovingUp = false; // L0294
    // __VB_LINE__:170 // L0295
    } else if (ballY <= centerY - amplitude) { // L0296
    // __VB_LINE__:171 // L0297
    ballY = centerY - amplitude; // L0298
    // __VB_LINE__:172 // L0299
    ballVY = abs(ballVY) * 0.75; // L0300
    // __VB_LINE__:173 // L0301
    isMovingUp = true; // L0302
    // __VB_LINE__:174 // L0303
    } else { // L0304
    // __VB_LINE__:176 // L0305
    isMovingUp = (ballVY < 0); // L0306
    // __VB_LINE__:177 // L0307
    } // L0308
    // __VB_LINE__:179 // L0309
    DrawBall(); // L0310
    // __VB_LINE__:182 // L0311
    prevBallX = ballX; // L0312
    // __VB_LINE__:183 // L0313
    prevBallY = ballY; // L0314
    // __VB_LINE__:186 // L0315
    delay(20); // L0316
} // L0317
