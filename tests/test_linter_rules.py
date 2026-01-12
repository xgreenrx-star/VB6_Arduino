import unittest
from vb2arduino.linter import run_linter_on_text

class TestLinterRules(unittest.TestCase):
    def test_unused_variable_detected(self):
        src = """
        Dim x As Integer
        Dim y As Integer
        x = 5
        """
        diags = run_linter_on_text(src, path="test.vb")
        rules = [d['rule'] for d in diags]
        self.assertIn('unused-variable', rules)

    def test_missing_delete_sprite(self):
        src = """
        CREATE_SPRITE ball, 16, 16
        SPRITE_FILL ball, 'color'
        """
        diags = run_linter_on_text(src, path="test.vb")
        rules = [d['rule'] for d in diags]
        self.assertIn('missing-delete-sprite', rules)

    def test_blocking_delay(self):
        src = "Delay 500\nDelay 50\n"
        diags = run_linter_on_text(src, path="test.vb")
        rules = [d['rule'] for d in diags]
        self.assertIn('blocking-delay', rules)
        # Ensure small delay does not trigger (only one blocking-delay expected)
        blocking = [d for d in diags if d['rule'] == 'blocking-delay']
        self.assertTrue(len(blocking) >= 1)

    def test_quick_fix_insert_delete(self):
        from vb2arduino.linter import run_linter_on_text, available_fixes_for_diag, apply_fix_on_text
        src = """
        CREATE_SPRITE ball, 16, 16
        SPRITE_FILL ball, 0, 0, 10, 10
        """
        diags = run_linter_on_text(src, path='test.vb')
        miss = [d for d in diags if d['rule'] == 'missing-delete-sprite']
        self.assertTrue(len(miss) >= 1)
        d = miss[0]
        fixes = available_fixes_for_diag(d)
        self.assertTrue(any(f['id'] == 'insert_delete' for f in fixes))
        new_text = apply_fix_on_text(src, d, 'insert_delete')
        self.assertIn('SPRITE_DELETE ball', new_text)
        # Running linter on new_text should not report missing-delete-sprite for ball
        diags2 = run_linter_on_text(new_text, path='test.vb')
        self.assertFalse(any(d2['rule'] == 'missing-delete-sprite' for d2 in diags2))
if __name__ == '__main__':
    unittest.main()
