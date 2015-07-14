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
        pass
        
    def can_identify(self):
        return False
    
    def get_name(self):
        return 'Modis'