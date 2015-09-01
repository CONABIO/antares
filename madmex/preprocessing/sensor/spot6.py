'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import re
import numpy
from madmex import LOGGER
from madmex.mapper.bundle.spot6 import Bundle as Bundle_spot6
from madmex.mapper.data import raster
import madmex.mapper.sensor.spot6 as spot6
from madmex.preprocessing.base import calculate_rad_toa_spot6
from madmex.util import create_directory_path
import os

class Bundle(Bundle_spot6):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
    def preprocessing(self):
        '''
        Calculates top of atmosphere for the given image, and the persists the
        result into a file.
        '''
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
        '''
        Returns the raster of the underlying bundle.
        '''
        return Bundle_spot6.get_raster(self)
    def get_sensor(self):
        '''
        Returns the sensor of the underlying bundle.
        '''
        return Bundle_spot6.get_sensor(self)
    def calculate_toa(self):
        '''
        Calculates the top of atmosphere for the image that is object represents.
        '''
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        metadata_band_order = self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)
        image_band_order = self.get_sensor().get_attribute(spot6.BAND_INDEX)
        LOGGER.debug('band metadata order: %s' % self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)) 
        LOGGER.debug('band image order: %s' % self.get_sensor().get_attribute(spot6.BAND_INDEX)) 
        band_order_reference = [u'B0', u'B1', u'B2', u'B3']
        if image_band_order == metadata_band_order and metadata_band_order != band_order_reference:
            band_solar_irradiance = self.get_sensor().get_attribute(spot6.BAND_SOLAR_IRRADIANCE_VALUE)
            band_solar_irradiance = list(numpy.array(band_solar_irradiance)[map(lambda x: metadata_band_order.index(x), band_order_reference)])
            LOGGER.info('band_solar_irradiance: %s' % band_solar_irradiance)
            gain = map(float, self.get_sensor().get_attribute(spot6.PHYSICAL_GAIN))
            offset = map(float, self.get_sensor().get_attribute(spot6.PHYSICAL_BIAS))
            gain = list(numpy.array(gain)[map(lambda x: metadata_band_order.index(x), band_order_reference)])
            offset = list(numpy.array(offset)[map(lambda x: metadata_band_order.index(x), band_order_reference)]) 
            LOGGER.info('gain: %s' % gain)
            LOGGER.info('offset: %s' % offset)         
            LOGGER.info('reading data_array')
            data_array = self.get_raster().read_data_file_as_array()
        sun_elevation = numpy.deg2rad(float(numpy.median(self.get_sensor().get_attribute(spot6.SUN_ELEVATION))))
        LOGGER.debug('sun_elevation: %s' % sun_elevation)
        imaging_date = datetime.date(self.sensor.get_attribute(spot6.ACQUISITION_DATE))
        self.toa = calculate_rad_toa_spot6(data_array, gain, offset, imaging_date, sun_elevation, band_solar_irradiance, self.number_of_bands)
    def export(self):
        '''
        Persists the processed image into a file.
        '''
        outname = re.sub(r'.JP2', '', self.file_dictionary[self.get_image_file()]) + '_TOA.TIF'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], self.get_raster().get_attribute(raster.GEOTRANSFORM), self.get_raster().get_attribute(raster.PROJECTION))
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None
