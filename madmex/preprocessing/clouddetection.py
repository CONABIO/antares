'''
Created on 16/07/2015

@author: erickpalacios
'''
from madmex.mapper.sensor import rapideye
from madmex.persistence.database.connection import SESSION_MAKER, RawProduct,\
    Information
from sqlalchemy import tuple_
from datetime import datetime
from madmex import LOGGER
import numpy
from madmex.mapper.data import raster
from madmex.preprocessing.base import filter_median, morph_dilation
# FMASK constants
FMASK_LAND = 0
FMASK_WATER = 1
FMASK_CLOUD_SHADOW = 2
FMASK_SNOW = 3
FMASK_CLOUD = 4
FMASK_OUTSIDE = 255
GENERALIZE = False
MORPHING_SIZE = 10
MORPHING_SIZES = [250,150,50] # pixel sizes of structure elements

#TODO: this module is lacking of landmasking....see rapideyeclouds.py of madmex_old
def masking(re_object):
    tile_id =  re_object.get_sensor().get_attribute(rapideye.TILE_ID)
    image_array = re_object.get_raster().read_data_file_as_array()
    folder = re_object.get_output_directory()
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    data_shape_reference, geotransform_reference, projection_reference, image_array_difference = reference_for_tile(folder, tile_id, image_array)
    image_mask_array = numpy.zeros([data_shape_reference[1], data_shape_reference[0]])
    numpy.putmask(image_mask_array, image_array[0, :, :] == 0, FMASK_OUTSIDE)
    solar_zenith = re_object.get_sensor().get_attribute(rapideye.SOLAR_ZENITH)
    solar_azimuth = re_object.get_sensor().get_attribute(rapideye.SOLAR_AZIMUTH)
    image_mask_path = mask_clouds(image_mask_array, image_array_difference, solar_zenith, solar_azimuth, folder, data_shape_reference, geotransform_reference, projection_reference)
    print image_mask_path
    return image_mask_path
def reference_for_tile(folder, tile_id, image_array):
    print 'reference'
    cloud_cover = 100
    sensor_id = 1
    product_id = 2
    start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
    images_references_paths = find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id)
    LOGGER.info("Number of acquired images: %d" % len(images_references_paths))
    print "Number of acquired images: %d" % len(images_references_paths)
    return get_image_array_difference(folder, images_references_paths, image_array)
def find_datasets(start_date, end_date, sensor_id, product_id, cloud_cover, tile_id):
    '''
    Given the parameters of the function find_datasets perform a sqlalchemy orm-query:
    Get the rows in DB that fulfill the condition in the orm-query 
    '''
    session = SESSION_MAKER()
    images_references_paths = session.query(RawProduct.path).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , RawProduct.pk_id == product_id, Information.cloud_percentage <= cloud_cover).all()
    images_references_paths = session.query(RawProduct.path).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , Information.cloud_percentage <= cloud_cover).all()
    #images_references_paths = session.query(RawProduct.path, Information.sensor).join(RawProduct.information).filter(tuple_(RawProduct.acquisition_date, RawProduct.acquisition_date).op('overlaps')(tuple_(start_date, end_date)) , RawProduct.product_type == product_id, Information.sensor == sensor_id, Information.cloud_percentage <= cloud_cover).all()
    session.close()
    return [tuples[0] for tuples in images_references_paths]
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
    print 'get'
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
    bundle_objects = list()
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
            print 'checking band1list'
            print numpy.unique(band_1_list[0])
            bundle_objects.append(bundle)
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
def mask_clouds(image_mask_array, image_array_difference, solar_zenith, solar_azimuth, folder, data_shape, geotransform, projection):
    clouds =  filter_median((numpy.sum(image_array_difference, axis=0) > 30000).astype(numpy.int), 13)
    shadows = filter_median((numpy.sum(image_array_difference[3:, :, :], axis=0) < -5500).astype(numpy.int), 13)
    if GENERALIZE:
        clouds = morph_dilation(clouds, MORPHING_SIZE)
        shadows = morph_dilation(shadows, MORPHING_SIZE)
    image_array_difference = None
    cloudrowcol = numpy.column_stack(numpy.where(clouds == 1))
    cloudheight = numpy.arange(1000, 3100, 100)
    cloudsproj = numpy.zeros([5000, 5000])   
    for h in cloudheight:    
        dist = h * numpy.tan(numpy.deg2rad(90 - solar_zenith))
        xdiff = dist * numpy.sin(numpy.deg2rad(360 - solar_azimuth))
        ydiff = dist * numpy.cos(numpy.deg2rad(360 - solar_azimuth))           
        rows = cloudrowcol[:, 0] + ydiff / 5
        cols = cloudrowcol[:, 1] + xdiff / 5
        rows = rows.astype(numpy.int)
        cols = cols.astype(numpy.int)                
        numpy.putmask(rows, rows < 0, 0)
        numpy.putmask(cols, cols < 0, 0)
        numpy.putmask(rows, rows >= 5000 - 1, 5000 - 1)
        numpy.putmask(cols, cols >= 5000 - 1, 5000 - 1)                
        cloudsproj[rows, cols] = 1                     
    inbetween = shadows * cloudsproj
    m = len(MORPHING_SIZES)
    for MORPHING_SIZE in MORPHING_SIZES:
        numpy.putmask(image_mask_array, morph_dilation(clouds, MORPHING_SIZE) == 1, FMASK_CLOUD*10+m)
        m = m-1
        numpy.putmask(image_mask_array, inbetween == 1, FMASK_CLOUD_SHADOW)
        numpy.putmask(image_mask_array, clouds == 1, FMASK_CLOUD)
    image_mask_path = folder + '/mask.tif'
    image_raster_class = raster.Data('', '')
    width, height, bands = data_shape
    #TODO: CREATE WITH XOFFSET, YOFFSET??
    image_mask_result = image_raster_class.create_from_reference(image_mask_path, width, height, 1, geotransform, projection)
    image_raster_class.write_array(image_mask_result, image_mask_array)
    return image_mask_path

