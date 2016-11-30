'''
Created on Nov 21, 2016

@author: agutierrez
'''


from __future__ import unicode_literals

import warnings

import gdal
import numpy
from sklearn.externals import joblib

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.createmodel import load_model
from madmex.core.controller.commands.indexes import open_handle
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data._gdal import create_raster_from_reference
from madmex.util import create_file_name, get_base_name


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--path', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--modelname', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--modeldir', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        output = options['output'][0]
        models = options['modelname']
        model_directory = options['modeldir'][0]
        
        for model_name in models:
            persistence_directory = create_file_name(model_directory, model_name)
            model = load_model(model_name)
            model_instance = model.Model(persistence_directory)
            model_instance.load(persistence_directory)
            step_step = 500
            for path in options['path']:
                image_array = open_handle(path)
                x = image_array.shape[1]
                y = image_array.shape[2]
                basename = get_base_name(path)[:7]
                warnings.filterwarnings('ignore')
                final = numpy.zeros((x,y))
                import time
                start_time = time.time()
                for i in range(0, x, step_step):
                    for j in range(0, y, step_step):
                        step = numpy.transpose(image_array[:,i:i+step_step,j:j+step_step])
                        step_ravel = numpy.transpose(numpy.ravel(step).reshape(10, step_step * step_step))
                        final[i:i+step_step,j:j+step_step] = model_instance.predict(step_ravel).reshape((step_step,step_step))
                        print i,j
                print("--- %s seconds ---" % (time.time() - start_time))
                classification = create_file_name(output, '%s-%s.tif' % (basename, model_name))
                create_raster_from_reference(classification, final.reshape(5000, 5000), path, data_type=gdal.GDT_Byte, creating_options=['COMPRESS=LZW'])
