'''
Created on Jun 23, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import logging

import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import GTIFF, create_raster_from_reference
from madmex.persistence.driver import persist_bundle
from madmex.processing.raster import calculate_index
from madmex.util import create_file_name, create_directory_path


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

BLUE = 1
GREEN = 2
RED = 3
NIR = 4
SWIR = 5

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)

def open_handle(filename):
    data = raster.Data(filename, GTIFF)
    data_array = data.read_data_file_as_array()
    data.close()
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
        parser.add_argument('--shape', nargs='*')
    def handle(self, **options):
        '''
        This is the code that does the ingestion.
        '''
        LOGGER.info('Calculating indexes for Landsat scenes.')
        
        band_name = 'LT50210472000022AAA02_sr_band%s.tif'
        
        result = '/Users/agutierrez/Documents/humedales'
        final_path = create_file_name(result, 'indexes2')
        create_directory_path(final_path)
        
        
        for path in options['path']:
            cloud_file = create_file_name(path, 'LT50210472000022AAA02_cfmask.tif')
            cloud_array = open_handle(cloud_file)
            print cloud_array
            print numpy.amin(cloud_array), numpy.amax(cloud_array)
            print numpy.unique(cloud_array)
            
            cloud_mask = (cloud_array == 4)
            
            
            blue_file = create_file_name(path, band_name % BLUE)
            green_file = create_file_name(path, band_name % GREEN)
            red_file = create_file_name(path, band_name % RED)
            nir_file = create_file_name(path, band_name % NIR)
            swir_file = create_file_name(path, band_name % SWIR)
            
            LOGGER.info('Loading bands of interest.')
            print green_file
            print red_file
            print nir_file
            print swir_file
            

            green_array = open_handle(green_file)
            red_array = open_handle(red_file)
            nir_array = open_handle(nir_file)
            swir_array = open_handle(swir_file)
            
            
            ndvi_array = calculate_index(nir_array, red_array)
            mndwi_array = calculate_index(green_array, swir_array)
            ndwig_array = calculate_index(nir_array, swir_array)
            ndwim_array = calculate_index(green_array, nir_array)
            
            ndvi_array[cloud_mask] = -999
            mndwi_array[cloud_mask] = -999
            ndwig_array[cloud_mask] = -999
            ndwim_array[cloud_mask] = -999
            
            print numpy.unique(ndvi_array)
            print numpy.unique(mndwi_array)
            print numpy.unique(ndwig_array)
            print numpy.unique(ndwim_array)
            
            ndvi_clipped_file = create_file_name(final_path, 'ndvi_clipped.tif')
            mndwi_clipped_file = create_file_name(final_path, 'mndwi_clipped.tif')
            ndwig_clipped_file = create_file_name(final_path, 'ndwig_clipped.tif')
            ndwim_clipped_file = create_file_name(final_path, 'ndwim_clipped.tif')
            
            ndvi_file = create_file_name(final_path, 'ndvi.tif')
            mndwi_file = create_file_name(final_path, 'mndwi.tif')
            ndwig_file = create_file_name(final_path, 'ndwig.tif')
            ndwim_file = create_file_name(final_path, 'ndwim.tif')
            
            files = [ndvi_file, mndwi_file, ndwig_file, ndwim_file]
            clipped_files = [ndvi_clipped_file, mndwi_clipped_file, ndwig_clipped_file, ndwim_clipped_file]
            
            create_raster_from_reference(ndvi_file, ndvi_array, green_file)
            create_raster_from_reference(mndwi_file, mndwi_array, green_file)
            create_raster_from_reference(ndwig_file, ndwig_array, green_file)
            create_raster_from_reference(ndwim_file, ndwim_array, green_file)
            
            
        from subprocess import call
        rgb_file = create_file_name(final_path, 'rgb.tif')
        merge_command = ['/Library/Frameworks/GDAL.framework/Programs/gdalbuildvrt', '-separate', '-o', rgb_file, red_file, green_file, blue_file]
        call(merge_command)
        
        shape = options['shape'][0]
        print shape
        
        for i in range(4):
            clip_command = ['/Library/Frameworks/GDAL.framework/Programs/gdalwarp', '-crop_to_cutline', '-cutline', shape, files[i], clipped_files[i]]
            call(clip_command)
        print 'Done'
