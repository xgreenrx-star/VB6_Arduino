' ESP32-S3-LCD-1.47 Hello World Example
' Displays "Hello World" on the built-in ST7789 screen

#Include <TFT_eSPI.h>

Dim tft As TFT_eSPI

Sub Setup()
	' Initialize serial for debugging
	SerialBegin 115200
	SerialPrintLine "LCD Hello World starting..."
    
	' Initialize the display
	tft.init()
	tft.setRotation(1)
    
	' Clear screen to black
	tft.fillScreen(0x0000)
    
	' Set text properties
	tft.setTextColor(0xFFFF, 0x0000)
	tft.setTextSize(3)
    
	' Display Hello World
	tft.setCursor(10, 60)
	tft.println("Hello")
	tft.setCursor(10, 90)
	tft.println("World!")
    
	SerialPrintLine "Display initialized"
End Sub

Sub Loop()
	' Nothing to do in loop
	Delay 1000
End Sub