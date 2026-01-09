' TFT Window Management Demo
' Demonstrates viewport, window, and efficient pixel operations
' Using TFT_eSPI library with ESP32

' TFT object must be created as 'tft'
' #Include <TFT_eSPI.h>

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "TFT Window Management Demo"
    
    ' Initialize TFT (assumes tft object declared in header)
    tft.init
    tft.setRotation 1
    tft.fillScreen TFT_BLACK
    
    ' Demo 1: Fast window filling with SetWindow + PushBlock
    DemoFastFill
    Delay 2000
    
    ' Demo 2: Viewport clipping
    DemoViewport
    Delay 2000
    
    ' Demo 3: Efficient gradients with PushPixel
    DemoGradient
    Delay 2000
    
    ' Demo 4: Multiple viewports (panels)
    DemoPanels
    
    SerialPrintLine "Demo complete!"
End Sub

Sub Loop()
    ' Animation: update panels
    Delay 1000
End Sub

Sub DemoFastFill()
    ' Fill screen quadrants with different colors using windows
    SerialPrintLine "Demo 1: Fast window fill"
    
    tft.fillScreen TFT_BLACK
    Delay 500
    
    ' Top-left quadrant (red)
    SetWindow 0, 0, 159, 119
    PushBlock TFT_RED, 19200
    
    ' Top-right quadrant (green)  
    SetWindow 160, 0, 319, 119
    PushBlock TFT_GREEN, 19200
    
    ' Bottom-left quadrant (blue)
    SetWindow 0, 120, 159, 239
    PushBlock TFT_BLUE, 19200
    
    ' Bottom-right quadrant (yellow)
    SetWindow 160, 120, 319, 239
    PushBlock TFT_YELLOW, 19200
End Sub

Sub DemoViewport()
    ' Viewport clipping demo
    SerialPrintLine "Demo 2: Viewport clipping"
    
    tft.fillScreen TFT_BLACK
    
    ' Set viewport to center 200x150 region
    SetViewport 60, 45, 200, 150
    
    ' Draw frame around viewport
    FrameViewport TFT_WHITE, 3
    
    ' All drawing is clipped to viewport
    tft.fillRect 0, 0, 300, 240, TFT_CYAN
    
    ' Draw some circles (will be clipped)
    tft.fillCircle 100, 75, 50, TFT_MAGENTA
    tft.fillCircle 100, 75, 30, TFT_YELLOW
    
    ' Reset to full screen
    Delay 1000
    ResetViewport
    
    ' Now circle extends beyond old viewport
    tft.fillCircle 100, 75, 60, TFT_GREEN
End Sub

Sub DemoGradient()
    ' Create horizontal gradient using PushPixel
    SerialPrintLine "Demo 3: Pixel-by-pixel gradient"
    
    tft.fillScreen TFT_BLACK
    
    ' 200x100 gradient in center
    Dim startX As Integer
    Dim startY As Integer
    startX = 60
    startY = 70
    
    SetAddrWindow startX, startY, 200, 100
    
    Dim x As Integer
    Dim y As Integer
    For y = 0 To 99
        For x = 0 To 199
            ' RGB565 gradient: red to blue
            Dim r As Integer
            Dim b As Integer
            r = x * 31 / 199  ' 0-31 red component
            b = 31 - r        ' 31-0 blue component
            
            Dim color As Integer
            color = r * 2048 + b  ' RGB565: (r << 11) | b
            
            PushPixel color
        Next x
    Next y
End Sub

Sub DemoPanels()
    ' Multiple viewport panels
    SerialPrintLine "Demo 4: Multiple viewport panels"
    
    tft.fillScreen TFT_BLACK
    
    ' Panel 1: Top-left (status)
    SetViewport 5, 5, 150, 110
    FrameViewport TFT_GREEN, 2
    tft.setCursor 10, 15
    tft.setTextColor TFT_WHITE, TFT_BLACK
    tft.setTextSize 1
    tft.println "Status Panel"
    tft.println "CPU: 240MHz"
    tft.println "Temp: 45C"
    
    ' Panel 2: Top-right (graph)
    SetViewport 165, 5, 150, 110
    FrameViewport TFT_BLUE, 2
    tft.fillRect 170, 10, 140, 100, TFT_BLACK
    ' Draw simple bar graph
    Dim i As Integer
    For i = 0 To 6
        Dim h As Integer
        h = 20 + i * 10
        tft.fillRect 175 + i * 20, 110 - h, 15, h, TFT_CYAN
    Next i
    
    ' Panel 3: Bottom (log)
    SetViewport 5, 125, 310, 110
    FrameViewport TFT_YELLOW, 2
    tft.setCursor 10, 135
    tft.setTextColor TFT_WHITE, TFT_BLACK
    tft.println "Event Log:"
    tft.println "> System started"
    tft.println "> Sensors OK"
    tft.println "> Ready"
    
    ResetViewport
End Sub
