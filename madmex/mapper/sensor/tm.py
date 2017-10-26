'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import json

from madmex.mapper.base import BaseSensor
from madmex.mapper.parser import landsat


PATH = [
        'L1_METADATA_FILE',
         'PRODUCT_METADATA',
          'WRS_PATH'
          ]
ROW = [
        'L1_METADATA_FILE',
         'PRODUCT_METADATA',
          'WRS_ROW'
          ]
CLOUD_COVER = [
        'L1_METADATA_FILE',
         'IMAGE_ATTRIBUTES',
          'CLOUD_COVER'
          ]
ACQUISITION_DATE = [
        'L1_METADATA_FILE',
         'PRODUCT_METADATA',
        'DATE_ACQUIRED'
    ]

DATA_TYPE = [
             'L1_METADATA_FILE',
              'PRODUCT_METADATA',
               'DATA_TYPE'
               ]

class Sensor(BaseSensor):
    '''
    classdocs
    '''
    def __init__(self, metadata_path):
        '''
        Constructor
        '''
        self.parser = landsat.Parser(metadata_path)
        self.parser.parse()
        
