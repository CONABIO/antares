'''
Created on Jun 10, 2015

@author: agutierrez
'''

import os

METADATA = "metadata"
IMAGE = "image"
FILE = "file"
QUICKLOOK = "quicklook"

class BundleError(Exception):
    '''
    Exception class indicating a problem when trying to parse a bundle.
    '''
    pass
    
class BaseBundle(object):
    '''
    This class serves as a base shell for a bundle. A bundle is a set of files
    that represent a working piece of information. The implementation of this
    class is in charge of looking for the needed files and throw an error in 
    case any of the given files is missing or is incorrect.
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_list = os.listdir(path)
        self.regex_dict = {}
        
    
    def scan(self):
        '''
        This method will traverse through the list of files in the given
        directory using the given regex dictionary, creating a map for the 
        founded files.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a scan() method')
    
    def is_consistent(self):
        '''
        Subclasses must implement this method.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a '
            'is_consistent() method')
