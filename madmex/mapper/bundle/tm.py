'''
Created on Jul 22, 2015

@author: agutierrez
'''
from __future__ import unicode_literals
from madmex.mapper.base import BaseBundle


class Bundle(BaseBundle):
    '''
    classdocs
    '''


    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_dictionary = {
                                
                                }    
    def can_identify(self):
        '''
        Test if the parsed path can be identified as a Modis bundle.
        '''
        return False
    def _look_for_files(self):
        BaseBundle._look_for_files(self)
        #do something with the files
        
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Landsat Thematic Mapper'
