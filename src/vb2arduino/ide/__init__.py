"""Asic (Arduino Basic) IDE - Modern Arduino IDE for Basic-like development."""

from PyQt6.QtWidgets import QApplication
import sys


def main():
    """Entry point for Asic (Arduino Basic) IDE."""
    from vb2arduino.ide.main_window import MainWindow
    
    app = QApplication(sys.argv)
    app.setApplicationName("Asic (Arduino Basic) IDE")
    app.setOrganizationName("Asic (Arduino Basic)")
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
