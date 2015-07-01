'''
Created on Jun 30, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import json
import logging
import re

from madmex.mapper.base import BaseParser, ParseError


LOGGER = logging.getLogger(__name__)

def _landsat_harmonizer(value):
    '''
    This method harmonizes between different type of landsat metadata files.
    '''
    value = value.replace("LANDSAT_7", "Landsat7")
    value = value.replace('ETM"', 'ETM+"')
    return value
def put_in_dictionary(dictionary, stack, value):
    '''
    This method puts the given value into a tree represented by the dictionary
    the path to the leaf will be retrieved from the stack.
    '''
    local = dictionary
    length = len(stack) - 1
    for i in range(length):
        local = local[stack[i]]
    local[stack[length]] = value
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
        return re.sub(pattern, r'\1', _landsat_harmonizer(value))
    else:
        try:
            return int(value) 
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass
    return _landsat_harmonizer(value)

class LandsatParser(BaseParser):
    '''
    Parses landsat metadata files creating a memory representation of the
    properties found in there.
    '''
    def __init__(self, filepath):
        '''
        Constructor
        '''
        self.version = None
        self.filepath = filepath
        self.metadata = None
        
        
    def parse(self):
        metadata = open(self.filepath, "r")
        group_dictionary = {}
        groups = {}
        stack = []
        LOGGER.debug("File: %s will be parsed as Landsat metadata file." % self.filepath)
        for line in metadata.readlines():
           
            if "=" in line:
                key, value = line.split(" = ")
                if "group" == key.lower().strip():
                    stack.append(value.strip())
                    put_in_dictionary(groups, stack, {})
                elif "end_group" == key.lower().strip():
                    if group_dictionary:
                        put_in_dictionary(groups, stack, group_dictionary)
                    stack.pop()
                    group_dictionary = {}
                else:
                    group_dictionary[key.strip()] = parse_value(value.strip())   
        metadata.close()
        self.metadata = groups
    def get_attribute(self):
        '''
        This method gets an attribute from the parser object that represents
        a field in the real world object that is being parsed.
        '''
        if not self.metadata:
            raise ParseError(
                'The file has not being parsed yet, please call parse() method'
                )
def main():
    '''
    TODO: remove this, this is just for testing purposes
    '''
    metadata = "/LUSTRE/MADMEX/eodata/etm+/25046/2013/2013-04-03/l1t/LE70250462013093ASN00_MTL.txt"
    parser = LandsatParser(metadata)
    print json.dumps(parser.parse(), indent=4)
if __name__ == "__main__":
    main()
