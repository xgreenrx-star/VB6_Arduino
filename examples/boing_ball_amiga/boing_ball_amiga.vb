' Amiga Boing Ball Demo (VB2Arduino Universal Graphics)
' Inspired by https://github.com/tobozo/ESP32-AmigaBoingBall

#Include <TFT_eSPI.h>

Const SCREEN_W = 240
Const SCREEN_H = 240
Const BALL_RADIUS = 40
Const BALL_TILES = 8
Const BALL_SPEED_X = 3.2
Const BALL_SPEED_Y = 0.09
Const FLOOR_GRID = 8
Const COLOR_BG = COLOR_GRAY
Const COLOR_GRID = COLOR_MAGENTA
Const COLOR_SHADOW = COLOR_DARKGRAY
Const COLOR_RED = COLOR_RED
Const COLOR_WHITE = COLOR_WHITE

Dim ballX As Single
Dim ballY As Single
Dim ballVX As Single
Dim ballVY As Single
Dim phase As Single
Dim shadowY As Single
Dim amplitude As Single
Dim centerY As Single
Dim bounceMargin As Single
Dim leftBound As Single
Dim rightBound As Single
Dim isMovingRight As Boolean
Dim isMovingUp As Boolean

Sub Setup()
    ' Set up screen and initial ball position
    ballX = SCREEN_W / 2
    centerY = SCREEN_H * 0.75
    amplitude = SCREEN_H * 0.25 - BALL_RADIUS
    ballY = centerY
    ballVX = BALL_SPEED_X
    ballVY = BALL_SPEED_Y
    phase = 0
    bounceMargin = BALL_RADIUS + 4
    leftBound = bounceMargin
    rightBound = SCREEN_W - bounceMargin
    isMovingRight = True
    isMovingUp = False
    shadowY = centerY + BALL_RADIUS + 12
    DrawBackground()
End Sub

Sub DrawBackground()
    ' Declare all variables at the start and avoid built-in function names
    FillRect 0, 0, SCREEN_W, SCREEN_H, COLOR_BG
    Dim i As Integer
    Dim x1v As Single, y1v As Single, x2v As Single, y2v As Single
    ' Perspective vanishing point for grid (below ball)
    Dim vanishingX As Single, vanishingY As Single
    vanishingX = SCREEN_W / 2
    vanishingY = SCREEN_H * 0.85
    ' Vertical lines (converge to vanishing point)
    For i = 0 To FLOOR_GRID
        x1v = vanishingX
        y1v = vanishingY
        x2v = i * (SCREEN_W / FLOOR_GRID)
        y2v = SCREEN_H
        DrawLine x1v, y1v, x2v, y2v, COLOR_GRID
    Next i
    ' Horizontal lines (spaced by perspective)
    For i = 0 To FLOOR_GRID
        y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID)
        DrawLine 0, y1v, SCREEN_W, y1v, COLOR_GRID
    Next i
End Sub

Sub DrawBall()
    ' Declare all variables at the start and avoid built-in function names
    Dim t As Integer, s As Integer
    Dim angle1v As Single
    Dim angle2v As Single
    Dim x1v As Single
    Dim y1v As Single
    Dim x2v As Single
    Dim y2v As Single
    Dim x3v As Single
    Dim y3v As Single
    Dim colorTile As Integer
    ' Draw shadow
    FillCircle ballX, shadowY, BALL_RADIUS * 0.7, COLOR_SHADOW
    ' Draw ball as checkerboard using triangles
    For t = 0 To BALL_TILES - 1
        angle1v = phase + t * (3.14159 * 2 / BALL_TILES)
        angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES)
        For s = 0 To 1
            x1v = ballX
            y1v = ballY
            x2v = ballX + Cos(angle1v) * BALL_RADIUS * (1 - s * 0.5)
            y2v = ballY + Sin(angle1v) * BALL_RADIUS * (1 - s * 0.5)
            x3v = ballX + Cos(angle2v) * BALL_RADIUS * (1 - s * 0.5)
            y3v = ballY + Sin(angle2v) * BALL_RADIUS * (1 - s * 0.5)
            If ((t + s) Mod 2) = 0 Then
                colorTile = COLOR_RED
            Else
                colorTile = COLOR_WHITE
            End If
            FillTriangle x1v, y1v, x2v, y2v, x3v, y3v, colorTile
        Next s
    Next t
    ' Ball outline
    DrawCircle ballX, ballY, BALL_RADIUS, COLOR_WHITE
End Sub

Sub Loop()
    DrawBackground()
    ' Ball physics
    If isMovingRight Then
        ballX = ballX + ballVX
        phase = phase + 0.18
        If ballX >= rightBound Then
            isMovingRight = False
        End If
    Else
        ballX = ballX - ballVX
        phase = phase - 0.18
        If ballX <= leftBound Then
            isMovingRight = True
        End If
    End If
    ballY = centerY - amplitude * Abs(Cos(phase * ballVY))
    If ballY < centerY Then
        isMovingUp = True
    Else
        isMovingUp = False
    End If
    DrawBall()
End Sub
