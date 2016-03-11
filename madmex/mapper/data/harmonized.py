'''
Created on 21/08/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

import logging

import numpy

from madmex.mapper.base import BaseData, _get_attribute, put_in_dictionary


# import numpy.ma as ma
# from Carbon.TextEdit import WIDTHHook
LOGGER = logging.getLogger(__name__)
PROJECTION = ['projection']
DATA_SHAPE = ['data_shape']
GEOTRANSFORM = ['geotransform']
XRANGE = ['x_range']
YRANGE = ['y_range']
XOFFSET = ['x_offset']
YOFFSET = ['y_offset']


def test():
    import raster
    image1 = '/LUSTRE/MADMEX/eodata/etm+/23047/2013/2013-06-24/l1t/LE70230472013175ASN00_B1.TIF'
    image2 = '/LUSTRE/MADMEX/eodata/etm+/23047/2013/2013-01-15/l1g/LE70230472013015ASN00_B1.TIF'
    image_pair_list = []
    image_pair_list.append(image1)
    image_pair_list.append(image2)
    gdal_format = "GTiff"
    image1_data_class = raster.Data(image1, gdal_format)
    image2_data_class = raster.Data(image2, gdal_format)

    harmonized_class = Data(image1_data_class, image2_data_class)
    extents = harmonized_class.harmonized_extents
    LOGGER.debug('Image extents: %s', extents)

    x_range = extents['x_range']
    y_range = extents['y_range']
    x_offset = extents['x_offset']
    y_offset = extents['y_offset']

    LOGGER.debug('x_range : %s' % x_range)
    LOGGER.debug('y_range : %s' % y_range)
    LOGGER.debug('x_offset : %s' % x_offset)
    LOGGER.debug('y_offset : %s' % y_offset)

    image1_data = image1_data_class.read_data_file_as_array()
    image2_data = image2_data_class.read_data_file_as_array()

    LOGGER.debug('Size of image1: %s', image1_data.shape)
    LOGGER.debug('Size of image2: %s', image2_data.shape)
    image1_data_class.close()
    image2_data_class.close()


    first = int(y_offset[0]) 
    second = int(y_offset[0] + y_range)
    third = int(x_offset[0])
    fourth = int(x_offset[0] + x_range)

    LOGGER.debug([first, second])
    LOGGER.debug([third, fourth])

    a = numpy.min(image1_data[first:second, third:fourth], axis=0)
    b = numpy.min(image2_data[int(y_offset[1]):int(y_offset[1] + y_range), int(x_offset[1]):int(x_offset[1] + x_range)], axis=0)
    
    mask_a = numpy.ones((y_range, x_range))
    mask_b = numpy.ones((y_range, x_range))


    mask = numpy.logical_not(numpy.logical_and(mask_a, mask_b))
    LOGGER.debug('mask : %s', mask)

    LOGGER.debug('a : %s', a)
    LOGGER.debug('b : %s', b)


    my_data = numpy.random.rand(10, 10)
    x = 2
    y = 2
    width = 3
    height = 4
    threshold = .3

   
    
    subset = my_data[x:x + width, y:y + height]
    LOGGER.debug('*********************************************')
    LOGGER.debug('my_data : %s', my_data)
    x_mask = get_image_mask(my_data, threshold)
    LOGGER.debug('*********************************************')
    LOGGER.debug('x_mask : %s', x_mask)
    x_mask_subset = get_image_subset(x, y, width, height, x_mask)
    LOGGER.debug('*********************************************')
    LOGGER.debug('x_mask_subset : %s', x_mask_subset)
    

    x_mask_subset = get_image_mask(subset, threshold)
                           
    subset_x_mask = get_image_subset(x, y, width, height, x_mask)

    LOGGER.debug('*************************')
    LOGGER.debug(subset)
    LOGGER.debug('*************************')
    LOGGER.debug(x_mask_subset)
    LOGGER.debug('*************************')
    LOGGER.debug(subset_x_mask)
    LOGGER.debug('*************************')
    LOGGER.debug(get_mask_image_subset(x, y, width, height, my_data, threshold))



    LOGGER.debug('multiband')


    my_data = numpy.random.rand(5, 10, 10)
    x = 2
    y = 2
    width = 3
    height = 4
    threshold = .3

    multi_subset = get_multiband_image_subset(x, y, width, height, my_data)
    multi_mask_subset = get_multiband_image_mask(multi_subset, threshold)


    LOGGER.debug('*************************')
    LOGGER.debug('my_data: %s', my_data)
    LOGGER.debug('*************************')
    LOGGER.debug('multi_subset: %s', multi_subset)
    LOGGER.debug('*************************')
    LOGGER.debug('multi_mask_subset: %s', multi_mask_subset)
    LOGGER.debug('*************************')
    LOGGER.debug(get_mask_multiband_image_subset(x, y, width, height, my_data, threshold))

def get_image_mask(data, threshold=0):
    '''
    The remaining argument, is used to create the values
    of the mask, if the values in the matrix fall under the threshold value, then
    the mask element in that position will be True; False otherwise.
    '''
    if len(data.shape) != 2:
        raise ValueError('Invalid data dimension, data should be 2 dimensional.')
    mask = numpy.zeros(data.shape)
    numpy.putmask(mask, data <= threshold, 1)
    return mask
def get_multiband_image_mask(data, threshold=0):
    '''
    This method takes as input a multiband image, it flattens the image by applying
    a minimum over the first axis, obtaining a 2x2 matrix. Then the process of
    creating a mask is applied to this new matrix.
    '''
    if len(data.shape) != 3:
        raise ValueError('Invalid data dimension, data should be 3 dimensional.')
    min_data = numpy.min(data, axis=0)
    return get_image_mask(min_data, threshold)
def get_image_subset(x, y, width, height, data):
    '''
    This method takes a matrix, usually representing an image, and takes a
    subset of the image using the offsets given by x and y, and the dimensions
    given by width and height.
    '''
    if len(data.shape) != 2:
        raise ValueError('Invalid data dimension, data should be 2 dimensional.')
    subset = data[x:x + width, y:y + height]
    return subset
def get_multiband_image_subset(x, y, width, height, data):
    '''
    This method takes a matrix representing a multiband image,  and takes a
    subset of the image using the offsets given by x and y, and the dimensions
    given by width and height. All of the bands in the image will be taken into
    account.
    '''
    if len(data.shape) != 3:
        raise ValueError('Invalid data dimension, data should be 3 dimensional.')
    subset = data[:, x:x + width, y:y + height]
    return subset
def get_mask_image_subset(x, y, width, height, data, threshold=0):
    '''
    This method is a helper method that calls the mask and subset methods one
    after the other.
    '''
    return get_image_mask(get_image_subset(x, y, width, height, data), threshold)
def get_mask_multiband_image_subset(x, y, width, height, data, threshold=0):
    '''
    This method is a helper method that calls the mask and subset methods one
    after the other. In particular it handles the case for a multiband image.
    '''
    return get_multiband_image_mask(get_multiband_image_subset(x, y, width, height, data), threshold)
def stack_images():
    pass

def harmonize_images(images, projection, shape):
    '''
    Harmonizes a list of images into the minimum common extent. If one of
    the images is not in the specified projection, it will be ignored.
    '''
    if not projection or not shape:
        LOGGER.error('Projection and shape should not be null.')
        raise Exception('Projection and shape should not be null.')
    import raster
    extents = {}
    geotransforms = []
    projections = []
    shapes = []
    accepted_images = []
    for image in images:
        if projection and shape and image and image.get_attribute(raster.PROJECTION) == projection and image.get_attribute(raster.DATA_SHAPE) == shape:
            geotransforms.append(image.get_attribute(raster.GEOTRANSFORM))
            projections.append(image.get_attribute(raster.PROJECTION))
            shapes.append(image.get_attribute(raster.DATA_SHAPE))
            accepted_images.append(image)
        else:
            LOGGER.warn('Image not in the specified projection or data_shape, will be ignored.')
    if accepted_images:
        put_in_dictionary(extents, PROJECTION, projection)
        put_in_dictionary(extents, DATA_SHAPE, shape)
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
        put_in_dictionary(extents, GEOTRANSFORM, geotransform)
        put_in_dictionary(extents, XRANGE, x_range)
        put_in_dictionary(extents, YRANGE, y_range)
        put_in_dictionary(extents, XOFFSET, x_offset)
        put_in_dictionary(extents, YOFFSET, y_offset)
    return extents

class Data(BaseData):
    '''
    classdocs
    '''
    def __init__(self, image1_data_class, image2_data_class):
        '''
        Constructor
        '''
        super(Data, self).__init__()
        self.harmonized_extents = {}
        self._harmonized_images(image1_data_class, image2_data_class)
    def _harmonized_images(self, image1_data_class, image2_data_class):
        '''
        Given two images of class raster create a new image with no data, the same projection, 
        and uniform xrange, yrange, xoffset, yoffset
        '''
        import raster
        if not self.harmonized_extents:
            self.harmonized_extents = harmonize_images([image1_data_class, image2_data_class], image1_data_class.get_attribute(raster.PROJECTION), image1_data_class.get_attribute(raster.DATA_SHAPE))
            if not self.harmonized_extents:
                print('No common extents for images')
    def harmonized_arrays(self, image1_data_class, image2_data_class):
        '''
        Given two images of class raster  returns two arrays with common harmonized properties        
        '''
        yoffset = self.get_attribute(YOFFSET)
        xoffset = self.get_attribute(XOFFSET)
        x_range = self.get_attribute(XRANGE)  
        y_range = self.get_attribute(YRANGE)
        try:
            image1_data_array = image1_data_class.read_data_file_as_array()[:, int(yoffset[0]):int(yoffset[0]) + y_range, int(xoffset[0]):int(xoffset[0]) + x_range]
            image2_data_array = image2_data_class.read_data_file_as_array()[:, int(yoffset[1]):int(yoffset[1]) + y_range, int(xoffset[1]):int(xoffset[1]) + x_range]
            return (image1_data_array, image2_data_array) 
        except Exception:
            LOGGER.error('Process of harmonize arrays failed, one image is %s', image1_data_class.image_path)
            print('Process of harmonize arrays failed, one image is %s', image1_data_class.image_path)
    def get_attribute(self, path_to_attribute):
        '''
        Returns the attribute that is found in the given path.
        '''
        return _get_attribute(path_to_attribute, self.harmonized_extents)

    