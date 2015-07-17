'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import logging

import gdal, gdalconst
import ogr, osr

from madmex.mapper.base import BaseData, _get_attribute


gdal.AllRegister()
gdal.UseExceptions()

LOGGER = logging.getLogger(__name__)

class Data(BaseData):
    '''
    This is a class to handle raster data. It might be convenient to use
    inheritance from this class to represent each type of image file, right now
    it is only a helper class to open raster files.
    '''
    def __init__(self, image_path, gdal_format):
        '''
        Constructor
        '''
        super(Data, self).__init__()
        self.image_path = image_path
        try:
            self.driver = gdal.GetDriverByName(gdal_format)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s' % gdal_format)
        self.data_file = self._open_file()
        self.metadata = {}
        self._extract_metadata()
    def _open_file(self, mode=gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal.
        '''
        try:
            LOGGER.debug('Open raster file: %s', self.image_path)
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
    def _extract_metadata(self):
        '''
        Extract metadata from the raster image file using gdal functions.
        '''
        self.metadata['projection'] = self.data_file.GetProjection()
        self.metadata['geotransform'] = self.data_file.GetGeoTransform()
        self.metadata['data_shape'] = (
            self.data_file.RasterXSize,
            self.data_file.RasterYSize,
            self.data_file.RasterCount
            )
        self.metadata['footprint'] = self._get_footprint()
    def _get_footprint(self):
        '''
        Returns the extent of the raster image.
        '''
        ring = ogr.Geometry(ogr.wkbLinearRing)
        geotransform = self.get_attribute('geotransform')
        data_shape = self.get_attribute('data_shape')
        ring.AddPoint_2D(geotransform[0], geotransform[3])
        ring.AddPoint_2D(geotransform[0] + geotransform[1] * data_shape[0], geotransform[3])
        ring.AddPoint_2D(
            geotransform[0] + geotransform[1] * data_shape[0],
            geotransform[3] + geotransform[5] * data_shape[1]
            )
        ring.AddPoint_2D(geotransform[0], geotransform[3] + geotransform[5] * data_shape[1])
        ring.CloseRings()
        spacial_reference = osr.SpatialReference()
        spacial_reference.ImportFromWkt(self.get_attribute('projection'))
        return self._footprint_helper(ring, spacial_reference)
    def get_attribute(self, key):
        '''
        Returns the attribute that is found with the given key in the metadata
        dictionary.
        '''
        return _get_attribute([key], self.metadata)
