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
from madmex.util import get_base_name, create_file_name, get_parent


INITIAL_ARRAY = [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,123,124,200,210],
                 [27,28,30,31],
                 [29,98,99]]
FINAL_ARRAY = [1,2,3]

MASK_ARRAY =[32]

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

    def method_one(self, path, output):
        
        print path
        print INITIAL_ARRAY
        print FINAL_ARRAY
        #data_array = open_handle(path)
        
        outDataset = create_empty_raster_from_reference(output, path, data_type=gdal.GDT_Byte)
        
        print 'back from dataset creation.'
        
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        
        print 'hello'
        
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
            
            new_row[old_row==32] = 1
            
            
            new_row.astype('f').tostring()
            
            '''
            for i in range(len(row_tuple)):
                #print row_tuple[i]
                
                if row_tuple[i] in MASK_ARRAY:
                    new_pixel = 1
                else:
                    new_pixel = 0
                outputLine = str(outputLine) + struct.pack('f', new_pixel)
            '''
            outDataset.GetRasterBand(1).WriteArray(numpy.resize(new_row, (1, cols)), 0, row)
            
            
            if row%10000==0:
                print 'Line %s was processed' % row
            
            del outputLine
            del old_row
            del new_row
            del row_tuple
            
    def method_by_block(self, path, output, block_size=8192):
        '''
        Method to create a mask from a given raster writing by block.
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
        
        
        
        create_raster_from_reference(output, to_vector_array, path, gdal.GDT_Byte)
        
        
    
    def method_four(self, path, output):
        '''
        This method replaces the incidences of the given list with the final list.
        '''
        print path
        
        data_array = open_handle(path)

        create_raster_from_reference(output, data_array, path, gdal.GDT_Byte)

    def method_five(self, path, output):
        '''
        This method replaces the incidences of the given list with the final list.
        '''
        
        print 'loading file'
        
        data_array = open_handle(path)
        
        print 'file was loaded'
        
        
        data_array[data_array!=32] = 0
        data_array[data_array==32] = 1

        create_raster_from_reference(output, data_array, path, gdal.GDT_Byte)
        
        del data_array
        
    
    
    def handle(self, **options):
        import time
        #start_time = time.time()
        #self.method_one(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        
        
        #start_time = time.time()
        #self.method_two(options)
        #print("--- %s seconds ---" % (time.time() - start_time))

        #print 'Dataset was written.'
        
        output = options['output'][0]
        
        for image_path in options['path']:
            print image_path
            
            basename = '%s.tif' % get_base_name(image_path)
                
            target = create_file_name(output, basename)
            
            print target
        
        
            start_time = time.time()
            self.method_by_block(image_path, target)
            print("--- %s seconds ---" % (time.time() - start_time))
        
            print 'Dataset was written.'
        
        #start_time = time.time()
        #self.method_four(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        #print 'Dataset was written.'
