'''
Created on Jan 9, 2017

@author: agutierrez
'''


from __future__ import unicode_literals

import logging

import gdal
import numpy
from numpy.random.mtrand import np

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.mapper.data.harmonized import harmonize_images
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_file_name


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
        log = local.execute(shell_string)
        
        print log
