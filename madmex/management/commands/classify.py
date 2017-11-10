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
from madmex.util.landsat import CLOUD, CLOUD_SHIFT, CLEAR, CLEAR_SHIFT, \
    CONFIDENCE_CLOUD, CONFIDENCE_CLOUD_SHIFT


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
            
            profile = src.profile
            
            print profile
            profile.update(
                dtype=rasterio.ubyte,
                compress='lzw',
                nodata=None)
            
            my_values =  map(lambda x: bin(x)[2:].zfill(16), numpy.unique(qa_array, return_counts=True)[0])
            my_count = numpy.unique(qa_array, return_counts=True)[1]
            for index in range(len(my_values)):
                print '%s -> %s' % (my_values[index],my_count[index])
           
            
            print qa_array.shape
            

            
            cloud_mask = numpy.bitwise_and(qa_array, CONFIDENCE_CLOUD) >> CONFIDENCE_CLOUD_SHIFT
            

            
            cloud_mask_file = create_filename(filepath, 'qa.tif')
            
            
            print numpy.unique(cloud_mask, return_counts=True)
            
            
            
            
            print cloud_mask_file
            
            print cloud_mask.shape
            
            with rasterio.open(cloud_mask_file, 'w', **profile) as dst:
                dst.write(cloud_mask.astype(rasterio.ubyte))
            
            
        
        
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
        
        