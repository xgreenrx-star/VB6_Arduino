import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.editor import CodeEditor

app = QApplication.instance() or QApplication([])

class TestEditorSnippets(unittest.TestCase):
    def setUp(self):
        self.ed = CodeEditor()

    def test_for_snippet_expansion(self):
        self.ed.setPlainText('for')
        cursor = self.ed.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.ed.setTextCursor(cursor)
        # Select word to simulate user state
        cursor.select(cursor.SelectionType.WordUnderCursor)
        self.ed.setTextCursor(cursor)
        self.assertEqual(self.ed.text_under_cursor().lower(), 'for')
        expanded = self.ed.snippet_manager.try_expand_snippet(self.ed)
        self.assertTrue(expanded)
        first_line = self.ed.toPlainText().splitlines()[0]
        self.assertTrue(first_line.strip().lower().startswith('for'))

    def test_snippet_field_selection(self):
        # Ensure first placeholder is selected after expansion
        self.ed.setPlainText('sub')
        cursor = self.ed.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.WordUnderCursor)
        self.ed.setTextCursor(cursor)
        expanded = self.ed.snippet_manager.try_expand_snippet(self.ed)
        self.assertTrue(expanded)
        # There should be a selection for the first field
        sel = self.ed.textCursor().selectedText()
        self.assertTrue(len(sel) > 0)

if __name__ == '__main__':
    unittest.main()
