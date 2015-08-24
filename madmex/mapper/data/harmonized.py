'''
Created on 21/08/2015

@author: erickpalacios
'''

from __future__ import unicode_literals
from madmex.mapper.base import BaseData, _get_attribute, put_in_dictionary
import numpy
import numpy.ma as ma
import logging
from Carbon.TextEdit import WIDTHHook

LOGGER = logging.getLogger(__name__)
PROJECTION = ['projection']
GEOTRANSFORM = ['geotransform']
XRANGE = ['x_range']
YRANGE = ['y_range']
XOFFSET = ['x_offset']
YOFFSET = ['y_offset'] 


def get_image_mask(x, y, width, height, data, threshold=0):
    '''
    This method takes a 2x2 matrix, usually representing an image, and takes a
    subset of the image using the offsets given by x and y, and the dimensions
    given by width and height. The remaining argument, is used to create the values
    of the mask, if the values in the matrix fall under the threshold value, then
    the mask element in that position will be True; False otherwise.
    '''
    if len(data.shape) != 2:
        raise ValueError('Invalid data dimension, data should be 2 dimensional.')
    subset = data[x:x + width,y:y + height]
    mask = numpy.zeros((width, height))
    numpy.putmask(mask, subset<=threshold, 1)
    return mask

def get_multiband_image_mask(x, y, width, height, data, threshold=0):
    '''
    This method takes as input a multiband image, it flattens the image by applying
    a minimum over the first axis, obtaining a 2x2 matrix. Then the process of
    creating a mask is applied to this new matrix.
    '''
    if len(data.shape) != 3:
        raise ValueError('Invalid data dimension, data should be 3 dimensional.')
    min_data = numpy.min(data, axis=0)
    return get_image_mask(x, y, width, height, min_data, threshold)
    
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
                             

if __name__ == '__main__':
    import raster
    image1 = '/LUSTRE/MADMEX/eodata/etm+/23047/2013/2013-06-24/l1t/LE70230472013175ASN00_B1.TIF'
    image2 = '/LUSTRE/MADMEX/eodata/etm+/23047/2013/2013-01-15/l1g/LE70230472013015ASN00_B1.TIF'
    image_pair_list = []
    image_pair_list.append(image1)
    image_pair_list.append(image2)
    gdal_format = "GTiff"
    image1_data_class =raster.Data(image1, gdal_format)
    image2_data_class = raster.Data(image2, gdal_format)
    
    
    
    harmonized_class = Data(image1_data_class, image2_data_class)
    extents = harmonized_class.harmonized_extents
    print extents
    
    x_range = extents['x_range']
    y_range = extents['y_range']
    x_offset = extents['x_offset']
    y_offset = extents['y_offset']
    
    
    print 'x_range : %s' % x_range
    print 'y_range : %s' % y_range
    print 'x_offset : %s' % x_offset
    print 'y_offset : %s' % y_offset
    
    image1_data = image1_data_class.read_data_file_as_array()
    image2_data = image2_data_class.read_data_file_as_array()

    print 'Size of image1 ' , image1_data.shape
    print 'Size of image2 ' , image2_data.shape

    image1_data_class.close()
    image2_data_class.close()
    
    print numpy.unique(image1_data)
    
    
    first = int(y_offset[0]) 
    second = int(y_offset[0] + y_range)
    third = int(x_offset[0])
    fourth = int(x_offset[0] + x_range)
    
    print [first, second]
    print [third, fourth]
    
    a = numpy.min(image1_data[first:second, third:fourth],axis=0)
    b = numpy.min(image2_data[int(y_offset[1]):int(y_offset[1] + y_range),int(x_offset[1]):int(x_offset[1] + x_range)],axis=0)
    
    mask_a = numpy.ones((y_range, x_range))
    mask_b = numpy.ones((y_range, x_range))
    
#   numpy.putmask(mask_a, a<=0, 0)
#   numpy.putmask(mask_b, b<=0, 0)
    
    mask =  numpy.logical_not(numpy.logical_and(mask_a, mask_b))
    
    

    print 'a : %s' % a
    print 'b : %s' % b
    print 'hello'
    
    
    my_data = numpy.random.rand(10,10)
    x = 2
    y = 2
    width = 3
    height = 4
    threshold = .3
    
    subset = my_data[x:x+width, y:y+height]
    
    x_mask = get_image_mask(x,y,width,height,my_data,threshold)
    
    print subset
    print x_mask
    
    masked_data = ma.masked_array(subset, x_mask)
 
    print masked_data
    
    print masked_data[~masked_data.mask]
    
    
    multi_data = numpy.random.rand(5, 10, 10)
    
    multi_mask = get_multiband_image_mask(x,y,width,height,multi_data,threshold)
    
    multi_subset = multi_data[:,x:x+width, y:y+height]
    
    
    #masked_multi_data = ma.masked_array(multi_subset, multi_mask)
    
    
    print multi_subset
    
    print multi_mask
    
    
    
    
    
    
    