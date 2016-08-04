'''
Created on Jul 29, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import struct
import sys

import gdal
import gdalconst
import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_empty_raster_from_reference, \
    create_raster_from_reference


INITIAL_ARRAY = [[1,2,3,8,9,10,11,12,13,16,14,15,20,24,25,26],
               [4,5,6,7,17,18,19,21,22,23,27,28,29,30,31]]
FINAL_ARRAY = [1,2]

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
        
        outDataset = create_empty_raster_from_reference(output, path)
        
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
        create_raster_from_reference(output, new_array.reshape(original_shape), path)
        
        
    
    
    def handle(self, **options):
        print 'hello'
        import time
        #start_time = time.time()
        #self.method_one(options)
        #print("--- %s seconds ---" % (time.time() - start_time))
        
        
        start_time = time.time()
        self.method_two(options)
        print("--- %s seconds ---" % (time.time() - start_time))
        print 'Dataset was written.'
        