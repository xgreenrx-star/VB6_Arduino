import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestAccessibility(unittest.TestCase):
    def test_widget_accessible_names(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        self.assertEqual(mw.verify_btn.accessibleName(), 'Compile Button')
        self.assertEqual(mw.upload_btn.accessibleName(), 'Upload Button')
        self.assertEqual(mw.board_combo.accessibleName(), 'Board Selector')
        # Serial monitor combos
        self.assertTrue(hasattr(mw, 'serial_monitor'))
        self.assertEqual(mw.serial_monitor.baud_combo.accessibleName(), 'Baud Rate Selector')
        # Plotter via serial monitor
        self.assertTrue(hasattr(mw.serial_monitor, 'plotter'))
        self.assertEqual(mw.serial_monitor.plotter.yrange_combo.accessibleName(), 'Y Range Selector')

    def test_high_contrast_toggle_persists(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # Ensure default is False
        initial = mw.settings.get('editor', 'high_contrast', False)
        mw.apply_high_contrast(not initial)
        self.assertEqual(mw.settings.get('editor', 'high_contrast', None), (not initial))
        # revert
        mw.apply_high_contrast(initial)
        self.assertEqual(mw.settings.get('editor', 'high_contrast', None), initial)

if __name__ == '__main__':
    unittest.main()
