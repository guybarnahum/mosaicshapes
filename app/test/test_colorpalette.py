import os
import sys
import unittest

from PIL import Image

from colorpalette import ColorPalette

parent = os.path.abspath(".")
sys.path.insert(1, parent)



class TestColorPalette(unittest.TestCase):
    def setUp(self):
        self.pal = ColorPalette()
        self.pal.quantize("../input/bryan.jpg", 64)
        pass

    def tearDown(self):
        pass

    def test_translate_color(self):
        r, g, b = (100, 0, 0)
        self.pal.translate_color(color=(r, g, b))

    def test_apply_palette_to_image(self):
        self.pal.quantize("../input/bryan.jpg", 12)
        # self.pal.apply_palette_to_image(china)
        # self.pal.apply_palette_to_image(io.imread("./input/bryan.jpg"))
        self.pal.apply_palette_to_image(Image.open("./input/bryan.jpg"))

    # def test_quantize(self):


if __name__ == "__main__":
    unittest.main()
