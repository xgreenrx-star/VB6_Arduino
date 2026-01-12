import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.editor import CodeEditor

app = QApplication.instance() or QApplication([])

class TestEditorCompleter(unittest.TestCase):
    def setUp(self):
        self.ed = CodeEditor()

    def test_base_completions_loaded(self):
        self.assertTrue(len(self.ed.base_completions) > 0)

    def test_completer_prefix(self):
        # Use a known prefix (e.g., 'Ser' should match SerialPrintLine etc.)
        prefix = 'Ser'
        self.ed.completer.setCompletionPrefix(prefix)
        count = self.ed.completer.completionCount()
        self.assertTrue(count > 0)

if __name__ == '__main__':
    unittest.main()
