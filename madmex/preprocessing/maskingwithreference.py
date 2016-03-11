'''
Created on 16/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import logging

import numpy

from madmex.mapper.data import raster
from madmex.mapper.data.raster import new_options_for_create_raster_from_reference, \
    create_raster_tiff_from_reference
from madmex.mapper.sensor import rapideye
from madmex.persistence.driver import find_datasets
from madmex.preprocessing.masking import filter_median, morph_dilation, calculate_cloud_shadow, morphing, \
    FMASK_CLOUD, FMASK_CLOUD_SHADOW
from madmex.mapper.data._gdal import create_raster_from_reference


LOGGER = logging.getLogger(__name__)
GENERALIZE = False
MORPHING_SIZE = 10


def masking(image_array, tile_id, solar_zenith, solar_azimuth, geotransform, sensor_id=1, product_id=2, cloud_cover=100):
    '''
    '''
    resolution = geotransform[1]
    images_references_paths = get_images_for_tile(tile_id, sensor_id, product_id, cloud_cover)
    image_difference_array = calculate_difference_from_reference(image_array, images_references_paths)
    cloud_shadow_array = cloud_shadow_mask_array(image_array, image_difference_array, solar_zenith, solar_azimuth, resolution)
    return cloud_shadow_array
def get_images_for_tile(tile_id, sensor_id, product_id, cloud_cover=100):
    '''
    This method will query the database for all the images between 1990 and 2020.
    '''
    start_date = datetime.strptime('1990-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
    return find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id)
def calculate_difference_from_reference(image_array, images_references_paths):
    '''
    This method calculates the difference between an array and an array created
    to get a reference.
    '''
    return image_array - create_reference_array(images_references_paths)
def create_reference_array(images_references_paths):
    '''
    New implementation of create reference image, performance was sacrificed in
    favor of clarity. This method creates a reference image by calculating the
    median of a set of images pixelwise.
    '''
    from madmex.mapper.bundle.rapideye import Bundle
    import madmex.mapper.sensor.rapideye as sensor
    identified = []
    bands = None
    rows = None
    columns = None
    for image_path in images_references_paths:
        bundle = Bundle(image_path)
        if bundle.can_identify():
            if not bands:
                bands = bundle.get_sensor().get_attribute(sensor.BANDS)
            if not rows:
                rows = bundle.get_sensor().get_attribute(sensor.ROWS)
            if not columns:
                columns = bundle.get_sensor().get_attribute(sensor.COLUMNS)
            identified.append(bundle)
    LOGGER.debug('Bands: %d, Rows: %d, Columns: %d.', bands, rows, columns) 
    number = len(identified)
    LOGGER.debug('Number of identified images: %d', number)
    my_array = numpy.empty((number, bands, rows, columns))
    for index in range(number):
        my_array[index] = identified[index].get_raster().read_data_file_as_array().astype(numpy.float)
    medians = numpy.empty((bands, rows, columns))
    for band in range(bands):
        medians[band] = numpy.median(my_array[:, band, :, :], axis=0)
    return medians
def cloud_mask_array(image_difference_array, threshold=30000, filter_size=13, morphing_size=0):  # TODO: Is it 0 in morphing_size?? is not 10??
    '''
    This method returns a mask for the given array, it stacks all the bands into
    one and filters values that match the threshold. The new array will be filled
    with 0 when the values are below the threshold and 1 when the values are above
    the threshold. We assume that clouds will have brighter values when compared
    to the reference array.
    '''
    clouds = filter_median((numpy.sum(image_difference_array, axis=0) > threshold).astype(numpy.int), filter_size)
    if morphing_size:
        clouds = morph_dilation(clouds, morphing_size)
    return clouds
def shadow_mask_array(image_difference_array, threshold=-5500, filter_size=13, morphing_size=0):  # TODO: Is it 0 in morphing_size?? is not 10??
    '''
    This method returns a mask for the given array, it stacks all the bands into
    one and filters values that match the threshold. The new array will be filled
    with 0 when the values are above the threshold and 1 when the values are bellow
    the threshold. We assume that shadows will have darker values when compared to
    the reference array.
    '''
    shadows = filter_median((numpy.sum(image_difference_array[3:, :, :], axis=0) < threshold).astype(numpy.int), filter_size)
    if morphing_size:
        shadows = morph_dilation(shadows, morphing_size)
    return shadows
def cloud_shadow_mask_array(image_array, image_difference_array, solar_zenith, solar_azimuth, resolution):
    '''
    This method creates a mask for clouds and shadows using a reference array.
    '''
    clouds = cloud_mask_array(image_difference_array)
    shadows = shadow_mask_array(image_difference_array)
    inbetween = calculate_cloud_shadow(clouds, shadows, solar_zenith, solar_azimuth, resolution)
    
    image_mask_array = outside_mask_array(image_array, outside_value=255)
    
    pixel_sizes = [250, 150, 50]
    number_of_sizes = len(pixel_sizes)
    for pixel_size in pixel_sizes:
        numpy.putmask(image_mask_array, morph_dilation(clouds, pixel_size) == 1, FMASK_CLOUD * 10 + number_of_sizes)
        number_of_sizes = number_of_sizes - 1
    numpy.putmask(image_mask_array, inbetween == 1, FMASK_CLOUD_SHADOW)
    numpy.putmask(image_mask_array, clouds == 1, FMASK_CLOUD)
    return image_mask_array
def outside_mask_array(image_array, no_data_value=0, outside_value=255):
    '''
    This method creates a mask for the values outside the image. We assume that
    a no data pixel will have 0 value in every band so when we add all the bands
    together, we mask values with 0 value in them.
    '''
    mask_array = numpy.zeros((image_array.shape[1], image_array.shape[2]))
    sum_of_bands_array = numpy.sum(image_array, axis=0) == 0
    numpy.putmask(mask_array, sum_of_bands_array, outside_value)
    return mask_array

