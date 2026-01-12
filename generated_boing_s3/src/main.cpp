#include <Arduino.h> // L0001
#include <vector> // L0002
#include <TFT_eSPI.h> // L0003
// L0004
void DrawBackground(); // L0005
void DrawBall(); // L0006
// L0007
// L0008
TFT_eSPI tft; // L0009
// __VB_LINE__:8 // L0010
const auto SCREEN_W = 172; // L0011
// __VB_LINE__:9 // L0012
const auto SCREEN_H = 320; // L0013
// __VB_LINE__:10 // L0014
const auto BALL_RADIUS = 30; // L0015
// __VB_LINE__:11 // L0016
const auto BALL_TILES = 8; // L0017
// __VB_LINE__:12 // L0018
const auto BALL_SPEED_X = 4.5; // L0019
// __VB_LINE__:13 // L0020
const auto BALL_SPEED_Y = 0.12; // L0021
// __VB_LINE__:14 // L0022
const auto PHASE_STEP = 0.25; // L0023
// __VB_LINE__:15 // L0024
const auto FLOOR_GRID = 8; // L0025
// __VB_LINE__:16 // L0026
const auto COLOR_BG = TFT_DARKGREY; // L0027
// __VB_LINE__:17 // L0028
const auto COLOR_GRID = TFT_MAGENTA; // L0029
// __VB_LINE__:18 // L0030
const auto COLOR_SHADOW = TFT_DARKGREY; // L0031
// __VB_LINE__:19 // L0032
const auto COLOR_RED = TFT_RED; // L0033
// __VB_LINE__:20 // L0034
const auto COLOR_WHITE = TFT_WHITE; // L0035
// __VB_LINE__:22 // L0036
float ballX = 0; // L0037
// __VB_LINE__:23 // L0038
float ballY = 0; // L0039
// __VB_LINE__:24 // L0040
float ballVX = 0; // L0041
// __VB_LINE__:25 // L0042
float ballVY = 0; // L0043
// __VB_LINE__:26 // L0044
float phase = 0; // L0045
// __VB_LINE__:27 // L0046
float shadowY = 0; // L0047
// __VB_LINE__:28 // L0048
float amplitude = 0; // L0049
// __VB_LINE__:29 // L0050
float centerY = 0; // L0051
// __VB_LINE__:30 // L0052
float bounceMargin = 0; // L0053
// __VB_LINE__:31 // L0054
float leftBound = 0; // L0055
// __VB_LINE__:32 // L0056
float rightBound = 0; // L0057
// __VB_LINE__:33 // L0058
float prevBallX = 0; // L0059
// __VB_LINE__:34 // L0060
float prevBallY = 0; // L0061
// __VB_LINE__:35 // L0062
bool isMovingRight = false; // L0063
// __VB_LINE__:36 // L0064
bool isMovingUp = false; // L0065
TFT_eSprite ball = TFT_eSprite(&tft); // L0066
TFT_eSprite shadow = TFT_eSprite(&tft); // L0067
TFT_eSprite bg = TFT_eSprite(&tft); // L0068
// L0069
void DrawBackground() { // L0070
// __VB_LINE__:95 // L0071
tft.fillRect(0, 0, SCREEN_W, SCREEN_H, COLOR_BG); // L0072
// __VB_LINE__:96 // L0073
int i = 0; // L0074
// __VB_LINE__:97 // L0075
float x1v = 0; // L0076
// __VB_LINE__:97 // L0077
float y1v = 0; // L0078
// __VB_LINE__:97 // L0079
float x2v = 0; // L0080
// __VB_LINE__:97 // L0081
float y2v = 0; // L0082
// __VB_LINE__:98 // L0083
float vanishingX = 0; // L0084
// __VB_LINE__:98 // L0085
float vanishingY = 0; // L0086
// __VB_LINE__:99 // L0087
vanishingX = SCREEN_W / 2; // L0088
// __VB_LINE__:100 // L0089
vanishingY = SCREEN_H * 0.85; // L0090
// __VB_LINE__:103 // L0091
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0092
// __VB_LINE__:104 // L0093
x1v = vanishingX; // L0094
// __VB_LINE__:105 // L0095
y1v = vanishingY; // L0096
// __VB_LINE__:106 // L0097
x2v = i * (SCREEN_W / FLOOR_GRID); // L0098
// __VB_LINE__:107 // L0099
y2v = SCREEN_H; // L0100
// __VB_LINE__:108 // L0101
tft.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0102
// __VB_LINE__:109 // L0103
} // L0104
// __VB_LINE__:112 // L0105
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0106
// __VB_LINE__:113 // L0107
y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0108
// __VB_LINE__:114 // L0109
tft.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0110
// __VB_LINE__:115 // L0111
} // L0112
} // L0113
void DrawBall() { // L0114
    float prevShadowX = 0; // L0115
    float prevShadowY = 0; // L0116
// __VB_LINE__:119 // L0117
int t = 0; // L0118
// __VB_LINE__:119 // L0119
int s = 0; // L0120
// __VB_LINE__:120 // L0121
float angle1v = 0; // L0122
// __VB_LINE__:120 // L0123
float angle2v = 0; // L0124
// __VB_LINE__:121 // L0125
float x1v = 0; // L0126
// __VB_LINE__:121 // L0127
float y1v = 0; // L0128
// __VB_LINE__:121 // L0129
float x2v = 0; // L0130
// __VB_LINE__:121 // L0131
float y2v = 0; // L0132
// __VB_LINE__:121 // L0133
float x3v = 0; // L0134
// __VB_LINE__:121 // L0135
float y3v = 0; // L0136
// __VB_LINE__:122 // L0137
int colorTile = 0; // L0138
// __VB_LINE__:123 // L0139
float spriteCX = 0; // L0140
// __VB_LINE__:124 // L0141
float spriteCY = 0; // L0142
// __VB_LINE__:125 // L0143
spriteCX = BALL_RADIUS; // L0144
// __VB_LINE__:126 // L0145
spriteCY = BALL_RADIUS; // L0146
// __VB_LINE__:129 // L0147
ball.fillSprite(COLOR_BG); // L0148
// __VB_LINE__:131 // L0149
for (int t = 0; ((1) >= 0 ? t <= BALL_TILES : t >= BALL_TILES); t += (1)) { // L0150
// __VB_LINE__:132 // L0151
angle1v = phase + t * (3.14159 * 2 / BALL_TILES); // L0152
// __VB_LINE__:133 // L0153
angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES); // L0154
// __VB_LINE__:134 // L0155
for (int s = 0; ((1) >= 0 ? s <= 1 : s >= 1); s += (1)) { // L0156
// __VB_LINE__:136 // L0157
x1v = ballX; // L0158
// __VB_LINE__:137 // L0159
y1v = ballY; // L0160
// __VB_LINE__:138 // L0161
x2v = ballX + cos(angle1v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0162
// __VB_LINE__:139 // L0163
y2v = ballY + sin(angle1v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0164
// __VB_LINE__:140 // L0165
x3v = ballX + cos(angle2v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0166
// __VB_LINE__:141 // L0167
y3v = ballY + sin(angle2v) * BALL_RADIUS * (1 - s * 0.5) * (amplitude / BALL_RADIUS); // L0168
// __VB_LINE__:143 // L0169
if (((t + s) % 2) == 0) { // L0170
// __VB_LINE__:144 // L0171
colorTile = TFT_RED; // L0172
// __VB_LINE__:145 // L0173
} else { // L0174
// __VB_LINE__:146 // L0175
colorTile = TFT_WHITE; // L0176
// __VB_LINE__:147 // L0177
} // L0178
// __VB_LINE__:150 // L0179
ball.fillTriangle(spriteCX, spriteCY, x2v - (ballX - spriteCX), y2v - (ballY - spriteCY), x3v - (ballX - spriteCX), y3v - (ballY - spriteCY), colorTile); // L0180
// __VB_LINE__:151 // L0181
} // L0182
// __VB_LINE__:152 // L0183
} // L0184
// __VB_LINE__:155 // L0185
float shadowScale = 0; // L0186
// __VB_LINE__:156 // L0187
shadowScale = 0.6 + 0.4 * (1 - ((ballY - (centerY - amplitude)) / (2 * amplitude))); // L0188
// __VB_LINE__:157 // L0189
shadow.fillSprite(COLOR_BG); // L0190
// __VB_LINE__:158 // L0191
shadow.fillEllipse(BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * shadowScale, BALL_RADIUS * 0.4 * shadowScale, COLOR_SHADOW); // L0192
// __VB_LINE__:161 // L0193
int pushX = 0; // L0194
// __VB_LINE__:162 // L0195
int pushY = 0; // L0196
// __VB_LINE__:163 // L0197
pushX = ballX - BALL_RADIUS; // L0198
// __VB_LINE__:164 // L0199
pushY = ballY - spriteCY; // L0200
// __VB_LINE__:167 // L0201
shadow.pushSprite(pushX, shadowY - BALL_RADIUS/2, TFT_TRANSPARENT); // L0202
// __VB_LINE__:168 // L0203
ball.pushSprite(pushX, pushY, TFT_TRANSPARENT); // L0204
// __VB_LINE__:171 // L0205
prevBallX = ballX; // L0206
// __VB_LINE__:172 // L0207
prevBallY = ballY; // L0208
// __VB_LINE__:174 // L0209
prevShadowX = pushX; // L0210
// __VB_LINE__:175 // L0211
prevShadowY = shadowY - BALL_RADIUS/2; // L0212
} // L0213
void setup() { // L0214
    delay(1000); // L0215
    tft.begin(); // L0216
    // __VB_LINE__:40 // L0217
    ballX = SCREEN_W / 2; // L0218
    // __VB_LINE__:41 // L0219
    centerY = SCREEN_H * 0.75; // L0220
    // __VB_LINE__:42 // L0221
    amplitude = SCREEN_H * 0.25 - BALL_RADIUS; // L0222
    // __VB_LINE__:43 // L0223
    ballY = centerY; // L0224
    // __VB_LINE__:44 // L0225
    ballVX = BALL_SPEED_X; // L0226
    // __VB_LINE__:45 // L0227
    ballVY = -3.5; // L0228
    // __VB_LINE__:46 // L0229
    phase = 0; // L0230
    // __VB_LINE__:47 // L0231
    bounceMargin = BALL_RADIUS + 8; // L0232
    // __VB_LINE__:48 // L0233
    leftBound = bounceMargin; // L0234
    // __VB_LINE__:49 // L0235
    rightBound = SCREEN_W - bounceMargin; // L0236
    // __VB_LINE__:50 // L0237
    isMovingRight = true; // L0238
    // __VB_LINE__:51 // L0239
    isMovingUp = false; // L0240
    // __VB_LINE__:52 // L0241
    shadowY = centerY + BALL_RADIUS + 8; // L0242
    // __VB_LINE__:53 // L0243
    prevBallX = ballX; // L0244
    // __VB_LINE__:54 // L0245
    prevBallY = ballY; // L0246
    // __VB_LINE__:56 // L0247
    DrawBackground(); // L0248
    // __VB_LINE__:59 // L0249
    int spriteW = 0; // L0250
    // __VB_LINE__:60 // L0251
    spriteW = BALL_RADIUS * 2; // L0252
    // __VB_LINE__:61 // L0253
    int spriteH = 0; // L0254
    // __VB_LINE__:62 // L0255
    spriteH = BALL_RADIUS * 2; // L0256
    ball.createSprite(spriteW, spriteH); // L0257
    // __VB_LINE__:63 // L0258
    // CREATE_SPRITE ball spriteW spriteH // L0259
    shadow.createSprite(spriteW, BALL_RADIUS); // L0260
    // __VB_LINE__:64 // L0261
    // CREATE_SPRITE shadow spriteW BALL_RADIUS // L0262
    bg.createSprite(SCREEN_W, SCREEN_H); // L0263
    // __VB_LINE__:67 // L0264
    // CREATE_SPRITE bg SCREEN_W SCREEN_H // L0265
    // __VB_LINE__:68 // L0266
    bg.fillSprite(COLOR_BG); // L0267
    // __VB_LINE__:71 // L0268
    int i = 0; // L0269
    // __VB_LINE__:72 // L0270
    float x1v = 0; // L0271
    // __VB_LINE__:72 // L0272
    float y1v = 0; // L0273
    // __VB_LINE__:72 // L0274
    float x2v = 0; // L0275
    // __VB_LINE__:72 // L0276
    float y2v = 0; // L0277
    // __VB_LINE__:73 // L0278
    float vanishingX = 0; // L0279
    // __VB_LINE__:73 // L0280
    float vanishingY = 0; // L0281
    // __VB_LINE__:74 // L0282
    vanishingX = SCREEN_W / 2; // L0283
    // __VB_LINE__:75 // L0284
    vanishingY = SCREEN_H * 0.85; // L0285
    // __VB_LINE__:76 // L0286
    for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0287
    // __VB_LINE__:77 // L0288
    x1v = vanishingX; // L0289
    // __VB_LINE__:78 // L0290
    y1v = vanishingY; // L0291
    // __VB_LINE__:79 // L0292
    x2v = i * (SCREEN_W / FLOOR_GRID); // L0293
    // __VB_LINE__:80 // L0294
    y2v = SCREEN_H; // L0295
    // __VB_LINE__:81 // L0296
    bg.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0297
    // __VB_LINE__:82 // L0298
    } // L0299
    // __VB_LINE__:83 // L0300
    for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0301
    // __VB_LINE__:84 // L0302
    y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0303
    // __VB_LINE__:85 // L0304
    bg.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0305
    // __VB_LINE__:86 // L0306
    } // L0307
    // __VB_LINE__:89 // L0308
    prevBallX = ballX; // L0309
    // __VB_LINE__:90 // L0310
    prevBallY = ballY; // L0311
} // L0312
// L0313
void loop() { // L0314
    // __VB_LINE__:180 // L0315
    bg.pushSprite(0, 0); // L0316
    // __VB_LINE__:182 // L0317
    if (isMovingRight) { // L0318
    // __VB_LINE__:183 // L0319
    ballX = ballX + ballVX; // L0320
    // __VB_LINE__:184 // L0321
    phase = phase + PHASE_STEP; // L0322
    // __VB_LINE__:185 // L0323
    if (ballX >= rightBound) { // L0324
    // __VB_LINE__:186 // L0325
    isMovingRight = false; // L0326
    // __VB_LINE__:187 // L0327
    } // L0328
    // __VB_LINE__:188 // L0329
    } else { // L0330
    // __VB_LINE__:189 // L0331
    ballX = ballX - ballVX; // L0332
    // __VB_LINE__:190 // L0333
    phase = phase - PHASE_STEP; // L0334
    // __VB_LINE__:191 // L0335
    if (ballX <= leftBound) { // L0336
    // __VB_LINE__:192 // L0337
    isMovingRight = true; // L0338
    // __VB_LINE__:193 // L0339
    } // L0340
    // __VB_LINE__:194 // L0341
    } // L0342
    // __VB_LINE__:197 // L0343
    ballY = ballY + ballVY; // L0344
    // __VB_LINE__:198 // L0345
    ballVY = ballVY + 0.6; // L0346
    // __VB_LINE__:199 // L0347
    if (ballY >= centerY + amplitude) { // L0348
    // __VB_LINE__:200 // L0349
    ballY = centerY + amplitude; // L0350
    // __VB_LINE__:201 // L0351
    ballVY = -abs(ballVY) * 0.85; // L0352
    // __VB_LINE__:202 // L0353
    isMovingUp = false; // L0354
    // __VB_LINE__:203 // L0355
    } else if (ballY <= centerY - amplitude) { // L0356
    // __VB_LINE__:204 // L0357
    ballY = centerY - amplitude; // L0358
    // __VB_LINE__:205 // L0359
    ballVY = abs(ballVY) * 0.85; // L0360
    // __VB_LINE__:206 // L0361
    isMovingUp = true; // L0362
    // __VB_LINE__:207 // L0363
    } else { // L0364
    // __VB_LINE__:209 // L0365
    isMovingUp = (ballVY < 0); // L0366
    // __VB_LINE__:210 // L0367
    } // L0368
    // __VB_LINE__:212 // L0369
    DrawBall(); // L0370
    // __VB_LINE__:215 // L0371
    prevBallX = ballX; // L0372
    // __VB_LINE__:216 // L0373
    prevBallY = ballY; // L0374
    // __VB_LINE__:219 // L0375
    delay(20); // L0376
} // L0377
