from PyQt6.QtWidgets import QApplication
app = QApplication([])
from vb2arduino.ide.main_window import MainWindow
window = MainWindow()
window.show()
app.exec()
