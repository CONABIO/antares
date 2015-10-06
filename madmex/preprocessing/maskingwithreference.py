'''
Created on 16/07/2015

@author: erickpalacios
'''
from madmex.mapper.sensor import rapideye
from datetime import datetime
from madmex import LOGGER
import numpy
from madmex.mapper.data import raster
from madmex.preprocessing.base import filter_median, morph_dilation, calculate_cloud_shadow, morphing
from madmex.persistence.driver import find_datasets

GENERALIZE = False
MORPHING_SIZE = 10
#TODO: this module is lacking of landmasking....see rapideyeclouds.py of madmex_old
def masking(re_object):
    tile_id =  re_object.get_sensor().get_attribute(rapideye.TILE_ID)
    image_array = re_object.get_raster().read_data_file_as_array()
    folder = re_object.get_output_directory()
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/CloudMasking/RE_1649125/1649125_2014-01-23_RE4_3A_301519'
    data_shape_reference, geotransform_reference, projection_reference, image_array_difference = reference_for_tile(folder, tile_id, image_array)
    solar_zenith = re_object.get_sensor().get_attribute(rapideye.SOLAR_ZENITH)
    solar_azimuth = re_object.get_sensor().get_attribute(rapideye.SOLAR_AZIMUTH)
    image_mask_path = mask_clouds_and_shadows(image_array, image_array_difference, data_shape_reference, solar_zenith, solar_azimuth, folder, geotransform_reference, projection_reference)
    return image_mask_path
def reference_for_tile(folder, tile_id, image_array):
    cloud_cover = 100
    sensor_id = 1
    product_id = 2
    start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
    images_references_paths = find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id)
    LOGGER.info("Number of acquired images: %d" % len(images_references_paths))
    print("Number of acquired images: %d" % len(images_references_paths))
    return get_image_array_difference(folder, images_references_paths, image_array)
def get_image_array_difference(folder, images_references_paths, image_array):
    data_shape, geotransform, projection, band_1_list, band_2_list, band_3_list, band_4_list, band_5_list = get_arrays(images_references_paths)
    band_1_stack = stack_images_per_band(band_1_list, len(band_1_list), data_shape)
    band_2_stack = stack_images_per_band(band_2_list, len(band_2_list), data_shape)
    band_3_stack = stack_images_per_band(band_3_list, len(band_3_list), data_shape)
    band_4_stack = stack_images_per_band(band_4_list, len(band_4_list), data_shape)
    band_5_stack = stack_images_per_band(band_5_list, len(band_5_list), data_shape)
    band_medians = numpy.zeros([data_shape[2], data_shape[1], data_shape[0]])
    LOGGER.debug("Get medians for band 1")
    band_medians[0, :, :] = numpy.median(band_1_stack, axis = 0)
    LOGGER.debug("Get medians for band 2")
    band_medians[1, :, :] = numpy.median(band_2_stack, axis=0)
    LOGGER.debug("Get medians for band 3")
    band_medians[2, :, :] = numpy.median(band_3_stack, axis=0)
    LOGGER.debug("Get medians for band 4")
    band_medians[3, :, :] = numpy.median(band_4_stack, axis=0)
    LOGGER.debug("Get medians for band 5")
    band_medians[4, :, :] = numpy.median(band_5_stack, axis=0)
    band_1_list, band_2_list, band_3_list, band_4_list, band_5_list = None, None, None, None, None
    #TODO: Is not necessary create a tif image, we only need the array and datashape, geotransform and projection for the next processes
    image_reference_class = raster.Data('', '')
    image_reference_path = folder + '/re_reference.tif'
    width, height, bands = data_shape
    image_reference_result = image_reference_class.create_from_reference(image_reference_path, width, height, bands, geotransform, projection)
    image_reference_class.write_raster(image_reference_result, band_medians)
    LOGGER.info("RE reference image: %s" % image_reference_path)
    LOGGER.info('Calculating difference between RapidEye image and reference')
    image_array_difference = numpy.zeros([data_shape[2], data_shape[1], data_shape[0]])
    for b in range(data_shape[2]):
        image_array_difference[b, :, :] = image_array[b, :, :] - band_medians[b, :, :]
    image_array = None
    band_medians = None     
    return data_shape, geotransform, projection, image_array_difference
def get_arrays(images_references_paths):
    '''
    Check consistency of folders and get arrays for every image
    '''
    from madmex.mapper.bundle.rapideye import Bundle
    band_1_list = list()
    band_2_list = list()
    band_3_list = list()
    band_4_list = list()
    band_5_list = list()
    for image_path in images_references_paths:
        bundle  = Bundle(image_path)
        first = False
        if bundle.can_identify():
            array = bundle.get_raster().read_data_file_as_array().astype(numpy.float)
            band_1_list.append(array[0, :, :])
            band_2_list.append(array[1, :, :])
            band_3_list.append(array[2, :, :])
            band_4_list.append(array[3, :, :])
            band_5_list.append(array[4, :, :])
            if not first:
                data_shape = bundle.get_raster().get_attribute(raster.DATA_SHAPE)
                geotransform = bundle.get_raster().get_attribute(raster.GEOTRANSFORM) 
                projection = bundle.get_raster().get_attribute(raster.PROJECTION)
                first = True
    return (data_shape, geotransform, projection, band_1_list, band_2_list, band_3_list, band_4_list, band_5_list)
def stack_images_per_band(band_list, length, data_shape):
    band = numpy.zeros([length, data_shape[1], data_shape[0]])
    for b in range(0, length):
        band[b, :, :] = band_list[b]
    return band
def mask_clouds_and_shadows(image_array, image_array_difference, data_shape_reference, solar_zenith, solar_azimuth, folder, geotransform, projection):
    clouds =  filter_median((numpy.sum(image_array_difference, axis=0) > 30000).astype(numpy.int), 13)
    shadows = filter_median((numpy.sum(image_array_difference[3:, :, :], axis=0) < -5500).astype(numpy.int), 13)
    if GENERALIZE:
        clouds = morph_dilation(clouds, MORPHING_SIZE)
        shadows = morph_dilation(shadows, MORPHING_SIZE)
    image_array_difference = None
    resolution = geotransform[1]
    inbetween = calculate_cloud_shadow(clouds, shadows, solar_zenith, solar_azimuth, resolution)
    image_mask_array = numpy.zeros([data_shape_reference[1], data_shape_reference[0]])
    image_mask_array = morphing(image_mask_array, image_array, inbetween, clouds)
    image_mask_path = folder + '/mask.tif'
    image_raster_class = raster.Data('', '')
    height, width = image_mask_array.shape
    #TODO: CREATE WITH XOFFSET, YOFFSET?? IS IT NECESSARY?? GO TO OLD MADMEX
    image_mask_result = image_raster_class.create_from_reference(image_mask_path, width, height, 1, geotransform, projection)
    image_raster_class.write_array(image_mask_result, image_mask_array)
    return image_mask_path

