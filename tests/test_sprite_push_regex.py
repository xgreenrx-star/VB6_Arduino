from vb2arduino.transpiler import transpile_string


def test_sprite_push_args_preserved():
    src = open('examples/boing_ball_s3_147/boing_ball_s3_147.vb').read()
    cpp = transpile_string(src)
    assert 'shadow.pushSprite(pushX, floorY - BALL_RADIUS/2, TFT_TRANSPARENT);' in cpp
    assert 'ball.pushSprite(pushX, pushY, TFT_TRANSPARENT);' in cpp
