import unittest
from PyQt6.QtWidgets import QApplication
from vb2arduino.ide.main_window import MainWindow

class TestNavigation(unittest.TestCase):
    def test_go_to_definition_within_same_file(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        mw.open_file_in_tab(None, title='NavTest')
        ed = mw.get_current_editor()
        src = """Sub Foo()
    ' body
End Sub

Sub Bar()
    Foo()
End Sub
"""
        ed.setPlainText(src)
        # Place cursor on the call to Foo
        idx = ed.toPlainText().find('Foo()')
        self.assertGreater(idx, -1)
        cursor = ed.textCursor()
        cursor.setPosition(idx + 1)
        ed.setTextCursor(cursor)
        # Invoke Go to Definition
        mw.go_to_definition()
        # After jump, current editor should have cursor at definition (line 1)
        ed_after = mw.get_current_editor()
        line_no = ed_after.textCursor().blockNumber() + 1
        self.assertEqual(line_no, 1)

    def test_find_references_across_tabs(self):
        app = QApplication.instance() or QApplication([])
        mw = MainWindow()
        # Tab A
        mw.open_file_in_tab(None, title='A')
        # Tab B
        mw.open_file_in_tab(None, title='B')
        # Ensure we set contents explicitly per tab (avoid focus/order assumptions)
        mw.tab_widget.setCurrentIndex(0)
        ed_a = mw.get_current_editor()
        ed_a.setPlainText("Sub Foo()\nEnd Sub\nCall Foo()\n")
        mw.tab_widget.setCurrentIndex(1)
        ed_b = mw.get_current_editor()
        ed_b.setPlainText("Sub Other()\n    Foo()\nEnd Sub\n")
        # Switch to tab A and put cursor on Foo in call
        mw.tab_widget.setCurrentIndex(0)
        ed_a = mw.get_current_editor()
        idx = ed_a.toPlainText().lower().find('foo()')
        self.assertGreater(idx, -1)
        cursor = ed_a.textCursor()
        cursor.setPosition(idx + 1)
        ed_a.setTextCursor(cursor)
        # Run find_references in non-dialog mode
        refs = mw.find_references(show_dialog=False)
        # Expect at least 2 references (one in each tab)
        self.assertIsInstance(refs, list)
        files = {r['tab_index'] for r in refs}
        self.assertTrue(len(files) >= 2)

if __name__ == '__main__':
    unittest.main()
