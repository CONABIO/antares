'''
Created on Aug 26, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseBundle
from madmex.configuration import SETTINGS

class Bundle(BaseBundle):
    '''
    A class to create a memory representation of a Landsat image including its
    metadata files. It is also responsible of creating a database object to be
    persisted.
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.file_dictionary = {
                           }
        self.output_directory = None
    def can_identify(self):
        '''
        Test if the parsed path can be identified as a Modis bundle.
        '''
        return False
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Landsat 8'
    
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            self.output_directory = destination
        return self.output_directory
