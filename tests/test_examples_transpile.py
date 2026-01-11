import subprocess
from pathlib import Path
from vb2arduino.transpiler import transpile_string

EXAMPLES = [
    'examples/blink/blink.vb',
    'examples/serial_echo/serial_echo.vb',
    'examples/button_led/button_led.vb',
]


def test_examples_transpile_and_syntax_check(tmp_path):
    fake = Path('build/fake_arduino')
    assert fake.exists(), 'Fake Arduino headers missing; run tests from repo root'
    for ex in EXAMPLES:
        src = Path(ex).read_text()
        cpp = transpile_string(src)
        out = tmp_path / (Path(ex).stem + '.cpp')
        out.write_text(cpp)
        cmd = ['g++', '-std=gnu++17', '-fsyntax-only', f'-I{str(fake)}', str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print('Example:', ex)
            print('STDERR:\n', proc.stderr)
        assert proc.returncode == 0, f'Failed syntax check for {ex}'