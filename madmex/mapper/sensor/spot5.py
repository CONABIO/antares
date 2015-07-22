'''
Created on 29/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseSensor
import madmex.mapper.parser.spot5 as spot5
from datetime import datetime

PROCESSING_LEVEL = ['Dimap_Document', 'Data_Processing', 'PROCESSING_LEVEL']
SENSOR = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'MISSION']
PLATFORM = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'MISSION_INDEX']
CREATION_DATE = ['Dimap_Document', 'Production', 'DATASET_PRODUCTION_DATE']
ACQUISITION_DATE = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'IMAGING_DATE']
ACQUISITION_TIME = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'IMAGING_TIME']
ANGLE = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'VIEWING_ANGLE']
CLOUDS = ['clouds']
QUICKLOOK = ['quicklook']
BAND_INDEX = ['Dimap_Document', 'Spectral_Band_Info', 'BAND_INDEX']
BAND_DESCRIPTION = ['Dimap_Document', 'Spectral_Band_Info', 'BAND_DESCRIPTION']
PHYSICAL_GAIN = ['Dimap_Document', 'Spectral_Band_Info', 'PHYSICAL_GAIN']
PHYSICAL_BIAS = ['Dimap_Document', 'Spectral_Band_Info', 'PHYSICAL_BIAS']
TIE_POINT_CRS_X = ['Dimap_Document', 'Geoposition', 'Geoposition_Points', 'Tie_Point', 'TIE_POINT_CRS_X']
TIE_POINT_CRS_Y = ['Dimap_Document', 'Geoposition', 'Geoposition_Points', 'Tie_Point', 'TIE_POINT_CRS_Y']
TIE_POINT_DATA_X = ['Dimap_Document', 'Geoposition', 'Geoposition_Points', 'Tie_Point', 'TIE_POINT_DATA_X']
TIE_POINT_DATA_Y = ['Dimap_Document', 'Geoposition', 'Geoposition_Points', 'Tie_Point', 'TIE_POINT_DATA_Y']
SCENE_ORIENTATION = ['Dimap_Document', 'Dataset_Frame', 'SCENE_ORIENTATION']
HORIZONTAL_CS_CODE = ['Dimap_Document', 'Coordinate_Reference_System', 'Horizontal_CS', 'HORIZONTAL_CS_CODE']
SUN_AZIMUTH = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'SUN_AZIMUTH']
SUN_ELEVATION = ['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'SUN_ELEVATION']
GRID_REFERENCE =['Dimap_Document', 'Dataset_Sources', 'Source_Information', 'Scene_Source', 'GRID_REFERENCE']
SOLAR_IRRADIANCE = ['SOLAR_IRRADIANCE']  # soudani et al 2006
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
            BAND_INDEX,
            BAND_DESCRIPTION,
            PHYSICAL_GAIN,
            PHYSICAL_BIAS,
            TIE_POINT_CRS_X,
            TIE_POINT_CRS_Y,
            TIE_POINT_DATA_X,
            TIE_POINT_DATA_Y,
            SCENE_ORIENTATION,
            HORIZONTAL_CS_CODE,
            SUN_AZIMUTH,
            SUN_ELEVATION,
            GRID_REFERENCE
            ])
        self.parser.parse()
        self.parser.apply_format(ANGLE, lambda x: float(x))
        self.parser.apply_format(
            ACQUISITION_DATE,
            lambda x: datetime.strptime(x, "%Y-%m-%d")
            )
        self.parser.set_attribute(CLOUDS, 999)
        self.parser.set_attribute(QUICKLOOK, 'PREVIEW.JPG')
        self.parser.set_attribute(SOLAR_IRRADIANCE, [1843,1568,1052,233])
        