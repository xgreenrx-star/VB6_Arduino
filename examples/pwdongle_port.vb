'PWDongle port' example for Asic (Arduino Basic) - VB6-like pseudocode

' This example demonstrates a multi-mode boot menu for a security dongle device.
' It shows how to use display, storage, USB, and BLE commands in Asic (Arduino Basic).

' --- Device/Peripheral Declarations ---
Dim tft As Display
Dim prefs As Storage
Dim Keyboard As USBKeyboard
Dim Mouse As USBMouse
Dim Gamepad As USBGamepad

Dim PASSWORDS(10) As String
Dim menuItems(10) As String
Dim MENU_ITEM_COUNT As Integer

Dim codeAccepted As Boolean
Dim awaitingFileNumber As Boolean
Dim bootMenuSelection As Integer

Dim inFileMenu As Boolean
Dim fileList(15) As String
Dim fileCount As Integer
Dim fileMenuSelection As Integer

Const BOOT_BUTTON_PIN = 0

Sub Main()
    tft.Init()
    tft.SetRotation(0)
    tft.FillScreen("black")
    Delay 500
    tft.FillScreen("blue")
    Delay 500
    tft.FillScreen("black")
    ShowStartupMessage("Starting...")

    LoadCorrectCode()
    PinMode BOOT_BUTTON_PIN, INPUT_PULLUP

    Dim bootToBLE As Boolean
    bootToBLE = prefs.GetBool("bootToBLE", False)
    InitializeMSCFlag()
    If GetBootToMSC() Then
        SetBootToMSC(False)
        ShowStartupMessage("Flash drive mode")
        StartUSBMode MODE_MSC
        Exit Sub
    End If
    If bootToBLE Then
        prefs.PutBool("bootToBLE", False)
        StartUSBMode MODE_HID
        StartBLEMode()
        tft.FillScreen("green")
        tft.SetTextColor("black", "green")
        tft.SetTextSize(2)
        tft.SetCursor(10, 40)
        tft.Print("BLE ACTIVE")
        ' ... show BLE instructions ...
        Exit Sub
    End If

    Dim userInterrupted As Boolean
    userInterrupted = False
    For countdown = 3 To 1 Step -1
        ShowCountdown(countdown)
        Dim startWait As Long
        startWait = Millis()
        While Millis() - startWait < 1000
            If DigitalRead(BOOT_BUTTON_PIN) = LOW Then
                userInterrupted = True
                Exit For
            End If
            Delay 10
        Wend
        If userInterrupted Then Exit For
    Next

    If userInterrupted Then
        bootMenuSelection = 0
        DrawBootMenu bootMenuSelection
        Dim menuConfirmed As Boolean
        menuConfirmed = False
        While Not menuConfirmed
            HandleBootMenuButton bootMenuSelection, menuConfirmed
            Delay 10
        Wend
        Select Case bootMenuSelection
            Case 0
                StartUSBMode MODE_HID
                StartBLEMode()
                tft.FillScreen("green")
                tft.SetTextColor("black", "green")
                tft.SetTextSize(2)
                tft.SetCursor(10, 40)
                tft.Print("BLE ACTIVE")
                ' ... show BLE instructions ...
                Exit Sub
            Case 1
                InitializeCDCFlag()
                ShowCDCReadyScreen()
                StartUSBMode MODE_CDC
                Dim start As Long
                start = Millis()
                While Millis() - start < 300000
                    If IsSerialDataAvailable() Then
                        Dim d As String
                        d = ReadSerialData()
                        ProcessSerialLine d
                    End If
                    Delay 50
                Wend
                Exit Sub
            Case 2
                ShowInstructions()
                ShowDigitScreen()
            Case 3, 4
                inFileMenu = True
                ListSDTextFiles fileList, fileCount
                fileMenuSelection = 0
                DrawFileMenu fileMenuSelection, fileList, fileCount
        End Select
        Exit Sub
    End If

    If Not userInterrupted Then
        StartUSBMode MODE_HID
        StartBLEMode()
        tft.FillScreen("green")
        tft.SetTextColor("black", "green")
        tft.SetTextSize(2)
        tft.SetCursor(10, 40)
        tft.Print("BLE ACTIVE")
        ' ... show BLE instructions ...
    End If

    InitializeCDCFlag()
    If GetBootToCDC() Then
        SetBootToCDC(False)
        ShowCDCReadyScreen()
        StartUSBMode MODE_CDC
        Dim start As Long
        start = Millis()
        While Millis() - start < 300000
            If IsSerialDataAvailable() Then
                tft.FillScreen("brown")
                Dim d As String
                d = ReadSerialData()
                ProcessSerialLine d
            End If
            Delay 50
        Wend
    End If

    If CurrentUSBMode = MODE_HID And CurrentBLEMode = 0 And Not codeAccepted And Not awaitingFileNumber Then
        ShowInstructions()
        ShowDigitScreen()
    End If
End Sub

Sub Loop()
    If CurrentBLEMode = 1 Then
        While IsBLEDataAvailable()
            Dim line As String
            line = ReadBLEData()
            ProcessBLELine line
        Wend
        Delay 10
        Exit Sub
    End If
    If CurrentUSBMode = MODE_MSC Then
        Delay 50
        Exit Sub
    End If
    If CurrentUSBMode = MODE_HID Then
        If inFileMenu Then
            Dim fileConfirmed As Boolean
            fileConfirmed = False
            HandleFileMenuButton fileMenuSelection, fileConfirmed, fileCount
            If fileConfirmed And fileCount > 0 Then
                ShowStartupMessage("Loading file...")
                Delay 200
                ProcessTextFileAuto fileList(fileMenuSelection)
                DrawFileMenu fileMenuSelection, fileList, fileCount
            End If
        ElseIf Not codeAccepted Then
            ReadButton()
        Else
            HandleMenuButton()
        End If
    End If
    If CurrentUSBMode = MODE_CDC Then
        While IsSerialDataAvailable()
            Dim line As String
            line = ReadSerialData()
            ProcessSerialLine line
        Wend
    End If
End Sub
