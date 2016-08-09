'''
Created on Jul 29, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import os
import struct
import sys

import gdal
import gdalconst
import numpy
import ogr
import osr

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_empty_raster_from_reference, \
    create_raster_from_reference
from madmex.util import get_base_name, create_file_name


INITIAL_ARRAY = [[1,2,3,8,9,10,11,12,13,16,14,15,20,24,25,26],
               [4,5,6,7,17,18,19,21,22,23,27,28,29,30,31,32]]
FINAL_ARRAY = [1,2]

def dictionary_from_list(key_list, value_list):
    new_dict = {}
    for i in range(len(key_list)):
        for j in range(len(key_list[i])):
            new_dict[key_list[i][j]] = value_list[i]
    return new_dict

def replace_in_array(data_array, dictionary):
    for key, value in dictionary.iteritems():
        print key, value
        data_array[(data_array==key)] = value
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

    def method_one(self, options):
        path = options['path'][0]
        output = options['output'][0]
        
        print path
        print INITIAL_ARRAY
        print FINAL_ARRAY
        #data_array = open_handle(path)
        
        outDataset = create_empty_raster_from_reference(output + "one.tif", path)
        
        print 'back from dataset creation.'
        
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        
        print 'hello'
        
        if dataset is None:
            print "The dataset could not opened"
        
            sys.exit(-1)
            
        classification_band = dataset.GetRasterBand(1)
        
        rows = classification_band.YSize
        
        print rows
        
        for row in range(rows):
            outputLine = str('')
            scanline = classification_band.ReadRaster( 0, row, classification_band.XSize, 1, classification_band.XSize, 1, gdal.GDT_Float32 )
            row_tuple = struct.unpack('f' * classification_band.XSize, scanline)
            for i in range(len(row_tuple)):
                new_pixel = row_tuple[i]
                outputLine = str(outputLine) + struct.pack('f', new_pixel)
            outDataset.GetRasterBand(1).WriteRaster(0, row, classification_band.XSize, 1, outputLine, buf_xsize=classification_band.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
            del outputLine
                
    def method_two(self, options):
        '''
        This method replaces the incidences of the given list with the final list.
        
        This is a new part of the comment.
        '''
        path = options['path'][0]
        output = options['output'][0]
        
        print path
        
        data_array = open_handle(path)
        original_shape = data_array.shape
        new_array = numpy.ravel(data_array)
        
        for i in xrange(len(INITIAL_ARRAY)):
            # list to numpy array
            nparray = numpy.array(INITIAL_ARRAY[i])
            print(nparray)
            found_idx = numpy.in1d(data_array,nparray)
            print(FINAL_ARRAY[i])
            new_array[found_idx] = FINAL_ARRAY[i]
        print output

        create_raster_from_reference(output + "two.tif", new_array.reshape(original_shape), path)
        
    def method_three(self, options):
        '''
        This method replaces the incidences of the given list with the final list.
        '''
        path = options['path'][0]
        output = options['output'][0]
        
        print path
        
        data_array = open_handle(path)

        
        my_dictionary = dictionary_from_list(INITIAL_ARRAY, FINAL_ARRAY)
        
        to_vector_array = replace_in_array(data_array, my_dictionary)
        
        
        
        create_raster_from_reference(output + "three.tif", to_vector_array, path, gdal.GDT_Byte)
        
        
    
    def method_four(self, options):
        '''
        This method replaces the incidences of the given list with the final list.
        '''
        path = options['path'][0]
        output = options['output'][0]
        
        print path
        
        data_array = open_handle(path)

        create_raster_from_reference(output + "four.tif", data_array, path)
        
    
    
    def handle(self, **options):
        print 'hello'
        import time
        #start_time = time.time()
        #self.method_one(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        
        
        #start_time = time.time()
        #self.method_two(options)
        #print("--- %s seconds ---" % (time.time() - start_time))

        #print 'Dataset was written.'
        
        start_time = time.time()
        self.method_three(options)
        print("--- %s seconds ---" % (time.time() - start_time))
        
        print 'Dataset was written.'
        
        #start_time = time.time()
        #self.method_four(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        #print 'Dataset was written.'
