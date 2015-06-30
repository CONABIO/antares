'''
Created on 10/06/2015

@author: erickpalacios
'''

from madmex.processes.base import Processes
from madmex import find_in_dir
from madmex import load_class

FORMAT_PACKAGE = 'madmex.mapper.format'

def find_formats(management_dir):
    
    return find_in_dir(management_dir,'')

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
        print __path__[0]
        
        format_list = find_formats('/Users/erickpalacios/Documents/EclipseWkspace/workspace/madmex/madmex/mapper/format')
        print format_list
        extension_file = self.get_extension(self.image_path).strip('.')
        if extension_file in format_list:
            format_class = load_class(FORMAT_PACKAGE, extension_file).Format()
        else:
            print 'Format  not supported'
        self.output = format_class
