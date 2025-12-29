#!/usr/bin/env python3
"""
Standalone entry point for Asic (Arduino Basic) IDE.
Used by PyInstaller to bundle the application.
"""

import sys
import os

# Ensure the package is importable
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from vb2arduino.ide.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
