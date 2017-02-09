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

def pixel_info(path):
    '''
    Given a raster path, it opens it and returns the pixel resolution
    and the dataset.
    '''
    LOGGER.info('Reading raster path: %s'  % (path) )
    dataset = gdal.Open(path)
    geotransform = dataset.GetGeoTransform()
    x_resolution = geotransform[1]
    y_resolution = geotransform[5]
    pixel_area   = abs(x_resolution * y_resolution)
    return pixel_area, dataset

def area(class_pixels, pixel_resolution):
    '''
    This method returns the area of the given pixels per hectare
    '''
    class_area = (pixel_resolution * class_pixels) / hectare
    return class_area

def class_info(raster, pixel_area):
    '''
    Calculates the area in hectares for each class.
    '''
    raster_array   = np.array(raster.GetRasterBand(1).ReadAsArray())
    arr_class_info = np.unique(raster_array, return_counts=True)
    area_arr = []
    for i in range(len(arr_class_info[0])):
        class_id = arr_class_info[0][i]
        num_pixels_per_class = arr_class_info[1][i]
        area_per_class = area(num_pixels_per_class, pixel_area)
        area_arr.append(area_per_class)
        print 'Class ID: ', class_id, '\t', 'No. Pixels per class: ', num_pixels_per_class, '\t', 'Area per class [ha]:', area_per_class
    return arr_class_info[0], area_arr
            
def tth(year_ini, year_fin, class_area_ini, class_area_fin):
    '''
    This method calculates the habitat transformation rate acording
    to the formula: 
    1 - (1 - (S1-S2)/S1)^(1/n)
    If any of the areas is 0 we return 0.
    '''
    if class_area_ini == 0 or class_area_fin == 0:
        return 0
    period = int(year_fin) - int(year_ini)
    #coef = Decimal(1.0 / period)
    #surface_class = Decimal((class_area_ini -class_area_fin) /  class_area_ini)
    #tth_class = 1- ((1 - surface_class)**(coef))
    tth_class = 1 - ( 1 - (class_area_ini - class_area_fin ) * 1.0 / class_area_ini )**(1.0/ period)
    return tth_class 

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
        
        
        pixel_area, info_at_open= pixel_info(rasterIni)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterIni), str(pixel_area) ))
        LOGGER.info('Getting classification info from %s', os.path.basename(rasterIni))
        arr_class_id_ini, area_arr_ini = class_info(info_at_open, pixel_area)
                
        pixel_area, info_at_open= pixel_info(rasterFin)
        LOGGER.info('Pixel area in raster %s: %s [m2]'  % ( os.path.basename(rasterFin), str(pixel_area) ))
        LOGGER.info('Getting classification info from %s', os.path.basename(rasterFin))
        arr_class_id_fin, area_arr_fin = class_info(info_at_open, pixel_area)

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
                tthv = tth(int(yearIni), int(yearFin), class_area_ini, class_area_fin)
                tth_arr.append( tthv * 100 )
                print 'Class ID: ', matching_class[i], '\t', 'S1 [ha]:  ',class_area_ini, '\t', 'S2 [ha]:  ', class_area_fin, '\t', 'TTH: ', tthv * 100, '\t', '%'              
        
        if orphan_class:
            LOGGER.info('There are %s classes with no match'  % (len(orphan_class)) )

        self.write_file(matching_class, clss_area_ini_arr, clss_area_fin_arr, tth_arr, csv_name, output_dir, yearIni, yearFin)     
    
    def write_file(self, match_class, area_ini, area_fin, tth, file_name, dir_path, year1, year2):
        '''
        '''
        titles = ['Class ID','S1 [ha]','S2 [ha]', 'tth [%]'] 
        keys = { 
        0: "No Data",
        1 : "Bosques Templado", 
        2 : "Selva Perennifolia, Subperennifolia, Caducifolia y Subcaducifolia", 
        3 : "Matorral", 
        4 : "Vegetacion Menor y Pastizales", 
        5 : "Tierras Agricolas", 
        6 : "Urbano y Contruido", 
        7 : "Suelo Desnudo",
        8 : "Agua",
        9 : "Nubes"} 
  
        key_names = []
        for id_class in match_class:
            key_names.append(keys[id_class])
        rows = zip(key_names,area_ini,area_fin,tth)
        
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
                
                
                
                
                
                
                
                
    
    
    