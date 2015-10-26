

'''
Created on 10/06/2015

@author: erickpalacios
'''
from __future__ import unicode_literals
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
GEOTRANSFORM = ['properties', 'geotransform']
GEOTRANSFORM_FROM_GCPS = ['properties', 'geotransform_from_gcps']
DATA_SHAPE = ['properties', 'data_shape']
FOOTPRINT = ['properties', 'footprint']
CREATE_WITH_NUMBER_OF_BANDS = ['features_of_image_for_create', 'number_of_bands']
CREATE_WITH_WIDTH = ['features_of_image_for_create', 'width']
CREATE_WITH_HEIGHT = ['features_of_image_for_create', 'height']
CREATE_WITH_PROJECTION = ['features_of_image_for_create', 'projection']
CREATE_WITH_GEOTRANSFORM = ['features_of_image_for_create', 'geotransform']
CREATE_WITH_GEOTRANSFORM_FROM_GCPS = ['features_of_image_for_create', 'create_using_geotransform_from_gcps']
GDAL_CREATE_OPTIONS = ['gdal_create_options']
GDAL_TIFF = 'GTiff'

def default_options_for_create_raster_from_reference(reference_metadata):
    '''
    This method will extract the metadata from a given reference file to be used
    in the creation of a new file.
    '''
    width, height, bands = _get_attribute(DATA_SHAPE, reference_metadata)
    geotransform = _get_attribute(GEOTRANSFORM, reference_metadata)
    projection = _get_attribute(PROJECTION, reference_metadata)
    options = {'features_of_image_for_create': None, 'gdal_create_options': None}
    options['features_of_image_for_create'] = {
        'number_of_bands': None,
        'width': None,
        'height': None,
        'projection': None,
        'geotransform': None,
        'create_using_geotransform_from_gcps': None
        }
    put_in_dictionary(options, CREATE_WITH_NUMBER_OF_BANDS, bands)
    put_in_dictionary(options, CREATE_WITH_WIDTH, width)
    put_in_dictionary(options, CREATE_WITH_HEIGHT, height)
    put_in_dictionary(options, CREATE_WITH_PROJECTION, projection)
    put_in_dictionary(options, CREATE_WITH_GEOTRANSFORM, geotransform)
    put_in_dictionary(options, CREATE_WITH_GEOTRANSFORM_FROM_GCPS, False)
    put_in_dictionary(options, GDAL_CREATE_OPTIONS, [])
    return options
def new_options_for_create_raster_from_reference(reference_metadata, new_option, value, options):
    '''
    Convenience method to add options to the dictionary.
    '''
    if not options:
        options = default_options_for_create_raster_from_reference(
            reference_metadata
            )
        put_in_dictionary(options, new_option, value)
        return options
    put_in_dictionary(options, new_option, value)
def create_raster_tiff_from_reference(reference_metadata,  output_file, array, options={}, data_type = gdal.GDT_Float32):
    '''
    This method creates a raster tif from a given tif file to be used as a
    reference. From the reference file, data such as the width, the height, the
    projection, and the transform will be extracted and used in the new file. 
    '''
    if not options:
        options =  default_options_for_create_raster_from_reference(reference_metadata)
    driver = gdal.GetDriverByName(str(GDAL_TIFF))
    width = _get_attribute(CREATE_WITH_WIDTH, options)
    height = _get_attribute(CREATE_WITH_HEIGHT, options)
    bands = _get_attribute(CREATE_WITH_NUMBER_OF_BANDS, options)
    gdal_options = _get_attribute(GDAL_CREATE_OPTIONS, options)
    data = driver.Create(output_file, width, height, bands, data_type, gdal_options)
    projection = _get_attribute(CREATE_WITH_PROJECTION, options)
    if _get_attribute(CREATE_WITH_GEOTRANSFORM_FROM_GCPS, options) is True:
        geotransform = _get_attribute(GEOTRANSFORM_FROM_GCPS, reference_metadata)
    else:
        geotransform = _get_attribute(CREATE_WITH_GEOTRANSFORM, options)
    data.SetProjection(projection)
    data.SetGeoTransform(geotransform)
    if bands != 1:
        for band in range(bands):
            data.GetRasterBand(band + 1).WriteArray(array[band, :, :])
    else:
        data.GetRasterBand(1).WriteArray(array)
    print('Created raster in %s' % output_file)

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
            self.driver = gdal.GetDriverByName(str(gdal_format))
            LOGGER.info('driver: %s' % self.driver)
        except AttributeError:
            LOGGER.error('Cannot access driver for format %s' % gdal_format)
        try:
            LOGGER.info('Extracting metadata of driver %s' % gdal_format)
            self.metadata[DRIVER_METADATA[0]] = self.driver.GetMetadata()
        except:
            LOGGER.error('Unable to extract metadata of driver of image %s' % image_path)
        self.data_file = self._open_file()
        if self.data_file != None:
            LOGGER.info("Extracting metadata_file of file %s" % self.data_file)
            self.metadata[METADATA_FILE[0]] = self.data_file.GetMetadata()
            if self.data_file.GetRasterBand(1) != None:
                LOGGER.info("Getting properties projection, geotransform, data_shape and footprint of raster %s" % self.data_file)
                self._extract_raster_properties()
        else:
            LOGGER.info("Image %s does not provide metadata_file" % self.data_file)
        self.data_array = None
    def _open_file(self, mode=gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal.
        '''
        try:
            LOGGER.debug('Open raster file: %s' % self.image_path)
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
    def _extract_raster_properties(self):
        '''
        Extract some raster info from the raster image file using gdal functions.
        '''
        self.metadata['properties'] ={'projection': None, 'geotransform': None, 'geotransform_from_gcps': None, 'data_shape': None, 'footprint': None}
        put_in_dictionary(self.metadata, PROJECTION, self.data_file.GetProjection())
        put_in_dictionary(self.metadata, GEOTRANSFORM, self.data_file.GetGeoTransform())
        put_in_dictionary(self.metadata, DATA_SHAPE, (self.data_file.RasterXSize, self.data_file.RasterYSize, self.data_file.RasterCount))
        put_in_dictionary(self.metadata, FOOTPRINT, self._get_footprint())
        put_in_dictionary(self.metadata, GEOTRANSFORM_FROM_GCPS, self.gcps_to_geotransform())
    def _get_footprint(self):
        '''
        Returns the extent of the raster image.
        '''
        try:
            ring = ogr.Geometry(ogr.wkbLinearRing)
            geotransform = self.get_attribute(GEOTRANSFORM)
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
        Get ground control points from image.
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
    def get_geotransform(self):
        '''
        Returns the geotransform data array from the current image.
        '''
        if self.data_file == None:
            self.data_file = self._open_file()
        return self.data_file.GetGeoTransform()
    def gcps_to_geotransform(self):
        '''
        Transforms ground control points into geotransform using gdal.
        '''
        return gdal.GCPsToGeoTransform(self.gcps())
    def close(self):
        '''
        This method will close the dataset, this will recover resources allocated
        for the file.
        '''
        self.data_file = None
    def get_attribute(self, path_to_attribute):
        '''
        Returns the attribute that is found in the given path.
        '''
        return _get_attribute(path_to_attribute, self.metadata)
