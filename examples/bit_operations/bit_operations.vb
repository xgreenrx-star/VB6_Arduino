' Bit Operations Example
' Demonstrates bitwise operations: BitRead, BitWrite, BitSet, BitClear, BitShift

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "=== Bit Operations Demo ==="
    
    Dim value As Integer
    Dim result As Integer
    Dim bit As Integer
    
    ' Test BitRead
    value = 0b10101010
    bit = BitRead(value, 3)
    SerialPrint "BitRead(0b10101010, 3) = "
    SerialPrintLine bit
    
    ' Test BitSet
    value = 0b10100000
    result = BitSet(value, 3)
    SerialPrint "BitSet(0b10100000, 3) = 0b"
    SerialPrintLine result
    
    ' Test BitClear
    value = 0b10101010
    result = BitClear(value, 1)
    SerialPrint "BitClear(0b10101010, 1) = 0b"
    SerialPrintLine result
    
    ' Test BitWrite
    value = 0b10100000
    result = BitWrite(value, 2, 1)
    SerialPrint "BitWrite(0b10100000, 2, 1) = 0b"
    SerialPrintLine result
    
    ' Test BitShiftLeft (multiply by 2^n)
    value = 5
    result = BitShiftLeft(value, 2)
    SerialPrint "BitShiftLeft(5, 2) = "
    SerialPrintLine result
    
    ' Test BitShiftRight (divide by 2^n)
    value = 20
    result = BitShiftRight(value, 2)
    SerialPrint "BitShiftRight(20, 2) = "
    SerialPrintLine result
    
    ' Practical example: Set individual GPIO configuration bits
    Dim config As Integer
    config = 0b00000000
    
    ' Set configuration bits
    config = BitSet(config, 0)    ' Enable feature 0
    config = BitSet(config, 2)    ' Enable feature 2
    config = BitSet(config, 4)    ' Enable feature 4
    
    SerialPrint "Config with bits 0,2,4 set: 0b"
    SerialPrintLine config
    
    ' Test individual bits
    Dim i As Integer
    For i = 0 To 7
        bit = BitRead(config, i)
        If bit Then
            SerialPrint "Bit "
            SerialPrint i
            SerialPrintLine " is SET"
        End If
    Next i
    
    SerialPrintLine ""
    SerialPrintLine "Setup complete!"
End Sub

Sub Loop()
    Delay 2000
    SerialPrintLine "Loop running..."
End Sub
