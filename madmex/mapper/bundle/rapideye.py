'''
Created on Jun 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
import madmex.mapper.data.raster as raster
import madmex.mapper.sensor.rapideye as rapideye
from madmex.persistence import driver
from madmex.persistence.database.connection import Information
from madmex.preprocessing import maskingwithreference
from madmex.preprocessing.base import calculate_rad_rapideye, calculate_toa_rapideye, calculate_distance_sun_earth,\
    base_top_of_atmosphere_rapideye
from madmex.util import get_path_from_list, create_file_name, \
    create_directory_path, get_base_name, get_parent
from madmex.mapper.data.raster import create_raster_tiff_from_reference,\
    default_options_for_create_raster_from_reference,\
    new_options_for_create_raster_from_reference
from madmex.preprocessing.masking import base_masking_rapideye


FORMAT = 'GTiff'
_IMAGE = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}\.tif$'
_BROWSE = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}_browse\.tif$'
_LICENSE = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}_license\.txt$'
_METADATA = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}_metadata\.xml$'
_README = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}_readme\.txt$'
_UDM = r'^(\d{4}-\d{2}-\d{2}T1)?\d{5}(\d{2})?(_\d{4}-\d{2}-\d{2})?_RE\d_3A(-NAC)?(_\d{8})?_\d{6}_udm\.tif$'
LOGGER = logging.getLogger(__name__)
class Bundle(BaseBundle):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.path = path
        self.FORMAT = 'GTiff'
        self.file_dictionary = {
                           _IMAGE:None,
                           _BROWSE:None,
                           _LICENSE:None,
                           _METADATA:None,
                           _README:None,
                           _UDM:None
                           }
        self._look_for_files()
        self.sensor = None
        self.raster = None
        self.output_directory = None
    def get_information_object(self):
        information = Information(
                    grid_id=self.get_sensor().get_attribute(rapideye.TILE_ID),
                    projection= self.get_raster().get_attribute(raster.PROJECTION),
                    cloud_percentage=self.get_sensor().get_attribute(rapideye.CLOUDS),
                    geometry=self.get_raster().get_attribute(raster.FOOTPRINT),       
                    elevation_angle=self.get_sensor().get_attribute(rapideye.AZIMUTH_ANGLE),
                    resolution=1.0 #TODO: change this to: self.get_raster().get_attribute(raster.GEOTRANSFORM)[1]
                    )
        return information
    def get_name(self):
        '''
        Returns the name of this bundle.
        '''
        return 'RapidEye'
    def get_files(self):
        '''
        Retrieves a list with the files found in the directory that this bundle
        represents.
        '''
        return [file_path for file_path in self.file_dictionary.itervalues() if file_path]
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = rapideye.Sensor(self.file_dictionary[_METADATA])
        return self.sensor
    def get_aquisition_date(self):
        '''
        Returns the data in which this image was aquired.
        '''
        return self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE)
    def get_sensor_name(self):
        '''
        Returns the data in which this image was aquired.
        '''
        return self.get_sensor().get_attribute(rapideye.SENSOR_NAME)
    def get_sensor_object(self):
        '''
        Returns the database object that represents this sensor.
        '''
        return driver.get_sensor_object(self.get_sensor_name())
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[_IMAGE], self.FORMAT)
        return self.raster
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(rapideye.SENSOR_NAME)
            grid_id = unicode(self.get_sensor().get_attribute(rapideye.TILE_ID))
            year = self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE).strftime('%Y')
            date = self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE).strftime('%Y-%m-%d')
            product_name = self.get_sensor().get_attribute(rapideye.PRODUCT_NAME)
            self.output_directory = get_path_from_list([
                destination,
                sensor_name,
                grid_id,
                year,
                date,
                product_name
                ])
        return self.output_directory
    def calculate_top_of_atmosphere_rapideye(self):
        '''
        This method calculates the top of atmosphere for the rapideye images.
        '''
        import numpy
        from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
        fun_get_attr_sensor_metadata = self.get_sensor().parser.get_attribute
        fun_get_attr_raster_metadata = self.get_raster().get_attribute
        top_of_atmosphere_data = base_top_of_atmosphere_rapideye(fun_get_attr_sensor_metadata, self.get_raster().read_data_file_as_array())
        top_of_atmosphere_directory = create_file_name(get_parent(self.path), 'TOA')
        create_directory_path(top_of_atmosphere_directory)
        output_file = create_file_name(top_of_atmosphere_directory, get_base_name(self.get_files()[2]) + '.toa.tif') #TODO: change [2] in self.get_files()[2] 
        options_to_create = default_options_for_create_raster_from_reference(self.get_raster().metadata)
        create_raster_tiff_from_reference(self.get_raster().metadata, options_to_create, output_file, top_of_atmosphere_data, data_type = NumericTypeCodeToGDALTypeCode(numpy.float32))
        self.masking(top_of_atmosphere_data, top_of_atmosphere_directory, fun_get_attr_sensor_metadata, fun_get_attr_raster_metadata)
    def masking(self, top_of_atmosphere_data, top_of_atmosphere_directory, fun_get_attr_sensor_metadata, fun_get_attr_raster_metadata):
        import numpy
        from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode   
        output_file = top_of_atmosphere_directory + '/image_masked.tif'
        image_masked = base_masking_rapideye(top_of_atmosphere_data, output_file, fun_get_attr_sensor_metadata, fun_get_attr_raster_metadata)
        options_to_create = new_options_for_create_raster_from_reference(self.get_raster().metadata, raster.CREATE_WITH_NUMBER_OF_BANDS, 1, {})
        create_raster_tiff_from_reference(self.get_raster().metadata, options_to_create, output_file, image_masked, data_type = NumericTypeCodeToGDALTypeCode(numpy.uint8))
    def masking_with_time_series(self):
        image_masked_path = maskingwithreference.masking(self.get_output_directory(), self.get_sensor().parser.get_attribute, self.get_raster().read_data_file_as_array(), self.get_raster().metadata)
        LOGGER.info('Image for masking clouds is: %s', image_masked_path)
    def preprocess(self):
        self.calculate_top_of_atmosphere_rapideye()
if __name__ == '__main__':    
    print 'Rapideye test'
    #path =  '/Users/agutierrez/Documents/rapideye/acopilco/1448013/2011/2011-03-20/l3a'
    #path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/CloudMasking/RE_1649125/1649125_2014-01-23_RE4_3A_301519'
    #path =  '/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/'
    bundle = Bundle(path)
    print bundle.get_raster().get_attribute(raster.FOOTPRINT)
    print bundle.get_files()
    print bundle.can_identify()
    print bundle.masking_with_time_series()
    path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/l3a'
    path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/CloudMasking/RE_1649125/1649125_2014-01-23_RE4_3A_301519'
    bundle = Bundle(path)
    print bundle.get_raster().get_attribute(raster.GEOTRANSFORM)
    print 'geotransform from gcps'
    print bundle.get_raster().get_attribute(raster.GEOTRANSFORM_FROM_GCPS)
    bundle.preprocess()
    print 'Done'
