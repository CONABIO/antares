'''
Created on Oct 21, 2016

@author: rmartinez
'''

from __future__ import unicode_literals
from decimal import Decimal
from madmex.core.controller.base import BaseCommand
from scipy.constants.constants import hectare
from operator import itemgetter

import shutil
import os
import sys
import gdal
import csv
import numpy as np
import logging


LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        
        '''
        parser.add_argument('tth', nargs='*', help='This script implements the tth analysis' )
        parser.add_argument('--rasterPathIni', nargs='*', help='Path to the initial year raster')
        parser.add_argument('--rasterPathFin', nargs='*', help='Path to the final year raster')
        parser.add_argument('--yearIni', nargs=1, help='Some help on initial year')
        parser.add_argument('--yearFin', nargs=1, help='Some help on final year')
        parser.add_argument('--csvName', nargs=1, help='CSV file name with the tth results')
        parser.add_argument('--outputDir', nargs=1, help='CSV output directory')
    


    def handle(self, **options):
        '''
        
        '''
        rasterIni = options['rasterPathIni'][0]
        rasterFin = options['rasterPathFin'][0]
        yearIni = options['yearIni'][0]
        yearFin = options['yearFin'][0]
        csv_name = options['csvName'][0]
        output_dir = options['outputDir'][0]
        
        
        pixel_area, info_at_open= self.pixel_info(rasterIni)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterIni), str(pixel_area) ))
        arr_class_id_ini, area_arr_ini = self.class_info(info_at_open, rasterIni, pixel_area)
                
        pixel_area, info_at_open= self.pixel_info(rasterFin)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterFin), str(pixel_area) ))
        arr_class_id_fin, area_arr_fin = self.class_info(info_at_open, rasterFin, pixel_area)

        matching_class = list(set(arr_class_id_ini).intersection(arr_class_id_fin))
        orphan_class = list(set(list(arr_class_id_ini)).symmetric_difference(list(arr_class_id_fin)))
        matching_class.pop(0)
        
        LOGGER.info('Computing tth analysis in period: %s - %s'  % (yearIni,yearFin) )        
        # computes the "tth" analysis only for those classes in both rasters
        tth_arr = []
        clss_area_ini_arr = []
        clss_area_fin_arr = []

        for i in range(len(matching_class)):
            if matching_class[i] in arr_class_id_ini and matching_class[i] in arr_class_id_fin :
                index_arr_class_ini = list(arr_class_id_ini).index(matching_class[i])
                index_arr_class_fin = list(arr_class_id_fin).index(matching_class[i])
                # print matching_class[i], area_arr_ini[index_arr_class_ini], area_arr_fin[index_arr_class_fin]
                class_area_ini = area_arr_ini[index_arr_class_ini]
                class_area_fin = area_arr_fin[index_arr_class_fin]
                clss_area_ini_arr.append(class_area_ini)
                clss_area_fin_arr.append(class_area_fin)
                tth = self.tth(int(yearIni), int(yearFin), class_area_ini, class_area_fin)
                tth_arr.append( tth * 100 )
                print 'Class ID: ', matching_class[i], '\t', 'S1 [ha]:  ',class_area_ini, '\t', 'S2 [ha]:  ', class_area_fin, '\t', 'TTH: ', tth * 100, '\t', '%'              
        
        if orphan_class:
            LOGGER.info('There are %s classes with no match'  % (len(orphan_class)) )

        self.write_file(matching_class, clss_area_ini_arr, clss_area_fin_arr, tth_arr, csv_name, output_dir, yearIni, yearFin)     

                    
                    
    
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
    
                
    def tth(self, year_ini, year_fin, class_area_ini, class_area_fin):
        '''
        '''
        period = int(year_fin) - int(year_ini)
        coef = Decimal(1.0 / period)
        surface_class = Decimal((class_area_ini -class_area_fin) /  class_area_ini)
        
        tth_class = 1- ((1 - surface_class)**(coef))
        
        return tth_class       
    
    def write_file(self, match_class, area_ini, area_fin, tth, file_name, dir_path, year1, year2):
        '''
        '''
        titles = ['Class ID','S1 [ha]','S2 [ha]', 'tth [%]'] 
        rows = zip(match_class,area_ini,area_fin,tth)
        
        csv_file = file_name + '_' + year1 + '_' + year2 + '.csv'
        file_path = dir_path + csv_file
        LOGGER.info('Writing results in  %s', file_path)

        #if not os.path.exists(os.path.dirname(dir_path)):
        #    os.makedirs(os.path.dirname(file_path))
        #else:
        #    shutil.rmtree(dir_path)
        #    os.makedirs(os.path.dirname(file_path))
        
        with open(file_path, 'wb') as f:
            wtr = csv.writer(f)
            wtr.writerows( [titles]) 
            for row in rows:
                wtr.writerow(row)
                
                
                
                
                
                
                
                
    
    
    