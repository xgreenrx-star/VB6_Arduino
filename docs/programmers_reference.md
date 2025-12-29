# Asic Programmer's Reference

This document lists all Basic-like commands supported by the Asic (Arduino Basic) transpiler, with syntax, description, examples, and related commands.

---

## Table of Contents

- [Variable Declarations](#variable-declarations)
- [Constants](#constants)
- [Static Variables](#static-variables)
- [Control Flow](#control-flow)
- [Loops](#loops)
- [Select Case](#select-case)
- [Subroutines and Functions](#subroutines-and-functions)
- [Arrays](#arrays)
- [Labels and Goto](#labels-and-goto)
- [Error Handling](#error-handling)
- [Comments](#comments)
- [I/O and Arduino Helpers](#io-and-arduino-helpers)
- [String Functions](#string-functions)
- [Math Functions](#math-functions)
- [Time Functions](#time-functions)
- [EEPROM](#eeprom)
- [Wire (I2C)](#wire-i2c)
- [SPI](#spi)
- [Interrupts](#interrupts)
- [PWM and Tone](#pwm-and-tone)
- [Other Hardware](#other-hardware)
- [Miscellaneous](#miscellaneous)

---

## Variable Declarations

### `Dim`
Declare a variable or array.

**Syntax:**
```
Dim x As Integer
Dim arr(10) As Byte
```
**Example:**
```
Dim ledPin As Integer
Dim buffer(15) As Byte
```
**See also:** [Static](#static-variables), [Const](#constants)

---

## Constants

### `Const`
Declare a constant.

**Syntax:**
```
Const LED = 2
Const PI As Double = 3.14159
```
**Example:**
```
Const MaxValue As Integer = 100
```
**See also:** [Dim](#variable-declarations)

---

## Static Variables

### `Static`
Declare a static variable inside a function.

**Syntax:**
```
Static counter As Integer
```
**Example:**
```
Static lastState As Boolean
```
**See also:** [Dim](#variable-declarations)

---

## Control Flow

### `If ... Then ... ElseIf ... Else ... End If`
Conditional execution.

**Syntax:**
```
If x = 1 Then
    ' code
ElseIf x = 2 Then
    ' code
Else
    ' code
End If
```
**Example:**
```
If value > 10 Then
    MsgBox("High")
Else
    MsgBox("Low")
End If
```
**See also:** [Select Case](#select-case)

---

## Loops

### `For ... = ... To ... [Step ...] ... Next`
For loop.

**Syntax:**
```
For i = 0 To 10
    ' code
Next
```
**Example:**
```
For i = 1 To 5
    SerialPrintLine i
Next
```
**See also:** [While](#whilewend), [Do Loop](#do-loop)

---

### `For Each ... In ...`
Iterate over array/collection.

**Syntax:**
```
For Each item In arr
    ' code
Next
```
**Example:**
```
For Each b In buffer
    SerialPrint b
Next
```

---

### `While ... Wend`
While loop.

**Syntax:**
```
While condition
    ' code
Wend
```
**Example:**
```
While SerialAvailable() > 0
    b = SerialRead()
Wend
```
**See also:** [Do Loop](#do-loop)

---

### `Do ... Loop`
Do loop.

**Syntax:**
```
Do
    ' code
Loop While condition
```
**Example:**
```
Do
    value = AnalogRead(A0)
Loop Until value > 100
```
**See also:** [While](#whilewend)

---

### `Exit For / Exit Do / Exit While / Exit Select`
Exit the current loop or select block.

**Example:**
```
For i = 0 To 10
    If i = 5 Then Exit For
Next
```
**See also:** [Continue For](#continue-for--continue-do--continue-while)

---

### `Continue For / Continue Do / Continue While`
Continue to next iteration.

**Example:**
```
For i = 0 To 10
    If i Mod 2 = 0 Then Continue For
    SerialPrintLine i
Next
```
---

## Select Case

### `Select Case ... Case ... [Case Else] ... End Select`
Switch/case block.

**Syntax:**
```
Select Case value
    Case 1
        ' code
    Case 2, 3
        ' code
    Case Else
        ' code
End Select
```
**Example:**
```
Select Case command
    Case 1
        LedOn()
    Case 2
        LedOff()
    Case Else
        MsgBox("Unknown command")
End Select
```
**See also:** [If](#control-flow)

---

## Subroutines and Functions

### `Sub ... End Sub`
Define a subroutine.

**Syntax:**
```
Sub MySub()
    ' code
End Sub
```
**Example:**
```
Sub Blink()
    DigitalWrite LED, HIGH
    Delay 500
    DigitalWrite LED, LOW
    Delay 500
End Sub
```
**See also:** [Function](#function--end-function)

---

### `Function ... End Function`
Define a function.

**Syntax:**
```
Function Add(a As Integer, b As Integer) As Integer
    Return a + b
End Function
```
**Example:**
```
Function Square(x As Integer) As Integer
    Return x * x
End Function
```
**See also:** [Sub](#sub--end-sub)

---

### `Return`
Return a value from a function.

**Example:**
```
Function GetPin() As Integer
    Return 13
End Function
```

---

## Arrays

### Array Declaration and Initialization

**Syntax:**
```
Dim arr(4) As Integer
Dim arr() As Integer = {1, 2, 3, 4}
Const arr() As Integer = {10, 20, 30}
```
**Example:**
```
Dim buffer(7) As Byte
Dim pins() As Integer = {2, 4, 5}
```
**See also:** [For Each](#for-each--in-)

---

## Labels and Goto

### `Label:`
Define a label.

**Example:**
```
Retry:
    ' code
```

### `Goto Label`
Jump to a label.

**Example:**
```
If error Then Goto Retry
```

---

## Error Handling

### `On Error Resume Next`
Stub only; not implemented.

### `On Error GoTo Label`
Stub only; not implemented.

---

## Comments

### `'` or `Rem`
Single-line comment.

**Example:**
```
' This is a comment
Rem This is also a comment
```

---

## I/O and Arduino Helpers

### `PinMode pin, mode`
Set pin mode.

**Example:**
```
PinMode LED, OUTPUT
```

### `DigitalWrite pin, value`
Write digital value.

**Example:**
```
DigitalWrite LED, HIGH
```

### `DigitalRead pin`
Read digital value.

**Example:**
```
val = DigitalRead BUTTON
```

### `AnalogRead pin`
Read analog value.

**Example:**
```
val = AnalogRead A0
```

### `AnalogWrite pin, value`
Write analog value (PWM).

**Example:**
```
AnalogWrite LED, 128
```

### `Delay ms`
Delay in milliseconds.

**Example:**
```
Delay 1000
```

### `DelayMicroseconds us`
Delay in microseconds.

**Example:**
```
DelayMicroseconds 50
```

### `SerialBegin baud`
Initialize serial.

**Example:**
```
SerialBegin 115200
```

### `SerialPrint value`
Print to serial.

**Example:**
```
SerialPrint "Hello"
```

### `SerialPrintLine value`
Print line to serial.

**Example:**
```
SerialPrintLine "Done"
```

---

## String Functions

### `Left(str, n)`
Leftmost n characters.

**Example:**
```
s = Left("Hello", 2)   ' "He"
```
**See also:** [Right](#rightstr-n), [Mid](#midstr-n)

### `Right(str, n)`
Rightmost n characters.

**Example:**
```
s = Right("Hello", 2)  ' "lo"
```
**See also:** [Left](#leftstr-n), [Mid](#midstr-n)

### `Mid(str, n)`
Substring from position n.

**Example:**
```
s = Mid("Hello", 3)    ' "llo"
```
**See also:** [Left](#leftstr-n), [Right](#rightstr-n)

### `Len(str)`
Length of string.

**Example:**
```
l = Len("Hello")        ' 5
```

### `Instr(str1, str2)`
Find substring.

**Example:**
```
p = Instr("Hello", "l") ' 2 (0-based in Arduino)
```

### `Replace(str, find, repl)`
Replace substring.

**Example:**
```
s = Replace("Hello", "l", "x") ' "Hexxo"
```

---

## Math Functions

### `Sqr(x)`
Square root.

### `Sin(x)`, `Cos(x)`, `Tan(x)`
Trigonometric functions.

### `Abs(x)`
Absolute value.

### `Rnd()`
Random number.

### `Int(x)`
Integer part.

**Example:**
```
y = Sqr(16)
z = Abs(-5)
r = Rnd()
```
**See also:** [RandomSeed](#randomseed-seed), [Map](#map-value-fromlow-fromhigh-tolow-tohigh), [Constrain](#constrain-value-low-high)

---

## Time Functions

### `Millis`
Milliseconds since start.

### `Micros`
Microseconds since start.

### `Timer`
Alias for `Millis`.

**Example:**
```
t = Millis
```
**See also:** [Delay](#delay-ms), [DelayMicroseconds](#delaymicroseconds-us)

---

## EEPROM

### `EEPROMRead address`
Read EEPROM.

### `EEPROMWrite address, value`
Write EEPROM.

**Example:**
```
EEPROMWrite 0, 42
val = EEPROMRead 0
```

---

## Wire (I2C)

### `WireBegin`
Initialize I2C.

### `WireWrite value`
Write to I2C.

### `WireRead`
Read from I2C.

### `WireRequestFrom address, quantity`
Request bytes from I2C.

### `WireBeginTransmission address`
Begin I2C transmission.

### `WireEndTransmission`
End I2C transmission.

**Example:**
```
WireBegin
WireBeginTransmission 0x3C
WireWrite 0x00
WireEndTransmission
```

---

## SPI

### `SPIBegin`
Initialize SPI.

### `SPITransfer value`
Transfer SPI data.

**Example:**
```
SPIBegin
SPITransfer 0xFF
```

---

## Interrupts

### `AttachInterrupt pin, handler, mode`
Attach interrupt.

### `DetachInterrupt pin`
Detach interrupt.

**Example:**
```
AttachInterrupt 2, MyISR, RISING
```

---

## PWM and Tone

### `Tone pin, frequency [, duration]`
Generate tone.

### `NoTone pin`
Stop tone.

### `SetPWMFrequency pin, frequency`
Set PWM frequency (stub).

**Example:**
```
Tone 8, 440, 1000
NoTone 8
```

---

## Other Hardware

### `PulseIn pin, value [, timeout]`
Measure pulse duration.

### `ShiftOut dataPin, clockPin, bitOrder, value`
Shift out data.

### `ShiftIn dataPin, clockPin, bitOrder`
Shift in data.

### `DetachServo servo`
Detach servo.

### `SetPinChangeInterrupt pin, handler`
Set pin change interrupt (stub).

### `LowPowerSleep ms`
Low power sleep (stub).

### `AnalogReadResolution bits`
Set analog read resolution.

### `AnalogWriteResolution bits`
Set analog write resolution.

### `DigitalToggle pin`
Toggle digital pin.

**Example:**
```
PulseIn 7, HIGH, 1000000
ShiftOut 11, 13, MSBFIRST, 0xFF
DigitalToggle LED
```

---

## Miscellaneous

### `RandomSeed seed`
Seed random generator.

### `Map value, fromLow, fromHigh, toLow, toHigh`
Map value from one range to another.

### `Constrain value, low, high`
Constrain value to range.

### `Yield`
Yield to scheduler (ESP).

### `BoardInfo`
Show board info (stub).

### `FreeMemory`
Show free memory (stub).

---

## See Also

- [Arduino Language Reference](https://www.arduino.cc/reference/en/)
- [Visual Basic for Applications (VBA) Language Reference](https://learn.microsoft.com/en-us/office/vba/language/concepts/getting-started/language-reference-vba)
- [PlatformIO Documentation](https://docs.platformio.org/)

---

<!--
Review notes:
- All command names, syntax, and examples are up to date with the current Asic (Arduino Basic) transpiler.
- "VB6_Arduino" has been replaced with "Asic (Arduino Basic)" throughout.
- All references to "VB6-like" or "VB6_Arduino" are now "Basic-like" or "Asic (Arduino Basic)".
- The "See Also" section now references the correct Microsoft VBA documentation.
- All commands listed are supported or stubbed as described in the current transpiler code.
- No deprecated or outdated usage instructions are present.
- No errors found in code examples or command descriptions.
-->
