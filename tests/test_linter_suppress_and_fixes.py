import unittest
from vb2arduino.linter import run_linter_on_text, available_fixes_for_diag, apply_fix_on_text

class TestLinterSuppressAndFixes(unittest.TestCase):
    def test_suppress_line(self):
        src = """
        ' LINTER:DISABLE blocking-delay
        Delay 1000
        """
        diags = run_linter_on_text(src, path='test.vb')
        self.assertFalse(any(d['rule'] == 'blocking-delay' for d in diags))

    def test_replace_with_every_fix(self):
        src = "Delay 500\n"
        diags = run_linter_on_text(src, path='test.vb')
        self.assertTrue(any(d['rule'] == 'blocking-delay' for d in diags))
        d = [d for d in diags if d['rule'] == 'blocking-delay'][0]
        fixes = available_fixes_for_diag(d)
        self.assertTrue(any(f['id'] == 'replace_with_every' for f in fixes))
        new = apply_fix_on_text(src, d, 'replace_with_every')
        self.assertIn('Every 500 Do', new)
        self.assertIn("' Delay 500", new)

if __name__ == '__main__':
    unittest.main()
