'''
Created on Jun 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import abc
import logging
import logging.config
import os
import re
import uuid

import xml.dom.minidom as dom



METADATA = "metadata"
IMAGE = "image"
FILE = "file"
QUICKLOOK = "quicklook"

LOGGER = logging.getLogger(__name__)

def _xml_to_json(element, stack, dictionary):
    '''
    This method creates a json representation of the given xml structure. It
    traverses the dom tree and adds elements to the dictionary as it goes.
    '''
    stack.append(element.nodeName)
    LOGGER.debug('Processing %s element.' % element.nodeName)
    if element.firstChild and element.firstChild.nodeValue and len(element.firstChild.nodeValue.strip()):
        put_in_dictionary(dictionary, stack, parse_value(element.firstChild.nodeValue.strip()))
    else:
        put_in_dictionary(dictionary, stack, {})
        pass
    for child in element.childNodes:
        if child.nodeType == dom.Node.ELEMENT_NODE:
            _xml_to_json(child, stack, dictionary)
            stack.pop()

def put_in_dictionary(dictionary, stack, value):
    '''
    This method puts the given value into a tree represented by the dictionary
    the path to the leaf will be retrieved from the stack. If the a leaf is
    missing, a empty dictionary will be inserted in its place.
    '''
    current = dictionary
    for i in range(len(stack)-1):
        if stack[i] not in current:
            current[stack[i]] = {}
        current = current[stack[i]]
    current[stack[len(stack)-1]] = value

def parse_value(value):
    '''
    This method tries to identify the value of a given string, if it is in fact
    a string it removes the unnecessary quotes. If value represents a numeric
    object such as an int or a float it parses it into one. If the previous
    tests fail, the value is returned.
    '''
    pattern = r'\"(.*)\"'
    string_matcher = re.compile(pattern)
    if string_matcher.match(value):
        return re.sub(pattern, r'\1', value)
    else:
        try:
            return int(value) 
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass
    return value
def _get_attribute(path_to_metadata, dictionary):
    '''
    This method gets an attribute from the given dictionary that represents
    a field in the real world object that is being parsed.
    '''
    if not isinstance(path_to_metadata, list) or len(path_to_metadata) == 0:
        return None
    try:
        local = dictionary
        length = len(path_to_metadata) 
        for i in range(length):
            local = local[path_to_metadata[i]]
        return local
    except KeyError:
        return None
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
    def scan(self, list_ref, list_test):
        '''
        This method test whether the elements of list_test are in list_ref and if success return the index 
        list_ref is the reference list
        list_test is the list that we want to test
        '''
        val = False
        k = 0
        while k < len(list_ref) and (not val):
            try:
                index = list_test.index(list_ref[k])
                val = True
                result = index
            except ValueError:
                    k = k+1
        if k == len(list_ref) and (not val):
            result = 'not founded'
        return result
    def is_consistent(self):
        '''
        Subclasses must implement this method.
        '''
        raise NotImplementedError(
            'subclasses of BaseBundle must provide a '
            'is_consistent() method')
    def get_entries(self, path):
        "return list of entries within a directory"
        return os.listdir(path)
    def join_path_folder(self, path, folder):
        '''
        return path of folder
        '''
        return os.path.join(path, folder)
    def get_extension(self, filename):
        '''
        return extension of file given it's name
        '''
        path_name, file_extension = os.path.splitext(filename)
        return file_extension.strip('.')
        
class BaseData(object):
    '''
    Implementers of this class will represent a Data object from the outside 
    world. In this case Data can be a raster image.
    '''
    
    def __init__(self):
        '''
        Constructor
        '''

class BaseSensor(object):
    '''
    Implementers of this class represent a sensor.
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.uuid = uuid.uuid4()
        self.format = "not set"
        self.product = "not set"
        self.nodata = -1
        self.parser = None
    
    def get_attribute(self, path_to_attribute):
        return self.parser.get_attribute(path_to_attribute)
        
    
class BaseFormat(object):
    '''
    Implementers of this class will represent a data format.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        
class ParseError(Exception):
    '''
    Handy exception for any error that happens during the parsing process.
    '''

class BaseParser(object):
    '''
    Helper class to parse meta data from the different providers.
    '''
    def __init__(self, filepath):
        '''
        Constructor
        '''
        self.version = None
        self.filepath = filepath
        self.metadata = None
    def parse(self):
        '''
        The method that starts the parsing process. Depending on the file
        that will be parsed, the implementors should be aware of what things
        are necessary in order to parse the given format.
        '''
        pass
    def get_attribute(self, path_to_metadata):
        '''
        This method is just a decorator for the protected _get_attribute method
        to provide a nice interface to get attributes from each parser.
        Classes extending a BaseParser may want to override the behavior of
        this method to adequate it to their needs.
        '''
        return _get_attribute(path_to_metadata, self.metadata)
    def set_attribute(self, stack, value):
        '''
        Puts the given value in the dictionary, using the list of strings to
        set a path.
        '''
        put_in_dictionary(self.metadata, stack, value)
    def apply_format(self, attribute, formatter):
        '''
        This method looks for the value at the given position and replaces it
        with the result of that value after applying the given formatter.
        '''
        put_in_dictionary(self.metadata, attribute, formatter(self.get_attribute(attribute)))

    