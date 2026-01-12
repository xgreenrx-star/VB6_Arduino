import unittest
from vb2arduino import transpile_string

class TestDimHoist(unittest.TestCase):
    def test_dim_hoisted_once(self):
        src = """
        Dim x As Integer
        Sub Setup()
            Dim x As Integer
            x = 1
        End Sub
        """
        cpp = transpile_string(src)
        # Ensure x not declared twice as int x; appears only once in globals or setup
        self.assertTrue(cpp.count('int x') <= 1)

if __name__ == '__main__':
    unittest.main()
