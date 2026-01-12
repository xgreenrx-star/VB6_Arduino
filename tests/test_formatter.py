import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestFormatter(unittest.TestCase):
    def test_format_document_simple(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title='Fmt')
        ed = mw.get_current_editor()
        src = """
Sub Foo()
If X=1 Then
Y=2
End If
End Sub
"""
        # Remove indentation and format
        ed.setPlainText(src)
        ed.format_document()
        out = ed.toPlainText()
        # Check that Y=2 line is indented
        self.assertIn('\n        Y=2\n', out)

if __name__ == '__main__':
    unittest.main()
