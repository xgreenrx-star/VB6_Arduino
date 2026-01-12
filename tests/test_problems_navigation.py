import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestProblemsNavigation(unittest.TestCase):
    def test_next_prev_navigation(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title="Test")
        ed = mw.get_current_editor()
        ed.setPlainText("l1\nl2\nl3\nl4\n")
        diags = [
            {"file":"<unsaved>", "line":2, "col":1, "severity":"warning", "message":"A"},
            {"file":"<unsaved>", "line":3, "col":1, "severity":"warning", "message":"B"},
            {"file":"<unsaved>", "line":4, "col":1, "severity":"info", "message":"C"},
        ]
        mw._show_problems_from_diags(diags)
        # Next problem (no selection) -> first (line 2)
        mw.next_problem()
        from PyQt6.QtCore import Qt
        cur = mw.problems_widget.currentItem()
        self.assertIsNotNone(cur)
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        self.assertEqual(int(d['line']), 2)
        # Next -> line 3
        mw.next_problem()
        cur = mw.problems_widget.currentItem()
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        self.assertEqual(int(d['line']), 3)
        # Prev -> back to line 2
        mw.prev_problem()
        cur = mw.problems_widget.currentItem()
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        self.assertEqual(int(d['line']), 2)

if __name__ == '__main__':
    unittest.main()
