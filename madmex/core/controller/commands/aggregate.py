'''
Created on Jul 29, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import os
import struct
import sys
import time

import gdal
import gdalconst
import numpy
import ogr
import osr

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_empty_raster_from_reference, \
    create_raster_from_reference
from madmex.persistence.driver import get_rapideye_footprints_from_state, \
    get_states_names
from madmex.util import get_base_name, create_file_name, get_parent


#from build.lib.madmex.core.controller.commands.aggregate import INITIAL_ARRAY
#from build.lib.madmex.core.controller.commands.aggregate import INITIAL_ARRAY,\
LOGGER = logging.getLogger(__name__)

#    FINAL_ARRAY


#INITIAL_ARRAY = [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,123,124,200,210],
#                 [27,28,30,31],
#                 [29,98,99]]
#FINAL_ARRAY = [1,2,3]
# INITIAL_ARRAY = [[1,2,3,4,5,6],
#                   [7,8,9,10,11,12,13],
#                   [22,23,24,25,26,27,28],
#                   [29],
#                   [30],
#                   [32],
#                   [14,15,16,17,18,19,20,21,31]]
# FINAL_ARRAY = [1,2,3,4,5,6,7]

# # Array for landsat
# INITIAL_ARRAY = [[1,3,2,6,4,123],
#                  [8,10,16,12,11,9,13],
#                  [5,7,22,17,19,18,23,21],
#                  [15,14,20,24,25,26,27],
#                  [28],
#                  [31],
#                  [30],
#                  [29],
#                  [98,99]]
# FINAL_ARRAY = [1,2,3,4,5,6,7,8,0]

# Array for rapideye
INITIAL_ARRAY = [[1,2,3,4,5,6],
                 [7,8,9,10,11,12,13],
                 [14,15,16,17,18,19,20,21],
                 [22,23,24,25,26,27,28],
                 [29],
                 [30],
                 [31],
                 [32],
                 [98,99]]
FINAL_ARRAY = [1,2,3,4,5,6,7,8,0]


INITIAL_IPCC = [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,100,123,124,200,210],
                 [27],
                 [28],
                 [29],
                 [30],
                 [31],
                 [98,99]]
FINAL_IPCC = [1,2,3,4,5,6,7]


MASK_ARRAY =[32]

MASK = 32


def dictionary_from_list(key_list, value_list):
    new_dict = {}
    for i in range(len(key_list)):
        for j in range(len(key_list[i])):
            new_dict[key_list[i][j]] = value_list[i]
    return new_dict

def replace_in_array(data_array, dictionary):
    for key, value in dictionary.iteritems():
        data_array[data_array==key] = value
    return data_array

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        This command defines only an additional argument. The user must provide
        a path to ingest, if several paths are given, all of the folders will
        be ingested.
        '''
        parser.add_argument('--path', nargs='*')
        parser.add_argument('--output', nargs='*')
        #parser.add_argument('--state', nargs='*')


    def mask_by_row(self, path, output):
        '''
        This method replaces the masked value for ones in the target array, one row at a time. 
        '''
        outDataset = create_empty_raster_from_reference(output, path, data_type=gdal.GDT_Byte)
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        if dataset is None:
            print "The dataset could not be opened"
            sys.exit(-1)
        classification_band = dataset.GetRasterBand(1)
        rows = classification_band.YSize
        cols = classification_band.XSize
        print rows
        for row in range(rows):
            outputLine = str('')
            scanline = classification_band.ReadRaster( 0, row, classification_band.XSize, 1, classification_band.XSize, 1, gdal.GDT_Float32 )
            row_tuple = struct.unpack('f' * classification_band.XSize, scanline)
            new_row = numpy.zeros(len(row_tuple))
            old_row = numpy.array(row_tuple)
            new_row[old_row==MASK_ARRAY] = 1
            new_row.astype('f').tostring()
            outDataset.GetRasterBand(1).WriteArray(numpy.resize(new_row, (1, cols)), 0, row)
            del outputLine
            del old_row
            del new_row
            del row_tuple
 
    def mask_by_block(self, path, output, block_size=8192):
        '''
        Method to create a mask from a given raster writing by block. This is attained by reading the
        dataset in blocks, this is useful when the original raster is really big.
        '''
        outDataset = create_empty_raster_from_reference(output, path, data_type=gdal.GDT_Byte)
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        if dataset is None:
            print "The dataset could not be opened"
            sys.exit(-1)        
        classification_band = dataset.GetRasterBand(1) 
        y_size = classification_band.YSize
        x_size = classification_band.XSize
        value_to_mask = 32
        total = (y_size + block_size) * (x_size + block_size) / block_size / block_size
        count = 0
        current = -1 
        for i in range(0, y_size, block_size):
            if i + block_size < y_size:
                rows = block_size
            else:
                rows = y_size - i
            for j in range(0, x_size, block_size):
                if j + block_size < x_size:
                    cols = block_size
                else:
                    cols = x_size - j
                data_array = classification_band.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                data_array[data_array!=value_to_mask] = 0
                data_array[data_array==value_to_mask] = 1
                count = count + 1
                outDataset.GetRasterBand(1).WriteArray(data_array,j,i)
                aux = current
                current = count * 100 / total
                if aux != current:
                    print current                
        outDataset = None
        
    def aggregate_by_block(self, path, output, ini_arr, fin_arr, block_size=8192):
        '''
        Method to create a mask from a given raster writing by block. This is attained by reading the
        dataset in blocks, this is useful when the original raster is really big.
        '''
        outDataset = create_empty_raster_from_reference(output, path, data_type=gdal.GDT_Byte)
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        my_dictionary = dictionary_from_list(ini_arr, fin_arr)
        if dataset is None:
            print "The dataset could not be opened"
            sys.exit(-1)        
        classification_band = dataset.GetRasterBand(1) 
        y_size = classification_band.YSize
        x_size = classification_band.XSize
        value_to_mask = 32
        total = (y_size + block_size) * (x_size + block_size) / block_size / block_size
        count = 0
        current = -1 
        for i in range(0, y_size, block_size):
            if i + block_size < y_size:
                rows = block_size
            else:
                rows = y_size - i
            for j in range(0, x_size, block_size):
                if j + block_size < x_size:
                    cols = block_size
                else:
                    cols = x_size - j
                data_array = classification_band.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                to_vector_array = replace_in_array(data_array, my_dictionary)
                count = count + 1
                outDataset.GetRasterBand(1).WriteArray(to_vector_array,j,i)
                aux = current
                current = count * 100 / total
                if aux != current:
                    LOGGER.debug('%s' % current)              
        outDataset = None        
        
        

    def mask_iterating_values(self, path, output, ini_arr, fin_arr):
        '''
        Iterating over the values in the initial and final arrays this replaces the
        desired values one by one.
        '''
        data_array = open_handle(path)
        my_dictionary = dictionary_from_list(ini_arr, fin_arr)
        to_vector_array = replace_in_array(data_array, my_dictionary)
        create_raster_from_reference(output, to_vector_array, path, gdal.GDT_Byte)

    def method_five(self, path, output):
        '''
        Using numpy utilities, this method mask the desired value.
        '''
        data_array = open_handle(path)
        data_array[data_array!=MASK] = 0
        data_array[data_array==MASK] = 1
        create_raster_from_reference(output, data_array, path, gdal.GDT_Byte)
        del data_array
        
    def print_unique(self, path):

        data_array = open_handle(path)
        unique, counts = numpy.unique(data_array, return_counts=True)
        print unique, counts
        
        
    def handle(self, **options):
        output = options['output'][0]
        #state = options['state'][0]
        
        
#         for name in get_states_names():
#             print name[0]
#             for footprint in get_rapideye_footprints_from_state(name[0]):
#                 print footprint[0]
#             
#         
#         import time
#         time.sleep(2)

        
        for image_path in options['path']:
            print image_path
            basename = '%s_ipcc.tif' % get_base_name(image_path)
            LOGGER.info(basename)
            target = create_file_name(output, basename)
            #print target
            start_time = time.time()
            
            self.aggregate_by_block(image_path, target, INITIAL_IPCC, FINAL_IPCC)
            
            #self.method_by_block(image_path, target)
            #self.mask_iterating_values(image_path, target, INITIAL_ARRAY, FINAL_ARRAY)
            LOGGER.info("--- %s seconds ---" % (time.time() - start_time))
            LOGGER.info('Dataset was written.')
        