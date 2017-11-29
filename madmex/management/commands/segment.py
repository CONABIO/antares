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
        
        

        output_vector_file = '/Users/agutierrez/Documents/jamaica/rapideye/%s.gpkg' % get_basename(stack)

        print output_vector_file

        # Read multilayer raster to 3D array. Dimensions order must be x,y,z
        with rasterio.open(stack) as src:
            meta = src.meta
            transform = src.transform
            img = np.empty((src.height, src.width, src.count),
                    dtype=src.meta['dtype'])
            for layer_id in range(src.count):
                img[:,:,layer_id] = src.read(layer_id + 1)
                area_ha = (src.res[0] ** 2 * src.width * src.height) / 10000



        ## Slick parameters
        avg_segment_size_ha = 5
        compactnesses = [0.01]
        n_segments = int(floor(area_ha / avg_segment_size_ha))
        # 
        for compactness in compactnesses:
            segments = segmentation.slic(img, compactness = compactness,
                                 n_segments=n_segments, multichannel = True,
                                enforce_connectivity=True)
            # Vectorize
            shapes = features.shapes(segments.astype(np.uint16), transform=transform)
            
            
            
            # Prepare schema
            fiona_kwargs = {'crs': meta['crs'],
                    'driver': 'GPKG',
                    'schema': {'geometry': 'Polygon',
                    'properties': {'id': 'int'}}}
            # Write to file
            with fiona.open(output_vector_file, 'w', layer='slic_%3f_%d' % (compactness, n_segments),
                    **fiona_kwargs) as dst:
                for item in shapes:
                    feature = {'geometry': item[0], 'properties': {'id': int(item[1])}}
                    
                    dst.write(feature)