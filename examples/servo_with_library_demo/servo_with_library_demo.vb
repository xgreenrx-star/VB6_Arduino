' Servo with ESP32Servo Library Demo
' Demonstrates actual servo control using writeMicroseconds()

#Include <ESP32Servo.h>

Dim myServo As Servo

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Servo Library Demo" & vbCrLf

    ' Attach servo on GPIO 18 (adjust as needed)
    myServo.attach 18
End Sub

Sub Loop()
    Dim angle As Integer

    ' Sweep 0..180 using default mapping
    For angle = 0 To 180 Step 10
        Dim us As Integer
        us = SERVO_CLAMP_DEG2PULSE(angle)
        myServo.writeMicroseconds us
        SerialPrintLine "Angle=" & angle & ", us=" & us
        Delay 150
    Next angle

    ' Sweep 180..0 using custom range 500..2500us
    For angle = 180 To 0 Step -10
        Dim us2 As Integer
        us2 = SERVO_CLAMP_DEG2PULSE(angle, 500, 2500)
        myServo.writeMicroseconds us2
        SerialPrintLine "Angle=" & angle & ", us2=" & us2
        Delay 150
    Next angle

    Delay 1000
End Sub
