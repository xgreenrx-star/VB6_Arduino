"""Asic (Arduino Basic) IDE - Arduino-like IDE for VB6-style development."""

from PyQt6.QtWidgets import QApplication
import sys


def main():
    """Entry point for Asic (Arduino Basic) IDE."""
    from vb2arduino.ide.main_window import MainWindow
    
    app = QApplication(sys.argv)
    app.setApplicationName("Asic (Arduino Basic) IDE")
    app.setOrganizationName("Asic (Arduino Basic)")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
