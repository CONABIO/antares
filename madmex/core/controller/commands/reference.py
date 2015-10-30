'''
Created on Oct 8, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex import _, util
from madmex.core.controller.base import BaseCommand
from madmex.mapper.data.raster import create_raster_tiff_from_reference
from madmex.preprocessing.maskingwithreference import get_images_for_tile, \
    create_reference_array


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
            bundle = Bundle(new_paths[0])
            re_raster_metadata = bundle.get_raster().metadata
            create_raster_tiff_from_reference(re_raster_metadata, '%s.tif' % name, reference_array)
