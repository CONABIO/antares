'''
Created on Jun 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from datetime import datetime
import re
import uuid

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
import madmex.mapper.data.raster as raster
import madmex.mapper.sensor.rapideye as rapideye
from madmex.persistence.database.connection import RawProduct
from madmex.util import create_file_name, get_files_from_folder, \
    get_path_from_list


FORMAT = 'GTiff'

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
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}\.tif$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_browse\.tif$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_license\.txt$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_metadata\.xml$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_readme\.txt$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_udm\.tif$':None
                           }
        self._look_for_files()
        self.sensor = None
        self.raster = None
        self.output_directory = None
    def _look_for_files(self):
        '''
        This method will be called by the constructor to look for files in the
        given directory. In order for a bundle to be valid, a file for each
        regular expression must be found.
        '''
        for key in self.file_dictionary.iterkeys():
            for name in get_files_from_folder(self.path):
                if re.match(key, name):
                    self.file_dictionary[key] = create_file_name(self.path, name)
    def is_consistent(self):
        '''
        Check if this bundle is consistent.
        '''
        pass
    def can_identify(self):
        '''
        If all of the regular expressions got a matching file, then the directory
        can be identified as a RapidEye bundle.
        '''
        return len(self.get_files()) == len(self.file_dictionary)
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'RapidEye'
    def get_files(self):
        '''
        Retrieves a list with the files found in the directory that this bundle
        represents.
        '''
        return [file_path for file_path in self.file_dictionary.itervalues() if file_path]
    def get_database_object(self):
        '''
        Creates the database object that will be ingested for this bundle.
        '''
        return RawProduct(
                uuid=str(uuid.uuid4()),
                acquisition_date=self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE),
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
            self.sensor = rapideye.Sensor(self.file_dictionary[
                r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_metadata\.xml$'
                ])
        return self.sensor
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[
                r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}\.tif$'
                ] )
        return self.raster
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(rapideye.SENSOR_NAME)
            grid_id = unicode(self.get_sensor().get_attribute(rapideye.TILE_ID))
            year = self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE).strftime('%Y')
            date = self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE).strftime('%Y-%m-%d')
            product_name = self.get_sensor().get_attribute(rapideye.PRODUCT_NAME)
            self.output_directory = get_path_from_list([
                destination,
                sensor_name,
                grid_id,
                year,
                date,
                product_name
                ])
        return self.output_directory
