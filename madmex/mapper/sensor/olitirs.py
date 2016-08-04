'''
Created on 03/08/2016

@author: erickpalacios
'''

from __future__ import unicode_literals
from datetime import datetime
from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.landsat as landsat

SENSOR_NAME = ['sensor_name']
SENSOR = [
          'searchResponse',
           'metaData',
            'sensor'
            ]
METADATA_EXT = 'txt'
SCENE_ID = [
            'searchResponse',
             'metaData',
              'sceneID'
              ]
ACQUISITION_DATE = [
                    'searchResponse',
                     'metaData',
                      'acquisitionDate'
                      ]
PATH = [
        'searchResponse',
         'metaData',
          'path'
          ]
ROW = [
       'searchResponse',
        'metaData',
         'row'
         ]
CLOUD_COVER = [
               'searchResponse',
                'metaData',
                 'cloudCover'
                 ]
SUN_ELEVATION = [
                 'searchResponse',
                  'metaData',
                   'sunElevation'
                   ]
SUN_AZIMUTH = [
               'searchResponse', 
               'metaData',
                'sunAzimuth'
                ]
DATA_TYPE = [
             'searchResponse',
              'metaData',
               'DATA_TYPE_L1'
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
        self.parser.set_attribute(SENSOR_NAME, 'oli_tirs')
        self.parser.apply_format(SENSOR,  lambda x:  x.lower())
        self.parser.apply_format(DATA_TYPE, lambda x: x.lower())
        self.parser.apply_format(
            ACQUISITION_DATE,
            lambda x: datetime.strptime(x, "%Y-%m-%d")
            )
        self.parser.apply_format(ROW, lambda x: '0' + str(x) if len(str(x)) is 2 else str(x))
        self.parser.apply_format(PATH, lambda x: str(x))        
    