'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.base import Processes
import logging
from madmex.mapper.format import find_formats, find_specifications
from madmex.mapper.sensor import get_metadata_extensions
from madmex.processes.bundle.imageandmetadata import Bundle

LOGGER = logging.getLogger(__name__)

METADATA = 'metadata'
IMAGE = 'image'

class Process(Processes):
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
        extensions_file = map(self.get_extension, self.file_list)
        image_extensions = find_formats()
        metadata_extensions = get_metadata_extensions()
        bundle_class = Bundle(extensions_file, image_extensions, metadata_extensions)
        bundle_class.identify()
        if bundle_class.is_consistent():
            self.image_path = self.join_path_folder(self.path, self.file_list[bundle_class.result_scan_image])
            self.metadata_path = self.join_path_folder(self.path, self.file_list[bundle_class.result_scan_metadata])
            specifications_extensions = find_specifications(self.get_extension(self.image_path))
            if specifications_extensions is not None:
                extensions_img_metadata = [self.get_extension(self.image_path), self.get_extension(self.metadata_path)]
                extensions_file_not_img_metadata = [x for x in self.extensions_file if x not in extensions_img_metadata]
                if bundle_class.identify_specifications(extensions_file_not_img_metadata, specifications_extensions):
                    print 'is consistent'
                    LOGGER.info('the directory is consistent')
                    self.output[METADATA] = self.metadata_path
                    self.output[IMAGE] = self.image_path
                else:
                    print 'failed in specifications'                      
            else:
                    print 'is consistent'
                    self.output[METADATA] = self.metadata_path
                    self.output[IMAGE] = self.image_path
        else:
            LOGGER.info('the directory is not consistent')
            print 'not consistent'
