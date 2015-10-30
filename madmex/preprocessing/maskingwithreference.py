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


LOGGER = logging.getLogger(__name__)
GENERALIZE = False
MORPHING_SIZE = 10
#TODO: this module is lacking of landmasking....see rapideyeclouds.py of madmex_old
def masking(re_directory, re_sensor_metadata, re_raster_array, re_raster_metadata):
    '''
    General function for controlling masking, it will read the files from a
    directory and create the cloud and shadow mask for that directory.
    '''
    tile_id = re_sensor_metadata(rapideye.TILE_ID)
    re_directory = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    re_directory = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/CloudMasking/RE_1649125/1649125_2014-01-23_RE4_3A_301519'
    data_shape_reference, geotransform_reference, image_array_difference = reference_for_tile(re_raster_metadata, re_directory, tile_id, re_raster_array) 
    solar_zenith = re_sensor_metadata(rapideye.SOLAR_ZENITH)
    solar_azimuth = re_sensor_metadata(rapideye.SOLAR_AZIMUTH)
    image_mask_path = mask_clouds_and_shadows(re_raster_metadata, re_raster_array, image_array_difference, data_shape_reference, solar_zenith, solar_azimuth, re_directory, geotransform_reference)
    return image_mask_path
def reference_for_tile(re_raster_metadata, folder, tile_id, image_array):
    '''
    Get reference image for given tile id. It will gather the available images
    for a particular tile and will return the difference between the given image
    and the reference one.
    '''
    cloud_cover = 100
    sensor_id = 1
    product_id = 2
    start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
    images_references_paths = find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id)
    LOGGER.info("Number of acquired images: %d" % len(images_references_paths))
    print("Number of acquired images: %d" % len(images_references_paths))
    return get_image_array_difference(re_raster_metadata, folder, images_references_paths, image_array, len(images_references_paths))
def get_image_array_difference(re_raster_metadata, folder, images_references_paths, image_array, max_number_of_images):
    '''
    Return array of differences between reference image (stacking of bands) and image_array
    '''
    #TODO This method can be deleted in favor of calculate_difference_from_reference that does not write an image.
    #TODO Clean this method once the images are available in local file
    data_shape, geotransform, list_with_arrays_stack_per_band = get_stack_arrays_per_band(images_references_paths, max_number_of_images)
    band_medians = numpy.zeros([data_shape[2], data_shape[1], data_shape[0]])    
    number_of_bands = data_shape[2]
    for k in range(number_of_bands-1, -1, -1):
        band_medians[k, :, :] = numpy.median(list_with_arrays_stack_per_band[k], axis = 0)
        list_with_arrays_stack_per_band.pop()
    image_reference_path = folder + '/re_reference.tif'
    create_raster_tiff_from_reference(re_raster_metadata, image_reference_path, band_medians)
    #TODO: Is not necessary create a tiff image, we only need the array and datashape and geotransform for the next processes
    LOGGER.info("RE reference image: %s" % image_reference_path)
    LOGGER.info('Calculating difference between RapidEye image and reference')
    image_array_difference = numpy.zeros([data_shape[2], data_shape[1], data_shape[0]])
    for b in range(data_shape[2]):
        image_array_difference[b, :, :] = image_array[b, :, :] - band_medians[b, :, :]
    image_array = None
    band_medians = None     
    return data_shape, geotransform, image_array_difference
def get_stack_arrays_per_band(images_references_paths, max_number_of_images):
    '''
    Check consistency of folders and get stack arrays for every band. Return a list with k number 
    of bands. Every element of the list is a stack array
    '''
    #TODO This method can be deleted in favor of create_reference_array that does not write an image.
    #TODO: change this line to identify different sensors
    from madmex.mapper.bundle.rapideye import Bundle
    number_of_identified_images = 0
    bands, height, width = 0, 0, 0
    data_shape = (width, height, bands)
    list_with_arrays_stack_per_band = list()
    geotransform = {}
    for image_path in images_references_paths:
        print image_path
        bundle  = Bundle(image_path)
        first = True
        if bundle.can_identify():
            array = bundle.get_raster().read_data_file_as_array().astype(numpy.float)
            bands, height, width = array.shape
            if first:
                data_shape = (width, height, bands)
                geotransform = bundle.get_raster().get_attribute(raster.GEOTRANSFORM) 
                for k in range(0, bands):
                    list_with_arrays_stack_per_band.append(numpy.zeros([max_number_of_images, data_shape[1], data_shape[0]]))
                first = False
            for k in range(0, bands):
                array_aux = array[k, :, :]
                list_with_arrays_stack_per_band[k][number_of_identified_images, :, :] = array_aux
            number_of_identified_images+= 1
    for k in range(0, bands):
        if number_of_identified_images == 0:
            list_with_arrays_stack_per_band[k] = list_with_arrays_stack_per_band[k][0:1, :, :]
        else:
            list_with_arrays_stack_per_band[k] = list_with_arrays_stack_per_band[k][0:number_of_identified_images, :, :]
    return (data_shape, geotransform, list_with_arrays_stack_per_band)



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
        bundle  = Bundle(image_path)
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
        medians[band] = numpy.median(my_array[:,band,:,:], axis=0)
    return medians
def cloud_mask_array(image_difference_array, threshold=30000, filter_size=13, morphing_size=0):
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
def shadow_mask_array(image_difference_array, threshold=-5500, filter_size=13, morphing_size=0):
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
    sum_of_bands_array = numpy.sum(image_array,axis = 0) == 0
    numpy.putmask(mask_array, sum_of_bands_array, outside_value)
    return mask_array
def mask_clouds_and_shadows(re_raster_metadata, image_array, image_array_difference, data_shape_reference, solar_zenith, solar_azimuth, folder, geotransform):
    '''
    This function use calculate_cloud_shadow in preprocessing.masking.py
    '''
    clouds =  filter_median((numpy.sum(image_array_difference, axis=0) > 30000).astype(numpy.int), 13)
    shadows =  filter_median((numpy.sum(image_array_difference[3:, :, :], axis=0) < -5500).astype(numpy.int), 13)
    if GENERALIZE:
        clouds = morph_dilation(clouds, MORPHING_SIZE)
        shadows = morph_dilation(shadows, MORPHING_SIZE)
    image_array_difference = None
    resolution = geotransform[1]
    inbetween = calculate_cloud_shadow(clouds, shadows, solar_zenith, solar_azimuth, resolution)
    image_mask_array = numpy.zeros([data_shape_reference[1], data_shape_reference[0]])
    image_mask_array = morphing(image_mask_array, image_array, inbetween, clouds)
    image_mask_path = folder + '/mask_reference.tif'
    options_to_create = new_options_for_create_raster_from_reference(re_raster_metadata, raster.CREATE_WITH_NUMBER_OF_BANDS, 1, {})
    #TODO: CREATE WITH XOFFSET, YOFFSET?? IS IT NECESSARY?? GO TO OLD MADMEX
    create_raster_tiff_from_reference(re_raster_metadata, image_mask_path, image_mask_array, options_to_create)
    return image_mask_path
