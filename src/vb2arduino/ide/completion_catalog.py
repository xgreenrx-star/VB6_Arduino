"""Completion catalog for Asic/VB2Arduino editor.
Provides comprehensive IntelliSense-style completion lists.
"""

from typing import List

# Core VB-like keywords and constructs
KEYWORDS: List[str] = [
    # Blocks
    "Sub", "End Sub", "Function", "End Function",
    "Type", "End Type",
    "With", "End With",
    "Property Get", "Property Let", "Property Set", "End Property",
    # Declarations
    "Dim", "Const", "Static", "As", "Optional", "ByRef", "ByVal",
    # Control flow
    "If", "Then", "ElseIf", "Else", "End If",
    "Select Case", "Case", "Case Else", "End Select",
    "For", "To", "Step", "Next",
    "While", "Wend",
    "Do", "Loop", "Loop While", "Loop Until",
    # Misc
    "Return", "Exit Sub", "Exit Function", "Exit For", "Exit Do", "Exit While", "Exit Select",
    "Goto", "Label:",
    "On Error Resume Next", "On Error GoTo",
    "Option Base",
    "#Include",
    "Rem",
]

# VB basic types
TYPES: List[str] = [
    "Integer", "Long", "Byte", "Boolean", "Single", "Double", "String",
]

# Arduino/Platform helpers
ARDUINO_FUNCS: List[str] = [
    # Entry points
    "Setup", "Loop",
    # GPIO & timing
    "PinMode", "DigitalWrite", "DigitalRead", "AnalogRead", "AnalogWrite",
    "Delay", "DelayMicroseconds", "Millis", "Micros",
    # Serial
    "SerialBegin", "SerialEnd", "SerialAvailable", "SerialRead",
    "SerialPrint", "SerialPrintLine", "SerialWrite",
    # Interrupts & utilities
    "AttachInterrupt", "DetachInterrupt", "PulseIn", "ShiftOut", "ShiftIn",
    # Math helpers
    "Map", "Constrain", "Min", "Max", "Abs", "Pow", "Sqrt",
    "Sin", "Cos", "Tan", "Random", "RandomSeed",
    # RGB/Servo convenience
    "RGB", "SERVO_DEG2PULSE", "SERVO_CLAMP", "SERVO_CLAMP_DEG2PULSE",
]

ARDUINO_CONSTS: List[str] = [
    "HIGH", "LOW", "INPUT", "OUTPUT", "INPUT_PULLUP", "LED_BUILTIN",
    "true", "false",
    "A0", "A1", "A2", "A3", "A4", "A5",
]

# VB6-style string functions and conversions
STRING_FUNCS: List[str] = [
    "Len", "Left$", "Right$", "Mid$", "Instr", "InStrRev",
    "Replace", "Trim", "LTrim", "RTrim", "UCase", "LCase",
    # Project-supported aliases
    "upper", "lower",
    # Runtime helpers
    "Split", "Join", "Filter",
    # Conversions
    "Val", "Hex$", "Oct$", "Chr$", "Asc", "Space", "String",
    # Other
    "StrComp", "StrReverse",
]

# Math & time functions (VB-like)
MATH_FUNCS: List[str] = [
    "Sqr", "Round", "Fix", "Sgn", "Log", "Exp", "Atn", "Abs", "Int", "Rnd",
]

TIME_FUNCS: List[str] = [
    "Timer", "Randomize", "Now", "Date", "Time",
]

# Built-in constants (VB-like)
VB_CONSTS: List[str] = [
    "vbCr", "vbLf", "vbCrLf", "vbTab", "vbNullString", "vbNullChar",
    "vbTrue", "vbFalse",
]

# Math/status constants
MATH_CONSTS: List[str] = [
    "PI", "TAU", "DEG2RAD", "RAD2DEG", "INF", "NAN", "OK", "FAILED",
]

# Unified catalog
ALL_COMPLETIONS: List[str] = (
    KEYWORDS
    + TYPES
    + ARDUINO_FUNCS
    + ARDUINO_CONSTS
    + STRING_FUNCS
    + MATH_FUNCS
    + TIME_FUNCS
    + VB_CONSTS
    + MATH_CONSTS
)

def get_all_completions() -> List[str]:
    """Return a de-duplicated, sorted list of completion items."""
    # Unique and case-preserving, sorted case-insensitively
    uniq = []
    seen = set()
    for item in ALL_COMPLETIONS:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    return sorted(uniq, key=str.lower)
