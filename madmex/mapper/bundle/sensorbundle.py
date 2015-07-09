'''
Created on 09/07/2015

@author: erickpalacios
'''
from madmex.mapper.base import BaseBundle
from madmex.mapper.format import find_formats
from madmex.mapper.sensor import get_metadata_extensions,\
    get_sensors_and_metadata_extensions
import logging
from madmex import load_class

METADATA = 'metadata'
IMAGE = 'image'

LOGGER = logging.getLogger(__name__)
SENSORS_PACKAGE = 'madmex.mapper.sensor'
FORMAT_PACKAGE = 'madmex.mapper.format'


class Bundle(BaseBundle):     
    
    
    def __init__(self, path):
        '''
        Constructor
        path: path to a directory with a list of files
        '''
        self.path = path
        self.file_list = self.get_entries(path)
    
    def get_files(self):
        self.files = {METADATA:list(), IMAGE:list()}
        extensions_file = map(self.get_extension, self.file_list)
        image_extensions = find_formats()
        metadata_extensions = get_metadata_extensions()
        self.identify(image_extensions, metadata_extensions, extensions_file)
        if self.is_consistent():
            self.image_path = self.join_path_folder(self.path, self.file_list[self.result_scan_image])
            self.metadata_path = self.join_path_folder(self.path, self.file_list[self.result_scan_metadata])
            self.extension_image = self.get_extension(self.image_path)
            self.extension_metadata = self.get_extension(self.metadata_path)
            print 'is consistent'
            LOGGER.info('the directory is consistent')
            self.files[METADATA] = self.metadata_path
            self.files[IMAGE] = self.image_path
            return self.files
        else:
            LOGGER.info('the directory is not consistent')
            print 'not consistent'
            
    def get_database_object(self):
        '''
        Create instance of Database object
        '''
        sensor_class = self.sensor_model()
        image_class =  self.image_model()
        print sensor_class
        print image_class
        print sensor_class.parser.metadata
        print image_class.driver
        print image_class.footprint

        
    def identify(self, image_extensions, metadata_extensions, extensions_file):
        '''
        Identify image file and metadata file in list of extensions of files within directory
        Output: indices in list of extensions of files
        '''
        self.result_scan_image = self.scan(image_extensions, extensions_file)
        self.result_scan_metadata = self.scan(metadata_extensions, extensions_file)
    def is_consistent(self):
        '''
        Test that the directory have both image and metadata files
        '''
        if isinstance(self.result_scan_image, int) and isinstance(self.result_scan_metadata, int) and len(self.file_list) > 0:
            return True
        else:
            return False
        
    def sensor_model(self):
        '''
        Create instance of sensor object
        '''
        sensors_metadata_ext = get_sensors_and_metadata_extensions()
        if self.extension_metadata in sensors_metadata_ext.keys():
            sensor_module = load_class(SENSORS_PACKAGE, sensors_metadata_ext[self.extension_metadata])
            sensor_class = sensor_module.Sensor(self.metadata_path)
        return sensor_class
    
    def image_model(self):
        '''
        Create instance of image object
        '''
        format_list = find_formats()
        if self.extension_image in format_list:
            format_class = load_class(FORMAT_PACKAGE, self.extension_image).Format(self.image_path)
            data_class = format_class.data_class
            data = data_class.open_file()
            data_class.extract_metadata(data)
        else:
            print 'Format  not supported'
        return data_class
    
if __name__ == "__main__":
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea9/folder_test/556_297_041114_dim_img_spot'
    bundle_class = Bundle(folder)
    files = bundle_class.get_files()
    print files
    bundle_class.get_database_object()
    
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea9/folder_test/556_297_041114_xml_tif_rapideye'
    bundle_class = Bundle(folder)
    files = bundle_class.get_files()
    print files
    bundle_class.get_database_object()
    
    
    folder = '/Users/erickpalacios/Documents/CONABIO/Tareas/Tarea9/folder_test/556_297_041114_xml_img_sindatosxml'
    bundle_class = Bundle(folder)
    files = bundle_class.get_files()
    print files
    bundle_class.get_database_object()
        

        
    