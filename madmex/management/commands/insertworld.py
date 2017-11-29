'''
Created on Nov 29, 2017

@author: agutierrez
'''
import logging
from math import floor

import fiona
from rasterio import features
import rasterio
from skimage import segmentation

from madmex.management.base import AntaresBaseCommand
from madmex.util import get_basename_of_file, get_basename
import numpy as np
from django.contrib.gis.utils.layermapping import LayerMapping
from madmex.models import WorldBorder


logger = logging.getLogger(__name__)

class Command(AntaresBaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs='*', help='The file to be segmented.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        stack = options['path'][0]
        
        worldborder_mapping = {
            'fips' : 'FIPS',
            'iso2' : 'ISO2',
            'iso3' : 'ISO3',
            'un' : 'UN',
            'name' : 'NAME',
            'area' : 'AREA',
            'pop2005' : 'POP2005',
            'region' : 'REGION',
            'subregion' : 'SUBREGION',
            'lon' : 'LON',
            'lat' : 'LAT',
            'mpoly' : 'MULTIPOLYGON',
            }
        lm = LayerMapping(
                WorldBorder, stack, worldborder_mapping,
                transform=False, encoding='iso-8859-1',
                )
        lm.save(strict=True, verbose=True)
        