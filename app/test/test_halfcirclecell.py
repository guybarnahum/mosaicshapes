

import unittest

import os, sys
parent = os.path.abspath('.')
sys.path.insert(1, parent)

from PIL import Image
import util
import numpy as np
from skimage import io, feature
from shapes.halfcirclecell import HalfCircleCell
from shapes.cell import Direction
from colorpalette import ColorPalette

class TestHalfCircleCell(unittest.TestCase):

    def setUp(self):
        pass
       
    def tearDown(self):
        pass

    def test_draw(self):

        pcell = HalfCircleCell(size=(10,10), base_colors=[(100,100,100)], second_colors=[(200,200,200)], direction=Direction.top,)
        pcell.draw().show()
        pcell = HalfCircleCell(size=(500,500), base_colors=[(100,100,100)], second_colors=[(200,200,200)], direction=Direction.top)
        pcell.draw()
        pcell = HalfCircleCell(size=(200,200), base_colors=[(100,100,100)], second_colors=[(200,200,200)], direction=Direction.right)
        pcell.draw()
        pcell = HalfCircleCell(size=(200,200), base_colors=[(100,100,100)], second_colors=[(200,200,200)], direction=Direction.bottom)
        pcell.draw()
        pcell = HalfCircleCell(size=(200,200), base_colors=[(100,100,100)], second_colors=[(200,200,200)], direction=Direction.left)
        pcell.draw()

if __name__ == '__main__':
    unittest.main()