

'''
Created on 10/06/2015

@author: erickpalacios
'''
#from __future__ import unicode_literals

import logging

import gdal, gdalconst
import ogr, osr

from madmex.mapper.base import BaseData, _get_attribute, put_in_dictionary


gdal.AllRegister()
gdal.UseExceptions()

LOGGER = logging.getLogger(__name__)

DRIVER_METADATA = ['driver_metadata'] 
METADATA_FILE = ['metadata_file']
PROJECTION = ['properties', 'projection']
GEO_TRANSFORM = ['properties', 'geotransform']
DATA_SHAPE = ['properties', 'data_shape']
FOOTPRINT = ['properties', 'footprint']

class Data(BaseData):
    '''
    This is a class to handle raster data. It might be convenient to use
    inheritance from this class to represent each type of image file, right now
    it is only a helper class to open raster files.
    '''
    def __init__(self, image_path, gdal_format):
        '''
        Constructor
        '''
        super(Data, self).__init__()
        self.image_path = image_path
        self.metadata ={}
        try:
            LOGGER.info("Extracting metadata of driver %s" % gdal_format)
            self.driver = gdal.GetDriverByName(gdal_format)
            LOGGER.info('driver: %s' % self.driver)
            LOGGER.info('Extracting metadata of driver %s' % gdal_format)
            self.metadata[DRIVER_METADATA[0]] = self.driver.GetMetadata()
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s' % gdal_format)
        self.data_file = self._open_file()
        if self.data_file != None:
            LOGGER.info("Extracting metadata of file %s" % self.data_file)
            LOGGER.info("Extracting metadata of file %s" % self.data_file)
            self.metadata[METADATA_FILE[0]] = self.data_file.GetMetadata()
        else:
            LOGGER.error("Image %s does not provide metadata" % self.data_file)
        if self.data_file.GetRasterBand(1)!= None:
            LOGGER.info("Getting properties projection, geotransform, data_shape and footprint of raster %s" % self.data_file)
            self._extract_raster_properties()
        self.data_array = None
    def _open_file(self, mode=gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal.
        '''
        try:
            LOGGER.debug('Open raster file: %s', self.image_path)
            LOGGER.info('Open raster file: %s' % self.image_path)
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
    def _extract_raster_properties(self):
        '''
        Extract some raster info from the raster image file using gdal functions.
        '''
        self.metadata['properties'] ={'projection': None, 'geotransform': None, 'data_shape': None, 'footprint': None}
        put_in_dictionary(self.metadata, PROJECTION, self.data_file.GetProjection())
        put_in_dictionary(self.metadata, GEO_TRANSFORM, self.data_file.GetGeoTransform())
        put_in_dictionary(self.metadata, DATA_SHAPE, (self.data_file.RasterXSize, self.data_file.RasterYSize, self.data_file.RasterCount))
        put_in_dictionary(self.metadata, FOOTPRINT, self._get_footprint())
    def _get_footprint(self):
        '''
        Returns the extent of the raster image.
        '''
        try:
            ring = ogr.Geometry(ogr.wkbLinearRing)
            geotransform = self.get_attribute(GEO_TRANSFORM)
            data_shape = self.get_attribute(DATA_SHAPE)
            ring.AddPoint_2D(geotransform[0], geotransform[3])
            ring.AddPoint_2D(geotransform[0] + geotransform[1] * data_shape[0], geotransform[3])
            ring.AddPoint_2D(
                geotransform[0] + geotransform[1] * data_shape[0],
                geotransform[3] + geotransform[5] * data_shape[1]
                )
            ring.AddPoint_2D(geotransform[0], geotransform[3] + geotransform[5] * data_shape[1])
            ring.CloseRings()
            spacial_reference = osr.SpatialReference()
            spacial_reference.ImportFromWkt(self.get_attribute(PROJECTION))
            return self._footprint_helper(ring, spacial_reference)
        except:
            LOGGER.info('Unable to get footprint of %s', self.image_path)
    def read_data_file_as_array(self):
        '''
        Read image data from already opened image
        '''
        if self.data_array is None:
            if self.data_file != None:
                self.data_array = self.data_file.ReadAsArray()
                self.close()
            else:
                self.data_file = self._open_file()
                self.data_array = self.data_file.ReadAsArray()
                self.close()
        return self.data_array
    def gcps(self):
        '''
        Get gcps from image
        '''
        if self.data_file != None:
            gcps = self.data_file.GetGCPs()
            self.close()
            return gcps
        else:
            self.data_file = self._open_file()
            gcps = self.data_file.GetGCPs()
            self.close()
            return gcps
    def gcps_to_geotransform(self):
        '''
        Gcps to geotransform using gdal
        '''
        return gdal.GCPsToGeoTransform(self.gcps()) 
    def create_from_reference(self, outname, width_raster, height_raster, number_of_bands, type_format, geotransform, projection, options = []):
        format_create = 'GTiff'
        driver = gdal.GetDriverByName(format_create)
        options = ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND']
        data = driver.Create(outname, width_raster, height_raster, number_of_bands, type_format, options)
        data.SetGeoTransform(geotransform)
        data.SetProjection(projection)
        return data
    def write_raster(self, number_of_bands, data_file, data_to_write):
        '''
        data_file: data that will have the data in parameter data_to_write
        '''
        for b in range(number_of_bands):
            data_file.GetRasterBand(b+1).WriteArray(data_to_write[b,:,:])       
    def close(self):
        '''
        Method for closing the gdal file
        '''
        self.data_file = None
    def get_attribute(self, path_to_attribute):
        '''
        Returns the attribute that is found in the given path
        '''
        return _get_attribute(path_to_attribute, self.metadata)
    