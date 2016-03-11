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
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return _NAME
