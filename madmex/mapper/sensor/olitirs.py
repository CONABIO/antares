'''
Created on 03/08/2016

@author: erickpalacios
'''

from __future__ import unicode_literals

from datetime import datetime
import json

from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.landsat as landsat


SENSOR_NAME = [
          'L1_METADATA_FILE',
           'PRODUCT_METADATA',
            'SPACECRAFT_ID'
            ]
SENSOR = [
          'L1_METADATA_FILE',
           'PRODUCT_METADATA',
            'SENSOR_ID'
            ]
METADATA_EXT = 'txt'
SCENE_ID = [
            'L1_METADATA_FILE',
             'METADATA_FILE_INFO',
              'LANDSAT_SCENE_ID'
              ]


SUN_ELEVATION = [
                 'L1_METADATA_FILE',
                  'IMAGE_ATTRIBUTES',
                   'SUN_ELEVATION'
                   ]
SUN_AZIMUTH = [
               'L1_METADATA_FILE', 
               'IMAGE_ATTRIBUTES',
                'SUN_AZIMUTH'
                ]

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
        super(Sensor, self).__init__()
        self.parser = landsat.Parser(metadata_path)
        self.parser.parse()
        print json.dumps(self.parser.metadata, indent=4, sort_keys=True)
        self.parser.set_attribute(SENSOR_NAME, 'oli_tirs')
        self.parser.apply_format(SENSOR,  lambda x:  x.lower())
        self.parser.apply_format(DATA_TYPE, lambda x: x.lower())
        self.parser.apply_format(
            ACQUISITION_DATE,
            lambda x: datetime.strptime(x, "%Y-%m-%d")
            )
        self.parser.apply_format(ROW, lambda x: '0' + str(x) if len(str(x)) is 2 else str(x))
        self.parser.apply_format(PATH, lambda x: str(x))        
        