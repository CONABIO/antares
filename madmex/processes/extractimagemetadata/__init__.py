'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex import load_class
from madmex.mapper.format import find_formats

FORMAT_PACKAGE = 'madmex.mapper.format'

class Process(Processes):
    '''
    classdocs
    '''
    def __init__(self, diction):
        self.diction = diction
        self.image_path = self.diction['image']     
    def execute(self):
        '''
        execute
        '''
        format_list = find_formats()
        extension_file = self.get_extension(self.image_path).strip('.')
        if extension_file in format_list:
            format_class = load_class(FORMAT_PACKAGE, extension_file).Format()
        else:
            print 'Format  not supported'
        self.output = format_class
