'''
Created on Nov 29, 2017

@author: agutierrez
'''
import json
import logging
from math import floor

from django.contrib.gis import geos
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.geos.geometry import GEOSGeometry
import fiona
import geojson
from rasterio import features
import rasterio
from shapely.geometry import shape
from skimage import segmentation

from madmex.management.base import AntaresBaseCommand
from madmex.models import Segment
from madmex.util import get_basename_of_file, get_basename
import numpy as np


logger = logging.getLogger(__name__)

worldborder_mapping = {
            'fips' : 'FIPS',
            'mpoly' : 'MULTIPOLYGON',
            }

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
        
        

        output_vector_file = '/Users/agutierrez/Desktop/Caribe/%s.gpkg' % get_basename(stack)


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
            
            
            

            # Write to file
            for item in shapes:
                feature = {'geometry': item[0], 'properties': {'id': int(item[1])}}
                    
                #print json.dumps(item[0])
                    
                    
                s = json.dumps(item[0])
                g1 = geojson.loads(s)
                g2 = shape(g1)
                    
                #epsg = meta['crs']['init'].split(':')[1]
                #print epsg
                myGeom = GEOSGeometry(g2.wkt)
                    
                #gcoord = SpatialReference(4326)
                #mycoord = SpatialReference(int(epsg))
                
                #trans = CoordTransform(mycoord, gcoord)

                    
                seg = Segment(segment_id = int(item[1]),
                                  mpoly = geos.MultiPolygon(myGeom))
                seg.save()
            '''
            # Prepare schema
            fiona_kwargs = {'crs': meta['crs'],
                    'driver': 'GPKG',
                    'schema': {'geometry': 'Polygon',
                    'properties': {'id': 'int'}}}
            with fiona.open(output_vector_file, 'w', layer='slic_%3f_%d' % (compactness, n_segments),
                    **fiona_kwargs) as dst:
                for item in shapes:
                    feature = {'geometry': item[0], 'properties': {'id': int(item[1])}}
                                        
                    dst.write(feature)
            '''