import subprocess
from pathlib import Path
from vb2arduino.transpiler import transpile_string


def test_boing_ball_transpiles_and_syntax_checks(tmp_path):
    src = Path('examples/boing_ball_amiga/boing_ball_amiga.vb').read_text()
    cpp = transpile_string(src)
    out = tmp_path / 'main.cpp'
    out.write_text(cpp)
    fake = Path('build/fake_arduino')
    assert fake.exists(), "Fake Arduino headers missing; run tests from repo root"
    cmd = ['g++', '-std=gnu++17', '-fsyntax-only', f'-I{str(fake)}', str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print('STDOUT:\n', proc.stdout)
        print('STDERR:\n', proc.stderr)
    assert proc.returncode == 0, 'Generated C++ failed syntax check'