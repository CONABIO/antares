'''
Created on Sep 28, 2017

@author: agutierrez
'''
from __future__ import unicode_literals

import csv
import logging

from madmex.core.controller.base import BaseCommand
from madmex.persistence.database.connection import Catalog
from madmex.persistence.driver import persist_catalog


LOGGER = logging.getLogger(__name__)
SCENES = ["18,45","18,46","18,47","19,45","19,46","19,47","19,48","20,45","20,46","20,47","20,48","20,49","21,45","21,46","21,47","21,48","21,49","21,50","22,45","22,47","22,48","22,49","23,47","23,48","23,49","24,46","24,47","24,48","24,49","25,45","25,46","25,47","25,48","25,49","26,42","26,43","26,44","26,45","26,46","26,47","26,48","26,49","27,41","27,42","27,43","27,44","27,45","27,46","27,47","27,48","28,40","28,41","28,42","28,43","28,44","28,45","28,46","28,47","28,48","29,39","29,40","29,41","29,42","29,43","29,44","29,45","29,46","29,47","30,39","30,40","30,41","30,42","30,43","30,44","30,45","30,46","30,47","31,39","31,40","31,41","31,42","31,43","31,44","31,45","31,46","32,38","32,39","32,40","32,41","32,42","32,43","32,44","33,38","33,39","33,40","33,41","33,42","33,43","33,44","34,38","34,39","34,40","34,41","34,42","34,43","34,44","34,47","35,38","35,39","35,40","35,41","35,42","35,43","36,38","36,39","36,40","36,41","36,42","36,43","36,47","37,38","37,39","37,40","37,41","38,37","38,38","38,39","38,40","38,41","39,37","39,38","39,39","40,37","40,38","40,40"]
TM = {'browse_url':1,
      'scene_id':2,
      'landsat_product_id' : 3,
      'sensor' : 4,
      'acquisition_date' : 5,
      'path' : 7,
      'row' : 8,
      'cloud_full' : 20,
      'day_night' : 21,
      'image_quality' : 61,
      'ground_control_points_model' : 39}

ETM = {'browse_url':1,
       'scene_id':2,
      'landsat_product_id' : 3,
      'sensor' : 4,
      'acquisition_date' : 5,
      'path' : 7,
      'row' : 8,
      'cloud_full' : 20,
      'day_night' : 25,
      'image_quality' : 32,
      'ground_control_points_model' : 62}

LS8 = {'browse_url':1,
       'scene_id':2,
      'landsat_product_id' : 3,
      'sensor' : 4,
      'acquisition_date' : 5,
      'path' : 7,
      'row' : 8,
      'cloud_full' : 20,
      'day_night' : 21,
      'image_quality' : 61,
      'ground_control_points_model' : 39}

INDEXES = {'TM':TM,'ETM':ETM,'LS8':LS8}

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--file', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--satellite', nargs='*', help='This argument represents'
            ' the first image to be processed.')

    def handle(self, **options):
        '''
        This comand is used to query the catalog database.
        '''
        collection = options['file'][0]
        satellite = options['satellite'][0]
        index = INDEXES[satellite]        
        
        with open(collection, 'rb') as f:
            reader = csv.reader(f)
            mexico = 0
            rest = 0
            for row in reader:
                if '%s,%s' % (row[7], row[8]) in SCENES:
                    #print row
                    scene = Catalog(scene_id = row[index['scene_id']],
                                    landsat_product_id = row[index['landsat_product_id']],
                                    sensor = row[index['sensor']],
                                    acquisition_date = row[index['acquisition_date']],
                                    path = int(row[index['path']]),
                                    row = int(row[index['row']]),
                                    cloud_full = float(row[index['cloud_full']]),
                                    day_night = row[index['day_night']],
                                    image_quality = int(row[index['image_quality']]),
                                    ground_control_points_model = row[index['ground_control_points_model']],
                                    browse_url = row[index['browse_url']])
                    persist_catalog(scene)
                    mexico += 1
                else:
                    rest += 1
        print mexico, rest