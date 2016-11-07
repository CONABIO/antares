'''
Created on 30/08/2016

@author: erickpalacios
'''
from madmex.mapper.bundle._vector import VectorBaseBundle
from madmex.mapper.data import vector
import logging
from madmex.processing.vector import rasterize_vector
LOGGER = logging.getLogger(__name__)

FORMAT = 'ESRI Shapefile'

class Bundle(VectorBaseBundle):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.FORMAT = FORMAT
        super(Bundle, self).__init__(path)
        self.vector =None
    def get_name(self):
        return FORMAT
    def get_vector(self):
        if self.vector is None:
            self.vector = vector.Data(self.file_dictionary['.*.shp$'], FORMAT)
        return self.vector
    def rasterize(self, target, band_list, burn_values, options=None):
        '''
        The target needs to be an output of the function Create of gdal
        The burn values are the data that we consider as relevant data
        '''
        if rasterize_vector(target, self.get_vector().layer, band_list, burn_values, options) != 0:
            LOGGER.info('Error when rasterizing the vector layer : %s' % self.get_vector().image_path)
if __name__ == '__main__':
    folder = '/Users/erickpalacios/Documents/CONABIO/MADMEXdata/eodata/footprints/country_mexico/'
    bundle = Bundle(folder)
    print bundle.file_dictionary
    print bundle.can_identify()