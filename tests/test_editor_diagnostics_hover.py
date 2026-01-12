import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPoint
from vb2arduino.ide.editor import CodeEditor

class TestEditorDiagnosticsHover(unittest.TestCase):
    def test_diagnostics_at_pos(self):
        app = QApplication.instance() or QApplication([])
        ed = CodeEditor()
        ed.show()
        app.processEvents()
        ed.setPlainText("line1\nline2\nline3\n")
        # Set a diagnostic on line 2
        diags = [{"file":"<unsaved>", "line":2, "col":1, "severity":"warning", "message":"Test issue"}]
        ed.set_diagnostics(diags)
        app.processEvents()
        # Find block for line 2
        block = ed.document().findBlockByNumber(1)
        top = ed.blockBoundingGeometry(block).translated(ed.contentOffset()).top()
        pos = QPoint(2, int(top + 2))
        found = ed.diagnostics_at_pos(pos)
        self.assertTrue(found)
        self.assertEqual(found[0]['message'], 'Test issue')

if __name__ == '__main__':
    unittest.main()
