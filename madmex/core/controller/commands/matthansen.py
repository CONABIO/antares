'''
Created on Nov 28, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

from subprocess import call
from zipfile import ZipFile

import gdal
import numpy
from scipy.fftpack import ifftn

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import get_contents_from_folder, create_filename, \
    get_basename, create_directory_path, remove_file, remove_directory


def tile_map(image_path, output, x_tile_size, y_tile_size, x_offset, y_offset):
    gdaltranString = ['gdal_translate', '-of', 'GTIFF', '-srcwin', str(x_offset),  str(y_offset) , str(x_tile_size) ,  str(y_tile_size) , image_path, output]
    call(gdaltranString)
    #shell_string = ' '.join(gdaltranString)    
    #launcher = LocalProcessLauncher()
    #launcher.execute(shell_string)

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
        zip = options['path'][0]
        basename = get_basename(zip)
        aux_name = create_filename(output, 'aux_%s' % basename)
        real_name = create_filename(output, basename)
        with ZipFile(zip, 'r') as unzipped:   
            unzipped.extractall(create_filename(output, 'aux_%s' % basename))
        path = create_filename(aux_name, 'trend_tiles')
        tifs =  get_contents_from_folder(path)
        create_directory_path(real_name)
        for tif in tifs:
            source = create_filename(path, tif)
            target = create_filename(real_name, tif)    
            tile_map(source, target, 4000, 4000, 2, 2)
        remove_directory(aux_name)
        
                      
        