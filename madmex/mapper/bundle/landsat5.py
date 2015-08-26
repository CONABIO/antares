'''
Created on Jul 22, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
from madmex.mapper.bundle._landsat import get_landsat_files


_MISSION = '5'

class Bundle(BaseBundle):
    '''
    A class to create a memory representation of a Landsat 5 image including its
    metadata files. It is also responsible of creating a database object to be
    persisted.
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_dictionary = get_landsat_files(_MISSION)
        self._look_for_files()
        self.output_directory = None
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Landsat 5'
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            self.output_directory = destination
        return self.output_directory
    def get_files(self):
        '''
        Retrieves a list with the files found in the directory that this bundle
        represents.
        '''
        return [file_path for file_path in self.file_dictionary.itervalues() if file_path]

if __name__ == '__main__':

    bundle = Bundle('/LUSTRE/MADMEX/eodata/tm/10052/2000/2000-08-20/l1g')
    print bundle.get_files()
    print bundle.can_identify()
    
    
    