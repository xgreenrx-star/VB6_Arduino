' Ultra-simple serial test
' This should print immediately in setup

Sub Setup()
	SerialBegin 115200
	' Wait for USB to initialize
	Delay 2000
	SerialPrintLine "HELLO"
	SerialPrintLine "WORLD"
End Sub

Sub Loop()
	Delay 1000
End Sub