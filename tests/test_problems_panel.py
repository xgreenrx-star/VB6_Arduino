import os
import tempfile
import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestProblemsPanel(unittest.TestCase):
    def test_linter_runs_on_save_and_populates_problems(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # Open an untitled editor and set text that triggers linter
        mw.open_file_in_tab(None, title="Test")
        editor_widget = mw.get_current_editor()
        editor_widget.setPlainText("tft.fillTriangle(x1, y1, x2, y2, x3, y3, TFT_RED)\nprint 'Hello'\n")
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vb', mode='w', encoding='utf-8') as tf:
            tf.write(editor_widget.toPlainText())
            tmpname = tf.name
        try:
            res = mw._save_to_file(tmpname)
            self.assertTrue(res)
            # Linter should have populated problems widget
            count = mw.problems_widget.topLevelItemCount()
            self.assertGreater(count, 0)
            # Ensure at least one item mentions Debug draw rule via message/snippet
            texts = [mw.problems_widget.topLevelItem(i).text(1) for i in range(count)]
            self.assertTrue(any('overlay' in t.lower() or 'debug' in t.lower() for t in texts))
            # Inline diagnostics should be set for the current editor
            ed = mw.get_current_editor()
            self.assertTrue(hasattr(ed, 'diagnostics'))
            self.assertGreater(len(ed.diagnostics), 0)
        finally:
            os.unlink(tmpname)

if __name__ == '__main__':
    unittest.main()
