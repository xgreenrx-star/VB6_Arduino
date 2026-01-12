#pragma once
#include <Arduino.h>
class TFT_eSPI {
public:
    void begin() {}
    void fillRect(int,int,int,int,int) {}
    void drawLine(int,int,int,int,int) {}
    void fillCircle(float,float,int,int) {}
    void drawCircle(float,float,int,int) {}
    void fillTriangle(float,float,float,float,float,float,int) {}
    void drawTriangle(float,float,float,float,float,float,int) {}
    void setTextSize(int) {}
    void print(const String&) {}
    void println(const String&) {}
    uint16_t color565(int r, int g, int b) { return 0; }
};

// Minimal TFT_eSprite stub for tests
#define TFT_TRANSPARENT 0x0120
class TFT_eSprite {
public:
    TFT_eSprite(TFT_eSPI* _tft) {}
    void createSprite(int w, int h) {}
    void fillSprite(int color) {}
    void fillEllipse(int cx, int cy, int rx, int ry, int color) {}
    void fillTriangle(int x1,int y1,int x2,int y2,int x3,int y3,int color) {}
    void pushSprite(int x,int y) {}
    void pushSprite(int x,int y, uint16_t transparent) {}
    void drawLine(int x1, int y1, int x2, int y2, int color) {}
    void deleteSprite() {}
};
