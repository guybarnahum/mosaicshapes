

import unittest

import os, sys
parent = os.path.abspath('.')
sys.path.insert(1, parent)

from grid import Grid
from gencolor import ColorType
import profile
import cProfile



class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(None,"../input/bryan.jpg", pix_multi=.014, diamond=True, colorful=ColorType.kANALOGOUS, 
            working_res=1600, enlarge=1600)
       
    def tearDown(self):
        pass

    def test_n_pass(self):
        n=1
        self.grid.n_pass(n)
        self.grid.save("/tmp/out.jpg")
        print('saved grid into out.jpg')
    # def test_occupy(self):
    #     x,y = (10,10)
    #     self.grid.occupy(x,y)
    #     result = self.grid.is_occupied(x,y)
    #     self.assertTrue(result)

    # # Test vertical expansion
    # def test_is_occupied(self):
    #     x,y = (10,10)
    #     result = self.grid.is_occupied(x,y)
    #     self.assertFalse(result)
    #     self.grid.occupy(x,y)
    #     result = self.grid.is_occupied(x,y)
    #     self.assertTrue(result)


if __name__ == '__main__':
    cProfile.run("unittest.main()", 'test.profile')
    # unittest.main()
