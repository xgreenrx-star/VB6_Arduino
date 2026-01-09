' Universal Graphics Demo
' Works with ANY graphics library: TFT_eSPI, Adafruit_GFX, U8g2!
' Just include your preferred library and the same code works.

' Choose ONE library (uncomment the one you want):
' #Include <TFT_eSPI.h>
' #Include <Adafruit_GFX.h>
' #Include <Adafruit_SSD1306.h>
' #Include <U8g2lib.h>

' Display object will be auto-detected:
' TFT_eSPI uses: tft
' Adafruit uses: display or gfx  
' U8g2 uses: u8g2

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Universal Graphics Demo"
    
    ' Initialize display (library-specific init still needed)
    ' For TFT_eSPI:
    tft.init
    tft.setRotation 1
    
    ' For Adafruit_GFX:
    ' display.begin
    
    ' For U8g2:
    ' u8g2.begin
    
    ' === UNIFIED COMMANDS WITH UNIFIED COLORS ===
    
    ' Clear screen
    ClearDisplay
    Delay 500
    
    ' Draw shapes with COLOR_ constants
    DrawLine 10, 10, 100, 100, COLOR_WHITE
    DrawRect 20, 20, 80, 60, COLOR_RED
    FillRect 30, 30, 60, 40, COLOR_BLUE
    
    ' Or use VB6-style vb constants
    DrawCircle 160, 120, 40, vbGreen
    FillCircle 160, 120, 30, vbYellow
    
    ' Draw triangle
    DrawTriangle 240, 180, 260, 140, 280, 180, vbCyan
    FillTriangle 250, 170, 260, 150, 270, 170, COLOR_MAGENTA
    
    ' Draw individual pixels
    Dim i As Integer
    For i = 0 To 50
        DrawPixel 10 + i, 180, vbWhite
    Next i
    
    ' Text operations
    SetTextSize 2
    SetTextColor vbWhite, COLOR_BLACK
    SetCursor 10, 200
    PrintLine "Hello World!"
    
    SetCursor 10, 220
    SetTextSize 1
    PrintText "Universal API!"
    
    SerialPrintLine "Drawing complete!"
End Sub

Sub Loop()
    ' Animation loop
    Delay 1000
    
    ' Draw random pixels
    Dim x As Integer
    Dim y As Integer
    Dim c As Integer
    
    x = Random(0, 319)
    y = Random(0, 239)
    c = Random(0, 65535)
    
    DrawPixel x, y, c
End Sub
