' PWDongle - VB6_Arduino Port
' Password Dongle with BLE and Macro Recording
' Requires: ESP32-S3, BLEDevice, BLEServer, Preferences

#Include <BLEDevice.h>
#Include <BLEServer.h>
#Include <BLEUtils.h>
#Include <BLE2902.h>
#Include <Preferences.h>

' Hardware Configuration
Const BUTTON_PIN As Integer = 0
Const LED_PIN As Integer = 2

' BLE UUIDs - Note: String constants need special handling
Const SERVICE_UUID As String = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
Const CHAR_UUID As String = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

' State Variables
Dim prefs As Preferences
Dim deviceConnected As Boolean
Dim recording As Boolean
Dim playing As Boolean
Dim buttonState As Integer
Dim lastButtonState As Integer
Dim pressStartTime As Long
Dim recordStartTime As Long
Dim macroCount As Integer

' BLE objects (pointers by default)
Dim bleServer As BLEServer*
Dim bleService As BLEService*
Dim bleCharacteristic As BLECharacteristic*
Dim bleAdvertising As BLEAdvertising*

' Note: BLE objects will be initialized in Setup using factory methods

' Macro Storage
Const MAX_MACROS As Integer = 10
Dim macroActions(MAX_MACROS) As String
Dim macroTimings(MAX_MACROS) As Long

'========================================
' Macro Persistence Helpers
'========================================
Function JoinActions() As String
    Dim result As String
    Dim i As Integer
    result = ""
    For i = 0 To macroCount - 1
        result = result + macroActions(i)
        If i < macroCount - 1 Then
            result = result + ","
        End If
    Next i
    Return result
End Function

Function JoinTimings() As String
    Dim result As String
    Dim i As Integer
    result = ""
    For i = 0 To macroCount - 1
        result = result + String(macroTimings(i))
        If i < macroCount - 1 Then
            result = result + ","
        End If
    Next i
    Return result
End Function

Sub ParseActions(csv As String)
    macroCount = 0
    If csv.length() = 0 Then
        macroCount = 0
    Else
        Dim startPos As Integer
        Dim sepPos As Integer
        startPos = 0
        sepPos = csv.indexOf(",", startPos)

        While sepPos >= 0 And macroCount < MAX_MACROS
            macroActions(macroCount) = csv.substring(startPos, sepPos)
            macroCount = macroCount + 1
            startPos = sepPos + 1
            sepPos = csv.indexOf(",", startPos)
        Wend

        If macroCount < MAX_MACROS And startPos <= csv.length() Then
            macroActions(macroCount) = csv.substring(startPos)
            macroCount = macroCount + 1
        End If
    End If
End Sub

Sub ParseTimings(csv As String)
    Dim slot As Integer

    If csv.length() = 0 Then
        slot = 0
    Else
        Dim startPos As Integer
        Dim sepPos As Integer
        Dim segment As String
        startPos = 0
        sepPos = csv.indexOf(",", startPos)
        slot = 0

        While sepPos >= 0 And slot < MAX_MACROS
            segment = csv.substring(startPos, sepPos)
            macroTimings(slot) = segment.toInt()
            slot = slot + 1
            startPos = sepPos + 1
            sepPos = csv.indexOf(",", startPos)
        Wend

        If slot < MAX_MACROS And startPos <= csv.length() Then
            segment = csv.substring(startPos)
            macroTimings(slot) = segment.toInt()
        End If
    End If
End Sub

'========================================
' Setup - Initialize System
'========================================
Sub Setup()
    ' Initialize Serial
    SerialBegin 115200
    SerialPrintLine "PWDongle Starting..."
    
    ' Initialize Hardware
    PinMode BUTTON_PIN, INPUT_PULLUP
    PinMode LED_PIN, OUTPUT
    DigitalWrite LED_PIN, LOW
    
    ' Initialize Preferences
    InitPreferences()
    
    ' Initialize BLE
    InitBLE()
    
    ' Load saved macros
    LoadMacros()
    
    ' Initialize state
    deviceConnected = False
    recording = False
    playing = False
    lastButtonState = HIGH
    ' macroCount set during LoadMacros
    
    SerialPrintLine "PWDongle Ready!"
    BlinkLED 3, 200
End Sub

'========================================
' Main Loop
'========================================
Sub Loop()
    ' Check button state
    CheckButton()
    
    ' Handle BLE connection
    HandleBLE()
    
    ' Handle macro playback
    If playing Then
        PlayMacro()
    End If
    
    ' Update LED status
    UpdateLED()
    
    Delay 10
End Sub

'========================================
' Preferences Management
'========================================
Sub InitPreferences()
    SerialPrintLine "Initializing preferences..."
    prefs.begin "pwdongle", False
End Sub

Sub LoadMacros()
    macroCount = prefs.getInt("macroCount", 0)
    Dim actionsCsv As String
    Dim timesCsv As String
    actionsCsv = prefs.getString("macroActions", "")
    timesCsv = prefs.getString("macroTimes", "")
    ParseActions actionsCsv
    ParseTimings timesCsv
    SerialPrint "Loading macros: "
    SerialPrintLine macroCount
End Sub

Sub SaveMacros()
    prefs.putInt "macroCount", macroCount
    prefs.putString "macroActions", JoinActions()
    prefs.putString "macroTimes", JoinTimings()
    SerialPrint "Saving macros: "
    SerialPrintLine macroCount
End Sub

'========================================
' BLE Initialization
'========================================
Sub InitBLE()
    SerialPrintLine "Initializing BLE..."
    SerialPrintLine "BLE Device: PWDongle"

    BLEDevice::init "PWDongle"
    bleServer = BLEDevice::createServer()
    bleService = bleServer.createService(SERVICE_UUID)
    bleCharacteristic = bleService.createCharacteristic(CHAR_UUID, BLECharacteristic::PROPERTY_READ + BLECharacteristic::PROPERTY_WRITE + BLECharacteristic::PROPERTY_NOTIFY)
    bleCharacteristic.setValue "Ready"
    bleService.start()

    bleAdvertising = BLEDevice::getAdvertising()
    bleAdvertising.addServiceUUID SERVICE_UUID
    bleAdvertising.start()

    deviceConnected = False
    SerialPrintLine "BLE init complete"
End Sub

Sub HandleBLE()
    If bleServer <> 0 Then
        Dim connectedNow As Boolean
        connectedNow = bleServer.getConnectedCount() > 0

        If connectedNow <> deviceConnected Then
            deviceConnected = connectedNow
            If deviceConnected Then
                SerialPrintLine "BLE connected"
            Else
                SerialPrintLine "BLE disconnected"
                If bleAdvertising <> 0 Then
                    bleAdvertising.start()
                End If
            End If
        End If
    End If
End Sub

'========================================
' Button Handling
'========================================
Sub CheckButton()
    buttonState = DigitalRead(BUTTON_PIN)
    
    ' Detect button press (falling edge)
    If buttonState = LOW And lastButtonState = HIGH Then
        OnButtonPress()
    End If
    
    ' Detect button release (rising edge)
    If buttonState = HIGH And lastButtonState = LOW Then
        OnButtonRelease()
    End If
    
    lastButtonState = buttonState
End Sub

Sub OnButtonPress()
    pressStartTime = Millis()
    SerialPrintLine "Button pressed"
    DigitalWrite LED_PIN, HIGH
    
    If recording Then
        RecordAction "PRESS", Millis()
    End If
End Sub

Sub OnButtonRelease()
    Dim pressDuration As Long
    pressDuration = Millis() - pressStartTime
    
    SerialPrint "Button released - Duration: "
    SerialPrintLine pressDuration
    DigitalWrite LED_PIN, LOW
    
    ' Check for long press (>2 seconds)
    If pressDuration > 2000 Then
        HandleLongPress()
    Else
        HandleShortPress()
    End If
End Sub

Sub HandleShortPress()
    SerialPrintLine "Short press detected"
    
    If Not recording And Not playing Then
        ' Start macro playback
        StartPlayback()
    End If
End Sub

Sub HandleLongPress()
    SerialPrintLine "Long press detected"
    
    ' Toggle recording mode
    If recording Then
        StopRecording()
    Else
        StartRecording()
    End If
End Sub

'========================================
' Macro Recording
'========================================
Sub StartRecording()
    recording = True
    macroCount = 0
    recordStartTime = Millis()
    SerialPrintLine "=== RECORDING STARTED ==="
    BlinkLED 5, 100
End Sub

Sub StopRecording()
    recording = False
    SerialPrintLine "=== RECORDING STOPPED ==="
    SerialPrint "Recorded "
    SerialPrint macroCount
    SerialPrintLine " actions"
    
    ' Save macro to preferences
    SaveMacros()
    BlinkLED 2, 500
End Sub

Sub RecordAction(action As String, timestamp As Long)
    If macroCount < MAX_MACROS Then
        macroActions(macroCount) = action
        macroTimings(macroCount) = timestamp - recordStartTime
        macroCount = macroCount + 1
        
        SerialPrint "Recorded: "
        SerialPrint action
        SerialPrint " @ "
        SerialPrintLine timestamp
    End If
End Sub

'========================================
' Macro Playback
'========================================
Sub StartPlayback()
    If macroCount > 0 Then
        playing = True
        SerialPrintLine "=== PLAYBACK STARTED ==="
        BlinkLED 1, 100
    Else
        SerialPrintLine "No macro to play"
    End If
End Sub

Sub PlayMacro()
    Dim i As Integer
    
    For i = 0 To macroCount - 1
        SerialPrint "Playing: "
        SerialPrintLine macroActions(i)
        
        ' Execute action via BLE
        SendBLECommand macroActions(i)
        
        ' Wait for timing
        If i < macroCount - 1 Then
            Delay macroTimings(i + 1) - macroTimings(i)
        End If
    Next i
    
    playing = False
    SerialPrintLine "=== PLAYBACK FINISHED ==="
End Sub

Sub SendBLECommand(command As String)
    If bleCharacteristic <> 0 Then
        bleCharacteristic.setValue command.c_str()
        bleCharacteristic.notify()
    End If

    SerialPrint "Sending BLE: "
    SerialPrintLine command
End Sub

'========================================
' LED Control
'========================================
Sub UpdateLED()
    If recording Then
        ' Pulse LED during recording
        BlinkLED 1, 50
    ElseIf playing Then
        ' Fast blink during playback
        DigitalWrite LED_PIN, HIGH
    ElseIf deviceConnected Then
        ' Solid on when connected
        DigitalWrite LED_PIN, HIGH
    Else
        ' Off when idle
        DigitalWrite LED_PIN, LOW
    End If
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

'========================================
' Utility Functions
'========================================
Function GetMacroCount() As Integer
    Return macroCount
End Function

Function IsConnected() As Boolean
    Return deviceConnected
End Function

Sub ResetMacros()
    macroCount = 0
    SerialPrintLine "Macros reset"
End Sub
