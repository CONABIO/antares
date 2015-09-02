'''
Created on Jul 14, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from datetime import datetime

from madmex.configuration import SETTINGS
from madmex.mapper.bundle._spot import SpotBaseBundle
import madmex.mapper.sensor.spot5 as spot5
from madmex.util import get_path_from_list


_IMAGE = r'[0-9]{3}_[0-9]{3}_[0-9]{6}_SP5.(IMG|img)$' #TODO: SP5 is going to be in the standard? if not, change this reg exp
_METADATA = r'[0-9]{3}_[0-9]{3}_[0-9]{6}_SP5.(DIM|dim)$'#TODO: SP5 is going to be in the standard? if not, change this reg exp
FORMAT = 'HFA'
_NAME = 'Spot5'

class Bundle(SpotBaseBundle):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.file_dictionary = {
                        _IMAGE:None,
                        _METADATA:None,
                           }
        self._look_for_files()
    def get_spot_dictionary(self):
        '''
        Returns the dictionary of regular expressions and file names found in
        the given path.
        '''
        return self.file_dictionary
    def get_metadata_file(self):
        '''
        Returns the regular expression to identify the metadata file for Spot 5.
        '''
        return _METADATA
    def get_image_file(self):
        '''
        Returns the regular expression to identify the image file for Spot 5.
        '''
        return _IMAGE
    def get_format_file(self):
        '''
        Returns the format in which Spot 5 images are configured.
        '''
        return FORMAT
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return _NAME
    def get_sensor_module(self):
        return spot5

if __name__ == '__main__':
    folder = '/Volumes/Imagenes_originales/Algoritmo_cambios/612_311_040310'
    bundle = Bundle(folder)
    print 'files ', bundle.file_dictionary 
    import madmex.mapper.data.raster as raster
    print bundle.can_identify()
    print bundle.get_raster().metadata
    print bundle.get_raster().get_attribute((raster.FOOTPRINT))
    print bundle.get_raster().get_attribute((raster.GEOTRANSFORM))
    print bundle.get_sensor()
    print bundle.get_sensor().get_attribute(bundle.get_sensor_module().SENSOR)
    
    print bundle.get_output_directory()