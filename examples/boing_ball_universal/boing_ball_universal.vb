#Include <TFT_eSPI.h>

' Boing Ball Demo using ASIC Universal Graphics API
' For ESP32-S3-LCD-1.47 or any supported display

Const SCREEN_WIDTH = 320
Const SCREEN_HEIGHT = 172
Const BALL_RADIUS = 32
Const BALL_SEGMENTS = 12
Const ROTATE_SPEED = 0.08
Const BOUNCE_HEIGHT = 60

Dim ballX As Single
Dim ballY As Single
Dim dx As Single
Dim dy As Single
Dim angle As Single


' --- Amiga Boing Ball Demo Physics ---
Const GRAVITY = 0.7
Const RESTITUTION = 0.85
Dim ballVX As Single
Dim ballVY As Single
Dim ballAngle As Single
Dim ballSpin As Single


Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Boing Ball Universal Demo (Amiga Physics)"
    ' Set grey background and draw grid/floor
    DrawBackground
    ballX = BALL_RADIUS
    ballY = SCREEN_HEIGHT / 2
    ballVX = 5.0 ' Ensure ball reaches both sides
    ballVY = -2.0 ' Less vertical speed
    ballAngle = 0
    ballSpin = 0.12
End Sub


Sub Loop()
    ' Redraw background (checkerboard, floor)
    DrawBackground

    ' Physics-based movement
    ballX = ballX + ballVX
    ballY = ballY + ballVY
    ballVY = ballVY + GRAVITY
    ballAngle = ballAngle + ballSpin

    ' Bounce off left/right walls
    If ballX < BALL_RADIUS Then
        ballX = BALL_RADIUS
        ballVX = Abs(ballVX)
    ElseIf ballX > SCREEN_WIDTH - BALL_RADIUS Then
        ballX = SCREEN_WIDTH - BALL_RADIUS
        ballVX = -Abs(ballVX)
    End If

    ' Bounce off floor
    Dim floorY As Integer
    floorY = SCREEN_HEIGHT - 10 - BALL_RADIUS
    If ballY > floorY Then
        ballY = floorY
        ballVY = -Abs(ballVY) * RESTITUTION
        If Abs(ballVY) < 2 Then ballVY = -8 ' Minimum bounce
    End If

    ' Bounce off ceiling
    If ballY < BALL_RADIUS Then
        ballY = BALL_RADIUS
        ballVY = Abs(ballVY)
    End If

    ' Draw checkered ball
    DrawBoingBall ballX, ballY, BALL_RADIUS, ballAngle

    Delay 20
End Sub
' --- Enhanced Amiga Boing Ball Visuals ---
Sub DrawBoingBall(cx As Integer, cy As Integer, r As Integer, a As Single)
    ' Declare all variables at the start and avoid built-in function names
    Dim i As Integer
    Dim segAngle As Single
    Dim color As Integer
    Dim x0v As Integer
    Dim y0v As Integer
    Dim x1v As Integer
    Dim y1v As Integer
    Dim highlightXv As Integer
    Dim highlightYv As Integer
    Dim highlightRv As Integer
    Dim shadowXv As Integer
    Dim shadowYv As Integer
    Dim shadowRv As Integer
    Dim segments As Integer
    segments = 16
    For i = 0 To segments - 1
        segAngle = a + i * (2 * 3.14159 / segments)
        If (i Mod 2) = 0 Then
            color = COLOR_RED
        Else
            color = COLOR_WHITE
        End If
        x0v = cx + r * Cos(segAngle)
        y0v = cy + r * Sin(segAngle)
        x1v = cx + r * Cos(segAngle + (2 * 3.14159 / segments))
        y1v = cy + r * Sin(segAngle + (2 * 3.14159 / segments))
        ' Draw ball segment as a filled triangle (approximate segment)
        FillTriangle cx, cy, x0v, y0v, x1v, y1v, color
    Next i
    ' Ball shading: highlight
    highlightXv = cx + r * 0.4
    highlightYv = cy - r * 0.4
    highlightRv = r / 3
    FillCircle highlightXv, highlightYv, highlightRv, COLOR_WHITE
    ' Ball shading: shadow
    shadowXv = cx - r * 0.3
    shadowYv = cy + r * 0.3
    shadowRv = r / 2
    FillCircle shadowXv, shadowYv, shadowRv, COLOR_DARKGRAY
End Sub

Sub DrawBackground()
    ' Declare all variables at the start and avoid built-in function names
    FillRect 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GRAY
    Dim gridSize As Integer
    Dim rows As Integer
    Dim cols As Integer
    Dim xg As Integer
    Dim yg As Integer
    Dim pxg As Integer
    Dim pyg As Integer
    Dim tileWg As Integer
    Dim tileHg As Integer
    gridSize = 32
    rows = 6
    cols = 10
    For yg = 0 To rows - 1
        tileHg = gridSize
        tileWg = Int(SCREEN_WIDTH / cols + yg * 4)
        pyg = SCREEN_HEIGHT - (yg + 1) * tileHg
        For xg = 0 To cols - 1
            pxg = xg * tileWg + (yg * 8)
            If ((xg + yg) Mod 2) = 0 Then
                FillRect pxg, pyg, tileWg, tileHg, COLOR_DARKGRAY
            Else
                FillRect pxg, pyg, tileWg, tileHg, COLOR_GRAY
            End If
        Next xg
    Next yg
    ' Draw full gridlines
    For xg = 0 To SCREEN_WIDTH Step gridSize
        DrawLine xg, 0, xg, SCREEN_HEIGHT, COLOR_BLACK
    Next xg
    For yg = 0 To SCREEN_HEIGHT Step gridSize
        DrawLine 0, yg, SCREEN_WIDTH, yg, COLOR_BLACK
    Next yg
    FillRect 0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10, COLOR_BLACK
End Sub
