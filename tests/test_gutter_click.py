import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPoint
from vb2arduino.ide.main_window import MainWindow

class TestGutterClick(unittest.TestCase):
    def test_gutter_click_selects_problem(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title="Test")
        ed = mw.get_current_editor()
        ed.setPlainText("line1\nline2\nline3\n")
        # Prepare diagnostic bound to unsaved file (current editor)
        diags = [{"file": "<unsaved>", "line": 2, "col": 1, "severity": "warning", "message": "Test gutter"}]
        # Populate problems widget and editor diagnostics
        mw._show_problems_from_diags(diags)
        # Compute y position inside line 2
        block = ed.document().findBlockByNumber(1)
        top = ed.blockBoundingGeometry(block).translated(ed.contentOffset()).top()
        pos = QPoint(2, int(top + 2))
        # Simulate gutter click
        ed.on_gutter_click(pos)
        # Problems widget should have current item selected
        cur = mw.problems_widget.currentItem()
        self.assertIsNotNone(cur)
        from PyQt6.QtCore import Qt
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        self.assertEqual(int(d['line']), 2)

if __name__ == '__main__':
    unittest.main()
