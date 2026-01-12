import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestSignatureHelp(unittest.TestCase):
    def test_get_procedure_signature(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title='Sig')
        ed = mw.get_current_editor()
        ed.setPlainText('Sub Foo(a, b)\nEnd Sub\n')
        ed.parse_code()
        sig = ed.get_procedure_signature('Foo')
        self.assertEqual(sig, 'Foo(a, b)')

if __name__ == '__main__':
    unittest.main()
