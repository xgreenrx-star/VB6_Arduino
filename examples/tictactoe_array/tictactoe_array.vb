' Tic-Tac-Toe with 2D Array - Single Boot Button Control
' Board: 3x3 grid (0=empty, 1=X/Human, 2=O/AI)
' Boot button (GPIO 0) to navigate and select

#include <Arduino.h>
#include <TFT_eSPI.h>

Const BOARD_SIZE = 2
Const EMPTY = 0
Const HUMAN = 1
Const AI = 2

' Game board as 2D array
Dim board(BOARD_SIZE, BOARD_SIZE) As Integer

' Game state
Dim cursor_row As Integer
Dim cursor_col As Integer
Dim game_over As Integer
Dim winner As Integer
Dim move_count As Integer
Dim board_dirty As Integer  ' 1 = needs redraw, 0 = up to date

' Button state
Dim last_button_state As Integer
Dim button_debounce As Integer

' TFT display
Dim tft As TFT_eSPI

Sub Setup()
    Serial.begin(115200)
    
    ' Init TFT
    tft.init()
    tft.setRotation(0)
    tft.fillScreen(TFT_BLACK)
    
    ' Init game
    InitBoard()
    
    ' Button setup
    pinMode(0, INPUT)
    last_button_state = 1
    button_debounce = 0
    
    ' Game state
    cursor_row = 0
    cursor_col = 0
    game_over = 0
    winner = 0
    move_count = 0
    board_dirty = 1
End Sub

Sub Loop()
    ' Check button with short/long press detection
    Dim button_state As Integer
    Dim press_duration As Integer
    button_state = digitalRead(0)
    
    ' Track button press and release
    If button_state = 0 And last_button_state = 1 Then
        ' Button just pressed - record time
        button_debounce = millis()
        last_button_state = 0
    ElseIf button_state = 1 And last_button_state = 0 Then
        ' Button released - check press duration
        press_duration = millis() - button_debounce
        
        If press_duration > 50 Then
            ' Valid press - check if short or long
            If press_duration < 500 Then
                ' Short press - move cursor
                MoveCursor()
            Else
                ' Long press - place X
                PlaceMove()
            End If
            board_dirty = 1
        End If
        last_button_state = 1
    End If
    
    ' Only redraw if board changed
    If board_dirty = 1 Then
        DrawBoard()
        board_dirty = 0
    End If
    
    ' Reduced delay since we're not always drawing
    delay(50)
End Sub

Sub InitBoard()
    Dim i As Integer
    Dim j As Integer
    
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            board(i, j) = EMPTY
        Next
    Next
    
    cursor_row = 0
    cursor_col = 0
    game_over = 0
    winner = 0
    move_count = 0
    board_dirty = 1
End Sub

Sub PlaceMove()
    ' Long press - place X on current square
    If game_over = 1 Then
        ' Game over - reset
        InitBoard()
        return
    End If
    
    ' Only place if square is empty
    If board(cursor_row, cursor_col) = EMPTY Then
        board(cursor_row, cursor_col) = HUMAN
        move_count = move_count + 1
        
        ' Check if human won
        If CheckWin(HUMAN) = 1 Then
            game_over = 1
            winner = HUMAN
            return
        End If
        
        ' Check for draw
        If move_count = 9 Then
            game_over = 1
            winner = 0
            return
        End If
        
        ' AI move
        AIMove()
        move_count = move_count + 1
        
        ' Check if AI won
        If CheckWin(AI) = 1 Then
            game_over = 1
            winner = AI
            return
        End If
        
        ' Check for draw
        If move_count = 9 Then
            game_over = 1
            winner = 0
            return
        End If
    End If
End Sub

Sub HandleButtonPress()
    If game_over = 1 Then
        ' Game over - reset
        InitBoard()
        return
    End If
    
    ' Try to place human move
    If board(cursor_row, cursor_col) = EMPTY Then
        board(cursor_row, cursor_col) = HUMAN
        move_count = move_count + 1
        
        ' Check if human won
        If CheckWin(HUMAN) = 1 Then
            game_over = 1
            winner = HUMAN
            return
        End If
        
        ' Check for draw
        If move_count = 9 Then
            game_over = 1
            winner = 0
            return
        End If
        
        ' AI move
        AIMove()
        move_count = move_count + 1
        
        ' Check if AI won
        If CheckWin(AI) = 1 Then
            game_over = 1
            winner = AI
            return
        End If
        
        ' Check for draw
        If move_count = 9 Then
            game_over = 1
            winner = 0
            return
        End If
    Else
        ' Move cursor instead
        MoveCursor()
    End If
End Sub

Sub MoveCursor()
    cursor_col = cursor_col + 1
    If cursor_col > UBound(board, 2) Then
        cursor_col = 0
        cursor_row = cursor_row + 1
        If cursor_row > UBound(board, 1) Then
            cursor_row = 0
        End If
    End If
End Sub

Sub AIMove()
    Dim i As Integer
    Dim j As Integer
    
    ' Try to win (check all winning conditions)
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            If board(i, j) = EMPTY Then
                board(i, j) = AI
                If CheckWin(AI) = 1 Then
                    return
                End If
                board(i, j) = EMPTY
            End If
        Next
    Next
    
    ' Try to block human
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            If board(i, j) = EMPTY Then
                board(i, j) = HUMAN
                If CheckWin(HUMAN) = 1 Then
                    board(i, j) = AI
                    return
                End If
                board(i, j) = EMPTY
            End If
        Next
    Next
    
    ' Take center
    If board(1, 1) = EMPTY Then
        board(1, 1) = AI
        return
    End If
    
    ' Take corner
    If board(0, 0) = EMPTY Then
        board(0, 0) = AI
        return
    End If
    If board(0, 2) = EMPTY Then
        board(0, 2) = AI
        return
    End If
    If board(2, 0) = EMPTY Then
        board(2, 0) = AI
        return
    End If
    If board(2, 2) = EMPTY Then
        board(2, 2) = AI
        return
    End If
    
    ' Take any empty
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            If board(i, j) = EMPTY Then
                board(i, j) = AI
                return
            End If
        Next
    Next
End Sub

Function CheckWin(player As Integer) As Integer
    Dim i As Integer
    Dim j As Integer
    
    ' Check rows
    For i = 0 To UBound(board, 1)
        If board(i, 0) = player And board(i, 1) = player And board(i, 2) = player Then
            return 1
        End If
    Next
    
    ' Check columns
    For j = 0 To UBound(board, 2)
        If board(0, j) = player And board(1, j) = player And board(2, j) = player Then
            return 1
        End If
    Next
    
    ' Check diagonals
    If board(0, 0) = player And board(1, 1) = player And board(2, 2) = player Then
        return 1
    End If
    If board(0, 2) = player And board(1, 1) = player And board(2, 0) = player Then
        return 1
    End If
    
    return 0
End Function

Sub DrawBoard()
    Dim i As Integer
    Dim j As Integer
    Dim cell_x As Integer
    Dim cell_y As Integer
    Dim cell_size As Integer
    Dim color As Integer
    
    cell_size = 50
    
    ' Clear screen
    tft.fillScreen(TFT_BLACK)
    
    ' Draw grid and pieces
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            cell_x = j * cell_size + 10
            cell_y = i * cell_size + 10
            
            ' Highlight selected cell with filled background (if empty and not game over)
            If i = cursor_row And j = cursor_col And game_over = 0 Then
                tft.fillRect(cell_x, cell_y, cell_size, cell_size, TFT_DARKGREEN)
                tft.drawRect(cell_x, cell_y, cell_size, cell_size, TFT_CYAN)
                tft.drawRect(cell_x + 1, cell_y + 1, cell_size - 2, cell_size - 2, TFT_CYAN)
            Else
                ' Draw normal cell border
                tft.drawRect(cell_x, cell_y, cell_size, cell_size, TFT_WHITE)
            End If
            
            ' Draw piece
            If board(i, j) = HUMAN Then
                tft.drawChar(cell_x + 15, cell_y + 15, 88, TFT_GREEN, TFT_BLACK, 3)  ' X
            ElseIf board(i, j) = AI Then
                tft.drawChar(cell_x + 15, cell_y + 15, 79, TFT_RED, TFT_BLACK, 3)    ' O
            End If
        Next
    Next
    
    ' Draw game status
    If game_over = 1 Then
        If winner = HUMAN Then
            tft.drawString("YOU WIN!", 80, 200, 2)
        ElseIf winner = AI Then
            tft.drawString("AI WINS!", 80, 200, 2)
        Else
            tft.drawString("DRAW!", 100, 200, 2)
        End If
        tft.drawString("Press to Restart", 50, 230, 1)
    Else
        tft.drawString("Press to Play", 60, 200, 2)
    End If
End Sub
