import unittest
from vb2arduino import transpile_string

class TestForEach(unittest.TestCase):
    def test_for_each_transpiles(self):
        src = """
        Dim arr(2) As Integer
        For Each x In arr
            x = x + 1
        Next
        """
        cpp = transpile_string(src)
        self.assertIn('for (auto& x : arr)', cpp)
        self.assertIn('x = x + 1;', cpp)

if __name__ == '__main__':
    unittest.main()
