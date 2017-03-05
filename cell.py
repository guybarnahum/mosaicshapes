
import util
import numpy as np
from enum import Enum
import abc
import random
from random import shuffle, randint

class Quadrant(Enum):
    top_left = 1
    top_right = 2
    bottom_right = 3
    bottom_left = 4


class Direction(Enum):
    top = 1
    right = 2
    bottom = 3
    left = 4

class Cell(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        print "I am init"

    @staticmethod
    def gen_colors(base_color, n, colorful=True):
        if colorful:
            return Cell.gen_colorful(base_color, n)
        else:
            return Cell.gen_colors_og(base_color, n)

    @staticmethod
    def gen_colorful(base_color, n):
        r,g,b = base_color
        adj_colors = util.adjacent_colors(base_color)
        complement_colors = [util.complement(c[0],c[1],c[2]) for c in adj_colors]

        # shuffle(complement_colors)
        c1 = Cell.gen_colors_og(adj_colors[0], random.randint(1,1))
        c2 = Cell.gen_colors_og(adj_colors[1], random.randint(1,1))

        # option for non complement
        all_colors = c1 + c2 #+ complement_colors
        shuffle(all_colors)
        if n==1:
            all_colors.append(base_color)

        #XXX: The complementary colors likely should be the main middle
        # it occupies too much space, it should be accentuating
        # base + adj colors should be more towards middle
        # all_colors = all_colors[:n-1]
        all_colors.append(base_color)
        shuffle(all_colors)


        # all_colors.insert(randint(1,len(all_colors)-1), complement_colors[0])
        
        # if len(all_colors)>2:
        if randint(0,100)>30:
            all_colors.insert(randint(1,len(all_colors)-1), complement_colors[randint(0,1)])

        # for ccolor in complement_colors:
            # all_colors.insert(randint(1,len(all_colors)-1), ccolor)

        return all_colors

    @staticmethod
    def gen_colors_og(base_color, n):
        colors = []
        if n==1:
            if isinstance(base_color, (np.ndarray, np.generic)):
                base_color = tuple(base_color.astype(int))
            colors.append(base_color)
        else:   
            # maximum distance between all colors combined
            distance = 25
            colors = []

            r,g,b = base_color
            quad = 1 if util.luminance(r,g,b) > 100 else 0


            for i in range(-n/2+quad, n/2+quad):
                color = np.asarray(base_color) + (i)*distance/float(n)
                color[0] = util.clamp_int(color[0], 0, 255) #R
                color[1] = util.clamp_int(color[1], 0, 255) #G
                color[2] = util.clamp_int(color[2], 0, 255) #B
                color = tuple(color.astype(int))
                colors.append(color)

            # if random.randrange(2):

            
            if not random.getrandbits(1):
                shuffle(colors)
                # colors = list(reversed(colors))

            if len(colors)>=3:
                colors[1], colors[2] = colors[2], colors[1]

        return colors

    @abc.abstractmethod
    def find_best(self):
        return
    
    @abc.abstractmethod
    def draw(self):
        return

    