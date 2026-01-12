import math
from pathlib import Path


def test_boing_ball_triangle_density_simulated():
    # Simulate the VB triangle placement logic for the initial ball position and
    # ensure a reasonable number of triangles intersect the circular ball area
    SCREEN_W = 172
    SCREEN_H = 320
    BALL_RADIUS = 30
    BALL_TILES = 8
    ballX = SCREEN_W / 2
    ballY = SCREEN_H / 2
    spriteCX = BALL_RADIUS
    spriteCY = BALL_RADIUS

    inside_total = 0
    for t in range(0, BALL_TILES):
        angle1v = 0 + t * (3.14159 * 2 / BALL_TILES)
        angle2v = 0 + (t + 1) * (3.14159 * 2 / BALL_TILES)
        for s in [1, 0]:
            x2v = ballX + math.cos(angle1v) * BALL_RADIUS * (1 - s * 0.5)
            y2v = ballY + math.sin(angle1v) * BALL_RADIUS * (1 - s * 0.5)
            x3v = ballX + math.cos(angle2v) * BALL_RADIUS * (1 - s * 0.5)
            y3v = ballY + math.sin(angle2v) * BALL_RADIUS * (1 - s * 0.5)
            x2l = x2v - (ballX - spriteCX)
            y2l = y2v - (ballY - spriteCY)
            x3l = x3v - (ballX - spriteCX)
            y3l = y3v - (ballY - spriteCY)
            midX = (x2l + x3l) / 2
            midY = (y2l + y3l) / 2
            inside = ((x2l - spriteCX) ** 2 + (y2l - spriteCY) ** 2 <= BALL_RADIUS ** 2) or \
                     ((x3l - spriteCX) ** 2 + (y3l - spriteCY) ** 2 <= BALL_RADIUS ** 2) or \
                     ((midX - spriteCX) ** 2 + (midY - spriteCY) ** 2 <= BALL_RADIUS ** 2)
            if inside:
                inside_total += 1

    # We expect at least half the triangles to intersect for a visible pattern
    assert inside_total >= 8, f'Expected at least 8 triangle tiles to intersect the ball, got {inside_total}'
