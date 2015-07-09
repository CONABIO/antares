'''
Created on 07/07/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseFormat
from madmex.mapper.data.vector import Data

FORMAT = 'ESRI Shapefile'
SPECIFICATIONS = ['shx', 'dbf', 'prj']
class Format(BaseFormat):
    '''
    classdocs
    '''     

    def __init__(self, image_path):
        '''
        Constructor
        '''
        self.data_class = Data(image_path, FORMAT)
