import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestProblemsStatusIndicator(unittest.TestCase):
    def test_status_updates_on_navigation(self):
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
        # Initially no selection -> shows total
        self.assertEqual(mw.status_problems.text(), 'Problems: 3')
        # Next problem -> selects first
        mw.next_problem()
        self.assertEqual(mw.status_problems.text(), 'Problem 1/3')
        # Next -> second
        mw.next_problem()
        self.assertEqual(mw.status_problems.text(), 'Problem 2/3')
        # Prev -> back to first
        mw.prev_problem()
        self.assertEqual(mw.status_problems.text(), 'Problem 1/3')

if __name__ == '__main__':
    unittest.main()
