'''
Created on 15/07/2015

@author: erickpalacios
'''
#from __future__ import unicode_literals

from datetime import datetime
import os
import re
import gdal
import osr
from madmex import LOGGER
from madmex.mapper.bundle.spot5 import Bundle as Bundle_spot5
from madmex.mapper.data import raster
import madmex.mapper.sensor.spot5 as spot5
from madmex.preprocessing.base import calculate_rad_toa_spot5
from madmex.util import create_directory_path
import numpy as np

class Bundle(Bundle_spot5):
    def __init__(self, path):
        super(Bundle, self).__init__(path)
        self.FORMAT = 'GTiff'
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
    def preprocessing(self):
        LOGGER.info('folder correctly identified')
        LOGGER.info("Starting DN to TOA")
        LOGGER.info("Start folder: %s" % self.path)
        LOGGER.info('calculating TOA')
        self.calculate_toa()
        LOGGER.info('finished TOA')
        LOGGER.info('exporting to tif')
        self.export()
        LOGGER.info('finished export')
        LOGGER.info('finished DN to TOA')    
    def get_raster(self):
        return Bundle_spot5.get_raster(self)
    def get_sensor(self):
        return Bundle_spot5.get_sensor(self)
    def calculate_toa(self):
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        image_band_order = self.get_raster().get_attribute(raster.METADATA_FILE)['TIFFTAG_IMAGEDESCRIPTION'].split(" ")[:self.number_of_bands]
        LOGGER.debug('sun_elevation: %s' % self.get_sensor().get_attribute(spot5.SUN_ELEVATION))
        LOGGER.debug('band metadata order: %s' % self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)) 
        LOGGER.debug('band image order: %s' % image_band_order)
        self.projection = osr.SpatialReference()
        self.projection.ImportFromEPSG(int(self.get_sensor().get_attribute(spot5.HORIZONTAL_CS_CODE).replace("epsg:", "")))
        LOGGER.debug('projection: %s' % self.projection.ExportToWkt())   
        sun_elevation = np.deg2rad(float(self.get_sensor().get_attribute(spot5.SUN_ELEVATION)))
        gain = map(float, self.get_sensor().get_attribute(spot5.PHYSICAL_GAIN))
        offset = [0] * len(gain)
        metadata_band_order = self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)
        data_array = self.get_raster().read_data_file_as_array()[map(lambda x: image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = str(datetime.date(self.sensor.get_attribute(spot5.ACQUISITION_DATE))) #to remove 00:00:00
        self.toa = calculate_rad_toa_spot5(data_array, gain, offset, imaging_date, sun_elevation)   
    def export(self):
        #outname = re.sub(r'.TIF', '', self.file_dictionary[self.IMAGE]) + '_TOA.tif'    
        outname = os.path.join(os.path.expanduser('~'), 'SinNubes/resultados')
        create_directory_path(outname)
        outname+= '/toa_res.tif'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], gdal.GDT_Float32, self.get_raster().gcps_to_geotransform(), self.projection.ExportToWkt())
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None
