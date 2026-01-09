' Tic-Tac-Toe for ESP32-S3-LCD using only the BOOT button
' Short press: move cursor to next cell. Long press: place mark.
' After win/draw: any press resets.

#Include <TFT_eSPI.h>

Const BTN_PIN = 0
Const SCREEN_W = 320
Const SCREEN_H = 240
Const CELL_SIZE = 70
Const ORIGIN_X = 35
Const ORIGIN_Y = 20
Const RESET_Y = 210
Const LONG_PRESS_MS = 600

Dim tft As TFT_eSPI
Dim g0 As Integer
Dim g1 As Integer
Dim g2 As Integer
Dim g3 As Integer
Dim g4 As Integer
Dim g5 As Integer
Dim g6 As Integer
Dim g7 As Integer
Dim g8 As Integer
Dim currentPlayer As Integer = 1
Dim selIndex As Integer = 0
Dim gameOver As Boolean = False
Dim lastState As Integer = 1
Dim pressStart As Long = 0

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "TicTacToe (BOOT button)"
    PinMode BTN_PIN, INPUT_PULLUP

    tft.init()
    tft.setRotation(1)

    DrawBoard()
    DrawResetBar("Short: move  Long: place")
    DrawCursor()
End Sub

Sub Loop()
    Dim nowMs As Long = Millis()
    Dim state As Integer = DigitalRead(BTN_PIN)

    If state = LOW And lastState = HIGH Then
        pressStart = nowMs
    ElseIf state = HIGH And lastState = LOW Then
        Dim pressDur As Long = nowMs - pressStart
        If gameOver Then
            ResetGame()
        ElseIf pressDur >= LONG_PRESS_MS Then
            PlaceMark()
        Else
            MoveCursor()
        End If
    End If

    lastState = state
    Delay 15
End Sub

Function GetCell(idx As Integer) As Integer
    If idx = 0 Then
        Return g0
    End If
    If idx = 1 Then
        Return g1
    End If
    If idx = 2 Then
        Return g2
    End If
    If idx = 3 Then
        Return g3
    End If
    If idx = 4 Then
        Return g4
    End If
    If idx = 5 Then
        Return g5
    End If
    If idx = 6 Then
        Return g6
    End If
    If idx = 7 Then
        Return g7
    End If
    If idx = 8 Then
        Return g8
    End If
    Return 0
End Function

Sub SetCell(idx As Integer, val As Integer)
    If idx = 0 Then
        g0 = val
    ElseIf idx = 1 Then
        g1 = val
    ElseIf idx = 2 Then
        g2 = val
    ElseIf idx = 3 Then
        g3 = val
    ElseIf idx = 4 Then
        g4 = val
    ElseIf idx = 5 Then
        g5 = val
    ElseIf idx = 6 Then
        g6 = val
    ElseIf idx = 7 Then
        g7 = val
    ElseIf idx = 8 Then
        g8 = val
    End If
End Sub

Sub MoveCursor()
    selIndex = selIndex + 1
    If selIndex > 8 Then
        selIndex = 0
    End If
    DrawBoard()
    DrawCursor()
End Sub

Sub PlaceMark()
    If GetCell(selIndex) <> 0 Then
        Exit Sub
    End If
    SetCell selIndex, currentPlayer
    DrawBoard()

    Dim winner As Integer = CheckWinner()
    If winner <> 0 Then
        ShowMessage("Player wins!")
        gameOver = True
        Exit Sub
    End If

    If IsFull() Then
        ShowMessage("Draw!")
        gameOver = True
        Exit Sub
    End If

    currentPlayer = 3 - currentPlayer
    DrawCursor()
End Sub

Sub DrawBoard()
    tft.fillScreen(TFT_BLACK)
    Dim i As Integer
    For i = 1 To 2
        tft.drawLine(ORIGIN_X + i * CELL_SIZE, ORIGIN_Y, ORIGIN_X + i * CELL_SIZE, ORIGIN_Y + 3 * CELL_SIZE, TFT_WHITE)
        tft.drawLine(ORIGIN_X, ORIGIN_Y + i * CELL_SIZE, ORIGIN_X + 3 * CELL_SIZE, ORIGIN_Y + i * CELL_SIZE, TFT_WHITE)
    Next
    DrawMarks()
    If gameOver Then
        DrawResetBar("Press to reset")
    Else
        DrawResetBar("Short: move  Long: place")
    End If
End Sub

Sub DrawMarks()
    Dim idx As Integer
    For idx = 0 To 8
        Dim r As Integer = idx \ 3
        Dim c As Integer = idx - r * 3
        Dim cx As Integer = ORIGIN_X + c * CELL_SIZE + CELL_SIZE \ 2
        Dim cy As Integer = ORIGIN_Y + r * CELL_SIZE + CELL_SIZE \ 2
        Dim val As Integer = GetCell(idx)
        If val = 1 Then
            tft.drawLine(cx - 20, cy - 20, cx + 20, cy + 20, TFT_CYAN)
            tft.drawLine(cx + 20, cy - 20, cx - 20, cy + 20, TFT_CYAN)
        ElseIf val = 2 Then
            tft.drawCircle(cx, cy, 22, TFT_YELLOW)
        End If
    Next
End Sub

Sub DrawCursor()
    If gameOver Then
        Exit Sub
    End If
    Dim r As Integer = selIndex \ 3
    Dim c As Integer = selIndex - r * 3
    Dim x0 As Integer = ORIGIN_X + c * CELL_SIZE
    Dim y0 As Integer = ORIGIN_Y + r * CELL_SIZE
    tft.drawRect(x0 + 2, y0 + 2, CELL_SIZE - 4, CELL_SIZE - 4, TFT_GREEN)
End Sub

Function CheckWinner() As Integer
    Dim i As Integer
    
    For i = 0 To 2
        Dim row0 As Integer = GetCell(i * 3)
        Dim row1 As Integer = GetCell(i * 3 + 1)
        Dim row2 As Integer = GetCell(i * 3 + 2)
        If row0 <> 0 And row0 = row1 And row1 = row2 Then
            Return row0
        End If

        Dim col0 As Integer = GetCell(i)
        Dim col1 As Integer = GetCell(i + 3)
        Dim col2 As Integer = GetCell(i + 6)
        If col0 <> 0 And col0 = col1 And col1 = col2 Then
            Return col0
        End If
    Next

    Dim d0 As Integer = GetCell(0)
    Dim d4 As Integer = GetCell(4)
    Dim d8 As Integer = GetCell(8)
    If d0 <> 0 And d0 = d4 And d4 = d8 Then
        Return d0
    End If

    Dim d2 As Integer = GetCell(2)
    Dim d6 As Integer = GetCell(6)
    Dim d4b As Integer = GetCell(4)
    If d2 <> 0 And d2 = d4b And d4b = d6 Then
        Return d2
    End If

    Return 0
End Function

Function IsFull() As Boolean
    Dim i As Integer
    For i = 0 To 8
        If GetCell(i) = 0 Then
            Return False
        End If
    Next
    Return True
End Function

Sub ShowMessage(msg As String)
    Dim fullMsg As String = msg + " (press)"
    DrawResetBar(fullMsg)
End Sub

Sub DrawResetBar(txt As String)
    tft.fillRect(0, RESET_Y, SCREEN_W, SCREEN_H - RESET_Y, TFT_DARKGREY)
    tft.setTextColor(TFT_WHITE, TFT_DARKGREY)
    tft.setTextSize(2)
    tft.setCursor(8, RESET_Y + 8)
    tft.print(txt)
End Sub

Sub ResetGame()
    g0 = 0
    g1 = 0
    g2 = 0
    g3 = 0
    g4 = 0
    g5 = 0
    g6 = 0
    g7 = 0
    g8 = 0
    currentPlayer = 1
    selIndex = 0
    gameOver = False
    DrawBoard()
    DrawCursor()
End Sub
