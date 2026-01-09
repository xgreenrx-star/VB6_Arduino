' VB6-Style Enhancements Demo
' Demonstrates IIf, type conversions, DoEvents, and string functions

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "VB6 Enhancements Demo" & vbCrLf
    
    ' === IIf() - Inline If ===
    Dim age As Integer
    age = 25
    Dim status As String
    status = IIf(age >= 18, "Adult", "Minor")
    SerialPrintLine "Age: " & age & " is " & status
    
    Dim score As Integer
    score = 85
    SerialPrintLine "Grade: " & IIf(score >= 90, "A", IIf(score >= 80, "B", "C"))
    
    ' === Type Conversion Functions ===
    SerialPrintLine vbCrLf & "Type Conversions:"
    
    Dim num As Integer
    num = 42
    Dim s As String
    s = CStr(num)
    SerialPrintLine "CStr(42) = " & s
    
    Dim str As String
    str = "123"
    Dim i As Integer
    i = CInt(str)
    SerialPrintLine "CInt(" & Chr(34) & "123" & Chr(34) & ") = " & i
    
    Dim d As Double
    d = CDbl("3.14159")
    SerialPrintLine "CDbl(3.14159) = " & d
    
    Dim b As Byte
    b = CByte(255)
    SerialPrintLine "CByte(255) = " & b
    
    ' === String Functions ===
    SerialPrintLine vbCrLf & "String Functions:"
    
    Dim spaces As String
    spaces = Space(5)
    SerialPrintLine "Space(5) = [" & spaces & "]"
    
    Dim stars As String
    stars = String(10, "*")
    SerialPrintLine "String(10, *) = " & stars
    
    ' === Type Checking ===
    SerialPrintLine vbCrLf & "Type Checking:"
    
    Dim test1 As String
    test1 = "456"
    If IsNumeric(test1) Then
        SerialPrintLine test1 & " is numeric"
    End If
    
    Dim test2 As String
    test2 = "abc"
    If Not IsNumeric(test2) Then
        SerialPrintLine test2 & " is not numeric"
    End If
    
    Dim empty As String
    empty = ""
    If IsEmpty(empty) Then
        SerialPrintLine "String is empty"
    End If
    
    ' === Memory Diagnostics ===
    SerialPrintLine vbCrLf & "Free RAM: " & FreeRAM() & " bytes"
    
    SerialPrintLine vbCrLf & "Setup complete!"
End Sub

Sub Loop()
    Dim i As Integer
    For i = 1 To 5
        SerialPrint "Processing " & i & "..."
        DoEvents  ' Yield to other tasks
        Delay 100
        SerialPrintLine "done"
    Next i
    
    Delay 2000
End Sub
