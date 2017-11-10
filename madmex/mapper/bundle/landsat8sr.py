'''
Created on 25/08/2016

@author: erickpalacios
'''
from madmex.mapper.bundle._landsat import LandsatBaseBundle, _BASE, _BASE_SR
from madmex.mapper.data import raster
from madmex.mapper.sensor import olitirs
from madmex.persistence import driver
from madmex.persistence.database.connection import Information
from madmex.configuration import SETTINGS
from madmex.util import get_path_from_list, create_filename, relative_path,\
    get_basename_of_file
import logging

FORMAT = 'HDF4'
_MISSION = '8'
_NAME = 'Landsat 8' #Defined according to key name of satellites_array in populate.py module
_LETTER = 'C'
_PROCESSING_LEVEL = 'SR'
#FILES = ('sr_band1', 'sr_band2', 'sr_band3', 'sr_band4', 'sr_band5', 'sr_band7')
FILES = ('sr_band2', 'sr_band3', 'sr_band4', 'sr_band5', 'sr_band6', 'sr_band7') #TODO: check if this files are the right ones
LOGGER = logging.getLogger(__name__)

class Bundle(LandsatBaseBundle):
    '''
    classdocs
    '''
    def __init__(self, path):
        '''
        Constructor
        '''
        super(Bundle, self).__init__(path)
        self.path = path
        self.FORMAT = FORMAT
        self.sensor = None
        self.raster = None
        self.output_directory = None
    #def get_format_file(self):
      #  return FORMAT
    #def get_sensor_module(self):
      #  return olitirs
    def get_name(self):
        '''
        Returns the name of the bundle.
        '''
        return 'Landsat 8 surfaces reflectances'
    def get_mission(self):
        '''
        Returns the mission for this particular implementation of the landsat
        satellite.
        '''
        return _MISSION
    def get_processing_level(self):
        '''
        In the case of the satellite Landsat we have different levels of processing,
        the case of this bundle is raw data
        '''
        return _PROCESSING_LEVEL
    def get_datatype(self):
        return self.get_sensor().get_attribute(olitirs.DATA_TYPE).upper()
    def get_letter(self):
        '''
        Files after 2012 have a letter to distinguish the different sensors
        In the case of landsat8, the LEDAPS process only can be applied to files with the letter C,
        that is, only for the oli tirs sensor
        '''
        return _LETTER
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[_BASE_SR % (self.get_letter(), self.get_mission(), '.hdf$')], self.FORMAT)
            self.raster._extract_hdf_raster_properties(FILES[0])
        return self.raster
    def get_sensor(self):
        '''
        Lazily creates and returns a sensor object for this bundle.
        '''
        if not self.sensor:
            self.sensor = olitirs.Sensor(self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'MTL.txt')])
        return self.sensor
    def read_hdf_data_file_as_array(self):
        self.get_raster().read_hdf_data_file_as_array(FILES)
        return 1 
    def get_aquisition_date(self):
        '''
        Returns the data in which this image was aquired.
        '''
        return self.get_sensor().get_attribute(olitirs.ACQUISITION_DATE)
    def get_satellite_object(self):
        '''
        Returns the database object that represents this sensor.
        '''
        return driver.get_satellite_object(_NAME)
    def get_product_type_object(self):
        '''
        Defined according to the attribute shortname of the table product_type
        '''
        return driver.get_product_type_object('lndsr')
    def get_information_object(self):
        row = self.get_sensor().get_attribute(olitirs.ROW)
        path = self.get_sensor().get_attribute(olitirs.PATH)
        basename_metadata = get_basename_of_file( self.file_dictionary[_BASE % (self.get_letter(), self.get_mission(), 'MTL.txt')])
        information = Information(
                    metadata_path = create_filename(self.get_output_directory(),basename_metadata),
                    grid_id = unicode(path + row),
                    projection = self.get_raster().get_attribute(raster.PROJECTION),
                    cloud_percentage = self.get_sensor().get_attribute(olitirs.CLOUD_COVER),
                    geometry = self.get_raster().get_attribute(raster.FOOTPRINT),
                    elevation_angle = 0.0,
                    resolution = self.get_raster().get_attribute(raster.GEOTRANSFORM)[1]
                    )
        return information
    def get_output_directory(self):
        '''
        Creates the output directory where the files in this bundle will be
        persisted on the file system.
        '''
        if self.output_directory is None:
            path = self.get_sensor().get_attribute(olitirs.PATH)
            row = self.get_sensor().get_attribute(olitirs.ROW)
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            sensor_name = self.get_sensor().get_attribute(olitirs.SENSOR_NAME)
            grid_id = unicode(path + row)
            year = self.get_aquisition_date().strftime('%Y')
            date = self.get_aquisition_date().strftime('%Y-%m-%d')
            product_name = _PROCESSING_LEVEL.lower()
            self.output_directory = get_path_from_list([
                destination,
                sensor_name,
                grid_id,
                year,
                date,
                product_name
                ])
        return self.output_directory
if __name__ == '__main__':
    import numpy
    path ='/LUSTRE/MADMEX/eodata/oli_tirs/21048/2015/2015-01-15/sr/'
    bundle = Bundle(path)
    print bundle.get_files()
    print bundle.can_identify()
    print "sensor"
    print bundle.get_sensor().get_attribute(olitirs.SENSOR)
    print "sensor_name"
    print bundle.get_sensor().get_attribute(olitirs.SENSOR_NAME)
    print 'datatype'
    print bundle.get_datatype()
    #print bundle.get_raster().data_file.GetSubDatasets()
    print bundle.get_raster().subdatasets
    print bundle.get_raster().driver
    print bundle.get_raster().metadata
    #print bundle.get_raster()._extract_raster_properties()
    print bundle.get_raster().get_geotransform()
    print bundle.get_raster().get_attribute(raster.PROJECTION)
    print bundle.get_raster().get_attribute(raster.DATA_SHAPE)
    print bundle.get_raster().get_attribute(raster.GEOTRANSFORM)[1]
    print bundle.get_raster().get_attribute(raster.FOOTPRINT)
    print 'read arrays'
    #print bundle.read_hdf_data_file_as_array()
    #print numpy.unique(bundle.get_raster().hdf_data_array)
    print bundle.get_raster().image_path
    print bundle.get_aquisition_date().strftime('%Y')
    print  bundle.file_dictionary[_BASE % (bundle.get_letter(), bundle.get_mission(), 'MTL.txt')]
    print getattr(SETTINGS, 'TEST_FOLDER') + '/'
    print bundle.get_output_directory()
    print 'file_name'