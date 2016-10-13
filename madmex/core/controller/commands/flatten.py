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

    def method_by_block(self, path, output, block_size=8192):
        '''
        Method to create a mask from a given raster writing by block.
        '''
        outDataset = create_empty_raster_from_reference(output, path, data_type=gdal.GDT_Byte)
        dataset = gdal.Open(path, gdalconst.GA_ReadOnly)
        if dataset is None:
            print "The dataset could not be opened"
        
            sys.exit(-1)        
        classification_band_a = dataset.GetRasterBand(1)
        classification_band_b = dataset.GetRasterBand(2)
        classification_band_c = dataset.GetRasterBand(3)
        classification_band_d = dataset.GetRasterBand(4)
        classification_band_e = dataset.GetRasterBand(5)
        classification_band_f = dataset.GetRasterBand(6) 
        y_size = classification_band_a.YSize
        x_size = classification_band_a.XSize
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
                A = classification_band_a.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                B = classification_band_b.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                C = classification_band_c.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                D = classification_band_d.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                E = classification_band_e.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                F = classification_band_f.ReadAsArray(j, i, cols, rows).astype(numpy.int16)
                
                
                res = numpy.maximum.reduce([A,B,C,D,E,F])
                
                count = count + 1
                outDataset.GetRasterBand(1).WriteArray(res,j,i)
                aux = current
                current = count * 100 / total
                
                if aux != current:
                    print current
                
        outDataset = None
        
    
    
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
        path = options['path'][0]
        
        
        self.method_by_block(path, output)
        
        print output
        #start_time = time.time()
        #self.method_four(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        #print 'Dataset was written.'
