'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
import logging
import gdal
import ogr
from madmex.mapper.base import BaseData


gdal.AllRegister()
ogr.UseExceptions()

LOGGER = logging.getLogger(__name__)

class Data(BaseData):
    '''
    This class represents a vector type file.
    '''
    def __init__(self, image_path, ogr_format):
        super(Data, self).__init__()
        self.image_path = image_path
        self.footprint = None
        self.layer = None
        try:
            self.driver = ogr.GetDriverByName(ogr_format)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s', ogr_format)
    def _open_file(self):
        '''
        Open the vector image file with ogr.
        '''
        try:
            return self.driver.Open(self.image_path, 0) # 0 means read-only. 1 means writeable.
        except Exception:
            LOGGER.error('Unable to open shape file: %s', self.image_path)
    def _extract_metadata(self, data):
        '''
        Extract metadata from the raster image file using gdal functions.
        '''
        self.layer = data.GetLayer()
        self.footprint = self._get_footprint()
    def _get_footprint(self):
        '''
        Returns the extent of the shape image.
        '''
        extent = self.layer.GetExtent()
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint_2D(extent[0], extent[2])
        ring.AddPoint_2D(extent[1], extent[2])
        ring.AddPoint_2D(extent[1], extent[3])
        ring.AddPoint_2D(extent[0], extent[3])
        ring.CloseRings()
        spacial_reference = self.layer.GetSpatialRef()
        return self._footprint_helper(ring, spacial_reference)
