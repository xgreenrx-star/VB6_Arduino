import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

def main():
    from src.vb2arduino.ide.main_window import MainWindow
    app = QApplication([])
    w = MainWindow()
    # Headless-friendly: suppress popups and open a known example
    w.settings.set("editor", "show_compile_success_popup", False)
    w.settings.set("editor", "show_compile_failure_popup", False)
    example_path = Path(__file__).resolve().parents[1] / "examples" / "blink.vb"
    if example_path.exists():
        w.open_file_in_tab(str(example_path))
    # Prefer an ESP32 board; fall back to existing logic
    preferred_board = "esp32-s3-devkitm-1"
    set_board = False
    for i in range(w.board_combo.count()):
        if w.board_combo.itemData(i) == preferred_board:
            w.board_combo.setCurrentIndex(i)
            set_board = True
            break
    # Ensure a concrete board is selected
    if not set_board and w.board_combo.currentData() is None:
        for i in range(w.board_combo.count()):
            if w.board_combo.itemData(i) == "esp32dev":
                w.board_combo.setCurrentIndex(i)
                break
    w.verify_code()
    print("[ok] verify_code completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
