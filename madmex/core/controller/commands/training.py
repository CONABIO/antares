'''
Created on Aug 15, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_raster_from_reference

NO_VALUE = -9999

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
        
        import time


        
        
        
        print 'Dataset was written.'
        
        for path in paths:
            start_time = time.time()
            arrays[path] = open_handle(path)
            print 'Opened %s' % path
            print("--- %s seconds ---" % (time.time() - start_time))
            
        size = arrays[paths[0]].shape
        
        result = numpy.full(size,NO_VALUE)
        
        print size
        start_time = time.time()
        for i in range(size[0]):
            for j in range(size[1]):
                pixel = True
                for p in range(1, len(paths)):
                    pixel = pixel and (arrays[paths[0]][i][j] == arrays[paths[p]][i][j])
                if pixel :
                    result[i][j] = arrays[paths[0]][i][j]
                    
        for path in paths:
            del arrays[path]
        print("--- %s seconds ---" % (time.time() - start_time))
        
        start_time = time.time()
        create_raster_from_reference(output, result, paths[0])
        print("--- %s seconds ---" % (time.time() - start_time))            
                
    