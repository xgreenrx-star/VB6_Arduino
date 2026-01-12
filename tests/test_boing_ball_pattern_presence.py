from vb2arduino.transpiler import transpile_string
from pathlib import Path


def test_checkered_colors_present():
    src = Path('examples/boing_ball_s3_147/boing_ball_s3_147.vb').read_text(encoding='utf-8')
    cpp = transpile_string(src)
    # Check that both color constants are used in triangle drawing logic
    assert 'TFT_WHITE' in cpp or 'COLOR_WHITE' in cpp
    assert 'TFT_RED' in cpp or 'COLOR_RED' in cpp
    # Ensure triangles are drawn with local coords x2l/x3l
    assert 'x2l' in cpp and 'x3l' in cpp
