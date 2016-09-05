'''
Created on Jun 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

import dateutil
import numpy
import osgeo
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
from madmex.mapper.data._gdal import create_raster_from_reference
import madmex.mapper.data.raster as raster
from madmex.mapper.sensor.rapideye import TILE_ID
import madmex.mapper.sensor.rapideye as rapideye
from madmex.persistence import driver
from madmex.persistence.database.connection import Information
from madmex.preprocessing import masking
from madmex.preprocessing import maskingwithreference
from madmex.preprocessing.topofatmosphere import calculate_distance_sun_earth, \
    calculate_toa_rapideye, calculate_rad_rapideye
from madmex.util import get_path_from_list, create_file_name, \
    create_directory_path, get_base_name, get_parent

FORMAT = 'GTiff'
ANOMALY_DETECTION = 1
TIME_SERIES = 2
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

    def __init__(self, path, algorithm=1):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.path = path
        self.FORMAT = FORMAT
        self.algorithm = algorithm
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
        #self.get_thumbnail() 
    def get_information_object(self):
        information = Information(
                    grid_id=self.get_sensor().get_attribute(rapideye.TILE_ID),
                    projection=self.get_raster().get_attribute(raster.PROJECTION),
                    cloud_percentage=self.get_sensor().get_attribute(rapideye.CLOUDS),
                    geometry=self.get_raster().get_attribute(raster.FOOTPRINT),
                    elevation_angle=self.get_sensor().get_attribute(rapideye.AZIMUTH_ANGLE),
                    resolution=1.0  # TODO: change this to: self.get_raster().get_attribute(raster.GEOTRANSFORM)[1]
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
    
    def get_product_type_object(self):
        '''
        Returns level of processing of this product.
        '''
        type_name = self.get_sensor().get_attribute(rapideye.PRODUCT_NAME)
        return driver.get_type_object(type_name)
    
    def get_aquisition_date(self):
        '''
        Returns the data in which this image was aquired.
        '''
        return self.get_sensor().get_attribute(rapideye.ACQUISITION_DATE)
    def get_satellite_name(self):
        '''
        Returns the database object that represents this sensor.
        '''
        return rapideye.SATELLITE_NAME
    def get_satellite_object(self):
        '''
        Returns the database object that represents this sensor.
        '''
        return driver.get_satellite_object(self.get_satellite_name())
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
    def get_thumbnail(self):
        '''
        Creates a thumbnail for the scene in true color.
        '''
        parent_directory = get_parent(self.path)
        self.get_thumbnail_with_path(parent_directory)
    def get_thumbnail_with_path(self, thumbnail_path):
        '''
        Creates a thumbnail for the scene in true color.
        '''
        from subprocess import call
        print thumbnail_path
        thumnail_directory = create_file_name(thumbnail_path, 'thumbnail')
        print thumnail_directory
        create_directory_path(thumnail_directory)
        filename = self.file_dictionary[_BROWSE]
        
        thumbnail = create_file_name(thumnail_directory, '%s.jpg' % get_base_name(filename))
        
        print thumbnail
        resize_command = ['/Library/Frameworks/GDAL.framework/Programs/gdal_translate', filename, '-of', 'JPEG', thumbnail]
        call(resize_command)


    # TODO: The next couple of methods can be abstracted in a base class and
    # inheritance.
    def anomaly_detection_cloud_mask(self, top_of_atmosphere_data, cloud_output_file, solar_zenith, solar_azimuth, geotransform):
        '''
        Top of atmosphere information is used to create a cloud mask using the 
        detection anomaly algorithm.
        '''
        return masking.base_masking_rapideye(top_of_atmosphere_data,
                                               cloud_output_file,
                                               solar_zenith,
                                               solar_azimuth,
                                               geotransform
                                               )
    def masking_with_time_series(self, data, cloud_output_file, solar_zenith, solar_azimuth, geotransform, tile_id):
        '''
        This method will create a mask using a time series of images as a reference
        to look for shadows and clouds to mask.
        '''
        return maskingwithreference.masking(data,
                                              tile_id,
                                              solar_zenith,
                                              solar_azimuth,
                                              geotransform)
    def preprocess(self):
        '''
        Top of atmosphere is calculated and persisted into a file. Then a cloud
        mask is created with the given algorithm.
        '''
        solar_zenith = self.get_sensor().parser.get_attribute(rapideye.SOLAR_ZENITH)
        data_acquisition_date = self.get_sensor().parser.get_attribute(rapideye.ACQUISITION_DATE)
        solar_azimuth = self.get_sensor().parser.get_attribute(rapideye.SOLAR_AZIMUTH)
        geotransform = self.get_raster().get_attribute(raster.GEOTRANSFORM)
        data = self.get_raster().read_data_file_as_array()

        sun_earth_distance = calculate_distance_sun_earth(data_acquisition_date)
        top_of_atmosphere_data = calculate_toa_rapideye(calculate_rad_rapideye(data), sun_earth_distance, solar_zenith)
        top_of_atmosphere_directory = create_file_name(get_parent(self.path), 'TOA')

        create_directory_path(top_of_atmosphere_directory)
        output_file = create_file_name(top_of_atmosphere_directory, get_base_name(self.get_files()[2]) + '_toa.tif')  # TODO: change [2] in self.get_files()[2] 

        create_raster_from_reference(output_file,
                                     top_of_atmosphere_data,
                                     self.file_dictionary[_IMAGE],
                                     data_type=NumericTypeCodeToGDALTypeCode(numpy.float32)
                                     )
        LOGGER.debug('Top of atmosphere file was created.')
        cloud_output_file = create_file_name(top_of_atmosphere_directory, get_base_name(self.get_files()[2]) + '_cloud.tif')

        if self.algorithm == ANOMALY_DETECTION:            
            LOGGER.debug('Cloud mask by anomaly detection process.')
            clouds = self.anomaly_detection_cloud_mask(top_of_atmosphere_data, cloud_output_file, solar_zenith, solar_azimuth, geotransform)
        elif self.algorithm == TIME_SERIES:
            LOGGER.debug('Cloud mask by reference with time series process.')
            tile_id = self.get_sensor().get_attribute(TILE_ID)
            clouds = self.masking_with_time_series(data, cloud_output_file, solar_zenith, solar_azimuth, geotransform, tile_id)

        create_raster_from_reference(cloud_output_file,
                     clouds,
                     self.file_dictionary[_IMAGE],
                     data_type=NumericTypeCodeToGDALTypeCode(numpy.float32)
                     )
        LOGGER.info('Cloud mask was created.')

if __name__ == '__main__':
    #path = '/Users/amaury/Documents/rapideye/df/1447813/2012/2012-03-14/l3a'
    #bundle = Bundle(path)
    #print bundle.get_files()
    #print bundle.can_identify()
    
    
    image = "/Users/agutierrez/Documents/rapideye/df/1447813/2012/2012-03-14/l3a/2012-03-14T182106_RE2_3A-NAC_11040070_149070.tif"
    gdal_format = "GTiff"
    data_class = raster.Data(image, gdal_format)
    array = data_class.read_data_file_as_array()
    width, height, bands = data_class.get_attribute(raster.DATA_SHAPE)
    feature_bands = numpy.zeros([2, width, height])
    from madmex.processing.raster import calculate_ndvi
    feature_bands[0, :, :] = calculate_ndvi(array[4, :, :], array[2, :, :])
    feature_bands[1, :, :] = calculate_ndvi(array[3, :, :], array[2, :, :])
    
    out1 = get_parent(image) + 'result_ndvi_1.tif'
    out2 = get_parent(image) + 'result_ndvi_2.tif'
    create_raster_from_reference(out1, feature_bands[0, :, :], image)
    create_raster_from_reference(out2, feature_bands[1, :, :], image)
    print 'Done'