'''
Created on Mar 11, 2016

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.mapper.data.harmonized import test, harmonize_images,\
    get_image_subset
from madmex.mapper.data import raster
from madmex.mapper.data.raster import new_options_for_create_raster_from_reference,\
    create_raster_tiff_from_reference

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--first_image', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--second_image', nargs='*', help='This argument represents'
            ' the second image to be processed.')
        parser.add_argument('--output_dir', nargs='*', help='This argument represents'
            ' the second image to be processed.')
    def handle(self, **options):
        '''
        Harmonize pair images based on three criteria: geographical transformation, 
        projection and shape of the data
        '''
        image1 = options['first_image'][0]
        image2 = options['second_image'][0]        
        output_dir = options['output_dir'][0]
        
        extents_dictionary =  harmonize_images([image1, image2])
        subset_counter = 0
        gdal_format = "GTiff"
        for image in [image1, image2]:
            image_class = raster.Data(image, gdal_format)
            yoffset = extents_dictionary['y_offset'][subset_counter]
            xoffset = extents_dictionary['x_offset'][subset_counter]
            y_range = extents_dictionary['y_range']
            x_range = extents_dictionary['x_range']   
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), 1), {})
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
            data_array_resized = get_image_subset(yoffset, xoffset, y_range, x_range, image_class.read_data_file_as_array())
            output_file = output_dir + image
            create_raster_tiff_from_reference(extents_dictionary, output_file, data_array_resized, options_to_create)   
            subset_counter+=1

        #test()

