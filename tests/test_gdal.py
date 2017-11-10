'''
Created on Nov 4, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import unittest

from madmex.configuration import SETTINGS
from madmex.mapper.data._gdal import create_raster, get_width, get_height, \
    get_bands, create_raster_from_reference
from madmex.util import create_filename


class Test(unittest.TestCase):
    def test_create_image(self):
        import numpy
        array = numpy.array([[ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                             [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                             [ 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
                             [ 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                             [ 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
                             [ 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                             [ 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
                             [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                             [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                             [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
        red = (1 - array) * 1000
        green = (1 - array) * 1000
        blue = array * 1000
        create_raster(create_filename(getattr(SETTINGS, 'TEST_FOLDER'), 'single.tif'), array)
        create_raster(create_filename(getattr(SETTINGS, 'TEST_FOLDER'), 'multi.tif'), numpy.array([red, green, blue]))
    @unittest.skip("testing skipping")
    def test_creat_image(self):
        import numpy
        filename = '/Users/agutierrez/Development/df/1448114/2015/2015-02-24/l3a/1448114_2015-02-24_RE3_3A_302417.tif'
        
        width = get_width(filename)
        height = get_height(filename)
        plain = width * height
        
        red = numpy.zeros(plain)
        green = numpy.zeros(plain)
        blue = numpy.zeros(plain)
        ired = numpy.zeros(plain)
        print 'before loop'
        for i in range(plain):
            if not i % 2:
                red [i] = 1
            if not i % 3:
                green [i] = 1
            if not i % 5:
                blue [i] = 1
            if not i % 7:
                ired [i] = 1
        print 'loop' 
        final=numpy.array([numpy.reshape(red,(width, height)),
                           numpy.reshape(green,(width, height)),
                           numpy.reshape(blue,(width, height)),
                           numpy.reshape(ired,(width, height))])
        print final.shape
        print 'hello'
        create_raster_from_reference(create_filename(getattr(SETTINGS, 'TEST_FOLDER'), 'sieve.tif'), final, filename)
        
if __name__ == '__main__':
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
