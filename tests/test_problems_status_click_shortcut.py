import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow
from PyQt6.QtCore import Qt

class TestProblemsStatusClickShortcut(unittest.TestCase):
    def test_status_label_click_opens_panel(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # Ensure hidden initially
        mw.problems_dock.setVisible(False)
        self.assertFalse(mw.problems_dock.isVisible())
        # Simulate click via signal emit -> should trigger the action (check state toggles)
        mw.status_problems.clicked.emit()
        self.assertTrue(mw.toggle_problems_action.isChecked())

    def test_toggle_problems_shortcut(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # The action should have the expected shortcut
        sc = mw.toggle_problems_action.shortcut().toString()
        self.assertIn('Ctrl+Shift+I', sc)
        # Trigger action to toggle -> check the action's checked state toggles
        mw.toggle_problems_action.trigger()
        self.assertTrue(mw.toggle_problems_action.isChecked())
        mw.toggle_problems_action.trigger()
        self.assertFalse(mw.toggle_problems_action.isChecked())

if __name__ == '__main__':
    unittest.main()
