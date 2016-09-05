'''
Created on 30/08/2016

@author: erickpalacios
'''
from madmex.mapper.base import BaseBundle


class VectorBaseBundle(BaseBundle):
    '''
    classdocs
    '''
    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_dictionary = None
        self.get_vector_files()
        self._look_for_files() 
    def get_vector_files(self):
        if not self.file_dictionary:
            shape_file = '.*.shp$'
            shx_file = '.*.shx'
            proj_file = '.*.prj'
            dbf_file = '.*.dbf'
            if self.FORMAT == 'ESRI Shapefile':
                self.file_dictionary = {
                                        shape_file:None,
                                        shx_file:None,
                                        proj_file:None,
                                        dbf_file:None
                                        }