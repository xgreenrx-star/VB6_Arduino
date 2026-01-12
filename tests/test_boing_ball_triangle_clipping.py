from vb2arduino.transpiler import transpile_string
from pathlib import Path


def test_triangle_vertices_clipped():
    src = Path('examples/boing_ball_s3_147/boing_ball_s3_147.vb').read_text(encoding='utf-8')
    cpp = transpile_string(src)
    assert 'x2l' in cpp and 'x3l' in cpp, 'Expected local triangle coordinates x2l/x3l to be present'
    # Ensure triangles use the local coords
    assert 'fillTriangle(spriteCX, spriteCY, x2l, y2l, x3l, y3l' in cpp or 'fillTriangle(spriteCX, spriteCY, x2l, y2l, x3l, y3l' in cpp
    # Check there's a conditional guarding the triangle draw
    assert 'if ((' in cpp and '<= BALL_RADIUS * BALL_RADIUS' in cpp
