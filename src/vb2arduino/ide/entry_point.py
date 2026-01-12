#!/usr/bin/env python3
"""
Standalone entry point for Asic (Arduino Basic) IDE.
Used by PyInstaller to bundle the application.

Usage:
    vb2arduino-ide              # Open IDE normally
    vb2arduino-ide <file.vb>    # Open IDE and load a VB file
"""
import sys
import os
import argparse
import argparse

# Ensure the package is importable
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)
def main():
    from PyQt6.QtWidgets import QApplication
    from vb2arduino.ide.main_window import MainWindow
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="VB2Arduino IDE - VB6-like language for Arduino/ESP32",
        add_help=False  # We'll handle help manually to avoid Qt conflicts
    )
    parser.add_argument("file", nargs="?", default=None, help="VB file to open")
    # Extract our arguments before passing to Qt
    args, remaining = parser.parse_known_args(sys.argv[1:])
    # Reconstruct sys.argv for Qt (without our custom arguments)
    sys.argv = [sys.argv[0]] + remaining
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow()
    # If a file was provided on command line, load it
    if args.file:
        window.load_file_on_startup(args.file)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
