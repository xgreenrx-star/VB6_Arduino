import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from vb2arduino.ide.main_window import MainWindow

class TestStatusLabelFlash(unittest.TestCase):
    def test_flash_changes_and_reverts_style(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        lbl = mw.status_problems
        # Ensure no initial custom style
        initial = lbl.styleSheet()
        # Flash with short duration
        lbl.flash(color="#00FF00", duration_ms=30)
        # Immediately should have a non-empty style indicating flash
        self.assertTrue(lbl.styleSheet() != initial)
        # Wait longer than duration to allow restore
        QTest.qWait(100)
        self.assertEqual(lbl.styleSheet(), initial)

if __name__ == '__main__':
    unittest.main()
