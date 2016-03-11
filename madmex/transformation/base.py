'''
Created on 24/08/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

class BaseTransformation(object):
    '''
    This class is the base for the implementation of an algorithm that tranforms
    data. Input and output should be standard between implementations so we can
    reuse code between implementations.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    def execute(self):
        '''
        Execute will call inner processes to complete the implementation of this
        algorithm. The idea behind having three methods instead of one is to have
        more granular control over the pieces that conform the algorithm.
        '''
        self.preprocessing()
        self.processing()
        self.postprocessing()
    
    def preprocessing(self):
        '''
        This step should prepare the data for the algorithm implemented. It should
        not depend on external inputs and should not have outputs. The idea is
        to keep things simple so this class could be overriden for many purposes.
        '''
        raise NotImplementedError(
            'Subclasses of BaseTransformation must provide a preprocessing() method.'
            )
    def processing(self):
        '''
        The implementation of the transformation algorithm should go inside here
        it transforms the input variables into something useful that can later be
        plugged in another process.
        '''
        raise NotImplementedError(
            'Subclasses of BaseTransformation must provide a processing() method.'
            )
    def postprocessing(self):
        '''
        Once the algorithm has finished, if some extra process is needed in order
        to have a final product, those steps should go inside here.
        '''
        raise NotImplementedError(
            'Subclasses of BaseTransformation must provide a postprocessing() method.'
            )
