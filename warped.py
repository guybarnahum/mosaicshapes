


from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import PiecewiseAffineTransform, warp
import scipy
from scipy.misc import toimage
import util

"""
Get average color of rect.
Draw multiple circles inside each other.  
Distort it (http://stackoverflow.com/questions/21940911/python-image-distortion)
"""
class Warped():

    def __init__(self, size=(200,200), color=(180,0,200)):
        self.width = size[0]
        self.height = size[1]
        self.color = color
        self.num_circles = 4
        self.warp_height = .03


    def draw(self):
        show_image = False

        is_horizontal = True if self.width >= self.height else False

        if is_horizontal:
            ratio = self.width / float(self.height)
        else:
            ratio = self.height / float(self.width)

        CIRCLE_SIZE = max(self.width, self.height)
        
        print "circle size", CIRCLE_SIZE

        circle_img=Image.new('RGB', (CIRCLE_SIZE,CIRCLE_SIZE))
        canvas = ImageDraw.Draw(circle_img)

        csize = CIRCLE_SIZE/(self.num_circles*2)

        color0 = (100,100,200)
        color1, color2 = util.adjacent_colors(color0)

        canvas.ellipse([0, 0, CIRCLE_SIZE,CIRCLE_SIZE], fill=color0)
        canvas.ellipse([csize, csize, CIRCLE_SIZE-csize, CIRCLE_SIZE-csize], fill=color0)
        canvas.ellipse([csize*2, csize*2, CIRCLE_SIZE-csize*2, CIRCLE_SIZE-csize*2], fill=color1)
        canvas.ellipse([csize*3, csize*3, CIRCLE_SIZE-csize*3, CIRCLE_SIZE-csize*3], fill=color2)
        if show_image:
            circle_img.show()
        image = np.asarray(circle_img)
        # rows, cols = image.shape[0], image.shape[1]
        rows, cols = self.height, self.width

        src_cols = np.linspace(0, cols, 50)
        src_rows = np.linspace(0, rows, 50)
        src_rows, src_cols = np.meshgrid(src_rows, src_cols)
        src = np.dstack([src_cols.flat, src_rows.flat])[0]

        # add sinusoidal oscillation to row coordinates
        HEIGHT_OSC = CIRCLE_SIZE * self.warp_height

        if is_horizontal:
            dst_rows = src[:, 1] - np.cos(np.linspace(0, 4 * np.pi, src.shape[0])) * HEIGHT_OSC
            dst_cols = src[:, 0] 

            dst_rows *= (ratio+self.warp_height)
            dst_rows -= ratio * HEIGHT_OSC # subtract y position to account for mutating up
        else:
            dst_rows = src[:, 1] 
            dst_cols = src[:, 0]  - np.sin(np.linspace(0, 3 * np.pi, src.shape[0])) * HEIGHT_OSC

            dst_cols *= (ratio+self.warp_height)
            # dst_cols -= ratio * HEIGHT_OSC # subtract y position to account for mutating up

        dst = np.vstack([dst_cols, dst_rows]).T

        tform = PiecewiseAffineTransform()
        tform.estimate(src, dst)

        out_rows = rows #image.shape[0] - 1.5 * HEIGHT_OSC
        out_cols = cols

        print out_cols, out_rows
        out = warp(image, tform, output_shape=(out_rows, out_cols))

        # fig, ax = plt.subplots()


        # if show_image:
        #     ax.imshow(out)
        #     # ax.plot(tform.inverse(src)[:, 0], tform.inverse(src)[:, 1], '.b') # plots the dots
        #     ax.axis((0, out_cols, out_rows, 0))
        #     plt.show()

        converted = scipy.misc.toimage(out)

        # if show_image:
        #     converted.show()

        return converted







