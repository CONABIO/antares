'''
Created on Jun 10, 2015

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
                
    def is_consistent(self):
        '''
        Check if this bundle is consistent.
        '''
        pass
