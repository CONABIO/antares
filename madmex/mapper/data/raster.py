'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import logging

import gdal, gdalconst
import ogr, osr

from madmex.mapper.base import BaseData


gdal.AllRegister()
gdal.UseExceptions()

LOGGER = logging.getLogger(__name__)

class Data(BaseData):
    
    def __init__(self, image_path, gdal_format):
        
        self.image_path = image_path
        try:
            self.driver = gdal.GetDriverByName(gdal_format)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s' % gdal_format)
    def open_file(self, mode = gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal.
        '''
        try:
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            print 'Unable to open raster file %s' % self.image_path
    def extract_metadata(self, data):
        '''
        Extract metadata from the raster image file using gdal functions.
        '''
        self.projection = data.GetProjection()
        self.geotransform = data.GetGeoTransform()
        self.dataShape = (data.RasterXSize, data.RasterYSize, data.RasterCount)
        self.footprint = self.get_footprint()
    def get_footprint(self):
        '''
        Returns the extent of the raster image.
        '''
        ring = ogr.Geometry(ogr.wkbLinearRing) 
        ring.AddPoint_2D(self.geotransform[0], self.geotransform[3]) 
        ring.AddPoint_2D(self.geotransform[0] + self.geotransform[1] * self.dataShape[0], self.geotransform[3])  
        ring.AddPoint_2D(self.geotransform[0] + self.geotransform[1] * self.dataShape[0], self.geotransform[3] + self.geotransform[5] * self.dataShape[1])  
        ring.AddPoint_2D(self.geotransform[0], self.geotransform[3] + self.geotransform[5] * self.dataShape[1]) 
        ring.CloseRings()
        spacial_reference = osr.SpatialReference()
        spacial_reference.ImportFromWkt(self.projection)
        return self._footprint_helper(ring, spacial_reference)