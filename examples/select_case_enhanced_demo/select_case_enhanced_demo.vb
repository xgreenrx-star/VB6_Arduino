' Select Case Enhanced Demo
' Demonstrates range and multiple value support

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Select Case Enhanced Demo" & vbCrLf
    
    ' Test different score values
    TestGrade 95
    TestGrade 85
    TestGrade 75
    TestGrade 65
    TestGrade 50
    
    SerialPrintLine vbCrLf
    
    ' Test day of week
    TestDayType 1
    TestDayType 3
    TestDayType 6
    TestDayType 7
End Sub

Sub TestGrade(score As Integer)
    Dim grade As String
    
    Select Case score
        Case 90 To 100
            grade = "A"
        Case 80 To 89
            grade = "B"
        Case 70 To 79
            grade = "C"
        Case 60 To 69
            grade = "D"
        Case Else
            grade = "F"
    End Select
    
    SerialPrintLine "Score " & score & " = Grade " & grade
End Sub

Sub TestDayType(day As Integer)
    Dim dayType As String
    
    Select Case day
        Case 1, 7
            dayType = "Weekend"
        Case 2, 3, 4, 5, 6
            dayType = "Weekday"
        Case Else
            dayType = "Invalid"
    End Select
    
    SerialPrintLine "Day " & day & " is a " & dayType
End Sub

Sub Loop()
    Delay 5000
End Sub
