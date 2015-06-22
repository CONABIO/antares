'''
Created on 10/06/2015

@author: erickpalacios
'''
from madmex.processes.base import Processes
from madmex.mapper.base import BaseBundle
import os, os.path
import re
import logging

LOGGER = logging.getLogger(__name__)

METADATA = "metadata"
IMAGE = "image"
FILE = "file"
QUICKLOOK = "quicklook"

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
        self.file_list = os.listdir(path)
        self.output = {METADATA:list(), IMAGE:list()}
        
    def execute(self):
        '''
        execute
        '''
        image_regexp ='\.tif$|\.img$' 
        result_scan_image = self.scan(image_regexp)
        metadata_regexp = '\.xml$|\.dim$'
        result_scan_metadata = self.scan(metadata_regexp)
        if(self.is_consistent(result_scan_image, result_scan_metadata)):        
            self.image_path = os.path.join(self.path, self.file_list[result_scan_image])
            self.metadata_path = os.path.join(self.path, self.file_list[result_scan_metadata])
            print 'is consistent'
            LOGGER.info('the directory is consistent')
            self.output[METADATA] = self.metadata_path
            self.output[IMAGE] = self.image_path
        else:
            LOGGER.info('the directory is not consistent')
                
    def scan(self, list_exp):
        val = False
        k = 0
        while (k<len(self.file_list) and (not val)):
            obj_regex = re.search(list_exp, self.file_list[k])
            if(obj_regex):
                val = True
            else:
                k = k+1
                
        if(val):
            result = k
        else:
            result = 'not founded'
        
        return result
    
    def is_consistent(self, result_scan_image, result_scan_metadata):
        if(isinstance(result_scan_image, int) and isinstance(result_scan_metadata, int) and len(self.file_list)>0):
            return True
        else:
            return False
        
        
        
        