' VB2Arduino Tree View Demo
' This file demonstrates the Project Explorer tree view

#Include <WiFi.h>
#Include <Preferences.h>

' Constants
Const LED_PIN As Integer = 2
Const BUTTON_PIN As Integer = 4
Const BAUD_RATE As Long = 115200

' Variables
Dim counter As Integer
Dim buttonState As Boolean
Dim lastButtonState As Boolean
Dim ledState As Boolean
Dim prefs As Preferences

'========================================
' Setup - Initialize system
'========================================
Sub Setup()
	' Initialize pins
	PinMode LED_PIN, OUTPUT
	PinMode BUTTON_PIN, INPUT_PULLUP
    
	' Initialize serial
	SerialBegin BAUD_RATE
	SerialPrintLine "System Starting..."
    
	' Initialize variables
	counter = 0
	buttonState = False
	lastButtonState = False
	ledState = False
    
	' Load preferences
	LoadPreferences()
    
	SerialPrintLine "Setup Complete!"
End Sub

'========================================
' Main Loop
'========================================
Sub Loop()
	CheckButton()
	UpdateDisplay()
	Delay 50
End Sub

'========================================
' Button Handling
'========================================
Sub CheckButton()
	' Read current button state
	buttonState = DigitalRead(BUTTON_PIN)
    
	' Check for button press (falling edge)
	If buttonState And Not lastButtonState Then
		HandleButtonPress()
	End If
    
	lastButtonState = buttonState
End Sub

Sub HandleButtonPress()
	' Toggle LED
	ledState = Not ledState
	DigitalWrite LED_PIN, ledState
    
	' Increment counter
	counter = counter + 1
    
	' Save to preferences
	SaveCounter()
    
	' Print status
	SerialPrint "Button pressed! Count: "
	SerialPrintLine counter
End Sub

'========================================
' Display Functions
'========================================
Sub UpdateDisplay()
	' Update status every 1000 cycles
	If counter Mod 1000 = 0 Then
		PrintStatus()
	End If
End Sub

Sub PrintStatus()
	SerialPrintLine "===================="
	SerialPrint "Counter: "
	SerialPrintLine counter
	SerialPrint "LED State: "
	If ledState Then
		SerialPrintLine "ON"
	Else
		SerialPrintLine "OFF"
	End If
	SerialPrintLine "===================="
End Sub

'========================================
' Preferences Management
'========================================
Sub LoadPreferences()
	SerialPrintLine "Loading preferences..."
	counter = GetSavedCounter()
	SerialPrint "Loaded counter value: "
	SerialPrintLine counter
End Sub

Sub SaveCounter()
	SerialPrint "Saving counter: "
	SerialPrintLine counter
End Sub

Function GetSavedCounter() As Integer
	' In real code, this would load from Preferences
	Return 0
End Function

'========================================
' Utility Functions
'========================================
Function GetLEDPin() As Integer
	Return LED_PIN
End Function

Function GetButtonPin() As Integer
	Return BUTTON_PIN
End Function

Function IsLEDOn() As Boolean
	Return ledState
End Function

Sub ResetCounter()
	counter = 0
	SaveCounter()
	SerialPrintLine "Counter reset to 0"
End Sub

Sub BlinkLED(times As Integer, delayMs As Integer)
	Dim i As Integer
	For i = 1 To times
		DigitalWrite LED_PIN, HIGH
		Delay delayMs
		DigitalWrite LED_PIN, LOW
		Delay delayMs
	Next i
End Sub