'''
Created on 29/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.spot5 as spot5

PROCESSING_LEVEL = [
    'Dimap_Document',
    'Data_Processing',
    'PROCESSING_LEVEL'
    ]
SENSOR = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'MISSION'
    ]
PLATFORM = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'MISSION_INDEX'
    ]
CREATION_DATE = [
    'Dimap_Document',
    'Production',
    'DATASET_PRODUCTION_DATE'
    ]
ACQUISITION_DATE = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'IMAGING_DATE'
    ]
ACQUISITION_TIME = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'IMAGING_TIME'
    ]
ANGLE = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'VIEWING_ANGLE'
    ]
SUN_AZIMUTH = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'SUN_AZIMUTH'
    ]
SUN_ELEVATION = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Information',
    'Scene_Source',
    'SUN_ELEVATION'
    ]
SOLAR_IRRADIANCE = ['SOLAR_IRRADIANCE']
class Sensor(BaseSensor):
    '''
    This class represents a Spot Sensor object. It owns a Spot parser in charge
    of reading, and holding the important metadata for this sensor. The constants
    are the paths to such metadata, from outside this file, this fields can be
    invoked with the get_attribute function.
    '''
    def __init__(self, metadata_path):
        super(Sensor, self).__init__()
        self.parser = spot5.Parser(metadata_path, [
            PROCESSING_LEVEL,
            SENSOR,
            PLATFORM,
            CREATION_DATE,
            ACQUISITION_DATE,
            ACQUISITION_TIME,
            ANGLE,
            SUN_AZIMUTH,
            SUN_ELEVATION,
            ])
        self.parser.parse()
        self.parser.apply_format(ANGLE, lambda x: float(x))
        self.parser.set_attribute(SOLAR_IRRADIANCE, [1843,1568,1052,233])
