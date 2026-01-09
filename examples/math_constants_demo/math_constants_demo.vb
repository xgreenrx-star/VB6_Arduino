' Math and Status Constants Demo
' Demonstrates PI, TAU, INF, NAN, OK, FAILED

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Math Constants Demo" & vbCrLf
    
    ' === PI and TAU Constants ===
    
    ' Calculate circle properties
    Dim radius As Double
    radius = 5.0
    
    ' Circumference using PI
    Dim circumference1 As Double
    circumference1 = 2 * PI * radius
    SerialPrint "Circumference (2*PI*r): "
    SerialPrintLine circumference1
    
    ' Circumference using TAU (cleaner!)
    Dim circumference2 As Double
    circumference2 = TAU * radius
    SerialPrint "Circumference (TAU*r): "
    SerialPrintLine circumference2
    
    ' Area of circle
    Dim area As Double
    area = PI * radius * radius
    SerialPrint "Area (PI*r^2): "
    SerialPrintLine area
    
    SerialPrintLine vbCrLf & "Angle Conversions:"
    
    ' Convert degrees to radians (use DEG2RAD)
    Dim degrees As Double
    degrees = 90
    Dim radians As Double
    radians = degrees * DEG2RAD
    SerialPrint "90 degrees = "
    SerialPrint radians
    SerialPrintLine " radians"
    
    ' Convert radians to degrees (use RAD2DEG)
    Dim rad2deg As Double
    rad2deg = radians * RAD2DEG
    SerialPrint "Back to degrees: "
    SerialPrintLine rad2deg
    
    ' Full circle in radians
    SerialPrint "Full circle: TAU = "
    SerialPrintLine TAU
    
    ' === Trigonometry with PI ===
    SerialPrintLine vbCrLf & "Trigonometry:"
    
    Dim angle As Double
    angle = PI / 4  ' 45 degrees
    
    SerialPrint "sin(PI/4) = "
    SerialPrintLine Sin(angle)
    
    SerialPrint "cos(PI/4) = "
    SerialPrintLine Cos(angle)
    
    SerialPrint "tan(PI/4) = "
    SerialPrintLine Tan(angle)
    
    ' === INF and NAN ===
    SerialPrintLine vbCrLf & "Special Values:"
    
    Dim infinite As Double
    infinite = INF
    SerialPrint "Infinity: "
    SerialPrintLine infinite
    
    Dim notANumber As Double
    notANumber = NAN
    SerialPrint "Not a Number: "
    SerialPrintLine notANumber
    
    ' === Status Constants (OK/FAILED) ===
    SerialPrintLine vbCrLf & "Function Return Values:"
    
    Dim result As Integer
    result = InitializeSensor()
    
    If result = OK Then
        SerialPrintLine "Sensor initialized successfully!"
    ElseIf result = FAILED Then
        SerialPrintLine "Sensor initialization failed!"
    End If
    
    result = ReadData()
    If result = OK Then
        SerialPrintLine "Data read successfully!"
    Else
        SerialPrintLine "Data read failed!"
    End If
    
    SerialPrintLine vbCrLf & "Setup complete!"
End Sub

Function InitializeSensor() As Integer
    ' Simulate sensor initialization
    Delay 100
    Return OK  ' Success
End Function

Function ReadData() As Integer
    ' Simulate data reading
    If Random(0, 10) > 2 Then
        Return OK  ' Success
    Else
        Return FAILED  ' Failure
    End If
End Function

Sub Loop()
    ' Servo sweep using TAU for smooth motion
    Dim angle As Double
    Dim servoPos As Integer
    
    Dim t As Long
    t = Millis() / 1000.0
    
    ' Smooth sine wave motion using TAU
    angle = Sin((t * TAU) / 4.0)
    servoPos = 90 + (angle * 45)
    
    SerialPrint "Servo angle: "
    SerialPrintLine servoPos
    
    Delay 50
End Sub
