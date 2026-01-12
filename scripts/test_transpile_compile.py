#!/usr/bin/env python3
"""Simple smoke test: transpile Amiga Boing Ball and run g++ -fsyntax-only with fake headers."""
from pathlib import Path
from vb2arduino.transpiler import transpile_string

src = Path('examples/boing_ball_amiga/boing_ball_amiga.vb').read_text()
cpp = transpile_string(src)
out = Path('generated_test_smoke')
out.mkdir(exist_ok=True)
(out / 'main.cpp').write_text(cpp)
# Write platformio-style fake headers include path
fake = Path('build/fake_arduino')
if not fake.exists():
    raise SystemExit('Fake Arduino headers missing (run from repo root)')
import subprocess
cmd = ['g++','-std=gnu++17','-fsyntax-only','-I'+str(fake),str(out / 'main.cpp')]
print('Running:', ' '.join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print('Return code:', proc.returncode)
if proc.stdout:
    print('STDOUT:\n', proc.stdout)
if proc.stderr:
    print('STDERR:\n', proc.stderr)
if proc.returncode != 0:
    raise SystemExit('Syntax check failed')
print('Syntax check passed')
