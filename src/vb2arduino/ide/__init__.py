"""VB2Arduino IDE - Arduino-like IDE for VB6-style development."""

from PyQt6.QtWidgets import QApplication
import sys


def main():
    """Entry point for VB2Arduino IDE."""
    from vb2arduino.ide.main_window import MainWindow
    
    app = QApplication(sys.argv)
    app.setApplicationName("VB2Arduino IDE")
    app.setOrganizationName("VB2Arduino")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
