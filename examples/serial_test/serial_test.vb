' Serial communication test
' Use this to verify serial port is working

Sub Setup()
	SerialBegin 115200
    
	' Add delay to allow USB CDC to initialize on ESP32-S3
	Delay 500
    
	SerialPrintLine "=== ESP32 Serial Test ==="
	SerialPrintLine "If you see this, serial is working!"
	SerialPrintLine ""
End Sub

Sub Loop()
	SerialPrintLine "Hello from ESP32"
	Delay 1000
End Sub