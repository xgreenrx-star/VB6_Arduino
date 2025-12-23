' Test file demonstrating procedure dropdown
' This file has multiple Subs and Functions

Const LED As Integer = 2
Dim counter As Integer

Sub Setup()
    ' Initialize the board
    PinMode LED, OUTPUT
    SerialBegin 115200
    counter = 0
End Sub

Sub Loop()
    ' Main loop
    BlinkLED()
    PrintCounter()
    Delay 1000
End Sub

Sub BlinkLED()
    ' Blink the LED once
    DigitalWrite LED, HIGH
    Delay 100
    DigitalWrite LED, LOW
End Sub

Sub PrintCounter()
    ' Print the counter value
    SerialPrint "Counter: "
    SerialPrintLine counter
    counter = counter + 1
End Sub

Function CalculateSum(a As Integer, b As Integer) As Integer
    ' Calculate and return the sum
    Return a + b
End Function

Function GetLEDPin() As Integer
    ' Return the LED pin number
    Return LED
End Function

Sub ResetCounter()
    ' Reset the counter to zero
    counter = 0
    SerialPrintLine "Counter reset"
End Sub
