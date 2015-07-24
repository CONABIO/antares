'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import os
import re
import logging
import gdal
import numpy

from madmex import LOGGER
from madmex.mapper.bundle.spot6 import Bundle as Bundle_spot6
from madmex.mapper.data import raster
import madmex.mapper.sensor.spot6 as spot6
from madmex.preprocessing.base import calculate_rad_toa_spot5,\
    calculate_rad_toa_spot6
from madmex.util import create_directory_path
import numpy as np

LOGGER = logging.getLogger(__name__)

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
    def calculate_toa(self):
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        metadata_band_order = self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)
        image_band_order = self.get_sensor().get_attribute(spot6.BAND_INDEX)
        LOGGER.debug('band metadata order: %s' % self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)) 
        LOGGER.debug('band image order: %s' % self.get_sensor().get_attribute(spot6.BAND_INDEX)) 
        LOGGER.info('reordering data_array')
        data_array = self.get_raster().read_data_file_as_array()[map(lambda x: image_band_order.index(x), metadata_band_order), :, :]
        sun_elevation = np.deg2rad(float(numpy.median(self.get_sensor().get_attribute(spot6.SUN_ELEVATION))))
        LOGGER.debug('sun_elevation: %s' % sun_elevation)
        gain = map(float, self.get_sensor().get_attribute(spot6.PHYSICAL_GAIN))
        offset = map(float, self.get_sensor().get_attribute(spot6.PHYSICAL_BIAS))
        imaging_date = str(datetime.date(self.sensor.get_attribute(spot6.ACQUISITION_DATE))) #to remove 00:00:00
        self.toa = calculate_rad_toa_spot6(data_array, gain, offset, imaging_date, sun_elevation, self.number_of_bands)
    def export(self):
        outname = os.path.join(os.path.expanduser('~'), 'Documents/CONABIO/Tareas/Tarea11/spot/SinNubes/resultados3')
        create_directory_path(outname)
        outname+= '/toa_res.tif'
        #outname = re.sub(r'.JP2', '', self.file_dictionary[self.IMAGE]) + '_TOA.TIF'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], self.get_raster().get_attribute(raster.GEOTRANSFORM), self.get_raster().get_attribute(raster.PROJECTION))
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None
if __name__ == '__main__':
    folder = '/Volumes/Imagenes_originales/SPOT6/E6554293150227_1751231K3A0U12N17L1003001/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A'
    bundle =Bundle(folder)
    bundle.preprocessing()