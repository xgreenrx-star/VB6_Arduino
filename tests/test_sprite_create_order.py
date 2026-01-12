from vb2arduino.transpiler import transpile_string


def test_create_sprite_after_sprite_size_assignments():
    src = open('examples/boing_ball_s3_147/boing_ball_s3_147.vb').read()
    cpp = transpile_string(src)
    # Ensure spriteW and spriteH are assigned before createSprite calls
    idx_spriteW_assign = cpp.find('spriteW =')
    idx_spriteH_assign = cpp.find('spriteH =')
    idx_create_ball = cpp.find('ball.createSprite(')
    idx_create_shadow = cpp.find('shadow.createSprite(')
    assert idx_spriteW_assign != -1 and idx_spriteH_assign != -1, 'sprite size assignments missing'
    assert idx_create_ball != -1 and idx_create_shadow != -1, 'createSprite calls missing'
    assert idx_spriteW_assign < idx_create_ball, 'spriteW assignment must come before ball.createSprite'
    assert idx_spriteH_assign < idx_create_ball, 'spriteH assignment must come before ball.createSprite'
    assert idx_spriteW_assign < idx_create_shadow, 'spriteW assignment must come before shadow.createSprite' 
