#pragma once
#include <cmath>
#include <string>
#include <cstring>
#include <algorithm>

// Minimal Arduino-like String wrapper for testing
class String {
public:
    std::string s;
    String() = default;
    String(const char* c): s(c) {}
    String(const std::string &ss): s(ss) {}
    size_t length() const { return s.length(); }
    int indexOf(const String& sub, int from = 0) const {
        auto pos = s.find(sub.s, (size_t)std::max(0, from));
        return pos == std::string::npos ? -1 : (int)pos;
    }
    String substring(int start, int end) const {
        if (start < 0) start = 0;
        if (end < 0) end = (int)s.length();
        return String(s.substr((size_t)start, (size_t)(end - start)));
    }
    String substring(int start) const { return String(s.substr((size_t)start)); }
    String& operator+=(const String& other) { s += other.s; return *this; }
    bool operator==(const String& other) const { return s == other.s; }
    operator std::string() const { return s; }
};

#define PI 3.14159
inline void delay(int) {}
inline unsigned long millis() { return 0; }
inline void randomSeed(unsigned long) {}
inline int abs(int x) { return std::abs(x); }

// Basic Arduino I/O stubs
#define OUTPUT 1
#define INPUT 0
#define INPUT_PULLUP 2
#define HIGH 1
#define LOW 0
inline void pinMode(int pin, int mode) {}
inline void digitalWrite(int pin, int value) {}
inline int digitalRead(int pin) { return HIGH; }

// Minimal Serial stub
struct SerialClass {
    void begin(int) {}
    void setRxBufferSize(int) {}
    void setTxBufferSize(int) {}
    int available() { return 0; }
    int read() { return -1; }
    void println(const String& s) {}
    void println(int v) {}
    void print(const String& s) {}
    void print(int v) {}
};
static SerialClass Serial;

// Basic color constants for TFT testing
#define TFT_DARKGREY 0
#define TFT_MAGENTA 1
#define TFT_DARKGREY 0
#define TFT_RED 2
#define TFT_WHITE 3
