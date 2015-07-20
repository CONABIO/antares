
'''
Created on 16/07/2015

@author: erickpalacios
'''
#from __future__ import unicode_literals
from madmex.mapper.bundle.spot5 import Bundle as Bundle_spot5
import madmex.mapper.sensor.spot5 as spot5
import gdal, gdalconst
from madmex import LOGGER
import osr
import numpy as np
from madmex.preprocessing.base import calculate_rad_ref
from datetime import datetime
from madmex.mapper.data import raster

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
    def get_raster_properties(self):
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        self.image_band_order = self.get_raster().get_attribute(raster.METADATA_FILE)['TIFFTAG_IMAGEDESCRIPTION'].split(" ")[:self.number_of_bands]
        self.data_array = self.get_raster().data_file.ReadAsArray()
        gcps = self.get_raster().data_file.GetGCPs()
        self.geotransform = gdal.GCPsToGeoTransform(gcps)
        self.get_raster().close()
    def get_raster(self):
        return Bundle_spot5.get_raster(self)
    def get_sensor(self):
        return Bundle_spot5.get_sensor(self)
    def calculate_toa(self):
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(int(self.get_sensor().get_attribute(spot5.HORIZONTAL_CS_CODE).replace("epsg:", "")))     
        sun_elevation = np.deg2rad(float(self.get_sensor().get_attribute(spot5.SUN_ELEVATION)))
        gain = map(float, self.sensor.get_attribute(spot5.PHYSICAL_GAIN))
        offset = [0] * len(gain)
        metadata_band_order = self.sensor.get_attribute(spot5.BAND_DESCRIPTION)
        self.data_array[map(lambda x: self.image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = self.sensor.get_attribute(spot5.ACQUISITION_DATE)
        imaging_date = str(datetime.date(imaging_date))
        self.toa = calculate_rad_ref(self.data_array, gain, offset, imaging_date, sun_elevation)
    def export(self):
        outname = self.get_output_directory() + '/toa_res'
        outname = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea11/spot5/E55542961503031J1A02002/SCENE01' + '/toa_res'
        data_empty = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], gdal.GDT_Float32, self.geotransform, self.srs.ExportToWkt())
        self.get_raster().write_raster(self.number_of_bands, data_empty, self.toa) 
        data_empty = None

