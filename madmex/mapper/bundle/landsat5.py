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
if __name__ == '__main__':

    bundle = Bundle('/LUSTRE/MADMEX/eodata/tm/10052/2000/2000-08-20/l1g')
    print bundle.get_files()
    print bundle.can_identify()
    
    
    