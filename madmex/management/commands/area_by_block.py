'''
Created on Nov 10, 2017

@author: rmartinez
'''

from __future__ import unicode_literals

import numpy as np
import logging

from osgeo import gdal, osr
from scipy.constants.constants import hectare
from madmex.management.base import AntaresBaseCommand


logger = logging.getLogger(__name__)

def open(path):
    '''
        Given a raster path, it opens it and returns the dataset.
    '''
    logger.info('Reading raster path: %s'  % (path) )
    return gdal.Open(path)
    
def get_NoData(dataset):
    '''
        Given a dataset, it returns the raster's NoData value 
    '''
    return dataset.GetRasterBand(1).GetNoDataValue()

def get_resolution(dataset):
    '''
        Given a dataset, it returns the x and y resolution
    '''
    geotransform = dataset.GetGeoTransform()
    x_resolution = geotransform[1]
    y_resolution = geotransform[5]
    return x_resolution, y_resolution

def get_pixel_area(x, y):
    '''
        Given the x and y resolutions, it returns the pixel's area
    '''
    return abs(x * y)
    
def get_natural_raster_block(dataset):
    '''
        Given a dataset, it returns the "natural" block size
        and the total XY size
    '''
    block_sizes = dataset.GetRasterBand(1).GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]
    xsize = dataset.GetRasterBand(1).XSize
    ysize = dataset.GetRasterBand(1).YSize
    return x_block_size, y_block_size, xsize, ysize

def area_per_block(class_pixels, pixel_resolution):
    '''
        This method returns the area of the given pixels per hectare
    '''
    return  (pixel_resolution * class_pixels) / hectare
    

def read_by_block(dataset, nodata, pixel_area, x_block_size, y_block_size, xsize, ysize):
    '''
        This method reads the raster by blocks and returns a dictionary with all classes as keys and their area values found in it.
    '''
    blocks = 0
    general_dict = dict ()
    for y in xrange(0, ysize, y_block_size):
        partial_area = []
        partial_classes = []
        if y + y_block_size < ysize:
            rows = y_block_size
        else:
            rows = ysize - y
        for x in xrange(0, xsize, x_block_size):
            if x + x_block_size < xsize:
                cols = x_block_size
            else:
                cols = xsize - x
            array = dataset.GetRasterBand(1).ReadAsArray(x, y, cols, rows)
            # Getting id's of distinct classes in the current block
            arr_class_info = np.unique(array, return_counts=True)
            for i in range(len(arr_class_info[0])):
                class_id = arr_class_info[0][i]
                if class_id != nodata:
                    num_pixels_per_class = arr_class_info[1][i]
                    area_per_class = area_per_block(num_pixels_per_class,pixel_area)
                    #logger.info('Class ID: %s \t Area in this class:  %s \t [ha] '  % (class_id, area_per_class))
                    partial_area.append(area_per_class)
                    partial_classes.append(str(class_id))
                    # Adding new area values to the same class key 
                    general_dict.setdefault(str(class_id), []).append(area_per_class)
            logger.info('Proccessing block %s: \t %s distinct class(es) found in this block. \t %s hectare(s) in this block.' %(y,len(partial_classes),sum(partial_area)))
            del array
            blocks += 1
    return general_dict
    
def get_total_area(dictionary):
    '''
        Given a dictionary with classes id's as keys and their area values by block, 
        it computes the total area in the raster and shows the area per class.  
    '''
    area=[]
    for key, value in dictionary.iteritems():
        a = sum(value)
        area.append(a)
        logger.info('Class ID: %s \t Area in this class:  %s \t [ha] '  % (key, a))
    return sum(area)
    
class Command(AntaresBaseCommand):
    '''
        classdocs
        
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1, help='Path to image.')

    def handle(self, **options):
        
        filepath = options['path'][0]
        ds = open(filepath)
        
        x, y = get_resolution(ds)
        logger.info('Raster resolution: x = %s , y = %s'  % (x, y))
        
        pixel_area = get_pixel_area(x, y)
        logger.info('Pixel area: %s'  % (pixel_area))
        
        nodata = get_NoData(ds)
        logger.info('No-Data value: %s'  % (nodata))
        
        x_block, y_block, xsize, ysize = get_natural_raster_block(ds)
        logger.info('Getting block size')
        
        dict = read_by_block(ds, nodata, pixel_area, x_block, y_block, xsize, ysize)
        
        area_total= get_total_area(dict)
        logger.info('--------------------------------')
        logger.info('Total area: %s [ha]'  % (area_total))
        logger.info('--------------------------------')