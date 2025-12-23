' Auto-completion Demo
' Try typing any of these prefixes to see suggestions:
' - "Di" for Dim, DigitalWrite, DigitalRead
' - "Se" for SerialBegin, SerialPrint, etc.
' - "PI" for PinMode
' - "Del" for Delay, DelayMicroseconds
' - Variable names like "ledPin" or "buttonState"
' - Function names like "BlinkLED" or "ReadButton"

Const ledPin As Integer = 2
Const buttonPin As Integer = 4
Dim buttonState As Boolean
Dim counter As Integer

Sub Setup()
    PinMode ledPin, OUTPUT
    PinMode buttonPin, INPUT_PULLUP
    SerialBegin 115200
    counter = 0
    SerialPrintLine "System started"
End Sub

Sub Loop()
    ReadButton()
    If buttonState Then
        BlinkLED()
        IncrementCounter()
    End If
    Delay 100
End Sub

Sub ReadButton()
    buttonState = DigitalRead(buttonPin)
End Sub

Sub BlinkLED()
    DigitalWrite ledPin, HIGH
    Delay 200
    DigitalWrite ledPin, LOW
End Sub

Sub IncrementCounter()
    counter = counter + 1
    SerialPrint "Count: "
    SerialPrintLine counter
End Sub

Function GetCounter() As Integer
    Return counter
End Function
