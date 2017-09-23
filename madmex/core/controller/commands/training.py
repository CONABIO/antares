'''
Created on Aug 15, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import gdal
import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_raster_from_reference


NO_DATA = 0

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

        paths = options['path']
        output = options['output'][0]
        
        print output
        arrays = {}

        image1 = open_handle(paths[0])
        
        #import time

        #for path in paths:
        #    start_time = time.time()
        #    arrays[path] = open_handle(path)
        #    print 'Opened %s' % path
        #    print("--- %s seconds ---" % (time.time() - start_time))

        size = image1.shape
        
        #start_time = time.time()     
        for p in range(2, len(paths)):
            #print 'Image %s ' % p
            image2 = open_handle(paths[p])
            mask = numpy.logical_and(numpy.equal(image1,open_handle(paths[1])), numpy.equal(image1,image2))
        image1[~mask]=NO_DATA

        #for path in paths:
            #del arrays[path]
        #print("--- %s seconds ---" % (time.time() - start_time))
        
        #start_time = time.time()
        create_raster_from_reference(output, image1y, paths[0], data_type=gdal.GDT_Byte)
        #print("--- %s seconds ---" % (time.time() - start_time))            
