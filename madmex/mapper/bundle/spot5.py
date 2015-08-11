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


class Bundle(BaseBundle):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.IMAGE = r'.*.img$'
        self.METADATA = r'.*.dim$'
        self.FORMAT = 'HFA'

        self.file_dictionary = {
                        self.IMAGE:None,
                        self.METADATA:None,
                           }
        self._look_for_files()
        self.sensor = None
        self.raster = None
        self.output_directory = None
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'Spot5'
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
                geometry=self.get_raster().get_attribute(raster.FOOTPRINT),
                information=None,
                product_type=None,
                type='raw'
                )
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = spot5.Sensor(self.file_dictionary[self.METADATA])
        return self.sensor
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[self.IMAGE], self.FORMAT)
        return self.raster
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(spot5.SENSOR)+self.get_sensor().get_attribute(spot5.PLATFORM)
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
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea9/folder_test/556_297_041114_dim_img_spot'
    bundle = Bundle(folder)
    print bundle.can_identify()
    print bundle.get_raster().metadata
    print bundle.get_raster().get_attribute((raster.FOOTPRINT))
    print bundle.get_raster().get_attribute((raster.GEOTRANSFORM))
    print bundle.get_sensor()
