' RGB Color Helper Demo
' Works with TFT_eSPI and Adafruit_GFX

#Include <TFT_eSPI.h>

Dim tft As TFT_eSPI

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "RGB Color Demo"
    
    tft.init
    tft.setRotation 1
    
    ' Clear with black
    FillScreen RGB(0, 0, 0)
    Delay 500
    
    ' Draw colored rectangles
    FillRect 10, 10, 100, 80, RGB(255, 0, 0)     ' Red
    FillRect 120, 10, 100, 80, RGB(0, 255, 0)    ' Green
    FillRect 230, 10, 80, 80, RGB(0, 0, 255)     ' Blue
    
    FillRect 10, 100, 100, 80, RGB(255, 255, 0)  ' Yellow
    FillRect 120, 100, 100, 80, RGB(0, 255, 255) ' Cyan
    FillRect 230, 100, 80, 80, RGB(255, 0, 255)  ' Magenta
    
    ' White text
    SetTextColor RGB(255, 255, 255), RGB(0, 0, 0)
    SetTextSize 2
    SetCursor 50, 200
    PrintText "RGB Colors!"
    
    SerialPrintLine "Drawing complete"
End Sub

Sub Loop()
    ' Cycle through rainbow colors
    Dim hue As Integer
    For hue = 0 To 360 Step 10
        Dim r As Integer, g As Integer, b As Integer
        
        ' Simple HSV to RGB conversion
        If hue < 60 Then
            r = 255
            g = hue * 4
            b = 0
        ElseIf hue < 120 Then
            r = 255 - ((hue - 60) * 4)
            g = 255
            b = 0
        ElseIf hue < 180 Then
            r = 0
            g = 255
            b = (hue - 120) * 4
        ElseIf hue < 240 Then
            r = 0
            g = 255 - ((hue - 180) * 4)
            b = 255
        ElseIf hue < 300 Then
            r = (hue - 240) * 4
            g = 0
            b = 255
        Else
            r = 255
            g = 0
            b = 255 - ((hue - 300) * 4)
        End If
        
        FillCircle 160, 120, 50, RGB(r, g, b)
        Delay 50
    Next hue
End Sub
