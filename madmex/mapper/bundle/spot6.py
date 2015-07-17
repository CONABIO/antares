'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from madmex.mapper.base import BaseBundle
from madmex.persistence.database.connection import RawProduct
import madmex.mapper.sensor.spot5 as spot5
import madmex.mapper.data.raster as raster
from datetime import datetime
from madmex.configuration import SETTINGS
from madmex.util import get_path_from_list

IMAGE = r'IMG.*\.JP2$'
METADATA = r'DIM.*\.XML$'
PREVIEW = r'PREVIEW.*\.JPG$'
ICON = r'ICON.*\.JPG$'

class Bundle(BaseBundle):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_dictionary = {
                        IMAGE:None,
                        METADATA:None,
                        PREVIEW:None,
                        ICON:None
                           }
        self._look_for_files()
        self.sensor = None
        self.raster = None
        self.output_directory = None
        
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'Spot6'
    def get_database_object(self):
        '''
        Creates the database object that will be ingested for this bundle.
        '''
        return RawProduct(
                uuid = self.get_sensor().uuid,
                acquisition_date=self.get_sensor().get_attribute(spot5.ACQUISITION_DATE),
                ingest_date=datetime.now(),
                path=self.get_output_directory(),
                legend=None,
                geometry=self.get_raster().get_attribute('footprint'),
                information=None,
                product_type=None,
                type='raw'
                )
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = spot5.Sensor(self.file_dictionary[METADATA])
        return self.sensor
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[IMAGE])
        return self.raster
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(spot5.SENSOR)
            grid_id = unicode(self.get_sensor().get_attribute(spot5.GRID_REFERENCE))
            year = self.get_sensor().get_attribute(spot5.ACQUISITION_DATE).strftime('%Y')
            date = self.get_sensor().get_attribute(spot5.ACQUISITION_DATE).strftime('%Y-%m-%d')
            product_name = self.get_sensor().get_attribute(spot5.PROCESSING_LEVEL)
            self.output_directory = get_path_from_list([
                destination,
                sensor_name,
                grid_id,
                year,
                date,
                product_name
                ])
        return self.output_directory

        
        
if __name__ == '__main__':
    folder = '/Volumes/Imagenes_originales/SPOT6/E6554293150227_1751231K3A0U12N17L1003001/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A'
    
    bundle = Bundle(folder)
    print bundle.get_files()
    print bundle.can_identify()