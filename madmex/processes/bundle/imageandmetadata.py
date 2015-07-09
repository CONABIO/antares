'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.bundle.base import BaseBundle
import logging

LOGGER = logging.getLogger(__name__)

class Bundle(BaseBundle):
    '''
    classdocs
    '''
    def __init__(self, extensions_file, image_extensions, metadata_extensions):
        '''
        Constructor
        '''
        self.extensions_file = extensions_file
        self.image_extensions = image_extensions
        self.metadata_extensions = metadata_extensions
    def identify(self):
        '''
        Identify image file and metadata file in list of extensions of files within directory
        Output: indices in list of extensions of files
        '''
        self.result_scan_image = self.scan(self.image_extensions, self.extensions_file)
        self.result_scan_metadata = self.scan(self.metadata_extensions, self.extensions_file)
    def is_consistent(self):
        '''
        Test that the directory have both image and metadata files
        '''
        if isinstance(self.result_scan_image, int) and isinstance(self.result_scan_metadata, int) and len(self.extensions_file) > 0:
            return True
        else:
            return False
    def identify_specifications(self, extensions_file_not_img_metadata, specifications_extensions):
        '''
        Test that the directory fulfill with specifications, if any
        '''
        if all(x in extensions_file_not_img_metadata for x in specifications_extensions):
            return True
        else:
            return False
        