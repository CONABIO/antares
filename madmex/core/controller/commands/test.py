'''
Created on Nov 21, 2016

@author: agutierrez
'''


from __future__ import unicode_literals

import numpy

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.util import create_filename, get_basename


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        output = options['output'][0]
        for path in options['path']:
            bundle = _get_bundle_from_path(path)
            basename = get_basename(bundle.get_raster_file())
            bundle.get_NDVI()
            ndvi_file = create_filename(output, 'ndvi.tif')
            red_edge_ndvi_file = create_filename(output, 'red_edge_ndvi.tif')
            gndvi_file = create_filename(output, 'gndvi.tif')
            ndre_file = create_filename(output, 'ndre.tif')
            sovel_file = create_filename(output, 'sovel2.tif')
            
            all_file = create_filename(output, '%s_all_features.tif' % basename)
            
            print all_file
            
            image_array = bundle.get_raster().read_data_file_as_array()
            
            ndvi_array = bundle.get_NDVI()
            ndvi_array[ndvi_array<=-1] = -1
            ndvi_array[ndvi_array>=1] = 1
            
            red_edge_ndvi_array = bundle.get_red_edge_NDVI()
            red_edge_ndvi_array[red_edge_ndvi_array<=-1] = -1
            red_edge_ndvi_array[red_edge_ndvi_array>=1] = 1
            
            gndvi_array = bundle.get_gndvi()
            gndvi_array[gndvi_array<=-1] = -1
            gndvi_array[gndvi_array>=1] = 1
            
            ndre_array = bundle.get_ndre()
            ndre_array[ndre_array<=-1] = -1
            ndre_array[ndre_array>=1] = 1
            
            sobel_filter_array = bundle.get_sobel_filter(sigma=2)
            
            #sobel_filter_array[sobel_filter_array<=-1] = -1
            #sobel_filter_array[sobel_filter_array>=1] = 1
            
            #create_raster_from_reference(ndvi_file, ndvi_array, bundle.get_raster_file())
            #create_raster_from_reference(red_edge_ndvi_file, red_edge_ndvi_array, bundle.get_raster_file())
            #create_raster_from_reference(gndvi_file, gndvi_array, bundle.get_raster_file())
            #create_raster_from_reference(ndre_file, ndre_array, bundle.get_raster_file())
            create_raster_from_reference(sovel_file, sobel_filter_array, bundle.get_raster_file())

            all_features = numpy.array([image_array[0],
                                        image_array[1],
                                        image_array[2],
                                        image_array[3],
                                        image_array[4],
                                        ndvi_array,
                                        red_edge_ndvi_array,
                                        gndvi_array,
                                        ndre_array,
                                        sobel_filter_array])
            
            print image_array[0].shape
            print image_array[1].shape
            print image_array[2].shape
            print image_array[3].shape
            print image_array[4].shape
            print ndvi_array.shape
            print red_edge_ndvi_array.shape
            print gndvi_array.shape
            print ndre_array.shape
            print sobel_filter_array.shape
            print all_features.shape
            
            create_raster_from_reference(all_file, all_features, bundle.get_raster_file(), creating_options=['BIGTIFF=YES'])
