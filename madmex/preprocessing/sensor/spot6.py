'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import os
import re

import gdal
import numpy

from madmex import LOGGER
from madmex.mapper.bundle.spot6 import Bundle as Bundle_spot6
from madmex.mapper.data import raster
import madmex.mapper.sensor.spot6 as spot6
from madmex.preprocessing.base import calculate_rad_toa_spot5
from madmex.util import create_directory_path
import numpy as np


class Bundle(Bundle_spot6):
    def __init__(self, path):
        super(Bundle, self).__init__(path)
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
        return Bundle_spot6.get_raster(self)
    def get_sensor(self):
        return Bundle_spot6.get_sensor(self)
        self.get_sensor()
    def calculate_toa(self):
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        LOGGER.debug('band metadata order: %s' % self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)) 
        LOGGER.debug('sun_elevation: %s' % self.get_sensor().get_attribute(spot6.SUN_ELEVATION))
        LOGGER.debug('band image order: %s' % self.get_sensor().get_attribute(spot6.BAND_INDEX)) 
        sun_elevation = np.deg2rad(float(numpy.median(self.get_sensor().get_attribute(spot6.SUN_ELEVATION))))
        gain = map(float, self.sensor.get_attribute(spot6.PHYSICAL_GAIN))
        offset = map(float, self.sensor.get_attribute(spot6.PHYSICAL_BIAS))
        metadata_band_order = self.sensor.get_attribute(spot6.BAND_DISPLAY_ORDER)
        image_band_order = self.get_sensor().get_attribute(spot6.BAND_INDEX)
        data_array = self.get_raster().read_data_file_as_array()[map(lambda x: image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = str(datetime.date(self.sensor.get_attribute(spot6.ACQUISITION_DATE))) #to remove 00:00:00
        self.toa = calculate_rad_toa_spot5(data_array, gain, offset, imaging_date, sun_elevation)
    def export(self):
        #outname = re.sub(r'.JP2', '', self.file_dictionary[self.IMAGE]) + '_TOA.TIF'
        outname = os.path.join(os.path.expanduser('~'), 'SinNubes/resultados')
        create_directory_path(outname)
        outname+= '/toa_res.tif'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], gdal.GDT_Float32, self.get_raster().get_attribute(raster.GEO_TRANSFORM), self.get_raster().get_attribute(raster.PROJECTION))
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None
