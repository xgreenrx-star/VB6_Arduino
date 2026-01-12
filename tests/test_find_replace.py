import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.editor import CodeEditor
from vb2arduino.ide.find_replace_dialog import FindReplaceDialog

app = QApplication.instance() or QApplication([])

class TestFindReplace(unittest.TestCase):
    def setUp(self):
        self.ed = CodeEditor()
        self.ed.setPlainText('alpha beta alpha gamma alpha')
        self.fd = FindReplaceDialog(self.ed)

    def test_find_next_and_previous(self):
        self.fd.find_edit.setText('alpha')
        self.fd.find_next()
        cur = self.ed.textCursor()
        self.assertEqual(cur.selectionStart(), 0)
        self.fd.find_next()
        cur = self.ed.textCursor()
        self.assertEqual(cur.selectionStart(), 11)

    def test_replace_all(self):
        self.fd.find_edit.setText('alpha')
        self.fd.replace_edit.setText('ALPHA')
        self.fd.replace_all()
        self.assertEqual(self.ed.toPlainText(), 'ALPHA beta ALPHA gamma ALPHA')

if __name__ == '__main__':
    unittest.main()
