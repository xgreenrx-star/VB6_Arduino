' ESP32 Sleep & Power Management Example
' Demonstrates low-power modes: DeepSleep, LightSleep, Hibernate, WakeOnInterrupt
' 
' For testing: Press BOOT button (GPIO0) to wake from deep sleep
' ESP32 will cycle through different sleep modes

Const WAKE_PIN = 0  ' BOOT button on most ESP32 boards

Sub Setup()
    SerialBegin 115200
    Delay 500
    SerialPrintLine ""
    SerialPrintLine "=== ESP32 Sleep & Power Management Demo ==="
    SerialPrintLine "This sketch cycles through different sleep modes."
    SerialPrintLine "Press BOOT button (GPIO0) to wake from deep sleep."
    SerialPrintLine ""
    
    ' Configure wake pin
    PinMode WAKE_PIN, INPUT_PULLUP
    WakeOnInterrupt WAKE_PIN
    
    SerialPrintLine "System initialized. Wakeup pin configured."
    SerialPrintLine ""
End Sub

Sub Loop()
    SerialPrintLine "--- Demo 1: Light Sleep for 5 seconds ---"
    SerialPrintLine "Entering light sleep..."
    Delay 100
    LightSleep 5000
    SerialPrintLine "Woke from light sleep!"
    Delay 1000
    
    SerialPrintLine ""
    SerialPrintLine "--- Demo 2: Deep Sleep for 10 seconds ---"
    SerialPrintLine "Entering deep sleep (timer wakeup)..."
    Delay 100
    DeepSleep 10000
    SerialPrintLine "Woke from deep sleep!"
    Delay 1000
    
    SerialPrintLine ""
    SerialPrintLine "--- Demo 3: Deep Sleep with Button Wakeup ---"
    SerialPrintLine "Entering deep sleep (press BOOT button to wake)..."
    Delay 100
    DeepSleep 60000
    SerialPrintLine "Woke from deep sleep via button interrupt!"
    Delay 1000
    
    ' Loop back and repeat
End Sub

' Example battery-powered application structure:
' Sub LoopBattery()
'     ' Read sensors
'     Dim sensorValue As Integer
'     sensorValue = AnalogRead(A0)
'     SerialPrint "Sensor: "
'     SerialPrintLine sensorValue
'     
'     ' Process data
'     ' ...
'     
'     ' Sleep to save battery
'     SerialPrintLine "Sleeping for 60 seconds..."
'     Delay 100  ' Flush serial
'     DeepSleep 60000  ' 60 second sleep
'     
'     ' Device wakes and loop repeats
' End Sub
