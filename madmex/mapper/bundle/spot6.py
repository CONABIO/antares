'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import re

import numpy

from madmex import LOGGER
from madmex.mapper.bundle._spot import SpotBaseBundle
import madmex.mapper.data.raster as raster
import madmex.mapper.sensor.spot6 as spot6
from madmex.preprocessing.topofatmosphere import calculate_rad_toa_spot6


_IMAGE = r'IMG.*\.JP2$'
_METADATA = r'DIM.*\.XML$'
_PREVIEW = r'PREVIEW.*\.JPG$'
_ICON = r'ICON.*\.JPG$'
FORMAT = 'JP2OpenJPEG'


class Bundle(SpotBaseBundle):
    '''            
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.file_dictionary = {
                        _IMAGE:None,
                        _METADATA:None,
                        _PREVIEW:None,
                        _ICON:None
                           }
        self._look_for_files()        
    def get_spot_dictionary(self):
        '''
        Returns the dictionary of regular expressions and file names found in
        the given path.
        '''
        return self.file_dictionary

    def get_metadata_file(self):
        return _METADATA
    def get_image_file(self):
        return _IMAGE
    def get_format_file(self):
        return FORMAT
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'Spot6'
    def get_sensor_module(self):
        return spot6
    def calculate_top_of_atmosphere_spot6(self):
        '''
        Calculates the top of atmosphere for the image that is object represents.
        '''
        LOGGER.info('folder correctly identified')
        LOGGER.info("Starting DN to TOA")
        LOGGER.info("Start folder: %s" % self.path)
        LOGGER.info('calculating TOA')
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
        LOGGER.info('finished TOA')
        LOGGER.info('exporting to tif')
        outname = re.sub(r'.JP2', '', self.file_dictionary[self.get_image_file()]) + '_TOA.TIF'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], self.get_raster().get_attribute(raster.GEOTRANSFORM), self.get_raster().get_attribute(raster.PROJECTION))
        self.get_raster().write_raster(data_file, self.toa) 
        data_file = None
        LOGGER.info('finished export')
        LOGGER.info('finished DN to TOA') 
    def preprocess(self):
        self.calculate_top_of_atmosphere_spot6()
        

if __name__ == '__main__':
    folder = '/Volumes/Imagenes_originales/SPOT6/E6554293150227_1751231K3A0U12N17L1003001/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A'
    bundle = Bundle(folder)
    print bundle.get_files()
    print bundle.can_identify()
    print bundle.get_output_directory()
    print bundle.get_sensor_module().SENSOR
    print bundle.get_output_directory()
    print bundle.get_raster().get_attribute(raster.FOOTPRINT)