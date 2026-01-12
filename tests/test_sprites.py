import unittest
from vb2arduino import transpile_string

class TestSprites(unittest.TestCase):
    def test_create_sprite_and_methods(self):
        src = """
        CREATE_SPRITE ball, 16, 16
        SPRITE_FILL_ELLIPSE ball, 8, 8, 4, 4, COLOR_RED
        SPRITE_PUSH ball, 20, 30
        SPRITE_DELETE ball
        """
        cpp = transpile_string(src)
        # Creation in setup (createSprite) and methods should appear
        self.assertIn('.createSprite(16, 16);', cpp)
        self.assertIn('.fillEllipse(', cpp)
        self.assertIn('.pushSprite(20, 30);', cpp)
        self.assertIn('.deleteSprite(', cpp)  # delete emits deleteSprite or similar

if __name__ == '__main__':
    unittest.main()
