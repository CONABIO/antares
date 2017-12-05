'''
Created on Dec 4, 2017

@author: agutierrez
'''
import json
from pydoc import locate

from django.contrib.gis.geos.geometry import GEOSGeometry
import fiona
import geojson
from shapely.geometry.geo import shape
from shapely.geometry.multipolygon import MultiPolygon

from madmex.management.base import AntaresBaseCommand
import madmex.models


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
        parser.add_argument('--column', nargs='*', help='The file to be segmented.')
        parser.add_argument('--model', nargs='*', help='The file to be segmented.')

    def handle(self, **options):
        path = options['path'][0]
        column = options['column'][0]
        model = options['model'][0]
        
        
        
        with fiona.open(path) as src:
            print json.dumps(src.schema, indent=4)
            print src.crs
            for feat in src:
                
                #print feat['geometry']['type']
                s = shape(feat['geometry'])
                if feat['geometry']['type'] == 'Polygon':
                    s = MultiPolygon([s])
                    print json.dumps(feat['geometry'])
                klass = locate('madmex.models.%s' % model)
                
                f = klass(name=feat['properties'][column], the_geom=GEOSGeometry(s.wkt))
                f.save()
                