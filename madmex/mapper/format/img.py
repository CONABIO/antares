'''
Created on 30/06/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseFormat
from madmex.mapper.data.raster import Data
FORMAT = "HFA"

class Format(BaseFormat):
    '''
    classdocs
    '''


    def __init__(self, image_path):
        '''
        Constructor
        '''
        self.data_class = Data(image_path, FORMAT)
        