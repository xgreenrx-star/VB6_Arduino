import unittest
from vb2arduino import transpile_string

class TestEveryTimer(unittest.TestCase):
    def test_every_transpiles_to_helper_and_loop_check(self):
        src = """
        Every 1000 Do
            SerialPrint "tick"
        End Do
        """
        cpp = transpile_string(src)
        # Should contain a helper function and a loop check using millis
        self.assertIn('void _every_task_1()', cpp)
        self.assertIn('if (millis() - _every_last_1 >= 1000)', cpp)
        self.assertIn('_every_task_1();', cpp)

if __name__ == '__main__':
    unittest.main()
