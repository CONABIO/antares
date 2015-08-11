'''
Created on Jul 22, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.mapper.base import BaseBundle


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
        pass
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Landsat Enhanced Thematic Mapper Plus'
