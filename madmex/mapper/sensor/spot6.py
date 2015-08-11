'''
Created on 29/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.spot6 as spot6
from datetime import datetime

PROCESSING_LEVEL = [
    'Dimap_Document',
    'Processing Information',
    'Product_Settings',
    'PROCESSING_LEVEL'
    ]
SENSOR = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Identification',
    'Strip_Source',
    'MISSION'
    ]
PLATFORM = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Identification',
    'Strip_Source',
    'MISSION_INDEX'
    ]
CREATION_DATE = [
    'Dimap_Document',
    'Product_Information',
    'Delivery_Identification',
    'PRODUCTION_DATE'
    ]
ACQUISITION_DATE = [
    'Dimap_Document',
    'Dataset_Sources',
    'Source_Identification',
    'Strip_Source',
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
    'Geometric_Data',
    'Use_Area',
    'Located_Geometric_Values',
    'Acquisition_Angles',
    'VIEWING_ANGLE'
    ]
SUN_AZIMUTH = [
    'Dimap_Document',
    'Geometric_Data',
    'Use_Area',
    'Located_Geometric_Values',
    'Solar_Incidences',
    'SUN_AZIMUTH'
    ]
SUN_ELEVATION = [
    'Dimap_Document',
    'Geometric_Data',
    'Use_Area',
    'Located_Geometric_Values',
    'Solar_Incidences',
    'SUN_ELEVATION'
    ]
PHYSICAL_GAIN = [
    'Dimap_Document',
    'Radiometric_Data',
    'Radiometric_Calibration',
    'Instrument_Calibration',
    'Band_Measurement_List',
    'Band_Radiance',
    'GAIN'
    ]
PHYSICAL_BIAS = [
    'Dimap_Document',
    'Radiometric_Data',
    'Radiometric_Calibration',
    'Instrument_Calibration',
    'Band_Measurement_List',
    'Band_Radiance',
    'BIAS'
    ]
RED_CHANNEL = [
    'Dimap_Document',
    'Raster_Data',
    'Raster_Display',
    'Band_Display_Order',
    'RED_CHANNEL'
    ]
GREEN_CHANNEL = [
    'Dimap_Document',
    'Raster_Data',
    'Raster_Display',
    'Band_Display_Order',
    'GREEN_CHANNEL'
    ]
BLUE_CHANNEL = [
    'Dimap_Document',
    'Raster_Data',
    'Raster_Display',
    'Band_Display_Order',
    'BLUE_CHANNEL'
    ]
ALPHA_CHANNEL = [
    'Dimap_Document',
    'Raster_Data',
    'Raster_Display',
    'Band_Display_Order',
    'ALPHA_CHANNEL'
    ]
BAND_DISPLAY_ORDER = [
    'Dimap_Document',
    'Raster_Data',
    'Raster_Display',
    'Band_Display_Order'
    ]
BAND_INDEX = [
    'Dimap_Document',
    'Radiometric_Data',
    'Dynamic_Adjustment',
    'Band_Adjustment_List',
    'Band_Adjustment',
    'BAND_ID'
    ]
BAND_SOLAR_IRRADIANCE_VALUE = [
    'Dimap_Document',
    'Radiometric_Data',
    'Radiometric_Calibration',
    'Instrument_Calibration',
    'Band_Measurement_List',
    'Band_Solar_Irradiance',
    'VALUE'
    ]
class Sensor(BaseSensor):
    '''
    This class represents a Spot Sensor object. It owns a Spot parser in charge
    of reading, and holding the important metadata for this sensor. The constants
    are the paths to such metadata, from outside this file, this fields can be
    invoked with the get_attribute function.
    '''
    def __init__(self, metadata_path):
        super(Sensor, self).__init__()
        self.parser = spot6.Parser(metadata_path, [
            PROCESSING_LEVEL,
            SENSOR,
            PLATFORM,
            CREATION_DATE,
            ACQUISITION_DATE,
            ACQUISITION_TIME,
            ANGLE,
            SUN_AZIMUTH,
            SUN_ELEVATION,
            PHYSICAL_BIAS,
            PHYSICAL_GAIN,
            BAND_DISPLAY_ORDER,
            BAND_INDEX
            ])
        self.parser.parse()
        self.parser.apply_format(
            ACQUISITION_DATE,
            lambda x: datetime.strptime(x, '%Y-%m-%d')
            )
        self.parser.apply_format(ANGLE, lambda x: [float(y) for y in x])
        self.parser.apply_format(SUN_ELEVATION, lambda x: [float(y) for y in x])
        self.parser.apply_format(BAND_SOLAR_IRRADIANCE_VALUE, lambda x: [float(y) for y in x])
