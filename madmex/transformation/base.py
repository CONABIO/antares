'''
Created on 24/08/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

class BaseTransformation(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        print params
        
    def execute(self):
        self.preprocessing()
        self.processing()
        self.postprocessing()
    
    def preprocessing(self):
        raise NotImplementedError('Subclasses of BaseTransformation must provide a preprocessing() method.')
    def processing(self):
        raise NotImplementedError('Subclasses of BaseTransformation must provide a processing() method.')
    def postprocessing(self):
        raise NotImplementedError('Subclasses of BaseTransformation must provide a postprocessing() method.')