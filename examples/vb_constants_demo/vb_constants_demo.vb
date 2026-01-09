' VB6 Built-in Constants Demo
' Demonstrates string constants and boolean constants

Sub Setup()
    SerialBegin 115200
    
    ' === String Constants ===
    SerialPrint "Line 1" & vbCrLf
    SerialPrint "Line 2" & vbCrLf & vbCrLf
    
    ' Tab-separated values
    SerialPrint "Name:" & vbTab & "John" & vbCrLf
    SerialPrint "Age:" & vbTab & "25" & vbCrLf
    SerialPrint "City:" & vbTab & "Boston" & vbCrLf
    
    ' Just carriage return (useful for progress indicators)
    SerialPrint "Loading" & vbCr
    Delay 1000
    SerialPrint "Complete!" & vbCrLf
    
    ' Line feed only (Unix-style)
    SerialPrint "Unix-style" & vbLf & "line breaks" & vbLf
    
    ' Null-terminated strings
    SerialPrint "C-style" & vbNullChar & "string" & vbCrLf
    
    ' Empty string
    Dim msg As String
    msg = vbNullString
    If msg = vbNullString Then
        SerialPrintLine "String is empty"
    End If
    
    ' === Boolean Constants ===
    Dim ready As Boolean
    Dim done As Boolean
    
    ready = vbTrue
    done = vbFalse
    
    If ready = vbTrue Then
        SerialPrintLine "System ready!"
    End If
    
    If done = vbFalse Then
        SerialPrintLine "Processing..."
    End If
    
    ' === Practical Example: CSV Output ===
    SerialPrintLine vbCrLf & "CSV Data:"
    SerialPrint "Sensor,Value,Status" & vbCrLf
    SerialPrint "Temp" & vbTab & "25.5" & vbTab & "OK" & vbCrLf
    SerialPrint "Humidity" & vbTab & "60" & vbTab & "OK" & vbCrLf
    SerialPrint "Pressure" & vbTab & "1013" & vbTab & "OK" & vbCrLf
    
    SerialPrintLine vbCrLf & "Setup complete!"
End Sub

Sub Loop()
    ' Progress indicator using carriage return
    Dim i As Integer
    For i = 0 To 100 Step 10
        SerialPrint "Progress: " & i & "%" & vbCr
        Delay 200
    Next i
    SerialPrintLine vbCrLf & "Done!"
    Delay 2000
End Sub
