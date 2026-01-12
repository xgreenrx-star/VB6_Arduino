import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestProblemsSelectionJump(unittest.TestCase):
    def test_selection_jumps_to_line(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title="Test")
        ed = mw.get_current_editor()
        ed.setPlainText("line1\nline2\nline3\n")
        diags = [{"file": "<unsaved>", "line": 2, "col": 1, "severity": "warning", "message": "Test select"}]
        mw._show_problems_from_diags(diags)
        item = mw.problems_widget.topLevelItem(0)
        mw.problems_widget.setCurrentItem(item)
        # After selection, editor cursor should be on the diagnostic line
        cursor = ed.textCursor()
        self.assertEqual(cursor.blockNumber() + 1, 2)

if __name__ == '__main__':
    unittest.main()
