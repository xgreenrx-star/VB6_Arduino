import os
import sys
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

def main():
    from src.vb2arduino.ide.main_window import MainWindow
    app = QApplication([])
    w = MainWindow()
    # Ensure a concrete board is selected
    if w.board_combo.currentData() is None:
        for i in range(w.board_combo.count()):
            if w.board_combo.itemData(i) == "esp32dev":
                w.board_combo.setCurrentIndex(i)
                break
    w.verify_code()
    print("[ok] verify_code completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
