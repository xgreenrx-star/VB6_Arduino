' Amiga-style Boing Ball for ESP32-S3-LCD-1.47
' Target: ESP32-S3-LCD-1.47 (ST7789 172x320)
' Ported from https://github.com/tobozo/ESP32-AmigaBoingBall (MIT License)
' Credits: tobozo (original), adapted by VB2Arduino transpiler edits

#Include <TFT_eSPI.h>

Const SCREEN_W = 172
Const SCREEN_H = 320
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
    ' Initialize ball and screen
    ballX = SCREEN_W / 2
    centerY = SCREEN_H * 0.75
    amplitude = SCREEN_H * 0.25 - 30 ' tune radius relative to screen
    ballY = centerY
    ballVX = BALL_SPEED_X
    ballVY = BALL_SPEED_Y
    phase = 0
    bounceMargin = 40
    leftBound = bounceMargin
    rightBound = SCREEN_W - bounceMargin
    isMovingRight = True
    isMovingUp = False
    shadowY = centerY + 40
    DrawBackground()
End Sub

Sub DrawBackground()
    ' Fill background and draw perspective grid
    FillRect 0, 0, SCREEN_W, SCREEN_H, COLOR_BG
    Dim i As Integer
    Dim x1v As Single, y1v As Single, x2v As Single, y2v As Single
    Dim vanishingX As Single, vanishingY As Single
    vanishingX = SCREEN_W / 2
    vanishingY = SCREEN_H * 0.85

    ' Vertical converging lines
    For i = 0 To FLOOR_GRID
        x1v = vanishingX
        y1v = vanishingY
        x2v = i * (SCREEN_W / FLOOR_GRID)
        y2v = SCREEN_H
        DrawLine x1v, y1v, x2v, y2v, COLOR_GRID
    Next i

    ' Horizontal perspective lines
    For i = 0 To FLOOR_GRID
        y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID)
        DrawLine 0, y1v, SCREEN_W, y1v, COLOR_GRID
    Next i
End Sub

Sub DrawBall()
    Dim t As Integer, s As Integer
    Dim angle1v As Single, angle2v As Single
    Dim x1v As Single, y1v As Single, x2v As Single, y2v As Single, x3v As Single, y3v As Single
    Dim colorTile As Integer

    ' Shadow under ball
    FillCircle ballX, shadowY, 30, COLOR_SHADOW

    For t = 0 To BALL_TILES - 1
        angle1v = phase + t * (3.14159 * 2 / BALL_TILES)
        angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES)
        For s = 0 To 1
            ' compute ring vertices
            x1v = ballX
            y1v = ballY
            x2v = ballX + Cos(angle1v) * 40 * (1 - s * 0.5) * (amplitude / 40)
            y2v = ballY + Sin(angle1v) * 40 * (1 - s * 0.5) * (amplitude / 40)
            x3v = ballX + Cos(angle2v) * 40 * (1 - s * 0.5) * (amplitude / 40)
            y3v = ballY + Sin(angle2v) * 40 * (1 - s * 0.5) * (amplitude / 40)

            If ((t + s) Mod 2) = 0 Then
                colorTile = COLOR_RED
            Else
                colorTile = COLOR_WHITE
            End If

            FillTriangle x1v, y1v, x2v, y2v, x3v, y3v, colorTile
        Next s
    Next t
End Sub

Sub Loop()
    DrawBackground()

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
