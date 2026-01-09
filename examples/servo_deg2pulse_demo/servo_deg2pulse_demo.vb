' Servo DEG2PULSE Demo
' Sweeps 0..180 degrees and prints pulse widths

' Optional: Use a servo library if available
' #Include <ESP32Servo.h>
' Dim myServo As Servo

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Servo DEG2PULSE Demo" & vbCrLf
    
    ' If using a servo library, uncomment and attach here
    ' myServo.attach 18  ' GPIO pin for servo signal
End Sub

Sub Loop()
    Dim angle As Integer
    
    ' Sweep forward 0..180
    For angle = 0 To 180 Step 15
        Dim us As Integer
        us = SERVO_DEG2PULSE(angle)  ' default 1000..2000us
        SerialPrint "Angle=" & angle & " deg, Pulse=" & us & " us" & vbCrLf
        ' If using library: myServo.writeMicroseconds us
        Delay 150
    Next angle
    
    ' Sweep backward 180..0 with custom range 500..2500us
    For angle = 180 To 0 Step -15
        Dim us2 As Integer
        us2 = SERVO_DEG2PULSE(angle, 500, 2500)  ' custom range
        SerialPrint "Angle=" & angle & " deg, Pulse=" & us2 & " us (custom)" & vbCrLf
        ' If using library: myServo.writeMicroseconds us2
        Delay 150
    Next angle
    
    Delay 1000
End Sub
