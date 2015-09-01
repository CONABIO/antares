#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 15/07/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

from datetime import datetime
import os
import re

import osr
import madmex.mapper.sensor.spot5 as spot5

from madmex import LOGGER
from madmex.mapper.bundle.spot5 import Bundle as Bundle_spot5
from madmex.mapper.data import raster
from madmex.preprocessing.base import calculate_rad_toa_spot5

_IMAGE = r'IMAGERY.TIF$'
_METADATA = r'METADATA.DIM$'
_PREVIEW = r'PREVIEW.JPG'
_ICON = r'ICON.JPG'
_STYLE = r'STYLE.XSL'
_OTHER = r'TN_01.TIF'
_FORMAT = 'GTiff'

class Bundle(Bundle_spot5):
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
                        _ICON:None,
                        _STYLE:None,
                        _OTHER:None, 
                           }
        self._look_for_files()
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
        return Bundle_spot5.get_raster(self)
    def get_sensor(self):
        '''
        Returns the sensor of the underlying bundle.
        '''
        return Bundle_spot5.get_sensor(self)
    
    def get_spot_dictionary(self):
        '''
        Returns the dictionary of regular expressions and file names found in
        the given path.
        '''
        return self.file_dictionary
    def get_metadata_file(self):
        '''
        Returns the regular expression to identify the metadata file for Spot 5.
        '''
        return _METADATA
    def get_image_file(self):
        '''
        Returns the regular expression to identify the image file for Spot 5.
        '''
        return _IMAGE
    def get_format_file(self):
        '''
        Returns the format in which Spot 5 images are configured.
        '''
        return _FORMAT
    def get_sensor_module(self):
        return spot5
    def calculate_toa(self):
        '''
        Calculates the top of atmosphere for the image that is object represents.
        '''
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        metadata_band_order = self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)
        image_band_order = self.get_raster().get_attribute(raster.METADATA_FILE)['TIFFTAG_IMAGEDESCRIPTION'].split(" ")[:self.number_of_bands]
        LOGGER.debug('band metadata order: %s' % self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)) 
        LOGGER.debug('band image order: %s' % image_band_order)
        self.geotransform_from_gcps = self.get_raster().gcps_to_geotransform()
        LOGGER.info('reordering data_array')
        data_array = self.get_raster().read_data_file_as_array()[map(lambda x: image_band_order.index(x), metadata_band_order), :, :]
        self.projection = osr.SpatialReference()
        self.projection.ImportFromEPSG(int(self.get_sensor().get_attribute(spot5.HORIZONTAL_CS_CODE).replace("epsg:", "")))
        LOGGER.debug('projection: %s' % self.projection.ExportToWkt())  
        sun_elevation = float(self.get_sensor().get_attribute(spot5.SUN_ELEVATION))
        LOGGER.debug('sun_elevation: %s' % sun_elevation) 
        gain = map(float, self.get_sensor().get_attribute(spot5.PHYSICAL_GAIN))
        offset = [0] * len(gain)
        hrg = self.get_sensor().get_attribute(spot5.HRG)
        LOGGER.debug('HRG type: %s' % hrg)
        imaging_date = datetime.date(self.sensor.get_attribute(spot5.ACQUISITION_DATE))
        self.toa = calculate_rad_toa_spot5(data_array, gain, offset, imaging_date, sun_elevation, hrg, self.number_of_bands)   
    def export(self):
        '''
        Persists the processed image into a file.
        '''
        outname = re.sub(r'.TIF', '', self.file_dictionary[self.get_image_file()]) + '_TOA.tif'    
        LOGGER.info('Result of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], self.geotransform_from_gcps, self.projection.ExportToWkt())
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None

if __name__ == '__main__':
    folder ='/Users/erickpalacios/Documents/CONABIO/Tareas/4_RediseñoMadmex/2_Preprocesamiento/Tarea11/spot/SinNubes/E55582961409182J1A00001/SCENE01'
    bundle = Bundle(folder)
    bundle.preprocessing()
    