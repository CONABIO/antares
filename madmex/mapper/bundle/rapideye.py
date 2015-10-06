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
from madmex.persistence.database.connection import Information
from madmex.preprocessing.base import calculate_rad_rapideye, calculate_toa_rapideye, calculate_distance_sun_earth,\
    base_masking
from madmex.util import get_path_from_list, create_file_name, \
    create_directory_path, get_base_name, get_parent
from madmex.preprocessing import clouddetection


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
                    elevation_angle=self.get_sensor().get_attribute(rapideye.AZIMUTH_ANGLE),
                    resolution=1.0
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
        self.get_raster()
        solar_zenith = self.get_sensor().get_attribute(rapideye.SOLAR_ZENITH)
        data_aquisition_date = self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE)
        sun_earth_distance  = calculate_distance_sun_earth(data_aquisition_date)
        top_of_atmosphere_data = calculate_toa_rapideye(calculate_rad_rapideye(self.get_raster().read_data_file_as_array()), sun_earth_distance, solar_zenith)
        top_of_atmosphere_directory = create_file_name(get_parent(self.path), 'toa')
        create_directory_path(top_of_atmosphere_directory)
        output = create_file_name(top_of_atmosphere_directory, get_base_name(self.get_files()[2]) + '.toa.tif') #TODO: remove the [2] in self.get_files()
        LOGGER.info('Top of atmosphere file will be written in: %s', output)
        projection = self.get_raster().get_attribute(raster.PROJECTION) 
        LOGGER.debug('Projection: %s', projection)
        geotransform_from_gcps = self.get_raster().get_attribute(raster.GEOTRANSFORM)
        data_file = self.get_raster().create_from_reference(output, top_of_atmosphere_data.shape[2], top_of_atmosphere_data.shape[1], top_of_atmosphere_data.shape[0], geotransform_from_gcps, projection, NumericTypeCodeToGDALTypeCode(numpy.float32))
        self.get_raster().write_raster(data_file, top_of_atmosphere_data) 
        solar_azimuth = self.get_sensor().get_attribute(rapideye.SOLAR_AZIMUTH)
        self.masking(top_of_atmosphere_data, top_of_atmosphere_directory, solar_zenith, solar_azimuth, geotransform_from_gcps, projection)
        data_file = None
    def masking(self, top_of_atmosphere_data, top_of_atmosphere_directory, solar_zenith, solar_azimuth, geotransform, projection):
        import numpy
        from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
        print 'masking'
        print top_of_atmosphere_directory
        output = top_of_atmosphere_directory + '/image_clouds_masked.tif'
        print output
        image_masked = base_masking(top_of_atmosphere_data, output, solar_zenith, solar_azimuth, geotransform)
        print type(image_masked)
        image_raster_class = raster.Data('', '')
        height, width = image_masked.shape
        image_mask_result = image_raster_class.create_from_reference(output, width, height, 1, geotransform, projection, NumericTypeCodeToGDALTypeCode(numpy.uint8))
        image_raster_class.write_array(image_mask_result, image_masked)
    def masking_with_time_series(self):
        image_clouds_masked_path = clouddetection.masking(self)
        LOGGER.info('Image for masking clouds is: %s', image_clouds_masked_path)
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
    path = '/Users/erickpalacios/Documents/CONABIO/Tareas/4_RedisenioMadmex/2_Preprocesamiento/Rapideye/CloudMasking/RE_1649125/1649125_2014-01-23_RE4_3A_301519'
    bundle = Bundle(path)
    bundle.preprocess()
    print 'Done'