'''
Created on Jun 23, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import os
from subprocess import call

import gdal
import ogr

from madmex.core.controller.base import BaseCommand
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import GTIFF, create_raster_from_reference
from madmex.processing.raster import calculate_index
from madmex.util import create_filename, create_directory_path


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

BLUE = 1
GREEN = 2
RED = 3
NIR = 4
SWIR = 5

BLUE_L8 = 2
GREEN_L8 = 3
RED_L8 = 4
NIR_L8 = 5
SWIR_L8 = 6

def open_handle(filename):
    data = raster.Data(filename, GTIFF)
    data_array = data.read_data_file_as_array()
    data.close()
    return data_array
    
def get_mask(filename):
    vector_fn = filename
    print vector_fn
    # Define pixel_size and NoData value of new raster
    pixel_size = 30
    NoData_value = -9999
        
    # Open the data source and read in the extent
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
        
    print source_layer.GetExtent()
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    print x_res, y_res
    target_ds = gdal.GetDriverByName(str('MEM')).Create('', x_res, y_res, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
        
    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])
        
    # Read as array
    array = band.ReadAsArray()
    return array

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
        parser.add_argument('--output', nargs='*')
        parser.add_argument('--debug')
    def handle(self, **options):
        '''
        This is the code that does the ingestion.        
        indexes --path /LUSTRE/MADMEX/staging/2016_tasks/Humedales_for_ctroche/LT/Landsat_2000_2008/L5_021_047_2000_022_sr/ --shape /LUSTRE/MADMEX/staging/2016_tasks/Humedales_for_ctroche/LT/AE_LT_new.shp --output 
        '''
        path = options['path'][0]

        for mask_file in os.listdir(path):
            if mask_file.endswith('_cfmask.tif'):
                print mask_file
                basename = mask_file.replace('_cfmask.tif', '')
                print basename
                cloud_file_name = mask_file

        LOGGER.info('Calculating indexes for Landsat scenes.')

        band_name = basename + '_sr_band%s.tif'
        
        final_path = options['output'][0]
        create_directory_path(final_path)
        cloud_file = create_filename(path, cloud_file_name)
        cloud_array = open_handle(cloud_file)
        cloud_mask = (cloud_array == 4)

        LOGGER.debug('Recognize sensor depending on file name.')

        if 'L8' in path:
            LOGGER.debug('Landsat 8 scene was detected.')
            blue_file = create_filename(path, band_name % BLUE_L8)
            green_file = create_filename(path, band_name % GREEN_L8)
            red_file = create_filename(path, band_name % RED_L8)
            nir_file = create_filename(path, band_name % NIR_L8)
            swir_file = create_filename(path, band_name % SWIR_L8)        
        else:
            LOGGER.debug('Landsat 4, 5 or scene was detected.')
            blue_file = create_filename(path, band_name % BLUE)
            green_file = create_filename(path, band_name % GREEN)
            red_file = create_filename(path, band_name % RED)
            nir_file = create_filename(path, band_name % NIR)
            swir_file = create_filename(path, band_name % SWIR)
            
        LOGGER.debug('Loading bands of interest.')

        green_array = open_handle(green_file)
        red_array = open_handle(red_file)
        nir_array = open_handle(nir_file)
        swir_array = open_handle(swir_file)
            
        LOGGER.debug('Calculating indexes.')
         
        ndvi_array = calculate_index(nir_array, red_array)
        mndwi_array = calculate_index(green_array, swir_array)
        ndwig_array = calculate_index(nir_array, swir_array)
        ndwim_array = calculate_index(green_array, nir_array)
        
        LOGGER.debug('Setting cloud mask values to -999.')    
        
        ndvi_array[cloud_mask] = -999
        mndwi_array[cloud_mask] = -999
        ndwig_array[cloud_mask] = -999
        ndwim_array[cloud_mask] = -999

        LOGGER.debug('Creating files for indexes.')

        ndvi_final_file = create_filename(final_path, basename + '_ndvi.tif')
        mndwi_final_file = create_filename(final_path, basename + '_mndwi.tif')
        ndwig_final_file = create_filename(final_path, basename + '_ndwig.tif')
        ndwim_final_file = create_filename(final_path, basename + '_ndwim.tif')
            
        ndvi_clipped_file = create_filename(final_path, basename + '_ndvi_clipped.tif')
        mndwi_clipped_file = create_filename(final_path, basename + '_mndwi_clipped.tif')
        ndwig_clipped_file = create_filename(final_path, basename + '_ndwig_clipped.tif')
        ndwim_clipped_file = create_filename(final_path, basename + '_ndwim_clipped.tif')
            
        ndvi_file = create_filename(final_path, basename + '_ndvi_pre.tif')
        mndwi_file = create_filename(final_path, basename + '_mndwi_pre.tif')
        ndwig_file = create_filename(final_path, basename + '_ndwig_pre.tif')
        ndwim_file = create_filename(final_path, basename + '_ndwim_pre.tif')
            
        files = [ndvi_file, mndwi_file, ndwig_file, ndwim_file]
        clipped_files = [ndvi_clipped_file, mndwi_clipped_file, ndwig_clipped_file, ndwim_clipped_file]
        final_files = [ndvi_final_file, mndwi_final_file, ndwig_final_file, ndwim_final_file]

        LOGGER.debug('Writing information to files.')

        create_raster_from_reference(ndvi_file, ndvi_array, green_file)
        create_raster_from_reference(mndwi_file, mndwi_array, green_file)
        create_raster_from_reference(ndwig_file, ndwig_array, green_file)
        create_raster_from_reference(ndwim_file, ndwim_array, green_file)

        LOGGER.debug('Deleting arrays to release memory.')

        del ndvi_array
        del mndwi_array
        del ndwig_array
        del ndwim_array
        del cloud_array

        LOGGER.debug('Reference rgb file creation.')

        rgb_file = create_filename(final_path, basename + '_rgb.tif')
        merge_command = ['/Library/Frameworks/GDAL.framework/Programs/gdalbuildvrt', '-separate', '-o', rgb_file, red_file, green_file, blue_file]
        call(merge_command)
        shape = options['shape'][0]

        LOGGER.debug('Cookie cut files using the given shape.')

        for i in range(4):
            clip_command = ['/Library/Frameworks/GDAL.framework/Programs/gdalwarp', '-crop_to_cutline', '-cutline', shape, files[i], clipped_files[i]]
            call(clip_command)
        
        for i in range(4):
            aux_array = open_handle(clipped_files[i])
            aux_array[(aux_array == 0)] = -9999
            create_raster_from_reference(final_files[i], aux_array, ndvi_clipped_file)
        
        if not options['debug']:
            LOGGER.info('Remove auxiliary files.')
            os.remove(ndvi_clipped_file)
            os.remove(mndwi_clipped_file)
            os.remove(ndwig_clipped_file)
            os.remove(ndwim_clipped_file)
            os.remove(ndvi_file)
            os.remove(mndwi_file)
            os.remove(ndwig_file)
            os.remove(ndwim_file)

        print 'Done'
        
