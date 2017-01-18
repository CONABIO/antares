'''
Created on Jan 9, 2017

@author: agutierrez
'''


from __future__ import unicode_literals

import logging

import gdal
import numpy
from numpy.random.mtrand import np
from scipy import ndimage, stats

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster_from_reference, tile_map
from madmex.mapper.data.harmonized import harmonize_images
from madmex.persistence.database.connection import QualityAssessment
from madmex.persistence.driver import find_datasets, \
    acquisitions_by_mapgrid_and_date, get_pair_quality, persist_quality
from madmex.processing.raster import phi, rho
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_file_name, is_file, adapt_numpy_float


LOGGER = logging.getLogger(__name__)

INV_MASK_VALUE = 2
MAX_GAP = 7
STAT_CLASSES = 14
STAT_MAX = 7
STAT_MIN = 0
THRESHOLD = 30
THRESHOLD_COD = 0.8
THRESHOLD_LOG = 270
WINDOW_SIZE = 5

def calculate_statistics_qa(image, reference, classes, minimum, maximum, threshold_cod, threshold_log):
    
    print image.shape
    print reference.shape

    print 'reference at beginning', reference.shape
    print reference
    
    for i in range(reference.shape[0]):
        print 'band number %s' % i
        gauss = ndimage.filters.gaussian_filter(reference[i], sigma=1)
        laplace = ndimage.filters.laplace(gauss, mode='constant', cval=0.0)
        reference[i] = numpy.abs(laplace)
    
    print 'reference'
    print reference
        
    minband = reference.min(axis=0)
    numpy.core.numeric.putmask(minband, minband <= int(threshold_log), 0)
    numpy.core.numeric.putmask(minband, minband != 0, 1)
    log_mask = minband
    
    print 'log_mask', log_mask.shape
    
    print log_mask
    
    for i in range(image.shape[0]):
        image[i] = image[i] * log_mask
    
    
    minband = image.min(axis=0)
    numpy.core.numeric.putmask(minband, minband <= float(threshold_cod), 0)
    numpy.core.numeric.putmask(minband, minband != 0, 1)
    cod_mask = minband
    
    print numpy.unique(cod_mask, return_counts=True)
    

    for i in range(image.shape[0]):
        image[i] = cod_mask * image[i]
    
    print 'Image', image
    
    stats = {}
    
    for i in range(image.shape[0]):    
        masked = numpy.ma.masked_equal(image[i], 0.0, copy=False)
        stat = {}
        stat['minimum'] = masked.min()
        stat['maximum'] = masked.max()
        stat['mean'] = masked.mean()
        stat['std'] = masked.mean()
        stat['median'] = numpy.ma.median(masked).data[0]
        histogram = numpy.histogram(masked.compressed(), classes, range=(minimum, maximum))
        normalized_histogram = 1.0 * histogram[0] / len(masked.compressed())
        stat['histogram_bins'] = histogram[1]
        stat['histogram'] = normalized_histogram
        stats['band_%s' % i] = stat
    return stats
    
def calculate_decision(histogram, bins):
    bins = bins[0:numpy.size(bins)-1]
    thresh_above = histogram[numpy.where(bins>2)]
    thresh_below = histogram[numpy.where(bins<=2)]
    thresh_above = numpy.sort(thresh_above)
    lower_quartile = stats.scoreatpercentile(thresh_above, 25)
    upper_quartile = stats.scoreatpercentile(thresh_above, 75)
    outlier = 2 * upper_quartile - lower_quartile
    decision = bool(numpy.size(thresh_above[numpy.where(thresh_below > outlier)]))
    return decision

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
        
        mapgrid = '1449619'
        
        acq = get_pair_quality(mapgrid)
        
        for image in acq:
            
            print image.pk_id
            print image.pk_id
            
        
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
        
        #create_raster_from_reference(to_polar, correlation_array, result)


        crosscorrelation_polar = raster.Data(to_polar, 'GTiff')

        extents = harmonize_images([crosscorrelation_polar, reference_bundle.get_raster()])
        x_offset = extents['x_offset'][1]
        y_offset = extents['y_offset'][1]
        x_tile_size = extents['x_range']
        y_tile_size = extents['y_range']
        aux_name = create_file_name(output, 'auxiliar.tif')
        tile_map(reference_bundle.get_raster_file(), aux_name, x_tile_size, y_tile_size, x_offset, y_offset)
        aux_array = raster.Data(aux_name, 'GTiff').read_data_file_as_array()
        crosscorrelation_polar_array = crosscorrelation_polar.read_data_file_as_array()
        stats = calculate_statistics_qa(crosscorrelation_polar_array, aux_array, STAT_CLASSES, STAT_MIN, STAT_MAX, THRESHOLD_COD, THRESHOLD_LOG)
        desision = calculate_decision(stats['band_1']['histogram'], stats['band_1']['histogram_bins'])
        
        
        print stats
        
        quality = QualityAssessment(
            decision=desision,
            max=adapt_numpy_float(stats['band_1']['maximum']),
            min=adapt_numpy_float(stats['band_1']['minimum']),
            median=adapt_numpy_float(stats['band_1']['median']),
            mean=adapt_numpy_float(stats['band_1']['mean']),
            standard_deviation=adapt_numpy_float(stats['band_1']['std']),
            product_id=1,
            reference_id=2)
        persist_quality(quality)
        
        
        
        print desision
        
        
