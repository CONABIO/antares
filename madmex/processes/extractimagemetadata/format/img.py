'''
Created on 30/06/2015

@author: erickpalacios
'''
from madmex.processes.extractimagemetadata.base import BaseFormat

class Format(BaseFormat):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.format_name = 'img'
    def __str__(self):
        return self.format_name