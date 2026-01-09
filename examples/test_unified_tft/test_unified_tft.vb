' Test with TFT_eSPI using unified color constants
#Include <TFT_eSPI.h>

Sub Setup()
    SerialBegin 115200
    tft.init
    
    ' Unified commands with unified colors!
    FillScreen COLOR_BLACK
    DrawLine 0, 0, 100, 100, vbWhite
    DrawRect 10, 10, 50, 30, COLOR_RED
    FillCircle 160, 120, 20, vbBlue
    SetTextSize 2
    SetCursor 10, 200
    PrintLine "Unified Colors!"
End Sub

Sub Loop()
    Delay 1000
End Sub
