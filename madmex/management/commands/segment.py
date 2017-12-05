'''
Created on Nov 29, 2017

@author: agutierrez
'''
import json
import logging
from math import floor
import time

from django.contrib.gis import geos
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.db import transaction, connection
import fiona
import geojson
from rasterio import features
import rasterio
from shapely.geometry import shape
from skimage import segmentation

from madmex.configuration import SETTINGS
from madmex.management.base import AntaresBaseCommand
from madmex.model.unsupervised import slic, bis
from madmex.models import Segment
from madmex.util import get_basename_of_file, get_basename
import numpy as np


logger = logging.getLogger(__name__)

worldborder_mapping = {
            'fips' : 'FIPS',
            'mpoly' : 'MULTIPOLYGON',
            }

def slic_segmentation(image_path, avg_segment_size_ha=5, compactness=0.01):
    with rasterio.open(image_path) as src:
        meta = src.meta
        transform = src.transform
        img = np.empty((src.height, src.width, src.count),
                    dtype=src.meta['dtype'])
        for layer_id in range(src.count):
            img[:,:,layer_id] = src.read(layer_id + 1)
        area_ha = (src.res[0] ** 2 * src.width * src.height) / 10000

    options = {'area_ha':area_ha,
               'avg_segment_size_ha':avg_segment_size_ha,
               'compactness':compactness}

    segmentation = slic.Model(options)
    segments = segmentation.predict(img)
    return segments, transform, meta



def persist_database(shapes, meta):
    data = []
    query = 'INSERT INTO madmex_segment (segment_id, mpoly) VALUES '
    insert_string = '(\'%d\', ST_Transform(ST_GeomFromText ( \'%s\' , %d ), 4326))'
    
    for item in shapes:
        s = json.dumps(item[0])
        g1 = geojson.loads(s)
        g2 = shape(g1)
        myGeom = GEOSGeometry(g2.wkt)   
        print myGeom 
        data.append(insert_string % (int(item[1]), myGeom, int(meta['crs']['init'].split(':')[1])))
    query = query + ','.join(data) +';'    
    return query
    
def persist_file(shapes, output, meta):
    fiona_kwargs = {'crs': meta['crs'],
                    'driver': 'GPKG',
                    'schema': {'geometry': 'Polygon',
                    'properties': {'id': 'int'}}}
    
    with fiona.open(output, 'w', layer='slic', **fiona_kwargs) as dst:
        for item in shapes:
            feature = {'geometry': item[0], 'properties': {'id': int(item[1])}}
            dst.write(feature)
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
        output_vector_file = '/Users/agutierrez/%s.gpkg' % get_basename(stack)
        
        
        segmentation = bis.Model()
        
        
        shapes, transform, meta = segmentation.predict(stack)
            
        # Vectorize
        #shapes = features.shapes(segments.astype(np.uint16), transform=transform)
            
        
        start_time = time.time()
        print 'about to start query' 
        query = persist_database(shapes, meta)
        print 'done'
        print time.time() - start_time
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute(query)
        transaction.commit()  
        print time.time() - start_time
        
        #persist_file(shapes, output_vector_file, meta)
