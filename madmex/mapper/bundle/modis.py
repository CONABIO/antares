'''
Created on Jul 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle


class Bundle(BaseBundle):
    '''
    classdocs
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
        return 'Modis'
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            self.output_directory = destination
        return self.output_directory
