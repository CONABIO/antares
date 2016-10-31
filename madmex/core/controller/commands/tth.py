'''
Created on Oct 21, 2016

@author: rmartinez
'''

from __future__ import unicode_literals
from decimal import Decimal
from madmex.core.controller.base import BaseCommand

import sys
import os
import gdal
import numpy as np
import re
import logging



LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        
        '''
        parser.add_argument('tth', nargs='*' )
        

    def handle(self, **options):
        '''
        
        '''
                
        for j in range(len(options['tth'])):
            pixel_area, info_at_open= self.get_pixel_info(options['tth'][j])
            LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(options['tth'][j]), str(pixel_area) ))
            self.get_class_info(info_at_open, options['tth'][j])
            
            
    def get_pixel_info(self, path):
        '''
        
        '''
        LOGGER.info('Reading raster path: %s'  % (path) )
           
        ds = gdal.Open(path)
        bands = ds.RasterCount
        geotransform = ds.GetGeoTransform()
        x_resolution = geotransform[1]
        y_resolution = geotransform[5]
        pixel_area   = abs(x_resolution * y_resolution)
        
        return pixel_area, ds
    
    def get_class_info(self, raster, raster_name):
        '''
        
        '''
        
        raster_array   = np.array(raster.GetRasterBand(1).ReadAsArray())
        arr_class_info = np.unique(raster_array, return_counts=True)
        LOGGER.info('Getting classification info from %s', os.path.basename(raster_name))

        for i in range(len(arr_class_info[0])):
            print arr_class_info[0][i],  arr_class_info[1][i]
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
    
    
    