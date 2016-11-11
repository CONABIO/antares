'''
Created on Oct 31, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import gdal
import numpy
from scipy.fftpack import ifftn

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_raster_from_reference



def tile_map(image_path, output, x_tile_size, y_tile_size):
    from subprocess import call
    data_array = open_handle(image_path)
    width = data_array.shape[1] 
    height = data_array.shape[0]
    for i in range(0, width, x_tile_size):
        for j in range(0, height, y_tile_size):
            gdaltranString = ['/Library/Frameworks/GDAL.framework/Programs/gdal_translate', '-of', 'GTIFF', '-srcwin', str(i),  str(j) , str(x_tile_size) ,  str(y_tile_size) , image_path, output + 'utm_' + str(i) + '_' + str(j) + '.tif']
            print ' '.join(gdaltranString)    
            call(gdaltranString)
    


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs='*')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        output = options['output'][0]
        image_path = options['path'][0]
        tilesize = 5000
        tile_map(image_path, output, tilesize, tilesize)
        print 'Done'
