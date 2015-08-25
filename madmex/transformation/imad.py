'''
Created on 24/08/2015

@author: erickpalacios
'''
from madmex.transformation.base import BaseTransformation
import numpy
class Transformation(BaseTransformation):
    '''
    classdocs
    '''

    def __init__(self, image1_array, image2_array):
        '''
        Constructor
        '''
        self.execute(image1_array, image2_array)
    def execute(self, image1_array, image2_array):
        print 'interfaces correctly made'
        print 'image1 array'
        print numpy.unique(image1_array)
        print 'image2 array'
        print numpy.unique(image2_array)
        