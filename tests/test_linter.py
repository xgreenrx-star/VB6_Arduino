import unittest
from vb2arduino.linter import run_linter_on_text

class TestLinter(unittest.TestCase):
    def test_debug_draw_detection(self):
        src = """
        ' simple draw
        tft.fillTriangle(x1, y1, x2, y2, x3, y3, TFT_RED)
        SPRITE_FILL_ELLIPSE 10, 10, 5, 5, COLOR_RED
        """
        diags = run_linter_on_text(src, path="example.vb")
        rules = {d['rule'] for d in diags}
        self.assertIn('debug-draw', rules)
        self.assertEqual(len([d for d in diags if d['rule']=='debug-draw']), 2)

    def test_wildcard_import(self):
        src = "from mymodule import *\nfrom other import something"
        diags = run_linter_on_text(src, path="imp.vb")
        rules = [d['rule'] for d in diags]
        self.assertIn('wildcard-import', rules)

    def test_baud_info(self):
        src = "Baud rate: 115200\nSome other text 9600"
        diags = run_linter_on_text(src, path="baud.vb")
        # both baud mentions should be detected as info-level
        ids = [d['rule'] for d in diags]
        self.assertIn('suspicious-baud', ids)
        self.assertTrue(all(d['severity'] in ('info','warning') for d in diags))

if __name__ == '__main__':
    unittest.main()
