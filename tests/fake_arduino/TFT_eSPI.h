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
};
