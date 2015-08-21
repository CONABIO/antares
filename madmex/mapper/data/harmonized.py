'''
Created on 21/08/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseData, _get_attribute, put_in_dictionary
import numpy
import logging

LOGGER = logging.getLogger(__name__)
PROJECTION = ['projection']
GEOTRANSFORM = ['geotransform']
XRANGE = ['xrange']
YRANGE = ['yrange']
XOFFSET = ['xoffset']
YOFFSET = ['yoffset'] 

class Data(BaseData): #TODO: not useful the inheritance from BaseData, change this inheritance to another Base class
    '''
    classdocs
    '''
    def __init__(self, image1_data_class, image2_data_class):
        '''
        Constructor
        '''
        self.harmonized_extents = {}
        self._harmonized_images(image1_data_class, image2_data_class)
    def _harmonized_images(self, image1_data_class, image2_data_class):
        '''
        Given two images of class raster create a new image with no data, the same projection, 
        and uniform xrange, yrange, xoffset, yoffset
        '''
        import raster
        proj_image1 = image1_data_class.get_attribute(raster.PROJECTION)
        if proj_image1 == image2_data_class.get_attribute(raster.PROJECTION):        
            geotransform_array = numpy.array([image1_data_class.get_attribute(raster.GEOTRANSFORM), image2_data_class.get_attribute(raster.GEOTRANSFORM)])
            data_shape_array = numpy.array([image1_data_class.get_attribute(raster.DATA_SHAPE), image2_data_class.get_attribute(raster.DATA_SHAPE)])    
            self.harmonized_extents ={'projection': None, 'geotransform': None, 'xrange': None, 'yrange': None, 'xoffset': None, 'yoffset': None}
            put_in_dictionary(self.harmonized_extents, PROJECTION, proj_image1)
            # Intersect boundary coordinates
            # Get upper left coordinates
            ul_x = max(geotransform_array[:, 0])
            ul_y = min(geotransform_array[:, 3])
            # Calculate lower right coordinates
            lr_x = min(geotransform_array[:, 0] + data_shape_array[:, 0] * geotransform_array[:, 1])
            lr_y = max(geotransform_array[:, 3] + data_shape_array[:, 1] * geotransform_array[:, 5])
            # Calculate range in x and y dimension in pixels
            x_range = (lr_x - ul_x) / geotransform_array[0, 1]
            y_range = (lr_y - ul_y) / geotransform_array[0, 5]
            # Calculate offset values for each image
            x_offset = (ul_x - geotransform_array[:, 0]) / geotransform_array[:, 1]
            y_offset = (ul_y - geotransform_array[:, 3]) / geotransform_array[:, 5]
            # Calculate unique geo transformation
            geotransform = (ul_x, geotransform_array[0, 1], 0.0, ul_y, 0.0, geotransform_array[0, 5])
            put_in_dictionary(self.harmonized_extents, GEOTRANSFORM, geotransform)
            put_in_dictionary(self.harmonized_extents, XRANGE, x_range)
            put_in_dictionary(self.harmonized_extents, YRANGE, y_range)
            put_in_dictionary(self.harmonized_extents, XOFFSET, x_offset)
            put_in_dictionary(self.harmonized_extents, YOFFSET, y_offset)
        else:
            LOGGER.info('Skipping a dataset because of different projection of image %s and image %s' %(image1_data_class.image_path, image2_data_class.image_path))

    def get_attribute(self, path_to_attribute):
        '''
        Returns the attribute that is found in the given path.
        '''
        return _get_attribute(path_to_attribute, self.harmonized_extents)                        
            