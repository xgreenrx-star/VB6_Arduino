from vb2arduino.transpiler import transpile_string
from pathlib import Path


def test_red_tiles_present_in_cpp():
    src = Path('examples/boing_ball_s3_147/boing_ball_s3_147.vb').read_text(encoding='utf-8')
    cpp = transpile_string(src)
    # Ensure red triangles are emitted directly (fillTriangle called with COLOR_RED/TFT_RED)
    assert 'fillTriangle' in cpp
    assert 'TFT_RED' in cpp or 'COLOR_RED' in cpp
    # Prefer direct red triangle fills rather than relying on colorTile variable
    assert 'fillTriangle(spriteCX, spriteCY' in cpp and ('TFT_RED' in cpp or 'COLOR_RED' in cpp)
