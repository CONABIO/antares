#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
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
from madmex.util import  INDEXES, SCENES


LOGGER = logging.getLogger(__name__)


def populate_catalog(collection, satellite):
    '''
    This method reads and parses the catalogs from usgs and populates the database
    to fit our needs. Using this approach we don't have to download the scenes in advance,
    instead we download only what we need.
    '''
    index = INDEXES[satellite]        
        
    with open(collection, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if '%s,%s' % (row[7], row[8]) in SCENES:
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
        This command is used to query the catalog database.
        '''
        #images = ["/Users/agutierrez/Downloads/ChisAOI_Pedro/2012-02-27T174651_RE2_3A-NAC_11045275_149076_recorte_bien.tif_50_07_03.tif" , "2012-04-07T174236_RE4_3A-NAC_11043988_149076_recorte_bien.tif_50_07_03.tif",  "2012-12-19T175610_RE2_3A-NAC_12448165_160401_recorte_bien.tif_50_07_03.tif",  "2012-12-23T174028_RE2_3A-NAC_12448111_160401_recorte_bien.tif_50_07_03.tif"]
        
        
        #print getattr(SETTINGS, 'MY_SECRET')
        
        #name = images[3]
        #basename = get_base_name(name)
        
        #vectorize_raster("/Users/agutierrez/Downloads/ChisAOI_Pedro/%s" % name , 1, str("/Users/agutierrez/Downloads/ChisAOI_Pedro/%s.shp" % basename) , str('objects'), str('id'))
        
        collection = options['file'][0]
        satellite = options['satellite'][0]
        
        populate_catalog(collection, satellite)
