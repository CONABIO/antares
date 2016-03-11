'''
Created on Jun 3, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

import logging
import os

from madmex import _
from madmex.configuration import SETTINGS
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path
from madmex.mapper.data import raster, harmonized
from madmex.transformation import imad, maf
from madmex.transformation.mafclassification import calc_threshold_grid, \
    recode_classes_grid
from madmex.util import create_file_name


LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--ima', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--imb', nargs='*', help='This argument represents'
            ' the second image to be processed.')
        parser.add_argument('--output', nargs='*', help='The output filename')

    def handle(self, **options):
        '''
        This process will call the change detection process from a set of two
        individual images. It will perform the harmonization and the multivariate
        alteration detection on the images. It will then perform a maximum
        correlation factor on them and work with the resulting bands.
        '''
        image_a = options['ima'][0]
        image_b = options['imb'][0]
        output_image = options['output'][0]

        print 'Image %s will be compared against image %s. Output will be available' \
              ' at %s.' % (image_a, image_b, output_image)        
        # bundle_a = _get_bundle_from_path(image_a)
        # bundle_b = _get_bundle_from_path(image_a)
        gdal_format = "GTiff"
        image_a_data_class = raster.Data(image_a, gdal_format)
        image_b_data_class = raster.Data(image_b, gdal_format)
        harmonized_class = harmonized.Data(image_a_data_class, image_b_data_class)
        if harmonized_class:
            data_shape_harmonized = harmonized_class.get_attribute(harmonized.DATA_SHAPE)
            width, height, bands = data_shape_harmonized
            geotransform_harmonized = harmonized_class.get_attribute(harmonized.GEOTRANSFORM)
            projection_harmonized = harmonized_class.get_attribute(harmonized.PROJECTION)    
            output = create_file_name(getattr(SETTINGS, 'TEST_FOLDER'), 'result_change_detection.tif')
            classification = create_file_name(getattr(SETTINGS, 'TEST_FOLDER'), 'result_reclassification.tif') 
            mad_image = harmonized_class.create_from_reference(output, width, height, (bands + 1), geotransform_harmonized, projection_harmonized)
            maf_image = harmonized_class.create_from_reference(classification, width, height, 1, geotransform_harmonized, projection_harmonized)
            image_a_data_array, image_b_data_array = harmonized_class.harmonized_arrays(image_a_data_class, image_b_data_class)            
            imad_class = imad.Transformation([image_a_data_array, image_b_data_array])
            imad_class.execute()
            
            maf_class = maf.Transformation(imad_class.output)
            
            maf_class.execute()
            
            pdf_file = create_file_name(getattr(SETTINGS, 'TEST_FOLDER'), 'result_maf_pdf.png')

            thresholds = calc_threshold_grid(maf_class.output, pdf_file)
            
            result = recode_classes_grid(maf_class.output, thresholds)
            
            print result.shape
            
            harmonized_class.write_raster(mad_image, maf_class.output)
            harmonized_class.write_raster(maf_image, result)
            
            maf_image
            
            
            
            print 'Output written in: %s' % output
            print 'Shape is ', imad_class.output.shape
