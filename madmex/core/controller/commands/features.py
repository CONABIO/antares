'''
Created on Aug 8, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        This command defines only an additional argument. The user must provide
        a path to ingest, if several paths are given, all of the folders will
        be ingested.
        '''
        parser.add_argument('--path', nargs='*')    
    def handle(self, **options):
        print 'hello'
        path = options['path'][0]
        print path
        
        #data_array = open_handle(path)
        #for i in range(data_array.shape[0]):
            #print 'band: %s' % (i + 1)
            #print numpy.mean(data_array[i,:,:])
            #print numpy.nanpercentile(data_array[i,:,:],25)
            #print numpy.nanpercentile(data_array[i,:,:],50)
            #print numpy.nanpercentile(data_array[i,:,:],75)
            #print numpy.nanpercentile(data_array[i,:,:],90)
            
        import random
        
        
        
        
        #print numpy.nanpercentile(data_array,25,axis=0)