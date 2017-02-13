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
CREATE_WITH_PROJECTION = ['features_of_image_for_create', 'projection']
CREATE_WITH_GEOTRANSFORM = ['features_of_image_for_create', 'geotransform']
CREATE_WITH_GEOTRANSFORM_FROM_GCPS = ['features_of_image_for_create', 'create_using_geotransform_from_gcps']
GDAL_CREATE_OPTIONS = ['gdal_create_options']
CREATE_STACKING = ['features_of_image_for_create', 'raster_stacked']
STACK_OFFSET = ['stack_offset']
DATASET = ['dataset']
GDAL_TIFF = 'GTiff'
MEMORY = 'MEM'
NO_DATA = -9999

def default_options_for_create_raster_from_reference(reference_metadata):
    '''
    This method will extract the metadata from a given reference file to be used
    in the creation of a new file.
    '''
    geotransform = _get_attribute(GEOTRANSFORM, reference_metadata)
    projection = _get_attribute(PROJECTION, reference_metadata)
    options = {'features_of_image_for_create': None, 'gdal_create_options': None, 'dataset':None}
    options['features_of_image_for_create'] = {
        'projection': None,
        'geotransform': None,
        'create_using_geotransform_from_gcps': None,
        'raster_stacked':None
        }
    put_in_dictionary(options, CREATE_WITH_PROJECTION, projection)
    put_in_dictionary(options, CREATE_WITH_GEOTRANSFORM, geotransform)
    put_in_dictionary(options, CREATE_WITH_GEOTRANSFORM_FROM_GCPS, False)
    put_in_dictionary(options, CREATE_STACKING, False)
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
def create_raster_tiff_from_reference(reference_metadata, output_file, array = None, options = {}, data_type = gdal.GDT_Float32):
    '''
    This method creates a raster tif from a given tif file to be used as a
    reference. From the reference file, data such as , the
    projection, and the geotransform will be extracted and used in the new file. 
    '''
    if not options:
        options = default_options_for_create_raster_from_reference(reference_metadata)
    if output_file == '':
        LOGGER.info('Creating raster in memory')
        driver = gdal.GetDriverByName(str(MEMORY))
    else:
        if  _get_attribute(CREATE_STACKING, options) is False:
            LOGGER.info('Creating raster tif from reference in %s' % output_file)
        else:
            LOGGER.info('Stacking in file %s' % output_file)
        driver = gdal.GetDriverByName(str(GDAL_TIFF))
    if array is None and  _get_attribute(DATA_SHAPE, options) is None:
        LOGGER.info('Error in creating raster, at least one of array or DATA_SHAPE attribute needs to be defined when calling this function')
        return None
    else:
        if array is not None:
            shape = array.shape
            if len(shape) == 2:
                bands = 1
                width = shape[1]
                height = shape[0]
            else:
                bands = shape[0]   
                width = shape[2]
                height = shape[1]
        else:
            if _get_attribute(DATA_SHAPE, options) is not None:
                width, height, bands = _get_attribute(DATA_SHAPE, options)
        gdal_options = _get_attribute(GDAL_CREATE_OPTIONS, options)
        if _get_attribute(CREATE_STACKING, options) is True:
            width, height, bands = _get_attribute(DATA_SHAPE, options)
        projection = _get_attribute(CREATE_WITH_PROJECTION, options)
        if _get_attribute(CREATE_WITH_GEOTRANSFORM_FROM_GCPS, options) is True:
            geotransform = _get_attribute(GEOTRANSFORM_FROM_GCPS, reference_metadata)
        else:
            geotransform = _get_attribute(CREATE_WITH_GEOTRANSFORM, options)
        if _get_attribute(DATASET, options) is None:
            data = driver.Create(output_file, width, height, bands, data_type, gdal_options)
            if projection :
                data.SetProjection(projection)
            if geotransform:
                data.SetGeoTransform(geotransform)
        else:
            data = _get_attribute(DATASET, options)  
        if bands != 1 and array != None:
            if  _get_attribute(CREATE_STACKING, options) is False:
                for band in range(bands):
                    data.GetRasterBand(band + 1).WriteArray(array[band, :, :])
                LOGGER.info('Created raster in %s' % output_file)
            else:
                data.GetRasterBand(_get_attribute(STACK_OFFSET, options)+1).WriteArray(array)
                LOGGER.info('Writing offset %s in %s' % (_get_attribute(STACK_OFFSET, options),output_file))
        else:
            if array != None:
                #data.SetNoDataValue(-9999)
                data.GetRasterBand(1).WriteArray(array)
                LOGGER.info('Created raster in %s' % output_file)
            else:
                if _get_attribute(DATASET, options) is None:
                    LOGGER.info('Returning dataset %s from function create raster tiff from reference' % data)
                    return data
class Data(BaseData):
    '''
    This is a class to handle raster data. It might be convenient to use
    inheritance from this class to represent each type of image file, right now
    it is only a helper class to open raster files.
    '''
    def __init__(self, image_path, gdal_format='GTiff'):
        '''
        Constructor
        '''
        super(Data, self).__init__()
        self.image_path = image_path
        self.metadata = {}
        self.gdal_format = gdal_format
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
            self.image_path = self.image_path.encode('utf-8')
            return gdal.Open(self.image_path, mode)
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
    def _extract_raster_properties(self):
        '''
        Extract some raster info from the raster image file using gdal functions.
        '''
        self.metadata['properties'] = {'projection': None, 'geotransform': None, 'geotransform_from_gcps': None, 'data_shape': None, 'footprint': None}
        put_in_dictionary(self.metadata, PROJECTION, self.data_file.GetProjection())
        put_in_dictionary(self.metadata, GEOTRANSFORM, self.data_file.GetGeoTransform())
        #DATA_SHAPE equivalence for numpy array.shape is data_shape[2], data_shape[1], data_shape[0]
        put_in_dictionary(self.metadata, DATA_SHAPE, (self.data_file.RasterXSize, self.data_file.RasterYSize, self.data_file.RasterCount))
        put_in_dictionary(self.metadata, FOOTPRINT, self._get_footprint())
        put_in_dictionary(self.metadata, GEOTRANSFORM_FROM_GCPS, self.gcps_to_geotransform())
    def get_projection(self):
        return self.data_file.GetProjection()
    def _extract_hdf_raster_properties(self, sr_band):
        '''
        Extract some raster info from the hdf raster image file using gdal functions.
        '''
        self.subdatasets = self.data_file.GetSubDatasets()
        subdataset = [(x,y) for (x,y) in self.subdatasets if x.endswith(sr_band)]
        #data_file_dummy =  self.data_file
        #self.hdf_data_file = self._open_hdf_file(subdataset[0][0])
        #self.data_file = self.hdf_data_file
        self.data_file = self._open_hdf_file_subdataset(subdataset[0][0])
        self._extract_raster_properties()
        #self.data_file = data_file_dummy
    def get_data_shape(self):
        return (self.data_file.RasterXSize, self.data_file.RasterYSize, self.data_file.RasterCount)
    def _get_footprint(self):
        '''
        Returns the extent of the raster image.
        '''
        try:
            ring = ogr.Geometry(ogr.wkbLinearRing)
            geotransform = self.get_geotransform()
            data_shape = self.get_data_shape(self)
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
    def _open_hdf_file_subdataset(self, subdataset, mode=gdalconst.GA_ReadOnly):
        '''
        Open the raster image file with gdal.
        '''
        try:
            LOGGER.debug('Open raster file: %s' % subdataset)
            return gdal.Open(subdataset, mode)
        except RuntimeError:
            LOGGER.error('Unable to open raster file %s', self.image_path)
    def read_data_file_as_array(self):
        '''
        Read image data from already opened image.
        '''
        if self.data_array is None:
            if self.data_file != None:
                self.data_array = self.data_file.ReadAsArray()
                #self.close()
            else:
                self.data_file = self._open_file()
                self.data_array = self.data_file.ReadAsArray()
                #self.close()
        return self.data_array
    def read(self, x_offset, y_offset, x_size, y_size):
        return self.data_file.ReadAsArray(x_offset, y_offset, x_size, y_size)
    def read_hdf_data_file_as_array(self, tuple_of_files):
        '''
        Read image data from hdf file of already opened image.
        '''
        #if self.data_file != None:
        self._helper_read_hdf_data_file_as_array(tuple_of_files)
        self.close()
        return self.hdf_data_array
    def _helper_read_hdf_data_file_as_array(self, tuple_of_files):
        import numpy
        counter=0
        subdatasets = [(x,y) for (x,y) in self.subdatasets if x.endswith(tuple_of_files)]
        z = len(tuple_of_files)
        x,y, z_useless = self.get_attribute(DATA_SHAPE)
        self.hdf_data_array = numpy.zeros((z,y,x))
        for subdataset in subdatasets:
            LOGGER.info('Reading subdataset %s %s into memory' %( str(subdataset[0]), str(subdataset[1])))
            data_file = self._open_hdf_file_subdataset(subdataset[0])
            #x, y, z = data_file.RasterXSize, data_file.RasterYSize, 6
            self.hdf_data_array[counter,:,:] = data_file.ReadAsArray()
            counter+=1
        LOGGER.info('Shape of hdf data array: %s' % str(self.hdf_data_array.shape))
        #return self.hdf_data_array
    def gcps(self):
        '''
        Get ground control points from image.
        '''
        if self.data_file == None:
            self.data_file = self._open_file()
        gcps = self.data_file.GetGCPs()    
        return gcps
    def get_spatial_reference(self):
        '''
        This method gets the spatial reference representation from the image.
        '''
        if self.data_file == None:
            self.data_file = self._open_file()
        projection = self.data_file.GetProjection()
        LOGGER.info("The well known text: %s" % projection)
        spatial_reference = osr.SpatialReference(wkt=projection)
        return spatial_reference
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
    def reproject(self, output, epgs, threshold = 0.125, resampling = gdal.GRA_NearestNeighbour):
        '''
        Creates and returns a copy of this raster in the given spatial reference.
        '''
        if self.data_file == None:
            self.data_file = self._open_file()        
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(epgs)
        well_know_text = spatial_reference.ExportToWkt()
        tmp_ds = gdal.AutoCreateWarpedVRT(self.data_file,
                                          None, # src_wkt : left to default value --> will use the one from source
                                          well_know_text,
                                          resampling,
                                          threshold)
        gdal.GetDriverByName(str('GTiff')).CreateCopy(output, tmp_ds)        
        return Data(output)

        
        