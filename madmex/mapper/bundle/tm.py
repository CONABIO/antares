'''
Created on Jul 22, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.mapper.bundle._tm import LandsatBaseBundle, _BASE
from madmex.mapper.data import raster
from madmex.mapper.sensor import tm
from madmex.persistence import driver
from madmex.persistence.database.connection import Information
from madmex.util import get_basename_of_file, create_file_name


FORMAT = 'GTiff'
_MISSION = '5'
_NAME = 'Landsat 5'
_LETTER = 'T'
_PROCESSING_LEVEL = 'L1T'

class Bundle(LandsatBaseBundle):
    '''
    A class to create a memory representation of a Landsat 5 image including its
    metadata files. It is also responsible of creating a database object to be
    persisted. This is basically a fork from the landsat5 bundle with the new layout
    of collection 1.
    '''
    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.FORMAT = FORMAT
        self.sensor = None
        self.raster = None
    def get_format_file(self):
        return FORMAT
    def get_sensor_module(self):
        return tm
    def get_mission(self):
        '''
        Returns the mission for this particular implementation of the landsat
        satellite.
        '''
        return _MISSION
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return _NAME
    def get_letter(self):
        '''
        Files after 2012 have a letter to distinguish the different sensors
        In the case of landsat5  letter T
        '''
        return _LETTER
    def get_processing_level(self):
        '''
        In the case of the satellite Landsat we have different levels of processing,
        the case of this bundle is raw data
        '''
        return _PROCESSING_LEVEL
    def get_datatype(self):
        return self.get_processing_level()
    def get_aquisition_date(self):
        '''
        Returns the data in which this image was aquired.
        '''
        return self.get_sensor().get_attribute(tm.ACQUISITION_DATE)
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = tm.Sensor(self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'MTL.txt')])
        return self.sensor
    
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'B1.TIF')], self.FORMAT)
        return self.raster
    
    def get_satellite_object(self):
        '''
        Returns the database object that represents this sensor.
        '''
        return driver.get_satellite_object(self.get_name())
    
    def get_product_type_object(self):
        return driver.get_product_type_object(self.get_sensor().get_attribute(tm.DATA_TYPE).upper())
    def get_information_object(self):
        
    
        
        
        row = self.get_sensor().get_attribute(tm.ROW)
        path = self.get_sensor().get_attribute(tm.PATH)
        basename_metadata = get_basename_of_file( self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'MTL.txt')])
        information = Information(
                    metadata_path = create_file_name(self.get_output_directory(),basename_metadata),
                    grid_id = unicode(path + row),
                    projection = self.get_raster().get_attribute(raster.PROJECTION),
                    cloud_percentage = self.get_sensor().get_attribute(tm.CLOUD_COVER),
                    geometry = self.get_raster().get_attribute(raster.FOOTPRINT),
                    elevation_angle = 0.0,
                    resolution = self.get_raster().get_attribute(raster.GEOTRANSFORM)[1]
                    )
        return information
if __name__ == '__main__':

    bundle = Bundle('/LUSTRE/MADMEX/eodata/tm/10052/2000/2000-08-20/l1g')
    print bundle.get_files()
    print bundle.can_identify()
    #from madmex.mapper.data import raster
    #print bundle.get_raster().get_attribute(raster.FOOTPRINT)
    
    
