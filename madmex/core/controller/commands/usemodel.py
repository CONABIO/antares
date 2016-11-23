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
        parser.add_argument('--model', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        output = options['output'][0]
        model_path = options['model'][0]
        model = joblib.load(model_path)
        for path in options['path']:
            image_array = open_handle(path)
            basename = get_base_name(path)[:7]
            warnings.filterwarnings('ignore')
            final = numpy.zeros((5000,5000))
            import time
            start_time = time.time()
            for i in range(5000):
                step = numpy.transpose(image_array[:,i,:])
                final[i] = model.predict(step)
            print("--- %s seconds ---" % (time.time() - start_time))
            classification = create_file_name(output, '%s.tif' % basename)
            create_raster_from_reference(classification, final.reshape(5000, 5000), path, data_type=gdal.GDT_Byte, creating_options=['COMPRESS=LZW'])
