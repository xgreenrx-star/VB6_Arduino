
# Asic (Arduino Basic) Programmer's Reference


This document lists all Basic-like commands supported by the Asic (Arduino Basic) transpiler and IDE, with syntax, description, examples, and related commands.

---

## About Asic (Arduino Basic)

Asic (Arduino Basic) is a modern, VB6-inspired language and IDE for Arduino and ESP32 development. It features a Visual Basic-like syntax, a graphical IDE, and seamless integration with PlatformIO for building and uploading code. Macro commands for keyboard automation and delays are supported in the IDE and transpiler.

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

### Built-in VB6 Constants

Asic supports these VB6-style built-in constants for string manipulation and boolean values:

#### String Constants
- **`vbCr`** - Carriage return (`"\r"`)
- **`vbLf`** - Line feed (`"\n"`)
- **`vbCrLf`** - Carriage return + line feed (`"\r\n"`)
- **`vbTab`** - Tab character (`"\t"`)
- **`vbNullChar`** - Null character (`"\0"`)
- **`vbNullString`** - Empty string (`""`)

#### Boolean Constants
- **`vbTrue`** - Boolean true (`true`)
- **`vbFalse`** - Boolean false (`false`)

**Examples:**
```vb
' Print with line endings
SerialPrint "Line 1" & vbCrLf
SerialPrint "Line 2" & vbLf

' Tab-separated values
SerialPrint "Name:" & vbTab & "John" & vbCrLf

' Progress indicator with carriage return
SerialPrint "Loading..." & vbCr
Delay 1000
SerialPrint "Complete!" & vbCrLf

' Boolean comparisons
Dim ready As Boolean
ready = vbTrue
If ready = vbTrue Then
    SerialPrintLine "Ready!"
End If
```

**See also:** [SerialPrint](#serialprint), [SerialPrintLine](#serialprintline)

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

### Math/Status Constants

Asic also provides a set of math and status constants (inspired by GDScript) for convenience:

- PI: Circle ratio constant (from Arduino core)
- TAU: Full circle in radians, equals 2×PI
- DEG2RAD: Degrees to radians conversion factor (PI / 180.0)
- RAD2DEG: Radians to degrees conversion factor (180.0 / PI)
- INF: Positive infinity
- NAN: Not-a-Number
- OK: Success code (0)
- FAILED: Failure code (-1)

Examples:
```vb
Dim d As Double, r As Double
d = 90
r = d * DEG2RAD   ' radians

Dim d2 As Double
d2 = r * RAD2DEG  ' back to degrees

If Initialize() = OK Then
    SerialPrintLine "Initialized"
Else
    SerialPrintLine "Init failed"
End If
```

### Servo Helpers

Convert a servo angle (degrees) into microsecond pulse width for typical 50Hz servos.

- `SERVO_DEG2PULSE(angle)`: maps 0..180° to 1000..2000 µs.
- `SERVO_DEG2PULSE(angle, minUS, maxUS)`: maps 0..180° to custom range.

- `SERVO_CLAMP(angle)`: clamps an angle into 0..180°.

- `SERVO_CLAMP_DEG2PULSE(angle[, minUS, maxUS])`: convenience combining clamp and mapping. Defaults to 1000..2000 µs.
' Convenience: clamp + map in one call
Dim p As Integer
p = SERVO_CLAMP_DEG2PULSE(angle)
Dim p2 As Integer
p2 = SERVO_CLAMP_DEG2PULSE(angle, 500, 2500)

Examples:
```vb
' Default 1000..2000us
Dim angle As Integer
angle = 90
Dim pulse As Integer
pulse = SERVO_DEG2PULSE(angle)
SerialPrintLine "Pulse=" & pulse & " us"

' Custom range 500..2500us
Dim pulse2 As Integer
pulse2 = SERVO_DEG2PULSE(angle, 500, 2500)
SerialPrintLine "Pulse2=" & pulse2 & " us"

' Clamp before using
angle = SERVO_CLAMP(angle)
```

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

> Enhancements: supports `Case 1 To 10` (range expands to multiple cases) and comma-separated values in one case. Breaks are emitted automatically (no fall-through).

### `Choose(index, v1, v2, ...)`
1-based value selection. Example: `day = Choose(3, "Mon", "Tue", "Wed")` → `"Wed"`.

### `Switch(c1, v1, c2, v2, ..., True, vDefault)`
Evaluates condition/value pairs in order and returns the first matching value; use `True` as final catch-all.

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

### Optional Parameters and ByRef
Functions and subs support `Optional` parameters with default values and either `ByVal` (default) or `ByRef` semantics.

**Syntax:**
```
Sub Drive(pin As Integer, Optional level As Integer = 1)
    ' level defaults to 1 if omitted
End Sub

Sub Scale(ByRef value As Integer, ByVal factor As Integer)
    value = value * factor
End Sub
```
**Notes:**
- `ByVal` is the default when not specified.
- `ByRef` lets the callee modify the caller's variable.
- Optional parameters must follow required parameters and have a default.

---

### `With ... End With`
Evaluate an expression once and use it as a prefix for multiple member accesses or calls.

**Example:**
```
With device
    .Begin()
    .Write(42)
    .End()
End With
```
**Notes:**
- The `With` target expression is evaluated a single time.
- Each dotted access inside the block uses that cached target.

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

## Unified Graphics Commands

**Library-Agnostic Drawing API** — Write once, works with any graphics library! Just like VB6's Form.Line() and PictureBox.Circle() worked everywhere, these commands automatically adapt to whichever display library you include.

**Supported Libraries:**
- ✅ **TFT_eSPI** (ESP32 TFT displays)
- ✅ **Adafruit_GFX** (SSD1306 OLED, ST7735, ILI9341, etc.)
- ✅ **U8g2** (Monochrome OLED/LCD displays)
- ⏳ **LVGL** (UI framework - coming soon)

**Library Auto-Detection:** The transpiler detects which library you include and generates the correct code automatically!

### Basic Drawing

### `DrawLine x1, y1, x2, y2, color`
Draw a line between two points.

**Example:**
```vb
DrawLine 10, 20, 100, 200, TFT_WHITE
```

**Works with:** All libraries (U8g2 ignores color parameter)

### `DrawRect x, y, width, height, color`
Draw a rectangle outline.

**Example:**
```vb
DrawRect 10, 10, 80, 60, TFT_RED
```

**See also:** [FillRect](#fillrect-x-y-width-height-color)

### `FillRect x, y, width, height, color`
Draw a filled rectangle.

**Example:**
```vb
FillRect 10, 10, 80, 60, TFT_BLUE
```

**See also:** [DrawRect](#drawrect-x-y-width-height-color)

### `DrawCircle x, y, radius, color`
Draw a circle outline.

**Example:**
```vb
DrawCircle 160, 120, 50, TFT_GREEN
```

**See also:** [FillCircle](#fillcircle-x-y-radius-color)

### `FillCircle x, y, radius, color`
Draw a filled circle.

**Example:**
```vb
FillCircle 160, 120, 50, TFT_YELLOW
```

**See also:** [DrawCircle](#drawcircle-x-y-radius-color)

### `DrawTriangle x1, y1, x2, y2, x3, y3, color`
Draw a triangle outline.

**Example:**
```vb
DrawTriangle 50, 100, 100, 50, 150, 100, TFT_CYAN
```

**See also:** [FillTriangle](#filltriangle-x1-y1-x2-y2-x3-y3-color)

### `FillTriangle x1, y1, x2, y2, x3, y3, color`
Draw a filled triangle.

**Example:**
```vb
FillTriangle 50, 100, 100, 50, 150, 100, TFT_MAGENTA
```

**See also:** [DrawTriangle](#drawtriangle-x1-y1-x2-y2-x3-y3-color)

### `DrawPixel x, y, color`
Draw a single pixel.

**Example:**
```vb
DrawPixel 100, 100, TFT_WHITE
```

### Text Operations

### `FillScreen color`
Fill entire screen with a color.

**Example:**
```vb
FillScreen TFT_BLACK
```

**See also:** [ClearDisplay](#cleardisplay)

### `ClearDisplay`
Clear the display (library-specific implementation).

**Example:**
```vb
ClearDisplay
```

**Note:** 
- TFT_eSPI: Fills with `TFT_BLACK`
- Adafruit_GFX: Calls `clearDisplay()`
- U8g2: Calls `clearBuffer()`

**See also:** [FillScreen](#fillscreen-color)

### `SetTextSize size`
Set text size (1 = normal, 2 = 2x, etc.).

**Example:**
```vb
SetTextSize 2
```

### `SetTextColor foreground, background`
Set text colors.

**Example:**
```vb
SetTextColor TFT_WHITE, TFT_BLACK
```

**Overload:** `SetTextColor color` (single parameter for transparent background)

### `SetCursor x, y`
Set cursor position for text.

**Example:**
```vb
SetCursor 10, 20
```

### `PrintText text`
Print text at current cursor position.

**Example:**
```vb
PrintText "Hello"
```

**See also:** [PrintLine](#printline-text)

### `PrintLine text`
Print text with newline.

**Example:**
```vb
SetCursor 10, 20
PrintLine "Hello World!"
PrintLine "Second line"
```

**See also:** [PrintText](#printtext-text)

### Example: Universal Graphics Code

```vb
' Works with ANY graphics library!
#Include <TFT_eSPI.h>  ' Or Adafruit_GFX.h, or U8g2lib.h

Sub Setup()
    SerialBegin 115200
    tft.init  ' Or display.begin(), or u8g2.begin()
    
    ' Same code works everywhere!
    FillScreen TFT_BLACK
    DrawLine 0, 0, 100, 100, TFT_WHITE
    DrawRect 20, 20, 80, 60, TFT_RED
    FillCircle 160, 120, 40, TFT_BLUE
    
    SetTextSize 2
    SetCursor 10, 200
    PrintLine "Universal API!"
End Sub
```

**See also:** [TFT Display - Window Management](#tft-display---window-management) for advanced window/viewport commands.

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

---

## Macro Commands (Keyboard/Automation)

Asic (Arduino Basic) supports macro commands for keyboard automation, including key presses and delays. Use these in macro strings or automation routines:

- `{{KEY:KEYNAME}}` — Send a keyboard key (e.g., `{{KEY:SPACE}}`, `{{KEY:RIGHT}}`)
- `{{DELAY:ms}}` — Delay for the specified milliseconds (e.g., `{{DELAY:500}}`)

**Example:**
```
{{KEY:SPACE}}{{DELAY:500}}{{KEY:RIGHT}}
```

This sends a space, waits 500 ms, then sends a right arrow key.

**Note:** Macro commands use double curly braces and a colon, and are case-insensitive. See the IDE's Help menu for a full list of supported keys.

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

### `SubString(str, start, length)`
Extract substring by position and length.

**Syntax:**
```
SubString(string, start_pos, length)
```

**Example:**
```
s = SubString("Hello World", 0, 5)  ' "Hello"
```
**See also:** [Left](#leftstr-n), [Right](#rightstr-n), [Mid](#midstr-n)

### `Trim(str)`
Remove leading and trailing whitespace.

**Example:**
```
s = Trim("  Hello  ")  ' "Hello"
```
**See also:** [LTrim](#ltrimstr), [RTrim](#rtrimstr)

### `LTrim(str)`
Remove leading whitespace.

**Example:**
```
s = LTrim("  Hello")  ' "Hello"
```
**See also:** [Trim](#trimstr), [RTrim](#rtrimstr)

### `RTrim(str)`
Remove trailing whitespace.

**Example:**
```
s = RTrim("Hello  ")  ' "Hello"
```
**See also:** [Trim](#trimstr), [LTrim](#ltrimstr)

### `StrReplace(str, find, replace)`
Replace all occurrences of a substring.

**Example:**
```
s = StrReplace("banana", "ana", "XXX")  ' "bXXXna"
```
**See also:** [Replace](#replacestr-find-repl)

### `Upper(str)`
Convert string to uppercase.

**Example:**
```
s = Upper("hello")  ' "HELLO"
```
**See also:** [Lower](#lowerstr)

### `Lower(str)`
Convert string to lowercase.

**Example:**
```
s = Lower("HELLO")  ' "hello"
```
**See also:** [Upper](#upperstr)

### `InStrRev(str, find)`
Find substring from the end (1-based result). Uses `String.lastIndexOf`.

### `StrComp(a, b)`
String comparison result (-1, 0, 1) using `String.compareTo`.

### `StrReverse(str)`
Reverse a string (helper emitted into generated code).

### `Split(str, delimiter)`
Splits into `std::vector<String>` using a runtime helper; works with `For Each`.

### `Join(list, delimiter)`
Concatenates `std::vector<String>` into a `String`.

### `Filter(list, match)`
Returns a filtered `std::vector<String>` containing elements that include `match`.

> Runtime note: Split/Join/Filter emit helper functions and include `<vector>`. Use `For Each` or `parts.size()` to iterate; `UBound/LBound` are not supported on these vectors.

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

### `Round(x)`
Round to nearest integer.

### `Fix(x)`
Truncate toward zero.

### `Sgn(x)`
Sign function (-1, 0, 1).

### `Log(x)`, `Exp(x)`, `Atn(x)`
Natural log, exponential, arctangent.

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
Alias for `Millis` (returns milliseconds).

### `Randomize [seed]`
Seeds the random generator (maps to `randomSeed()`). If no seed is given, uses `millis()`.

**Example:**
```
Randomize        ' seed with millis()
Randomize 12345  ' deterministic seed
t = Timer
```
**See also:** [Delay](#delay-ms), [DelayMicroseconds](#delaymicroseconds-us), [Rnd](#rnd)

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

## Bit Operations

Bitwise operations for efficient register and flag manipulation.

### `BitRead(value, bit)`
Read a single bit from a value.

**Syntax:**
```
BitRead(value, bit_position)
```

**Example:**
```
bit = BitRead(0b10101010, 3)  ' Read bit 3 (returns 1)
```
**See also:** [BitWrite](#bitwritevalue-bit-state), [BitSet](#bitsetvalue-bit)

### `BitWrite(value, bit, state)`
Write (set or clear) a single bit.

**Syntax:**
```
BitWrite(value, bit_position, state)
```

**Example:**
```
val = BitWrite(0b10100000, 2, 1)  ' Set bit 2 to 1
```
**See also:** [BitRead](#bitreadvalue-bit), [BitSet](#bitsetvalue-bit), [BitClear](#bitcoldvalue-bit)

### `BitSet(value, bit)`
Set a bit to 1.

**Example:**
```
val = BitSet(0b10100000, 3)  ' Result: 0b10101000
```
**See also:** [BitClear](#bitcoldvalue-bit), [BitWrite](#bitwritevalue-bit-state)

### `BitClear(value, bit)`
Clear a bit (set to 0).

**Example:**
```
val = BitClear(0b10101010, 1)  ' Result: 0b10101000
```
**See also:** [BitSet](#bitsetvalue-bit), [BitWrite](#bitwritevalue-bit-state)

### `BitShiftLeft(value, count)`
Shift bits left (multiply by 2^count).

**Example:**
```
val = BitShiftLeft(5, 2)  ' 5 << 2 = 20
```
**See also:** [BitShiftRight](#bitshiftrightvalue-count)

### `BitShiftRight(value, count)`
Shift bits right (divide by 2^count).

**Example:**
```
val = BitShiftRight(20, 2)  ' 20 >> 2 = 5
```
**See also:** [BitShiftLeft](#bitshiftleftvalue-count)

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

## TFT Display - Window Management

Window and viewport functions for efficient partial screen updates with TFT_eSPI displays. These allow you to constrain drawing operations to specific screen regions, similar to VB6's PictureBox clipping regions.

### `SetWindow x1, y1, x2, y2`
Define a drawing window using **start and end coordinates**. All subsequent pixel push operations write to this window.

**Syntax:**
```
SetWindow start_x, start_y, end_x, end_y
```

**Example:**
```
' Set window to top-left quadrant
SetWindow 0, 0, 159, 119

' Now push pixels rapidly to this region
For i = 0 To 19199
    PushPixel TFT_BLUE
Next i
```

**See also:** [SetAddrWindow](#setaddrwindow-x-y-w-h), [PushPixel](#pushpixel-color)

### `SetAddrWindow x, y, w, h`
Define a drawing window using **start coordinates + width and height**.

**Syntax:**
```
SetAddrWindow start_x, start_y, width, height
```

**Example:**
```
' Set 100x50 window at position (20, 30)
SetAddrWindow 20, 30, 100, 50

' Fill with red pixels
PushBlock TFT_RED, 5000  ' 100 * 50 pixels
```

**See also:** [SetWindow](#setwindow-x1-y1-x2-y2), [PushBlock](#pushblock-color-count)

### `SetViewport x, y, w, h`
Define a viewport (constrained drawing area). All drawing commands are clipped to this region.

**Syntax:**
```
SetViewport x, y, width, height
```

**Example:**
```
' Create a 200x100 viewport at (10, 10)
SetViewport 10, 10, 200, 100

' All drawing clipped to this area
tft.fillCircle 50, 50, 60, TFT_GREEN  ' Clipped to viewport
```

**Note:** Similar to VB6's `ScaleMode` and clipping regions.

**See also:** [ResetViewport](#resetviewport), [FrameViewport](#frameviewport-color-width)

### `ResetViewport`
Reset the viewport to the full screen.

**Example:**
```
SetViewport 0, 0, 100, 100  ' Small viewport
' ... draw clipped graphics ...
ResetViewport               ' Back to full screen
```

**See also:** [SetViewport](#setviewport-x-y-w-h)

### `FrameViewport color, width`
Draw a frame (border) around the current viewport.

**Syntax:**
```
FrameViewport color, border_width
```

**Example:**
```
SetViewport 10, 10, 200, 100
FrameViewport TFT_WHITE, 2  ' White 2-pixel border
```

**See also:** [SetViewport](#setviewport-x-y-w-h)

### `SetOrigin x, y`
Change the coordinate origin from the default top-left corner.

**Syntax:**
```
SetOrigin origin_x, origin_y
```

**Example:**
```
' Set origin to center of screen
SetOrigin 160, 120

' Now (0, 0) is at center
tft.drawPixel 0, 0, TFT_RED  ' Draws at screen center
```

**Note:** `SetRotation`, `SetViewport`, and `ResetViewport` reset origin to top-left.

**See also:** [SetViewport](#setviewport-x-y-w-h)

### `PushPixel color`
Push (write) a single pixel to the current window set by `SetWindow` or `SetAddrWindow`.

**Syntax:**
```
PushPixel color
```

**Example:**
```
SetWindow 0, 0, 99, 99  ' 100x100 window

' Draw gradient
For y = 0 To 99
    For x = 0 To 99
        Dim c As Integer
        c = x * 2 + y  ' Calculate color
        PushPixel c
    Next x
Next y
```

**See also:** [SetWindow](#setwindow-x1-y1-x2-y2), [PushBlock](#pushblock-color-count)

### `PushBlock color, count`
Push (write) a solid block of pixels with the same color to the current window.

**Syntax:**
```
PushBlock color, pixel_count
```

**Example:**
```
' Fill 50x50 area with blue
SetAddrWindow 10, 10, 50, 50
PushBlock TFT_BLUE, 2500  ' 50 * 50 pixels
```

**Note:** Much faster than calling `PushPixel` repeatedly for the same color.

**See also:** [PushPixel](#pushpixel-color), [SetAddrWindow](#setaddrwindow-x-y-w-h)

---

## Sleep & Power Management (ESP32)

Power management commands for battery-powered and low-power applications.

### `DeepSleep ms`
Enter deep sleep mode for specified milliseconds. Wakes on timer or configured interrupt.

**Syntax:**
```
DeepSleep duration_ms
```

**Example:**
```
' Sleep for 10 seconds
DeepSleep 10000
```

**Note:** ESP32 will wake automatically after the specified duration.

**See also:** [LightSleep](#lightsleep-ms), [Hibernate](#hibernate), [WakeOnInterrupt](#wakeoninterrupt-pin)

### `LightSleep ms`
Enter light sleep mode (less power consumption than normal operation, but more than deep sleep).

**Syntax:**
```
LightSleep duration_ms
```

**Example:**
```
' Light sleep for 1 second
LightSleep 1000
```

**See also:** [DeepSleep](#deepsleep-ms), [Hibernate](#hibernate)

### `Hibernate`
Enter maximum sleep state. Only wakes on interrupt or external reset.

**Example:**
```
' Maximum power saving - only wakes on interrupt
Hibernate
```

**Note:** Requires `WakeOnInterrupt` to be configured to wake the device.

**See also:** [DeepSleep](#deepsleep-ms), [WakeOnInterrupt](#wakeoninterrupt-pin)

### `WakeOnInterrupt pin`
Configure an external pin as wake source for deep sleep or hibernation.

**Syntax:**
```
WakeOnInterrupt pin_number
```

**Example:**
```
' Wake on GPIO25 interrupt
WakeOnInterrupt 25

' Now enter deep sleep
DeepSleep 60000  ' Or Hibernate
```

**Note:** Pin must support external wakeup on your board (usually GPIO0, GPIO2, GPIO4, GPIO12-15, GPIO25-27 on ESP32).

**See also:** [DeepSleep](#deepsleep-ms), [Hibernate](#hibernate)

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


---

*This document is up to date with the current Asic (Arduino Basic) IDE and transpiler. All references to VB2Arduino or VB6_Arduino have been replaced. For more details, see the README and User Guide.*
