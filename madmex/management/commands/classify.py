'''
Created on Oct 31, 2017

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import os
import re

import numpy
import rasterio

from madmex.management.base import AntaresBaseCommand
from madmex.util import create_file_name


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1, help='Path to image.')

    def handle(self, **options):
        
        filepath = options['path'][0]
    
        pattern = re.compile(r'.*sr_band.*')    
        bands = []
        for filename in [name for name in os.listdir(filepath) if pattern.match(name)]:
            complete_path = create_file_name(filepath, filename)
            with rasterio.open(complete_path) as src:
                
                
                bands.append(src.read())
                
                
        stack = numpy.array(bands)
        
        print stack.shape
        
        