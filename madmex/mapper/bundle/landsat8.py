'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.mapper.bundle._landsat import LandsatBaseBundle
from madmex.mapper.sensor import etmplus


FORMAT = 'GTiff'
_MISSION = '8'
_NAME = 'Landsat 8'
_LETTER = 'C'

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
        return etmplus
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
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return _NAME

if __name__ == '__main__':
    path = '/LUSTRE/MADMEX/eodata/oli_tirs/21048/2013/2013-04-15/l1t/'
    bundle = Bundle(path)
    print bundle.get_files()
    print bundle.can_identify()
