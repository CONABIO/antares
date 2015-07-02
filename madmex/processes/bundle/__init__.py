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
        self.filelist = self.get_entries(path)
        self.output = {METADATA:list(), IMAGE:list()}
    def execute(self):
        '''
        execute
        '''
        imageextensions = find_formats()
        extensionsfile = [x.strip('.') for x in map(self.get_extension, self.filelist)]
        resultscanimage = self.scan(imageextensions, extensionsfile)
        sensorsmetadataext = get_sensors_and_metadata_extensions()
        metadataextensions = sensorsmetadataext.keys()
        resultscanmetadata = self.scan(metadataextensions, extensionsfile)
        if self.is_consistent(resultscanimage, resultscanmetadata):
            self.imagepath = self.join_path_folder(self.path, self.filelist[resultscanimage])
            self.metadatapath = self.join_path_folder(self.path, self.filelist[resultscanmetadata])
            print 'is consistent'
            LOGGER.info('the directory is consistent')
            self.output[METADATA] = self.metadatapath
            self.output[IMAGE] = self.imagepath
        else:
            LOGGER.info('the directory is not consistent')
            print 'not consistent'
    def is_consistent(self, resultscanimage, resultscanmetadata):
        if isinstance(resultscanimage, int) and isinstance(resultscanmetadata, int) and len(self.filelist) > 0:
            return True
        else:
            return False
        