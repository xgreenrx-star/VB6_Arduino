' Amiga-style Boing Ball for ESP32-S3-LCD-1.47
' Target: ESP32-S3-LCD-1.47 (ST7789 172x320)
' Ported from https://github.com/tobozo/ESP32-AmigaBoingBall (MIT License)
' Credits: tobozo (original), adapted by VB2Arduino transpiler edits

#Include <TFT_eSPI.h>

Const SCREEN_W = 172
Const SCREEN_H = 320
Const BALL_RADIUS = 30
Const BALL_TILES = 12
Const BALL_SPEED_X = 4.5     ' faster horizontal speed
Const BALL_SPEED_Y = 0.12    ' vertical phase speed
Const PHASE_STEP = 0.25      ' phase increment per frame
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
Dim prevBallX As Single
Dim prevBallY As Single
Dim isMovingRight As Boolean
Dim isMovingUp As Boolean

Sub Setup()
    ' Initialize ball and screen
    ballX = SCREEN_W / 2
    ' Use center vertically to maximize available bounce space
    centerY = SCREEN_H / 2
    amplitude = centerY - BALL_RADIUS - 8 ' max amplitude so ball can use available screen height
    ballY = centerY
    ballVX = BALL_SPEED_X
    ballVY = -6.0 ' stronger initial upward impulse for higher bounce
    phase = 0
    bounceMargin = BALL_RADIUS + 8
    leftBound = bounceMargin
    rightBound = SCREEN_W - bounceMargin
    isMovingRight = True
    isMovingUp = False
    shadowY = centerY + BALL_RADIUS + 8
    prevBallX = ballX
    prevBallY = ballY
    ' Draw static background only once to avoid flicker
    DrawBackground()

    ' Create sprites for ball, shadow, and background
    Dim spriteW As Integer
    spriteW = BALL_RADIUS * 2
    Dim spriteH As Integer
    spriteH = BALL_RADIUS * 2
    CREATE_SPRITE ball, spriteW, spriteH
    CREATE_SPRITE shadow, spriteW, BALL_RADIUS

    ' Background sprite to restore grid each frame (pre-rendered)
    CREATE_SPRITE bg, SCREEN_W, SCREEN_H
    SPRITE_FILL bg, COLOR_BG

    ' Draw background grid into bg sprite
    Dim i As Integer
    Dim x1v As Single, y1v As Single, x2v As Single, y2v As Single
    Dim vanishingX As Single, vanishingY As Single
    vanishingX = SCREEN_W / 2
    vanishingY = SCREEN_H * 0.85
    For i = 0 To FLOOR_GRID
        x1v = vanishingX
        y1v = vanishingY
        x2v = i * (SCREEN_W / FLOOR_GRID)
        y2v = SCREEN_H
        bg.drawLine x1v, y1v, x2v, y2v, COLOR_GRID
    Next i
    For i = 0 To FLOOR_GRID
        y1v = vanishingY + i * ((SCREEN_H - vanishingY) / FLOOR_GRID)
        bg.drawLine 0, y1v, SCREEN_W, y1v, COLOR_GRID
    Next i

    ' Initialize previous background push coords
    prevBallX = ballX
    prevBallY = ballY
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
    Dim spriteCX As Single
    Dim spriteCY As Single
    spriteCX = BALL_RADIUS
    spriteCY = BALL_RADIUS

    ' Clear ball sprite and draw a circular ball (smooth)
    SPRITE_FILL ball, COLOR_BG

    ' Draw main white circle for checkered base (red tiles will be drawn on top)
    SPRITE_FILL_ELLIPSE ball, spriteCX, spriteCY, BALL_RADIUS, BALL_RADIUS, COLOR_WHITE

    ' Add a small subtle highlight
    SPRITE_FILL_ELLIPSE ball, spriteCX - (BALL_RADIUS/4), spriteCY - (BALL_RADIUS/4), BALL_RADIUS/6, BALL_RADIUS/6, COLOR_LIGHTGRAY

    ' Overlay a checkered pattern of alternating tiles to mimic the classic Boing Ball
    Dim t As Integer, s As Integer
    Dim angle1v As Single, angle2v As Single
    Dim x2v As Single, y2v As Single, x3v As Single, y3v As Single
    For t = 0 To BALL_TILES - 1
        angle1v = phase + t * (3.14159 * 2 / BALL_TILES)
        angle2v = phase + (t + 1) * (3.14159 * 2 / BALL_TILES)
        ' Draw outer tiles first (s=1) so inner tiles do not consistently overwrite their partners
        For s = 1 To 0 Step -1
            x2v = ballX + Cos(angle1v) * BALL_RADIUS * (1 - s * 0.35)
            y2v = ballY + Sin(angle1v) * BALL_RADIUS * (1 - s * 0.35)
            x3v = ballX + Cos(angle2v) * BALL_RADIUS * (1 - s * 0.35)
            y3v = ballY + Sin(angle2v) * BALL_RADIUS * (1 - s * 0.35)
            ' Only draw red tiles (odd parity) directly for stronger contrast
            If ((t + s) Mod 2) <> 0 Then
                ' Local triangle coords relative to sprite top-left
                Dim x2l As Single, y2l As Single, x3l As Single, y3l As Single
                x2l = x2v - (ballX - spriteCX)
                y2l = y2v - (ballY - spriteCY)
                x3l = x3v - (ballX - spriteCX)
                y3l = y3v - (ballY - spriteCY)
                ' Draw tile if it intersects the circular ball area: either vertex or the midpoint inside
                Dim midX As Single, midY As Single
                midX = (x2l + x3l) / 2
                midY = (y2l + y3l) / 2
                If ((x2l - spriteCX) * (x2l - spriteCX) + (y2l - spriteCY) * (y2l - spriteCY) <= BALL_RADIUS * BALL_RADIUS) Or _
                   ((x3l - spriteCX) * (x3l - spriteCX) + (y3l - spriteCY) * (y3l - spriteCY) <= BALL_RADIUS * BALL_RADIUS) Or _
                   ((midX - spriteCX) * (midX - spriteCX) + (midY - spriteCY) * (midY - spriteCY) <= BALL_RADIUS * BALL_RADIUS) Then
                    SPRITE_FILL_TRIANGLE ball, spriteCX, spriteCY, x2l, y2l, x3l, y3l, COLOR_RED
                    ' DEBUG DIRECT DRAW REMOVED: tft.fillTriangle x1v, y1v, x2v, y2v, x3v, y3v, COLOR_RED
                End If
            End If
        Next s
    Next t

    ' DEBUG: Draw a prominent red disk on top to detect whether red draws are visible (removed)
    ' SPRITE_FILL_ELLIPSE ball, spriteCX, spriteCY, BALL_RADIUS/2, BALL_RADIUS/2, COLOR_RED

    ' Compute shadow size based on height and draw soft multi-layer shadow
    Dim shadowScale As Single
    Dim shadowNorm As Single
    shadowNorm = 1 - ((ballY - (centerY - amplitude)) / (2 * amplitude)) ' 0..1 (1 = top, 0 = bottom)
    shadowScale = 0.6 + 0.9 * shadowNorm ' range ~0.6..1.5
    If shadowScale < 0.5 Then shadowScale = 0.5
    If shadowScale > 1.6 Then shadowScale = 1.6

    ' Pre-render a soft shadow by drawing concentric ellipses (outer -> inner)
    SPRITE_FILL shadow, COLOR_BG
    ' Outer (light)
    SPRITE_FILL_ELLIPSE shadow, BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 1.8), BALL_RADIUS * (0.55 * shadowScale), RGB(140,140,140)
    ' Mid (medium)
    SPRITE_FILL_ELLIPSE shadow, BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 1.25), BALL_RADIUS * (0.5 * shadowScale), RGB(100,100,100)
    ' Inner (dark)
    SPRITE_FILL_ELLIPSE shadow, BALL_RADIUS, BALL_RADIUS/2, BALL_RADIUS * (shadowScale * 0.95), BALL_RADIUS * (0.4 * shadowScale), RGB(40,40,40)

    ' Compute push positions in temporary ints to avoid expression issues in transpiler
    Dim pushX As Integer
    Dim pushY As Integer
    Dim floorY As Integer
    pushX = ballX - BALL_RADIUS
    pushY = ballY - spriteCY
    floorY = centerY + amplitude + BALL_RADIUS/2 ' ground Y where shadow sits

    ' Push shadow at floor position (so shadow stays on the ground) then ball sprite (transparent)
    SPRITE_PUSH shadow, pushX, floorY - BALL_RADIUS/2, TFT_TRANSPARENT
    SPRITE_PUSH ball, pushX, pushY, TFT_TRANSPARENT

    ' Save previous ball position for next frame erase
    prevBallX = ballX
    prevBallY = ballY
    ' Save previous shadow top-left for potential debugging
    prevShadowX = pushX
    prevShadowY = shadowY - BALL_RADIUS/2
End Sub

Sub Loop()
    ' Restore background each frame from bg sprite to remove artifacts
    SPRITE_PUSH bg, 0, 0

    If isMovingRight Then
        ballX = ballX + ballVX
        phase = phase + PHASE_STEP
        If ballX >= rightBound Then
            isMovingRight = False
        End If
    Else
        ballX = ballX - ballVX
        phase = phase - PHASE_STEP
        If ballX <= leftBound Then
            isMovingRight = True
        End If
    End If

    ' Vertical physics: gravity + bounce
    ballY = ballY + ballVY
    ballVY = ballVY + 0.6 ' gravity
    If ballY >= centerY + amplitude Then
        ballY = centerY + amplitude
        ballVY = -Abs(ballVY) * 0.92 ' stronger restitution for higher bounce
        isMovingUp = False
    ElseIf ballY <= centerY - amplitude Then
        ballY = centerY - amplitude
        ballVY = Abs(ballVY) * 0.92
        isMovingUp = True
    Else
        ' In mid-air
        isMovingUp = (ballVY < 0)
    End If

    DrawBall()

    ' Save previous ball position for next frame erase
    prevBallX = ballX
    prevBallY = ballY

    ' Small delay to control frame speed - adjust as needed
    Delay 20
End Sub
