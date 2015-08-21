'''
Created on 21/08/2015

@author: erickpalacios
'''

from __future__ import unicode_literals
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
        self.harmonize_images([image1_data_class, image2_data_class], image1_data_class.get_attribute(raster.PROJECTION))
    def harmonize_images(self, images, projection):
        '''
        Harmonizes a list of images into the minimum common extent. If one of
        the images is not in the specified projection, it will be ignored.
        '''
        import raster
        geotransforms = []
        projections = []
        shapes = []
        accepted_images = []
        put_in_dictionary(self.harmonized_extents, PROJECTION, projection)
        for image in images:
            if image and image.get_attribute(raster.PROJECTION) == projection:
                geotransforms.append(image.get_attribute(raster.GEOTRANSFORM))
                projections.append(image.get_attribute(raster.PROJECTION))
                shapes.append(image.get_attribute(raster.DATA_SHAPE))
                accepted_images.append(image)
            else:
                LOGGER.warn('Image not in the specified projection, will be ignored.')
        geotransforms = numpy.array(geotransforms)
        projections = numpy.array(projections)
        shapes = numpy.array(shapes)
        
        
        # Intersect boundary coordinates
        # Get upper left coordinates
        ul_x = max(geotransforms[:, 0])
        ul_y = min(geotransforms[:, 3])
        # Calculate lower right coordinates
        lr_x = min(geotransforms[:, 0] + shapes[:, 0] * geotransforms[:, 1])
        lr_y = max(geotransforms[:, 3] + shapes[:, 1] * geotransforms[:, 5])
        # Calculate range in x and y dimension in pixels
        x_range = (lr_x - ul_x) / geotransforms[0, 1]
        y_range = (lr_y - ul_y) / geotransforms[0, 5]
        # Calculate offset values for each image
        x_offset = (ul_x - geotransforms[:, 0]) / geotransforms[:, 1]
        y_offset = (ul_y - geotransforms[:, 3]) / geotransforms[:, 5]
        # Calculate unique geo transformation
        geotransform = (ul_x, geotransforms[0, 1], 0.0, ul_y, 0.0, geotransforms[0, 5])
        put_in_dictionary(self.harmonized_extents, GEOTRANSFORM, geotransform)
        put_in_dictionary(self.harmonized_extents, XRANGE, x_range)
        put_in_dictionary(self.harmonized_extents, YRANGE, y_range)
        put_in_dictionary(self.harmonized_extents, XOFFSET, x_offset)
        put_in_dictionary(self.harmonized_extents, YOFFSET, y_offset)
        return self.harmonized_extents
    def get_attribute(self, path_to_attribute):
        '''
        Returns the attribute that is found in the given path.
        '''
        return _get_attribute(path_to_attribute, self.harmonized_extents)                        
    