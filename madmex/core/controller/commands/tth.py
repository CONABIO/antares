'''
Created on Oct 21, 2016

@author: rmartinez
'''

from __future__ import unicode_literals
from decimal import Decimal
from madmex.core.controller.base import BaseCommand
from scipy.constants.constants import hectare
from operator import itemgetter
import os
import gdal
import numpy as np
import logging


#from test.pystone import nargs



LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        
        '''
        parser.add_argument('tth', nargs='*', help='Some general help' )
        parser.add_argument('--rasterPathIni', nargs='*', help='Some help on raster path initial')
        parser.add_argument('--rasterPathFin', nargs='*', help='Some help on raster path initial')
        parser.add_argument('--yearIni', nargs=1, help='Some help on initial year')
        parser.add_argument('--yearFin', nargs=1, help='Some help on final year')
    


    def handle(self, **options):
        '''
        
        '''
        rasterIni = options['rasterPathIni'][0]
        rasterFin = options['rasterPathFin'][0]
        yearIni = options['yearIni'][0]
        yearFin = options['yearFin'][0]
        
        
        pixel_area, info_at_open= self.pixel_info(rasterIni)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterIni), str(pixel_area) ))
        arr_class_id_ini, area_arr_ini = self.class_info(info_at_open, rasterIni, pixel_area)
                
        pixel_area, info_at_open= self.pixel_info(rasterFin)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterFin), str(pixel_area) ))
        arr_class_id_fin, area_arr_fin = self.class_info(info_at_open, rasterFin, pixel_area)

        matching_class = list(set(arr_class_id_ini).intersection(arr_class_id_fin))
        orphan_class = list(set(list(arr_class_id_ini)).symmetric_difference(list(arr_class_id_fin)))
        
        print matching_class
        print orphan_class
        print list(arr_class_id_ini)
        print list(arr_class_id_fin)
        
        # computes the "tth" anaysis only for those classes in both rasters
         
        for i in range(len(matching_class)):
            if matching_class[i] in arr_class_id_ini and matching_class[i] in arr_class_id_fin :
                index_arr_class_ini = list(arr_class_id_ini).index(matching_class[i])
                index_arr_class_fin = list(arr_class_id_fin).index(matching_class[i])
                print matching_class[i], area_arr_ini[index_arr_class_ini], area_arr_fin[index_arr_class_fin]
            
                    
                    
    
    def pixel_info(self, path):
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
    
    def class_info(self, raster, raster_name, pixel_area):
        '''
        
        '''
        
        raster_array   = np.array(raster.GetRasterBand(1).ReadAsArray())
        arr_class_info = np.unique(raster_array, return_counts=True)
        LOGGER.info('Getting classification info from %s', os.path.basename(raster_name))
        area_arr = []
        for i in range(len(arr_class_info[0])):
            class_id = arr_class_info[0][i]
            num_pixels_per_class = arr_class_info[1][i]
            area_per_class = self.area(num_pixels_per_class, pixel_area)
            area_arr.append(area_per_class)
            print 'Class ID: ', class_id, '\t', 'No. Pixels per class: ', num_pixels_per_class, '\t', 'Area per class [ha]:', area_per_class
        
        return arr_class_info[0], area_arr
                    
                    
    def area(self, class_pixels, pixel_area):
        '''
        '''
        area_class = (pixel_area * class_pixels) / hectare
        return area_class
    
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
    
    
    