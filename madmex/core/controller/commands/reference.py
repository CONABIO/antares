'''
Created on Oct 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import numpy

from madmex import _, util
from madmex.core.controller.base import BaseCommand
from madmex.mapper.data.raster import create_raster_tiff_from_reference
from madmex.preprocessing.maskingwithreference import get_images_for_tile, \
    create_reference_array, create_stacked_array_rapideye


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--paths', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--tiles', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--name', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        paths = options['paths']
        print paths
        tiles = options['tiles']
        name = ''.join(options['name'])

        from madmex.mapper.bundle.rapideye import Bundle
        
        if tiles:
            for tile in tiles:
                sensor_id = 1
                product_id = 2
                new_paths = get_images_for_tile(int(tile), sensor_id, product_id)
                reference_array = create_reference_array(new_paths)
                bundle = Bundle(new_paths[0])
                re_raster_metadata = bundle.get_raster().metadata
                create_raster_tiff_from_reference(re_raster_metadata, '%s.tif' % tile, reference_array)
        if paths:
            new_paths = map(util.get_parent, paths)
            reference_array = numpy.sort(create_stacked_array_rapideye(new_paths), axis=0)
            
            
            medians = numpy.empty((reference_array.shape[1], reference_array.shape[2], reference_array.shape[3]))
            limit = reference_array.shape[1] / 5
            
            for band in range(reference_array.shape[1]):
                array_band = numpy.ma.array(reference_array[:, band, :, :], mask = reference_array[:, band, :, :]==0)
                medians[band] = numpy.ma.median(array_band, axis=0)
            
            bundle = Bundle(new_paths[0])
            re_raster_metadata = bundle.get_raster().metadata
            create_raster_tiff_from_reference(re_raster_metadata, '%s_max.tif' % name, reference_array[0])
            create_raster_tiff_from_reference(re_raster_metadata, '%s_mean.tif' % name, reference_array[8])
            create_raster_tiff_from_reference(re_raster_metadata, '%s_median.tif' % name, medians)
            create_raster_tiff_from_reference(re_raster_metadata, '%s_min.tif' % name, reference_array[reference_array.shape[0] - 1])
