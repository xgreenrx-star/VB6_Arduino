' Simple Hello World for ESP32-S3-LCD-1.47
' Displays "Hello World" on the built-in ST7789 screen

#Include <TFT_eSPI.h>

Dim tft As TFT_eSPI

Sub Setup()
    SerialBegin 115200
    
    ' Initialize backlight
    PinMode 46, OUTPUT
    DigitalWrite 46, HIGH
    
    ' Initialize the display
    tft.init()
    tft.setRotation(1)
    tft.fillScreen(TFT_BLACK)
    
    ' Display "Hello World"
    tft.setTextColor(TFT_WHITE)
    tft.setTextSize(3)
    tft.setCursor(20, 140)
    tft.println "Hello World"
    
    SerialPrintLine "Display initialized"
End Sub

Sub Loop()
    Delay 1000
End Sub
