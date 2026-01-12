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
const auto BALL_TILES = 12; // L0017
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
// __VB_LINE__:96 // L0071
tft.fillRect(0, 0, SCREEN_W, SCREEN_H, COLOR_BG); // L0072
// __VB_LINE__:97 // L0073
int i = 0; // L0074
// __VB_LINE__:98 // L0075
float x1v = 0; // L0076
// __VB_LINE__:98 // L0077
float y1v = 0; // L0078
// __VB_LINE__:98 // L0079
float x2v = 0; // L0080
// __VB_LINE__:98 // L0081
float y2v = 0; // L0082
// __VB_LINE__:99 // L0083
float vanishingX = 0; // L0084
// __VB_LINE__:99 // L0085
float vanishingY = 0; // L0086
// __VB_LINE__:100 // L0087
vanishingX = SCREEN_W / 2; // L0088
// __VB_LINE__:101 // L0089
vanishingY = SCREEN_H * 0.85; // L0090
// __VB_LINE__:104 // L0091
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0092
// __VB_LINE__:105 // L0093
x1v = vanishingX; // L0094
// __VB_LINE__:106 // L0095
y1v = vanishingY; // L0096
// __VB_LINE__:107 // L0097
x2v = i * (SCREEN_W / FLOOR_GRID); // L0098
// __VB_LINE__:108 // L0099
y2v = SCREEN_H; // L0100
// __VB_LINE__:109 // L0101
tft.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0102
// __VB_LINE__:110 // L0103
} // L0104
// __VB_LINE__:113 // L0105
for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0106
// __VB_LINE__:114 // L0107
y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0108
// __VB_LINE__:115 // L0109
tft.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0110
// __VB_LINE__:116 // L0111
} // L0112
} // L0113
void DrawBall() { // L0114
    float prevShadowX = 0; // L0115
    float prevShadowY = 0; // L0116
// __VB_LINE__:120 // L0117
int t = 0; // L0118
// __VB_LINE__:120 // L0119
int s = 0; // L0120
// __VB_LINE__:121 // L0121
float angle1v = 0; // L0122
// __VB_LINE__:121 // L0123
float angle2v = 0; // L0124
// __VB_LINE__:122 // L0125
float x1v = 0; // L0126
// __VB_LINE__:122 // L0127
float y1v = 0; // L0128
// __VB_LINE__:122 // L0129
float x2v = 0; // L0130
// __VB_LINE__:122 // L0131
float y2v = 0; // L0132
// __VB_LINE__:122 // L0133
float x3v = 0; // L0134
// __VB_LINE__:122 // L0135
float y3v = 0; // L0136
// __VB_LINE__:123 // L0137
int colorTile = 0; // L0138
// __VB_LINE__:124 // L0139
float spriteCX = 0; // L0140
// __VB_LINE__:125 // L0141
float spriteCY = 0; // L0142
// __VB_LINE__:126 // L0143
spriteCX = BALL_RADIUS; // L0144
// __VB_LINE__:127 // L0145
spriteCY = BALL_RADIUS; // L0146
// __VB_LINE__:130 // L0147
ball.fillSprite(COLOR_BG); // L0148
// __VB_LINE__:133 // L0149
ball.fillEllipse(spriteCX, spriteCY, BALL_RADIUS, BALL_RADIUS, TFT_WHITE); // L0150
// __VB_LINE__:136 // L0151
ball.fillEllipse(spriteCX - (BALL_RADIUS/4), spriteCY - (BALL_RADIUS/4), BALL_RADIUS/6, BALL_RADIUS/6, TFT_LIGHTGREY); // L0152
// __VB_LINE__:142 // L0153
for (int t = 0; ((1) >= 0 ? t <= BALL_TILES - 1 : t >= BALL_TILES - 1); t += (1)) { // L0154
// __VB_LINE__:143 // L0155
angle1v = phase + t * (3.14159 * 2 / BALL_TILES); // L0156
// __VB_LINE__:144 // L0157
angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES); // L0158
// __VB_LINE__:146 // L0159
for (int s = 1; ((-1) >= 0 ? s <= 0 : s >= 0); s += (-1)) { // L0160
// __VB_LINE__:147 // L0161
x2v = ballX + cos(angle1v) * BALL_RADIUS * (1 - s * 0.35); // L0162
// __VB_LINE__:148 // L0163
y2v = ballY + sin(angle1v) * BALL_RADIUS * (1 - s * 0.35); // L0164
// __VB_LINE__:149 // L0165
x3v = ballX + cos(angle2v) * BALL_RADIUS * (1 - s * 0.35); // L0166
// __VB_LINE__:150 // L0167
y3v = ballY + sin(angle2v) * BALL_RADIUS * (1 - s * 0.35); // L0168
// __VB_LINE__:152 // L0169
if (((t + s) % 2) != 0) { // L0170
// __VB_LINE__:154 // L0171
float x2l = 0; // L0172
// __VB_LINE__:154 // L0173
float y2l = 0; // L0174
// __VB_LINE__:154 // L0175
float x3l = 0; // L0176
// __VB_LINE__:154 // L0177
float y3l = 0; // L0178
// __VB_LINE__:155 // L0179
x2l = x2v - (ballX - spriteCX); // L0180
// __VB_LINE__:156 // L0181
y2l = y2v - (ballY - spriteCY); // L0182
// __VB_LINE__:157 // L0183
x3l = x3v - (ballX - spriteCX); // L0184
// __VB_LINE__:158 // L0185
y3l = y3v - (ballY - spriteCY); // L0186
// __VB_LINE__:160 // L0187
float midX = 0; // L0188
// __VB_LINE__:160 // L0189
float midY = 0; // L0190
// __VB_LINE__:161 // L0191
midX = (x2l + x3l) / 2; // L0192
// __VB_LINE__:162 // L0193
midY = (y2l + y3l) / 2; // L0194
// __VB_LINE__:163 // L0195
if (((x2l - spriteCX) * (x2l - spriteCX) + (y2l - spriteCY) * (y2l - spriteCY) <= BALL_RADIUS * BALL_RADIUS) || ((x3l - spriteCX) * (x3l - spriteCX) + (y3l - spriteCY) * (y3l - spriteCY) <= BALL_RADIUS * BALL_RADIUS) || ((midX - spriteCX) * (midX - spriteCX) + (midY - spriteCY) * (midY - spriteCY) <= BALL_RADIUS * BALL_RADIUS)) { // L0196
// __VB_LINE__:164 // L0197
ball.fillTriangle(spriteCX, spriteCY, x2l, y2l, x3l, y3l, TFT_RED); // L0198
// __VB_LINE__:166 // L0199
} // L0200
// __VB_LINE__:167 // L0201
} // L0202
// __VB_LINE__:168 // L0203
} // L0204
// __VB_LINE__:169 // L0205
} // L0206
// __VB_LINE__:175 // L0207
float shadowScale = 0; // L0208
// __VB_LINE__:176 // L0209
float shadowNorm = 0; // L0210
// __VB_LINE__:177 // L0211
shadowNorm = 1 - ((ballY - (centerY - amplitude)) / (2 * amplitude)); // L0212
// __VB_LINE__:178 // L0213
shadowScale = 0.6 + 0.9 * shadowNorm; // L0214
// __VB_LINE__:179 // L0215
if (shadowScale < 0.5) { shadowScale = 0.5; } // L0216
// __VB_LINE__:180 // L0217
if (shadowScale > 1.6) { shadowScale = 1.6; } // L0218
// __VB_LINE__:183 // L0219
shadow.fillSprite(COLOR_BG); // L0220
// __VB_LINE__:185 // L0221
shadow.fillEllipse(BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 1.8), BALL_RADIUS * (0.55 * shadowScale), tft.color565(140, 140, 140)); // L0222
// __VB_LINE__:187 // L0223
shadow.fillEllipse(BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 1.25), BALL_RADIUS * (0.5 * shadowScale), tft.color565(100, 100, 100)); // L0224
// __VB_LINE__:189 // L0225
shadow.fillEllipse(BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 0.95), BALL_RADIUS * (0.4 * shadowScale), tft.color565(40, 40, 40)); // L0226
// __VB_LINE__:192 // L0227
int pushX = 0; // L0228
// __VB_LINE__:193 // L0229
int pushY = 0; // L0230
// __VB_LINE__:194 // L0231
int floorY = 0; // L0232
// __VB_LINE__:195 // L0233
pushX = ballX - BALL_RADIUS; // L0234
// __VB_LINE__:196 // L0235
pushY = ballY - spriteCY; // L0236
// __VB_LINE__:197 // L0237
floorY = centerY + amplitude + BALL_RADIUS/2; // L0238
// __VB_LINE__:200 // L0239
shadow.pushSprite(pushX, floorY - BALL_RADIUS/2, TFT_TRANSPARENT); // L0240
// __VB_LINE__:201 // L0241
ball.pushSprite(pushX, pushY, TFT_TRANSPARENT); // L0242
// __VB_LINE__:204 // L0243
prevBallX = ballX; // L0244
// __VB_LINE__:205 // L0245
prevBallY = ballY; // L0246
// __VB_LINE__:207 // L0247
prevShadowX = pushX; // L0248
// __VB_LINE__:208 // L0249
prevShadowY = shadowY - BALL_RADIUS/2; // L0250
} // L0251
void setup() { // L0252
    delay(1000); // L0253
    tft.begin(); // L0254
    // __VB_LINE__:40 // L0255
    ballX = SCREEN_W / 2; // L0256
    // __VB_LINE__:42 // L0257
    centerY = SCREEN_H / 2; // L0258
    // __VB_LINE__:43 // L0259
    amplitude = centerY - BALL_RADIUS - 8; // L0260
    // __VB_LINE__:44 // L0261
    ballY = centerY; // L0262
    // __VB_LINE__:45 // L0263
    ballVX = BALL_SPEED_X; // L0264
    // __VB_LINE__:46 // L0265
    ballVY = -6.0; // L0266
    // __VB_LINE__:47 // L0267
    phase = 0; // L0268
    // __VB_LINE__:48 // L0269
    bounceMargin = BALL_RADIUS + 8; // L0270
    // __VB_LINE__:49 // L0271
    leftBound = bounceMargin; // L0272
    // __VB_LINE__:50 // L0273
    rightBound = SCREEN_W - bounceMargin; // L0274
    // __VB_LINE__:51 // L0275
    isMovingRight = true; // L0276
    // __VB_LINE__:52 // L0277
    isMovingUp = false; // L0278
    // __VB_LINE__:53 // L0279
    shadowY = centerY + BALL_RADIUS + 8; // L0280
    // __VB_LINE__:54 // L0281
    prevBallX = ballX; // L0282
    // __VB_LINE__:55 // L0283
    prevBallY = ballY; // L0284
    // __VB_LINE__:57 // L0285
    DrawBackground(); // L0286
    // __VB_LINE__:60 // L0287
    int spriteW = 0; // L0288
    // __VB_LINE__:61 // L0289
    spriteW = BALL_RADIUS * 2; // L0290
    // __VB_LINE__:62 // L0291
    int spriteH = 0; // L0292
    // __VB_LINE__:63 // L0293
    spriteH = BALL_RADIUS * 2; // L0294
    ball.createSprite(spriteW, spriteH); // L0295
    // __VB_LINE__:64 // L0296
    // CREATE_SPRITE ball spriteW spriteH // L0297
    shadow.createSprite(spriteW, BALL_RADIUS); // L0298
    // __VB_LINE__:65 // L0299
    // CREATE_SPRITE shadow spriteW BALL_RADIUS // L0300
    bg.createSprite(SCREEN_W, SCREEN_H); // L0301
    // __VB_LINE__:68 // L0302
    // CREATE_SPRITE bg SCREEN_W SCREEN_H // L0303
    // __VB_LINE__:69 // L0304
    bg.fillSprite(COLOR_BG); // L0305
    // __VB_LINE__:72 // L0306
    int i = 0; // L0307
    // __VB_LINE__:73 // L0308
    float x1v = 0; // L0309
    // __VB_LINE__:73 // L0310
    float y1v = 0; // L0311
    // __VB_LINE__:73 // L0312
    float x2v = 0; // L0313
    // __VB_LINE__:73 // L0314
    float y2v = 0; // L0315
    // __VB_LINE__:74 // L0316
    float vanishingX = 0; // L0317
    // __VB_LINE__:74 // L0318
    float vanishingY = 0; // L0319
    // __VB_LINE__:75 // L0320
    vanishingX = SCREEN_W / 2; // L0321
    // __VB_LINE__:76 // L0322
    vanishingY = SCREEN_H * 0.85; // L0323
    // __VB_LINE__:77 // L0324
    for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0325
    // __VB_LINE__:78 // L0326
    x1v = vanishingX; // L0327
    // __VB_LINE__:79 // L0328
    y1v = vanishingY; // L0329
    // __VB_LINE__:80 // L0330
    x2v = i * (SCREEN_W / FLOOR_GRID); // L0331
    // __VB_LINE__:81 // L0332
    y2v = SCREEN_H; // L0333
    // __VB_LINE__:82 // L0334
    bg.drawLine(x1v, y1v, x2v, y2v, COLOR_GRID); // L0335
    // __VB_LINE__:83 // L0336
    } // L0337
    // __VB_LINE__:84 // L0338
    for (int i = 0; ((1) >= 0 ? i <= FLOOR_GRID : i >= FLOOR_GRID); i += (1)) { // L0339
    // __VB_LINE__:85 // L0340
    y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID); // L0341
    // __VB_LINE__:86 // L0342
    bg.drawLine(0, y1v, SCREEN_W, y1v, COLOR_GRID); // L0343
    // __VB_LINE__:87 // L0344
    } // L0345
    // __VB_LINE__:90 // L0346
    prevBallX = ballX; // L0347
    // __VB_LINE__:91 // L0348
    prevBallY = ballY; // L0349
} // L0350
// L0351
void loop() { // L0352
    // __VB_LINE__:213 // L0353
    bg.pushSprite(0, 0); // L0354
    // __VB_LINE__:215 // L0355
    if (isMovingRight) { // L0356
    // __VB_LINE__:216 // L0357
    ballX = ballX + ballVX; // L0358
    // __VB_LINE__:217 // L0359
    phase = phase + PHASE_STEP; // L0360
    // __VB_LINE__:218 // L0361
    if (ballX >= rightBound) { // L0362
    // __VB_LINE__:219 // L0363
    isMovingRight = false; // L0364
    // __VB_LINE__:220 // L0365
    } // L0366
    // __VB_LINE__:221 // L0367
    } else { // L0368
    // __VB_LINE__:222 // L0369
    ballX = ballX - ballVX; // L0370
    // __VB_LINE__:223 // L0371
    phase = phase - PHASE_STEP; // L0372
    // __VB_LINE__:224 // L0373
    if (ballX <= leftBound) { // L0374
    // __VB_LINE__:225 // L0375
    isMovingRight = true; // L0376
    // __VB_LINE__:226 // L0377
    } // L0378
    // __VB_LINE__:227 // L0379
    } // L0380
    // __VB_LINE__:230 // L0381
    ballY = ballY + ballVY; // L0382
    // __VB_LINE__:231 // L0383
    ballVY = ballVY + 0.6; // L0384
    // __VB_LINE__:232 // L0385
    if (ballY >= centerY + amplitude) { // L0386
    // __VB_LINE__:233 // L0387
    ballY = centerY + amplitude; // L0388
    // __VB_LINE__:234 // L0389
    ballVY = -abs(ballVY) * 0.92; // L0390
    // __VB_LINE__:235 // L0391
    isMovingUp = false; // L0392
    // __VB_LINE__:236 // L0393
    } else if (ballY <= centerY - amplitude) { // L0394
    // __VB_LINE__:237 // L0395
    ballY = centerY - amplitude; // L0396
    // __VB_LINE__:238 // L0397
    ballVY = abs(ballVY) * 0.92; // L0398
    // __VB_LINE__:239 // L0399
    isMovingUp = true; // L0400
    // __VB_LINE__:240 // L0401
    } else { // L0402
    // __VB_LINE__:242 // L0403
    isMovingUp = (ballVY < 0); // L0404
    // __VB_LINE__:243 // L0405
    } // L0406
    // __VB_LINE__:245 // L0407
    DrawBall(); // L0408
    // __VB_LINE__:248 // L0409
    prevBallX = ballX; // L0410
    // __VB_LINE__:249 // L0411
    prevBallY = ballY; // L0412
    // __VB_LINE__:252 // L0413
    delay(20); // L0414
} // L0415
