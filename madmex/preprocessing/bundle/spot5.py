'''
Created on 16/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
from madmex.mapper.bundle.spot5 import Bundle as Bundle_spot5
import madmex.mapper.sensor.spot5 as spot5
import gdal
from madmex import LOGGER
import osr
import numpy as np
from madmex.preprocessing.base import calculate_rad_ref

class Bundle(Bundle_spot5):
    def __init__(self, path):
        super(Bundle, self).__init__(path)
        self.FORMAT = "GTiff"
        self.IMAGE = r'IMAGERY.TIF$'
        self.METADATA = r'METADATA.DIM$'
        self.PREVIEW = r'PREVIEW.JPG'
        self.ICON = r'ICON.JPG'
        self.STYLE = r'STYLE.XSL'
        self.OTHER = r'TN_01.TIF'
        self.file_dictionary = {
                        self.IMAGE:None,
                        self.METADATA:None,
                        self.PREVIEW:None,
                        self.ICON:None,
                        self.STYLE:None,
                        self.OTHER:None, 
                           }
        self._look_for_files()        
    def get_sensor(self):
        Bundle_spot5.get_sensor(self)
    def calculate_toa(self):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(int(self.sensor.get_attribute(spot5.HORIZONTAL_CS_CODE).replace("epsg:", "")))     
        sun_elevation = np.deg2rad(float(self.sensor.get_attribute(spot5.SUN_ELEVATION)))
        gain = map(float, self.sensor.get_attribute(spot5.PHYSICAL_GAIN))
        offset = [0] * len(gain)
        metadata_band_order = self.sensor.get_attribute(spot5.BAND_DESCRIPTION)
        self.data_array[map(lambda x: self.image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = self.sensor.get_attribute(spot5.ACQUISITION_DATE)
        self.toa = calculate_rad_ref(self.data_array, gain, offset, imaging_date, sun_elevation)
        print self.get_output_directory()
    def export(self):
        #driver = gdal.GetDriverByName(self.FORMAT)
        print self.get_output_directory()

        
    def get_raster(self):
        data_file = self._open_file()
        self.image_band_order = data_file.GetMetadata()['TIFFTAG_IMAGEDESCRIPTION'].split(" ")[:4]
        self.data_array = data_file.ReadAsArray()
        gcps = data_file.GetGCPs()
        self.geotransform = gdal.GCPsToGeoTransform(gcps)
        data_file = None       
    def _open_file(self):
        '''
        Open the raster image file with gdal.
        '''
        try:
            LOGGER.debug('Open raster file: %s', self.file_dictionary[self.IMAGE])
            return gdal.Open(self.file_dictionary[self.IMAGE])
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
        