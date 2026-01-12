import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from vb2arduino.ide.main_window import MainWindow
from PyQt6.QtWidgets import QGraphicsOpacityEffect

class TestStatusLabelOpacity(unittest.TestCase):
    def test_flash_opacity_animates_and_restores(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        lbl = mw.status_problems
        # Ensure no effect initially
        self.assertTrue(lbl.graphicsEffect() is None)
        # Flash with a short duration
        lbl.flash(duration_ms=50)
        # Immediately after, effect should be present and be QGraphicsOpacityEffect
        eff = lbl.graphicsEffect()
        self.assertIsInstance(eff, QGraphicsOpacityEffect)
        # Wait longer than duration to allow restore
        QTest.qWait(120)
        self.assertTrue(lbl.graphicsEffect() is None)

if __name__ == '__main__':
    unittest.main()
