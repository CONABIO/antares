'''
Created on Nov 4, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import logging

import gdal
from osgeo._gdalconst import GA_ReadOnly
import osr
from lib2to3.pgen2.driver import Driver
from madmex.persistence import driver


GTIFF = 'GTiff'

LOGGER = logging.getLogger(__name__)

def get_width(image_path):
    '''
    This function will query the width from raster and return it.
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    width = dataset.RasterXSize
    return width   
def get_height(image_path):
    '''
    This function will query the height from a raster and return it.
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    height = dataset.RasterXSize
    return height   
def get_bands(image_path):
    '''
    This function will query the number of bands from a raster return it.
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    bands = dataset.RasterCount
    return bands
def get_driver(image_path):
    '''
    This function will return the driver from a given raster file.
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    driver = _get_driver(dataset)
    dataset = None
    return driver
def _get_driver(dataset):
    '''
    Helper function to get the geotransform from an already open dataset.
    '''
    driver = dataset.GetDriver().ShortName
    return driver
def get_projection(image_path):
    '''
    This function will query the projection from a file and return it.
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    projection = _get_projection(dataset)
    dataset = None
    return projection
def _get_projection(dataset):
    '''
    Helper function to get the projection from an already open dataset.
    '''
    projection = osr.SpatialReference()
    projection.ImportFromWkt(dataset.GetProjectionRef())
    return projection
def get_geotransform(image_path):
    '''
    This function will query the geotransform from a file and return it. The 
    geotransform object is a list of six numbers that represent:
    top left x
    0
    top left y
    0
    w-e pixel resolution
    n-s pixel resolution (negative value)
    '''
    dataset = gdal.Open(image_path, GA_ReadOnly)
    geotransform = _get_geotransform(dataset)
    dataset = None
    return geotransform
def _get_geotransform(dataset):
    '''
    Helper function to get the geotransform from an already open dataset.
    '''
    geotransform = dataset.GetGeoTransform()
    return geotransform
def create_raster_from_reference(image_path, array, reference_path, data_type=gdal.GDT_Float32):
    '''
    This function creates a raster image with the info in the given array. It
    uses the reference path to extract the geotransform and the projection from
    it.
    '''
    dataset = gdal.Open(reference_path, GA_ReadOnly)
    projection = _get_projection(dataset)
    geotransform =  _get_geotransform(dataset)
    driver_type = _get_driver(dataset)
    print projection
    print geotransform
    print driver_type
    dataset = None
    create_raster(image_path, array, geotransform, projection, driver_type, data_type)
def create_raster(image_path, array, geotransform=None, projection=None, driver_type=GTIFF, data_type=gdal.GDT_Float32):
    '''
    This method facilitates the creation of a raster image using gdal. By setting
    several attributes by default, it removes the overhead of creating images
    with no projection or geotransform. It can handle multiband or singleband
    images seamlessly, considering the dimensions of the array.
    '''
    shape = array.shape
    if not (len(shape) == 2 or len(shape) == 3):
        LOGGER.error('Trying to create a raster with an incorrect number of bands.')
    else:
        if len(shape) == 2:
            bands = 1
            width = shape[1]
            height = shape[0]
        else:
            bands = shape[0]   
            width = shape[2]
            height = shape[1]            
        data = gdal.GetDriverByName(str(GTIFF)).Create(image_path,
                                                       width,
                                                       height,
                                                       bands,
                                                       data_type)
        if geotransform:
            data.SetGeoTransform(geotransform)
        if projection:
            data.SetProjection(str(projection))
        if bands == 1:
            data.GetRasterBand(bands).WriteArray(array)
        else:
            for band in range(bands):
                data.GetRasterBand(band + 1).WriteArray(array[band, :, :])
        data.FlushCache()

        