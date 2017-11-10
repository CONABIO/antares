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
from madmex.model.unsupervised import pca
from madmex.util import create_filename, get_basename, create_directory_path


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
        
        pca_model = pca.Model(5)
        pca_model.load(create_filename(model_directory, 'pca'))
        
        for model_name in models:
            persistence_directory = create_filename(model_directory, model_name)
            model = load_model(model_name)
            model_instance = model.Model(persistence_directory)
            model_instance.load(persistence_directory)
            block_size = 500
            for path in options['path']:
                image_array = open_handle(path)
                y_size = image_array.shape[1]
                x_size = image_array.shape[2]
                basename = get_basename(path)[:7]
                warnings.filterwarnings('ignore')
                final = numpy.zeros((x_size,y_size))
                import time
                start_time = time.time()
                for i in range(0, y_size, block_size):
                    if i + block_size < y_size:
                        rows = block_size
                    else:
                        rows = y_size - i
                    for j in range(0, x_size, block_size):
                        if j + block_size < x_size:
                            cols = block_size
                        else:
                            cols = x_size - j
                        step = image_array[:,i:i+rows,j:j+cols]
                        step_ravel = step.reshape(10, -1)
                        prediction = model_instance.predict(pca_model.transform(numpy.transpose(step_ravel)))
                        final[i:i+rows,j:j+cols] = prediction.reshape((rows,cols))
                print("--- %s seconds ---" % (time.time() - start_time))
                create_directory_path(output)
                classification = create_filename(output, '%s-%s.tif' % (basename, model_name))
                create_raster_from_reference(classification, final.reshape(x_size, y_size), path, data_type=gdal.GDT_Byte, creating_options=['COMPRESS=LZW'])
