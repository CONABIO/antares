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
from madmex.util import get_basename_of_file

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
        gdal_format = "GTiff"
        image1_class = raster.Data(image1, gdal_format)
        image2_class = raster.Data(image2, gdal_format)
        extents_dictionary =  harmonize_images([image1_class, image2_class])
        list_class_dummy = [image1_class, image2_class]
        list_images_dummy =[get_basename_of_file(image1), get_basename_of_file(image2)]
        counter = 0
        for image in list_images_dummy:
            yoffset = extents_dictionary['y_offset'][counter]
            xoffset = extents_dictionary['x_offset'][counter]
            y_range = extents_dictionary['y_range']
            x_range = extents_dictionary['x_range']
            print list_class_dummy[counter].get_attribute(raster.FOOTPRINT)
            print list_class_dummy[counter].get_geotransform()
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), 1), {})
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
            data_array_resized = get_image_subset(yoffset, xoffset, y_range, x_range, list_class_dummy[counter].read_data_file_as_array())
            output_file = output_dir+ '/' + image + 'harmonise.tif'
            create_raster_tiff_from_reference(extents_dictionary, output_file, data_array_resized, options_to_create)   
            counter+=1

        #test()

