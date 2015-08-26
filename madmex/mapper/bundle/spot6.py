'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime

from madmex.configuration import SETTINGS
from madmex.mapper.bundle._spot import SpotBaseBundle
import madmex.mapper.data.raster as raster
import madmex.mapper.sensor.spot6 as spot6
from madmex.util import get_path_from_list


_IMAGE = r'IMG.*\.JP2$'
_METADATA = r'DIM.*\.XML$'
_PREVIEW = r'PREVIEW.*\.JPG$'
_ICON = r'ICON.*\.JPG$'
_FORMAT = 'JP2OpenJPEG'


class Bundle(SpotBaseBundle):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path

        self.file_dictionary = {
                        _IMAGE:None,
                        _METADATA:None,
                        _PREVIEW:None,
                        _ICON:None
                           }
        self._look_for_files()
        self.sensor = None
        self.raster = None
        self.output_directory = None
        
    def get_spot_dictionary(self):
        '''
        Returns the dictionary of regular expressions and file names found in
        the given path.
        '''
        return self.file_dictionary

    def get_metadata_file(self):
        return _METADATA
    def get_image_file(self):
        return _IMAGE
    def get_format_file(self):
        return _FORMAT
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'Spot6'
    def get_sensor_module(self):
        return spot6

if __name__ == '__main__':
    folder = '/Volumes/Imagenes_originales/SPOT6/E6554293150227_1751231K3A0U12N17L1003001/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A'
    bundle = Bundle(folder)
    print bundle.get_files()
    print bundle.can_identify()
    print bundle.get_output_directory()
    print bundle.get_sensor_module().SENSOR
    
    print bundle.get_output_directory()