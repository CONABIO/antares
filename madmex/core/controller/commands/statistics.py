'''
Created on Jan 19, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import math

import gdal
import numpy
from numpy.f2py.rules import aux_rules

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.util import get_base_name


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)

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

    def handle(self, **options):
        '''
        This is the code that does the ingestion.
        '''
        interest_band = 1
        
        for image_path in options['path']:
                ds = gdal.Open(image_path)
                bands = ds.RasterCount                
                
                array = numpy.array(ds.GetRasterBand(interest_band).ReadAsArray())
                
                flat = numpy.ravel(array)
                
                length = len(flat)
                
                print get_base_name(image_path)
                count = 1                
                values = {}
                print length

                progress = 0
                print progress
                for value in flat:
                    count = count + 1
                    if not values.get(value):
                        values[value] = 1
                    else:
                        values[value] = values[value] + 1
                    
                    if count % 1000000 == 0:    
                        aux = progress
                        
                        progress = math.floor(100 * count / float(length))
                        if not aux == progress:
                            print  str(int(progress)) + '%\r'
                self.print_dict(values)
    
    def print_dict(self, values):
        for key in values.keys():
            if not key == 0:
                print '%s : %s' % (key, values.get(key))
                
    def sum_no_zero(self, values):
        
        total = 0
        for key in values.keys():
            if not key == 0:
                total = total + values.get(key)
                
        print total
        
        for key in values.keys():
            if not key == 0:
                print values.get(key) * 100 / float(total)
        
        