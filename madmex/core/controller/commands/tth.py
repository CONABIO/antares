'''
Created on Oct 21, 2016

@author: rmartinez
'''

from __future__ import unicode_literals
from decimal import Decimal
from madmex.core.controller.base import BaseCommand

import sys
import os
import argparse
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
        raster_path1 = options['tth'][0]
        raster_path2 = options['tth'][1]
        LOGGER.info('Reading raster path initial year: %s'  % (raster_path1) )
        area_raster1, info_at_open1 = self.get_pixel_info(raster_path1)
        LOGGER.info('Pixel area in raster %s: %s'  % (os.path.basename(raster_path1), str(area_raster1)) )
        
        LOGGER.info('Reading raster path final year:   %s'  % (raster_path2) )
        area_raster2, info_at_open2 = self.get_pixel_info(raster_path2)
        LOGGER.info('Pixel area in raster %s: %s'  % (os.path.basename(raster_path2), str(area_raster2)) )

        
    def get_pixel_info(self, path):
        '''
        
        '''
        ds = gdal.Open(path)
        bands = ds.RasterCount
        geotransform = ds.GetGeoTransform()
        x_resolution = geotransform[1]
        y_resolution = geotransform[5]
        pixel_area   = abs(x_resolution * y_resolution)
        
        return pixel_area, ds