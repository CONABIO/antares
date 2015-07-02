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
        self.imagepath = self.diction['image']     
    def execute(self):
        '''
        execute
        '''
        formatlist = find_formats()
        extensionfile = self.get_extension(self.imagepath).strip('.')
        if extensionfile in formatlist:
            formatclass = load_class(FORMAT_PACKAGE, extensionfile).Format()
        else:
            print 'Format  not supported'
        self.output = formatclass
