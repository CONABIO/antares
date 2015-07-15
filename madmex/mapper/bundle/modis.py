'''
Created on Jul 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.mapper.base import BaseBundle


class Bundle(BaseBundle):
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        super(Bundle, self).__init__()
        pass
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