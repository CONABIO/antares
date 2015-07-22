'''
Created on 15/07/2015

@author: erickpalacios
'''
#from __future__ import unicode_literals
#from madmex.preprocessing.bundle import spot6
from madmex.mapper.bundle.spot6 import Bundle as Bundle_spot6
import madmex.mapper.sensor.spot6 as spot6
import gdal, gdalconst
from madmex import LOGGER
import osr
import numpy as np
from madmex.preprocessing.base import calculate_rad_ref
from datetime import datetime
from madmex.mapper.data import raster
import numpy

def Spot6DN2TOA(indir):
    print "Start folder: ", indir
    bundle = Bundle(indir)
    if bundle.can_identify():
        print 'folder correctly identified'
        bundle.get_raster_properties()
        print 'raster properties successfully extracted'
        bundle.get_sensor()
        print 'finished extracting metadata of sensor'
        bundle.calculate_toa()
        print 'finished toa calculated'
        bundle.export()
        print 'finished export'
        print 'finished DN to TOA'
class Bundle(Bundle_spot6):
    def __init__(self, path):
        super(Bundle, self).__init__(path)
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
        #LOGGER.debug('data_shape: %s' %self.get_raster().get_attribute(raster.DATA_SHAPE))
        #LOGGER.debug('gdal.GetMetadata(): %s' % self.get_raster().get_attribute(raster.METADATA_FILE))
        self.number_of_bands = self.get_raster().get_attribute(raster.DATA_SHAPE)[2]
        self.data_array = self.get_raster().data_file.ReadAsArray()
        self.geotransform = self.get_raster().get_attribute(raster.GEO_TRANSFORM)
        self.projection = self.get_raster().get_attribute(raster.PROJECTION)
        #LOGGER.debug('geotransform: %s' % self.geotransform)
        #LOGGER.debug('projection: %s' % self.projection)
        #LOGGER.debug('footprint %s' % self.get_raster().get_attribute(raster.FOOTPRINT))
        self.get_raster().close()
    def get_raster(self):
        return Bundle_spot6.get_raster(self)
    def get_sensor(self):
        return Bundle_spot6.get_sensor(self)
    def calculate_toa(self):
        self.get_sensor()
        LOGGER.debug('sun_elevation: %s' % self.get_sensor().get_attribute(spot6.SUN_ELEVATION))
        LOGGER.debug('band display order: %s' % self.get_sensor().get_attribute(spot6.BAND_DISPLAY_ORDER)) 
        LOGGER.debug('band index: %s' % self.get_sensor().get_attribute(spot6.BAND_INDEX)) 
        sun_elevation = np.deg2rad(float(numpy.median(self.get_sensor().get_attribute(spot6.SUN_ELEVATION))))
        gain = map(float, self.sensor.get_attribute(spot6.PHYSICAL_GAIN))
        offset = map(float, self.sensor.get_attribute(spot6.PHYSICAL_BIAS))
        metadata_band_order = self.sensor.get_attribute(spot6.BAND_DISPLAY_ORDER)
        image_band_order = self.get_sensor().get_attribute(spot6.BAND_INDEX)
        self.data_array[map(lambda x: image_band_order.index(x), metadata_band_order), :, :]
        imaging_date = self.sensor.get_attribute(spot6.ACQUISITION_DATE)
        imaging_date = str(datetime.date(imaging_date)) #to remove 00:00:00
        self.toa = calculate_rad_ref(self.data_array, gain, offset, imaging_date, sun_elevation)
    def export(self):
        outname = self.get_output_directory() + '/toa_res'
        outname = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea11/spot6/IMG_SPOT6_MS_001_A' + '/toa_res'
        data_file = self.get_raster().create_from_reference(outname, self.toa.shape[2], self.toa.shape[1], self.toa.shape[0], gdal.GDT_Float32, self.geotransform, self.projection)
        self.get_raster().write_raster(self.number_of_bands, data_file, self.toa) 
        data_file = None


if __name__ == '__main__':
    
    #folder = '/Volumes/Imagenes_originales/SPOT6/E6554293150227_1751231K3A0U12N17L1003001/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A'
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea11/spot6/IMG_SPOT6_MS_001_A'
    Spot6DN2TOA(folder)