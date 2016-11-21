'''
Created on Nov 21, 2016

@author: agutierrez
'''


from __future__ import unicode_literals

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.util import create_file_name


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs=1, help='This is a stub for the, \
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
            bundle.get_NDVI()
            ndvi_file = create_file_name(output, 'ndvi.tif')
            red_edge_ndvi_file = create_file_name(output, 'red_edge_ndvi.tif')
            gndvi_file = create_file_name(output, 'gndvi.tif')
            ndre_file = create_file_name(output, 'ndre.tif')
            sovel_file = create_file_name(output, 'sovel2.tif')
            create_raster_from_reference(ndvi_file, bundle.get_NDVI(), bundle.get_raster_file())
            create_raster_from_reference(red_edge_ndvi_file, bundle.get_red_edge_NDVI(), bundle.get_raster_file())
            create_raster_from_reference(gndvi_file, bundle.get_gndvi(), bundle.get_raster_file())
            create_raster_from_reference(ndre_file, bundle.get_ndre(), bundle.get_raster_file())
            create_raster_from_reference(sovel_file, bundle.get_sobel_filter(sigma=2), bundle.get_raster_file())
