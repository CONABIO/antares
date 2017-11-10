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
from madmex.util import create_filename, get_files_from_folder_filter, \
    get_files_from_folder


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--path', nargs=1, help='Path to image.')

    def handle(self, **options):
        
        filepath = options['path'][0]
    
        qa_file = get_files_from_folder_filter(filepath, r'.*qa.tif$')[0]
        
        print qa_file
        
        with rasterio.open(create_filename(filepath, qa_file)) as src:
            qa_array = src.read()
            
            print numpy.unique(qa_array, return_counts=True)
            
            print qa_array.shape
        
        
        files_of_interest = get_files_from_folder_filter(filepath, r'.*sr_band[0-9]+.tif$')   
        bands = []
        print files_of_interest
        for filename in files_of_interest:
            print filename
            complete_path = create_filename(filepath, filename)
            with rasterio.open(complete_path) as src:
                
                
                bands.append(src.read())
                
                
        stack = numpy.array(bands)
        
        print stack.shape
        
        