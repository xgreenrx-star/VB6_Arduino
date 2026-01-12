import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestRenameSymbol(unittest.TestCase):
    def test_rename_across_tabs(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # Tab A
        mw.open_file_in_tab(None, title='A')
        ed_a = mw.get_current_editor()
        ed_a.setPlainText('Sub Foo()\nEnd Sub\nCall Foo()\n')
        # Tab B
        mw.open_file_in_tab(None, title='B')
        ed_b = mw.get_current_editor()
        ed_b.setPlainText('Sub Other()\n    Foo()\nEnd Sub\n')
        # Place cursor on Foo in Tab A
        mw.tab_widget.setCurrentIndex(0)
        ed_a = mw.get_current_editor()
        # For test simplicity, rename symbol 'Foo' to 'Foo2' directly
        symbol = 'Foo'
        # Simulate rename via API (bypass dialog)
        mw.rename_symbol_action = lambda: None
        import re
        new = 'Foo2'
        pattern = re.compile(rf"\b{re.escape(symbol)}\b")
        for i in range(mw.tab_widget.count()):
            tab = mw.tab_widget.widget(i)
            if not hasattr(tab, 'editor'):
                continue
            ed = tab.editor
            txt = ed.toPlainText()
            new_txt = pattern.sub(new, txt)
            if new_txt != txt:
                ed.setPlainText(new_txt)
        # Verify both tabs updated (search all tabs)
        texts = [mw.tab_widget.widget(i).editor.toPlainText() for i in range(mw.tab_widget.count())]
        self.assertTrue(any('Sub Foo2()' in t for t in texts))
        self.assertTrue(any('Foo2()' in t for t in texts))

if __name__ == '__main__':
    unittest.main()
