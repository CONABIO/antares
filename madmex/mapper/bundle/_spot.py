'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
from madmex.mapper.data import raster
from madmex.util import get_path_from_list


class SpotBaseBundle(BaseBundle):

    def __init__(self, path):
        self.path = path
        self.sensor = None
        self.raster = None
        self.output_directory = None
    def get_aquisition_date(self):
        return self.get_sensor().get_attribute(self.get_sensor_module().ACQUISITION_DATE)
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = self.get_sensor_module().Sensor(self.file_dictionary[self.get_metadata_file()])
        return self.sensor
    def get_spot_dictionary(self):
        '''
        This method prepares the dictonary that holds the regular expressions
        to identify the files that this bundle represent.
        '''
        raise NotImplementedError('Subclasses of SpotBaseBundle must provide a get_spot_dictionary() method.')
    def get_image_file(self):
        raise NotImplementedError('Subclasses of SpotBaseBundle must provide a get_image_file() method.')
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(self.get_sensor_module().SENSOR) + self.get_sensor().get_attribute(self.get_sensor_module().PLATFORM)
            grid_id = '0'  # grid_reference in spot6?
            year = self.get_sensor().get_attribute(self.get_sensor_module().ACQUISITION_DATE).strftime('%Y')
            date = self.get_sensor().get_attribute(self.get_sensor_module().ACQUISITION_DATE).strftime('%Y-%m-%d')
            product_name = self.get_sensor().get_attribute(self.get_sensor_module().PROCESSING_LEVEL)
            self.output_directory = get_path_from_list([
                destination,
                sensor_name,
                grid_id,
                year,
                date,
                product_name
                ])
        return self.output_directory
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[self.get_image_file()], self.get_format_file())
        return self.raster
