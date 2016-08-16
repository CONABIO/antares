'''
Created on Aug 8, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import datetime

import numpy

from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.bundle.rapideye import Bundle
from madmex.mapper.data._gdal import get_geotransform
from madmex.util import get_parent


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
        features_array = []
        data_array = open_handle(path)
        for i in range(data_array.shape[0]):
            print 'band: %s' % (i + 1)
            features_array.append(numpy.mean(data_array[i,:,:]))
            features_array.append(numpy.nanpercentile(data_array[i,:,:],25))
            features_array.append(numpy.nanpercentile(data_array[i,:,:],50))
            features_array.append(numpy.nanpercentile(data_array[i,:,:],75))
            features_array.append(numpy.nanpercentile(data_array[i,:,:],90))
        geotransform = get_geotransform(path)
        
        features_array.append(geotransform[0])
        features_array.append(geotransform[3])
        
        bundle = Bundle(get_parent(path))
        features_array.append((bundle.get_aquisition_date() - datetime.datetime(1970, 1, 1)).total_seconds())


        print features_array
        print len(features_array)