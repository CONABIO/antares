'''
Created on Jan 9, 2017

@author: agutierrez
'''


from __future__ import unicode_literals

import logging

import gdal
import numpy
from numpy.random.mtrand import np
from scipy import ndimage
import scipy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster_from_reference, tile_map
from madmex.mapper.data.harmonized import harmonize_images
from madmex.processing.raster import phi, rho, calculate_zonal_statistics
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_file_name, is_file


LOGGER = logging.getLogger(__name__)

INV_MASK_VALUE = 2
MAX_GAP = 7
STAT_CLASSES = 14
STAT_MAX = 7
STAT_MIN = 0
THRESHOLD = 30
THRESHOLD_COD = 0.99
THRESHOLD_LOG = 270
WINDOW_SIZE = 5

def calculate_statistics_qa(image, reference, classes, minimum, maximum, threshold_cod, threshold_log):
    
    print image.shape
    print reference.shape
    
    for i in range(reference.shape[0]):
        print 'band number %s' % i
        gauss = ndimage.filters.gaussian_filter(reference[i], sigma=1)
        laplace = ndimage.filters.laplace(gauss, mode='constant', cval=0.0)
        reference[i] = numpy.abs(laplace)
        
    minband = reference.min(axis=0)
    numpy.core.numeric.putmask(minband, minband <= int(threshold_log), 0)
    numpy.core.numeric.putmask(minband, minband != 0, 1)
    log_mask = minband
    
    
    minband = image.min(axis=0)
    numpy.core.numeric.putmask(minband, minband <= float(threshold_cod), 0)
    numpy.core.numeric.putmask(minband, minband != 0, 1)
    cod_mask = minband
    
    print numpy.unique(cod_mask, return_counts=True)
    
    image[2] = cod_mask * image[2]
    
    for i in range(image.shape[0]):
        label = numpy.zeros([image.shape[1],image.shape[2]])
    
        zonal_stats_result = calculate_zonal_statistics(image[i], label, [0])
    
        stat = {}
        stat['minimum'] = zonal_stats_result[0]
        stat['maximum'] = zonal_stats_result[1]
        stat['mean'] = zonal_stats_result[2]
        stat['std'] = zonal_stats_result[3]
        stat['median'] = numpy.array([numpy.median(image[i])])
        print stat
    
    
        
    return reference
    

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--id', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--image', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--reference', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        
        id = options["id"][0]
        image_path = options["image"][0]
        reference_path = options["reference"][0]
        output = options["output"][0]
        
        
        print image_path
        print reference_path


        image_bundle = _get_bundle_from_path(image_path)
        reference_bundle = _get_bundle_from_path(reference_path) 
        
        #extents = harmonize_images([image_bundle.get_raster(), reference_bundle.get_raster()])
        #print extents
        #print extents['x_offset']
        #print extents['y_offset']
        
        shape = image_bundle.get_raster().get_attribute(raster.DATA_SHAPE)
        
        
        invariant_array = numpy.full((shape[0], shape[1]), INV_MASK_VALUE, dtype=np.int)


        in1 = reference_bundle.get_raster_file()
        in2 = image_bundle.get_raster_file()
        in_invar = create_file_name(output, 'invariantPixelMask.tif')
        result = create_file_name(output, 'crosscorrelation_next.tif')
        to_polar = create_file_name(output, 'crosscorrelation_polar.tif')
        create_raster_from_reference(in_invar, invariant_array, image_bundle.get_raster_file(), gdal.GDT_Byte)    

        
        local = LocalProcessLauncher()
        volume = '%s:%s' % (output, output)
        shell_array = ['docker',
                       'run',
                       '--rm',
                       '-v',
                       volume,
                       'madmex/antares',
                       'correlation',
                       '-in1',
                       in1,
                       '-in2',
                       in2,
                       '-in_invar',
                       in_invar,
                       '-val_invar',
                       '%s' % INV_MASK_VALUE,
                       '-out',
                       result,
                       '-window_size',
                       '%s' % WINDOW_SIZE,
                       '-max_gap',
                       '%s' % MAX_GAP]
        shell_string = ' '.join(shell_array)
        

        
        
        print shell_string
        
        if not is_file(result):
            log = local.execute(shell_string)
            print log
        
        crosscorrelation = raster.Data(result, 'GTiff')
        
        print crosscorrelation.get_attribute(raster.PROJECTION)
        print crosscorrelation.get_attribute(raster.GEOTRANSFORM)
        

        
        #tile_map(result, result)
        
        
        correlation_array = crosscorrelation.read_data_file_as_array()
        
        
        
        
        band_0 = correlation_array[0,:]
        band_1 = correlation_array[1,:]

        phi_band = phi(band_0, band_1)
        rho_band = rho(band_0, band_1)
        
        correlation_array[0,:] = phi_band
        correlation_array[1,:] = rho_band
        
        create_raster_from_reference(to_polar, correlation_array, result)


        crosscorrelation_polar = raster.Data(to_polar, 'GTiff')

        extents = harmonize_images([crosscorrelation_polar, reference_bundle.get_raster()])
        x_offset = extents['x_offset'][1]
        y_offset = extents['y_offset'][1]
        x_tile_size = extents['x_range']
        y_tile_size = extents['y_range']
        print x_offset        
        
        aux_name = create_file_name(output, 'auxiliar.tif')
        
        
        
        tile_map(reference_bundle.get_raster_file(), aux_name, x_tile_size, y_tile_size, x_offset, y_offset)
        
        
        aux_array = raster.Data(aux_name, 'GTiff').read_data_file_as_array()
        crosscorrelation_polar_array = crosscorrelation_polar.read_data_file_as_array()
        
        res = calculate_statistics_qa(crosscorrelation_polar_array, aux_array, STAT_CLASSES, STAT_MIN, STAT_MAX, THRESHOLD_COD, THRESHOLD_LOG)
        
        
        to_see = create_file_name(output, 'just_to_see.tif')
               
        create_raster_from_reference(to_see, res, aux_name)
        
        
