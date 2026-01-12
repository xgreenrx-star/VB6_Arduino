import unittest
from vb2arduino import transpile_string

class TestEnum(unittest.TestCase):
    def test_enum_transpiles(self):
        src = """
        Enum Colors
            RED = 1
            BLUE
        End Enum
        """
        cpp = transpile_string(src)
        self.assertIn('enum Colors', cpp)
        self.assertIn('RED = 1', cpp)
        self.assertIn('BLUE', cpp)

if __name__ == '__main__':
    unittest.main()
