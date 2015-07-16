'''
Created on Jul 14, 2015

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
        super(Bundle, self).__init__(params)
        self.target = None
    def can_identify(self):
        '''
        Test if the parsed path can be identified as a Spot bundle.
        '''
        return False
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Spot'
    def get_output_directory(self):
        return self.target
