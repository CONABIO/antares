'''
Created on Jul 29, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import struct
import sys

import gdal
import gdalconst

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_empty_raster_from_reference


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
    def handle(self, **options):
        print 'hello'
        path = options['path'][0]
        output = options['output'][0]
        
        print path
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
            
            if (row%100) == 0:
                print row
        
        print 'Dataset was written.'
        