'''
Created on Jul 22, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.mapper.bundle._landsat import LandsatBaseBundle
from madmex.mapper.sensor import tm


FORMAT = 'GTiff'
_MISSION = '5'
_NAME = 'Landsat 5'
_LETTER = 'T'
_PROCESSING_LEVEL = 'L1T'

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
if __name__ == '__main__':

    bundle = Bundle('/LUSTRE/MADMEX/eodata/tm/10052/2000/2000-08-20/l1g')
    print bundle.get_files()
    print bundle.can_identify()
    #from madmex.mapper.data import raster
    #print bundle.get_raster().get_attribute(raster.FOOTPRINT)
    
    
