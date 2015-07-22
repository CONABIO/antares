'''
Created on 15/07/2015

@author: erickpalacios
'''
from madmex.mapper.bundle.spot5 import Bundle as Bundle_spot5
import madmex.mapper.sensor.spot5 as spot5
import gdal
from madmex import LOGGER
import osr
import numpy as np
from madmex.preprocessing.base import calculate_rad_ref
from datetime import datetime
from madmex.mapper.data import raster
from madmex.util import create_directory_path
import re

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
    def preprocessing(self):
        LOGGER.info("Start folder: %s" % self.path)
        LOGGER.info('folder correctly identified')
        self.get_raster_properties()
        LOGGER.info('raster properties successfully extracted')
        self.get_sensor()
        LOGGER.info('finished extracting metadata of sensor')
        self.calculate_toa()
        LOGGER.info('finished toa calculated')
        self.export()
        LOGGER.info('finished export')
        LOGGER.info('finished DN to TOA')    
    def get_raster_properties(self):
        self.get_raster()
        #LOGGER.debug('data_shape: %s' % self.get_raster().get_attribute(raster.DATA_SHAPE))
        #LOGGER.debug('gdal.GetMetadata(): %s' % self.get_raster().get_attribute(raster.METADATA_FILE))
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        self.image_band_order = self.get_raster().get_attribute(raster.METADATA_FILE)['TIFFTAG_IMAGEDESCRIPTION'].split(" ")[:self.number_of_bands]
        self.data_array = self.get_raster().data_file.ReadAsArray()
        gcps = self.get_raster().data_file.GetGCPs()
        self.geotransform = gdal.GCPsToGeoTransform(gcps)
        #LOGGER.debug('geotransform: %s' % self.geotransform)
        #LOGGER.debug('footprint: %s' % self.get_raster().get_attribute(raster.FOOTPRINT))
        self.get_raster().close()
    def get_raster(self):
        return Bundle_spot5.get_raster(self)
    def get_sensor(self):
        return Bundle_spot5.get_sensor(self)
    def calculate_toa(self):
        self.get_sensor()
        LOGGER.debug('sun_elevation: %s' % self.get_sensor().get_attribute(spot5.SUN_ELEVATION))
        LOGGER.debug('band display order: %s' % self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)) 
        LOGGER.debug('band index: %s' % self.image_band_order)
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(int(self.get_sensor().get_attribute(spot5.HORIZONTAL_CS_CODE).replace("epsg:", "")))
        LOGGER.debug('projection: %s' % self.srs.ExportToWkt())   
        sun_elevation = np.deg2rad(float(self.get_sensor().get_attribute(spot5.SUN_ELEVATION)))
        gain = map(float, self.get_sensor().get_attribute(spot5.PHYSICAL_GAIN))
        offset = [0] * len(gain)
        metadata_band_order = self.get_sensor().get_attribute(spot5.BAND_DESCRIPTION)
        self.data_array[map(lambda x: self.image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = self.sensor.get_attribute(spot5.ACQUISITION_DATE)
        imaging_date = str(datetime.date(imaging_date)) #to remove 00:00:00
        self.toa = calculate_rad_ref(self.data_array, gain, offset, imaging_date, sun_elevation)
    def export(self):
        #outname = re.sub(r'.TIF', '', self.file_dictionary[self.IMAGE]) + '_TOA.tif'    
        outname = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea11/spot/SinNubes/resultados2'
        create_directory_path(outname)
        outname+= '/toa_res.tif'
        LOGGER.info('Results of folder %s is %s' % (self.path, outname))
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], gdal.GDT_Float32, self.geotransform, self.srs.ExportToWkt())
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None
