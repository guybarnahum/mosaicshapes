

import unittest
from PIL import Image
import util
import numpy as np
from skimage import io, feature
from skimage.color import rgb2grey
from trianglerect import TriangleRect
from trianglerect import Quadrant
from colorpalette import ColorPalette

class TestCompColor(unittest.TestCase):

    def setUp(self):
        pass
       
    def tearDown(self):
        pass

    def test_avg_lum(self):
        triangle = TriangleRect(size=(200,200), base_color=(100,100,100), 
            second_color=(200,200,200), n=4, sn=1, quadrant=Quadrant.top_right)
        self.assertEqual(triangle.avg_lum(), 95)

    # def test_gen_colors(self):
    #     base_color = (200,200,200)
    #     colors = CompColor.gen_colors(base_color, n=1)
    #     self.assertEqual(len(colors), 1)
    #     self.assertEqual(colors[0], base_color)

    #     colors = CompColor.gen_colors(base_color, n=2)
    #     self.assertEqual(len(colors), 2)
    #     self.assertEqual(colors, [(200.0, 200.0, 200.0), (220.0, 220.0, 220.0)])

    #     base_color = (245,245,245)
    #     colors = CompColor.gen_colors(base_color, n=2)
    #     self.assertEqual(len(colors), 2)
    #     self.assertEqual(colors, [(245.0, 245.0, 245.0), (255.0, 255.0, 255.0)])

    #     base_color = (200,200,200)
    #     colors = CompColor.gen_colors(base_color, n=3)
    #     self.assertEqual(len(colors), 3)
    #     self.assertEqual(colors, [(186.0, 186.0, 186.0), (200.0, 200.0, 200.0), (213.0, 213.0, 213.0)])

    #     base_color = (100,100,100)
    #     colors = CompColor.gen_colors(base_color, n=4)
    #     self.assertEqual(len(colors), 4)
    #     self.assertEqual(colors, [(80.0, 80.0, 80.0), (90.0, 90.0, 90.0), (100.0, 100.0, 100.0), (110.0, 110.0, 110.0)])

    def test_find_best(self):
        og_image = Image.open("./examples/test.JPEG")

        # Test lower left jaw
        cropped = og_image.crop((125,370,150,395))
        fg,bg = ColorPalette.average_colors(cropped,2)
        fg = (fg*255).astype(int)
        bg = (bg*255).astype(int)

        trect = TriangleRect.find_best(cropped, bg, fg, n=2, sn=2)
        self.assertEqual(trect.quadrant, Quadrant.top_right)

        # Test upper right ear
        crop_right_ear = og_image.crop((340-25,270-25,340+25,270+25))       
        fg,bg = ColorPalette.average_colors(crop_right_ear,2)
        fg = (fg*255).astype(int)
        bg = (bg*255).astype(int)
        trect = TriangleRect.find_best(crop_right_ear, fg, bg, n=2, sn=3)
        self.assertEqual(trect.quadrant, Quadrant.top_left)

        crop_left_ear = og_image.crop((50-25,200-25, 50+25, 200+25))
        fg,bg = ColorPalette.average_colors(crop_left_ear,2)
        fg = (fg*255).astype(int)
        bg = (bg*255).astype(int)
        crop_left_ear.show()
        trect = TriangleRect.find_best(crop_left_ear, bg, fg, n=2, sn=3)
        trect.draw().show()
        import pdb; pdb.set_trace()
        self.assertEqual(trect.quadrant, Quadrant.bottom_right)

        

    def test_draw(self):
        # colors = TriangleRect.gen_colors(base_color, n=4)
        triangle = TriangleRect(size=(200,200), base_color=(100,100,100), 
            second_color=(200,200,200), n=3, sn=2, quadrant=Quadrant.bottom_right)
        triangle.draw()
        triangle = TriangleRect(size=(200,200), base_color=(100,100,100), 
            second_color=(200,200,200), n=3, sn=2, quadrant=Quadrant.bottom_left)
        triangle.draw()
        triangle = TriangleRect(size=(200,200), base_color=(100,100,100), 
            second_color=(200,200,200), n=3, sn=2, quadrant=Quadrant.top_left)
        triangle.draw()
        triangle = TriangleRect(size=(200,200), base_color=(100,100,100), 
            second_color=(200,200,200), n=3, sn=2, quadrant=Quadrant.top_right)
        triangle.draw()


if __name__ == '__main__':
    unittest.main()