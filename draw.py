

from PIL import Image, ImageDraw, ImageChops
import math
import random
from drawshape import DrawShape
from rect import Rect
import pdb
import timeit

TOTAL_SHAPES = 500

for j in range(1):
    ds = DrawShape("moi.JPEG")
    for i in range(TOTAL_SHAPES):

        rect = ds.find_best_shape(tries=50)
        print "best starting rect"
        print rect, rect.area()

        # start_time = timeit.default_timer()
        rect, color = ds.find_best_mutate(rect, tries=100)
        # print(timeit.default_timer() - start_time)
        color = ds.find_best_alpha(rect)
        # print color

        diff0 = DrawShape.rmsdiff(ds.og_image, ds.image)

        staged = ds.stage_draw(rect, color)
        diff1 = DrawShape.rmsdiff(ds.og_image, staged)

        print diff1, diff0
        if diff1 < diff0:
            print "{i} drawing...".format(i=i)
            print rect, rect.area(), color
            ds.draw_shape(rect, color)

        if i%50==0:
            ds.image.show()
        #     # import pdb; pdb.set_trace()
            


       

    ds.image.show()
    ds.image.save("bloop{j}.JPEG".format(j=j), "JPEG")

