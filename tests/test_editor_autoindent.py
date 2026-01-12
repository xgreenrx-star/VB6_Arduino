import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.editor import CodeEditor

app = QApplication.instance() or QApplication([])

class TestEditorAutoIndent(unittest.TestCase):
    def setUp(self):
        self.ed = CodeEditor()

    def test_enter_indents(self):
        self.ed.setPlainText('If True Then')
        cursor = self.ed.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.ed.setTextCursor(cursor)
        handled = self.ed.auto_indenter.handle_return_key(self.ed)
        self.assertTrue(handled)
        lines = self.ed.toPlainText().splitlines()
        self.assertEqual(lines[0].strip(), 'If True Then')
        self.assertTrue(lines[1].startswith(' ' * 4))

if __name__ == '__main__':
    unittest.main()
