' String Manipulation Example
' Demonstrates new string functions: Len, SubString, InStr, StrReplace, Trim, Upper, Lower

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "=== String Manipulation Demo ==="
    
    ' Test Len function
    Dim message As String
    message = "Hello World"
    Dim length As Integer
    length = Len(message)
    SerialPrint "Len(""Hello World"") = "
    SerialPrintLine length
    
    ' Test SubString function
    Dim substring As String
    substring = SubString(message, 0, 5)
    SerialPrint "SubString(""Hello World"", 0, 5) = """
    SerialPrint substring
    SerialPrintLine """"
    
    ' Test InStr function
    Dim position As Integer
    position = InStr(message, "World")
    SerialPrint "InStr(""Hello World"", ""World"") = "
    SerialPrintLine position
    
    ' Test StrReplace function
    Dim replaced As String
    replaced = StrReplace(message, "World", "Arduino")
    SerialPrint "StrReplace(""Hello World"", ""World"", ""Arduino"") = """
    SerialPrint replaced
    SerialPrintLine """"
    
    ' Test Upper and Lower
    Dim uppercase As String
    Dim lowercase As String
    uppercase = Upper(message)
    lowercase = Lower(message)
    SerialPrint "Upper(""Hello World"") = """
    SerialPrint uppercase
    SerialPrintLine """"
    SerialPrint "Lower(""Hello World"") = """
    SerialPrint lowercase
    SerialPrintLine """"
    
    ' Test Trim functions
    Dim padded As String
    padded = "  Trim Me  "
    Dim trimmed As String
    trimmed = Trim(padded)
    SerialPrint "Trim(""  Trim Me  "") = """
    SerialPrint trimmed
    SerialPrintLine """"
    
    SerialPrintLine ""
    SerialPrintLine "Setup complete!"
End Sub

Sub Loop()
    Delay 1000
    SerialPrintLine "Loop running..."
End Sub
