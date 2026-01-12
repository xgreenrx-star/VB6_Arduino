import os
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication
from src.vb2arduino.ide.main_window import MainWindow


def test_parse_compile_errors_maps_redeclaration_to_cpp_line(tmp_path, monkeypatch):
    # Create a fake generated main.cpp with a declaration of 't' at line 10
    cpp = "\n".join([f"// line {i}" for i in range(1, 9)]) + "\nint t = 0;\n" + "\n".join([f"// line {i}" for i in range(11, 40)])
    cpp_file = tmp_path / "main.cpp"
    cpp_file.write_text(cpp, encoding="utf-8")

    # Simulate a compiler stderr that reports redeclaration in another file
    stderr = "other.c:5: error: redeclaration of 't'\n"

    # Ensure Qt runs in headless mode for tests
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    w = MainWindow()

    errors = w._parse_compile_errors(stderr, cpp_file)
    # Expect at least one error mapped to the line where 'int t' was declared
    # New parser returns tuples of shape (cpp_line, level, msg, orig_ref, ambiguous)
    assert errors, "Expected parser to return at least one mapped error"

    # Find a matching entry for token 't'
    matched = None
    for e in errors:
        if len(e) >= 5 and e[3] is not None:
            matched = e
            break
    assert matched is not None, f"No mapped error with orig_ref found in {errors}"
    cpp_line, level, msg, orig_ref, ambiguous = matched
    assert cpp_line == 9, f"Expected mapping to line 9 in generated cpp, got {cpp_line}"
    assert 'redeclaration of' in msg
    assert ambiguous is True
    assert 'other.c:5' in orig_ref
