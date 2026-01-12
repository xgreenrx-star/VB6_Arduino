import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestQuickFix(unittest.TestCase):
    def test_apply_quick_fix_removes_debug_draw_line(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title="TestFix")
        ed = mw.get_current_editor()
        # Insert a debug draw line and another line
        ed.setPlainText("First line\ntft.fillTriangle(x1, y1, x2, y2, x3, y3, TFT_RED)\nSecond line\n")
        # Run linter
        mw.run_linter()
        count = mw.problems_widget.topLevelItemCount()
        self.assertGreater(count, 0)
        # Select the debug draw problem
        found = False
        from PyQt6.QtCore import Qt
        for i in range(count):
            item = mw.problems_widget.topLevelItem(i)
            d = item.data(0, Qt.ItemDataRole.UserRole)
            if d and d.get('rule') == 'debug-draw':
                mw.problems_widget.setCurrentItem(item)
                found = True
                break
        self.assertTrue(found)
        # Apply quick fix
        mw.apply_quick_fix_for_current_problem()
        # The debug draw line should be removed from editor text
        txt = ed.toPlainText()
        self.assertNotIn('tft.fillTriangle', txt)
        # Re-run linter and ensure no debug-draw diagnostics remain
        mw.run_linter()
        diags = [mw.problems_widget.topLevelItem(i).data(0, 0) for i in range(mw.problems_widget.topLevelItemCount())]
        self.assertFalse(any(d and d.get('rule') == 'debug-draw' for d in diags))

if __name__ == '__main__':
    unittest.main()
