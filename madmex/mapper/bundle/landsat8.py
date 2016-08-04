'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.mapper.bundle._landsat import LandsatBaseBundle, _BASE
from madmex.mapper.sensor import olitirs
from madmex.persistence.database.connection import Information
from madmex.mapper.data import raster


FORMAT = 'GTiff'
_MISSION = '8'
_NAME = 'Landsat 8'
_LETTER = 'C'
#_METADATA = 

class Bundle(LandsatBaseBundle):
    '''
    A class to create a memory representation of a Landsat 5 image including its
    metadata files. It is also responsible of creating a database object to be
    persisted.
    '''
    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.path = path
        self.FORMAT = FORMAT
        self.sensor = None
        self.raster = None
    def get_format_file(self):
        return FORMAT
    def get_sensor_module(self):
        return olitirs

    def get_mission(self):
        '''
        Returns the mission for this particular implementation of the landsat
        satellite.
        '''
        return _MISSION
    def get_letter(self):
        '''
        Files after 2012 have a letter to distinguish the different sensors
        In the case of landsat8, the LEDAPS process only can be applied to files with the letter C,
        that is, only for the oli tirs sensor
        '''
        return _LETTER
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'B1.TIF')], self.FORMAT)
        return self.raster
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = olitirs.Sensor(self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'MTL.txt')])
        return self.sensor
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return _NAME
    def get_information_object(self):
        information = Information(
                    grid_id = self.get_sensor().get_attribute(olitirs.PATH),
                    projection = self.get_raster().get_attribute(raster.PROJECTION),
                    cloud_percentage = self.get_sensor().get_attribute(olitirs.CLOUD_COVER),
                    geometry = self.get_raster().get_attribute(raster.FOOTPRINT),
                    )
        return information

if __name__ == '__main__':
    path = '/LUSTRE/MADMEX/eodata/oli_tirs/21048/2013/2013-04-15/l1t/'
    bundle = Bundle(path)
    print bundle.get_files()
    print bundle.can_identify()
    print "sensor"
    print bundle.get_sensor().get_attribute(olitirs.SENSOR)
    print "sensor_name"
    print bundle.get_sensor().get_attribute(olitirs.SENSOR_NAME)
    print "scene"
    print bundle.get_sensor().get_attribute(olitirs.SCENE_ID)
    print "cloud"
    print bundle.get_sensor().get_attribute(olitirs.CLOUD_COVER)
    print "sun"
    print bundle.get_sensor().get_attribute(olitirs.SUN_ELEVATION)
    print "data type"
    print bundle.get_sensor().get_attribute(olitirs.DATA_TYPE)
    print "path + row"
    print str(bundle.get_sensor().get_attribute(olitirs.PATH)) + '0' + str(bundle.get_sensor().get_attribute(olitirs.ROW))
    print bundle.get_raster().get_attribute(raster.FOOTPRINT)

    #print bundle.get_sensor().parser.metadata
