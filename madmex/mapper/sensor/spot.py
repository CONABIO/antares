'''
Created on 29/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
from madmex.mapper.base import BaseSensor
from datetime import datetime
import madmex.mapper.parser.spot5 as spot5

PRODUCT = ['Dimap_Document', 'Data_Processing', 'PROCESSING_LEVEL']
SENSOR = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'MISSION']
PLATFORM = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'MISSION_INDEX']
CREATION_DATE = ['Dimap_Document', 'Production', 'DATASET_PRODUCTION_DATE']
ACQUISITION_DATE = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'IMAGING_DATE']
ACQUISITION_TIME = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'IMAGING_TIME']
ANGLE = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'VIEWING_ANGLE']
TILE_ID = ['Dimap_Document', 'Dataset_Sources', 'Scene_Source', 'GRID_REFERENCE']
CLOUDS = ['clouds']
QUICKLOOK = ['quicklook']

class Sensor(BaseSensor):
    '''
    This class represents a Spot Sensor object. It owns a Spot parser in charge
    of reading, and holding the important metadata for this sensor. The constants
    are the paths to such metadata, from outside this file, this fields can be
    invoked with the get_attribute function.
    '''
    def __init__(self, metadata_path):
        self.sensor_name = 'spot'
        self.metadata_ext = 'dim'
        self.parser = spot5.Parser(metadata_path, [PRODUCT, SENSOR, PLATFORM, CREATION_DATE, ACQUISITION_DATE, ACQUISITION_TIME, ANGLE, TILE_ID])
        self.parser.parse()
        self.parser.apply_format(ANGLE, lambda x: float(x))
        self.parser.set_attribute(CLOUDS, 999)
        self.parser.set_attribute(QUICKLOOK, 'PREVIEW.JPG')
