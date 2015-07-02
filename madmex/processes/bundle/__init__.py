'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.base import Processes
from madmex.processes.bundle.base import BaseBundle
import logging
from madmex.mapper.format import find_formats
from madmex.mapper.sensor import get_sensors_and_metadata_extensions

LOGGER = logging.getLogger(__name__)

METADATA = "metadata"
IMAGE = "image"

class Process(Processes, BaseBundle):
    '''
    classdocs
    '''
    def __init__(self, path):
        '''
        Constructor
        path: path to a directory with a list of files
        '''
        self.path = path
        self.file_list = self.get_entries(path)
        self.output = {METADATA:list(), IMAGE:list()}
    def execute(self):
        '''
        execute
        '''
        image_extensions = find_formats()
        extensions_file = [x.strip('.') for x in map(self.get_extension, self.file_list)]
        result_scan_image = self.scan(image_extensions, extensions_file)
        sensors_metadata_extensions = get_sensors_and_metadata_extensions()
        metadata_extensions = sensors_metadata_extensions.keys()
        result_scan_metadata = self.scan(metadata_extensions, extensions_file)
        if self.is_consistent(result_scan_image, result_scan_metadata):
            self.image_path = self.join_path_folder(self.path, self.file_list[result_scan_image])
            self.metadata_path = self.join_path_folder(self.path, self.file_list[result_scan_metadata])
            print 'is consistent'
            LOGGER.info('the directory is consistent')
            self.output[METADATA] = self.metadata_path
            self.output[IMAGE] = self.image_path
        else:
            LOGGER.info('the directory is not consistent')
            print 'not consistent'
    def is_consistent(self, result_scan_image, result_scan_metadata):
        if isinstance(result_scan_image, int) and isinstance(result_scan_metadata, int) and len(self.file_list) > 0:
            return True
        else:
            return False
        