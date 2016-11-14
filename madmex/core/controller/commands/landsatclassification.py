'''
Created on 26/08/2016

@author: erickpalacios
'''
from madmex.core.controller.base import BaseCommand
import logging
from madmex.core.controller.commands import get_bundle_from_path
from madmex.persistence.driver import find_datasets, get_host_from_command
from datetime import datetime
from madmex.mapper.data import raster, vector
from madmex.mapper.data.harmonized import harmonize_images, get_image_subset
from madmex.mapper.data.raster import create_raster_tiff_from_reference,\
    new_options_for_create_raster_from_reference
from madmex.processing.raster import mask_values, \
    calculate_ndvi_2, calculate_sr, calculate_evi, calculate_arvi,\
    calculate_tasseled_caps, calculate_statistics_metrics, vectorize_raster,\
    calculate_zonal_statistics, append_labels_to_array, build_dataframe_from_array,\
    create_names_of_dataframe_from_filename, resample_numpy_array,\
    get_gradient_of_image, get_grid, calculate_zonal_histograms,\
    get_pure_objects_from_raster_as_dataframe
from madmex.configuration import SETTINGS
import numpy
from madmex.mapper.bundle.landsat8sr import FILES
from numpy import ndarray
from madmex.remote.dispatcher import RemoteProcessLauncher
from madmex.util import get_parent, get_basename_of_file, create_directory_path
from madmex.mapper.data._gdal import get_array_from_image_path,\
    warp_raster_from_reference, get_array_resized_from_reference_dataset
import pandas
import subprocess
from madmex.mapper.data.dataframe import reduce_dimensionality,\
    outlier_elimination_for_dataframe, generate_namesfile,\
    join_C5_dataframe_and_shape, join_dataframes_by_column_name,\
    write_C5_result_to_csv
LOGGER = logging.getLogger(__name__)
BUNDLE_PACKAGE = 'madmex.mapper.bundle'
FMASK_LAND = 0
FMASK_WATER = 1
FMASK_CLOUD_SHADOW = 2
FMASK_SNOW = 3
FMASK_CLOUD = 4
FMASK_OUTSIDE = 255

def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper', BUNDLE_PACKAGE)

def _get_class_method(list_of_objects, name_method):
    'Resolve method of every object in list of objects given the name'
    list_methods = []
    for obj in list_of_objects:
        #print inspect.getmembers(obj)
        #lista = [y for (x,y) in inspect.getmembers(obj) if class_instance == x]
        #print inspect.getmembers(lista[0])
        list_methods.append(getattr(obj, name_method)())
    return list_methods 

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        parser.add_argument('--start_date', nargs='*')
        parser.add_argument('--end_date', nargs='*')
        parser.add_argument('--satellite', nargs='*')
        parser.add_argument('--cloud_coverage', nargs='*')
        parser.add_argument('--gridid', nargs='*')
        parser.add_argument('--landmask_path', nargs = '*')
        
    def handle(self, **options):
        start_date = datetime.strptime(options['start_date'][0], "%Y-%m-%d")
        end_date = datetime.strptime(options['end_date'][0], "%Y-%m-%d")
        satellite = options['satellite'][0]
        cloud = options['cloud_coverage'][0]
        product = 4 #This is ledaps product
        gridid = options['gridid'][0]
        landmask_path = options['landmask_path'][0]
        sr_image_paths = find_datasets(start_date, end_date, satellite, product, cloud, gridid)
        print sr_image_paths
        product = 7 #This is fmask product
        fmask_image_paths = find_datasets(start_date, end_date, satellite, product, cloud, gridid)
        print fmask_image_paths

        #sr_image_paths = [u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-15/sr', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-31/sr', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-02-16/sr', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-03-04/sr']
        #fmask_image_paths = [u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-15/fmask', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-31/fmask', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-02-16/fmask', u'/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-03-04/fmask']
        
        sr_image_paths_l1t = []
        for path in sr_image_paths:
            bundle = _get_bundle_from_path(path)
            if bundle and bundle.get_datatype() == 'L1T':
                LOGGER.info('Directory %s is a %s bundle and data type is %s', path, bundle.get_name(), bundle.get_datatype())
                sr_image_paths_l1t.append(bundle)
            else:
                if not bundle:
                    LOGGER.info('No bundle was able to identify the directory: %s.', path)
                if not bundle.get_datatype() == 'L1T':
                    LOGGER.info('The folder %s was dropped because of data type', bundle.path)
                    bundle  = None
        fmask_image_paths_l1t = []
        for path in fmask_image_paths:
            bundle = _get_bundle_from_path(path)
            if bundle and bundle.get_datatype() == 'L1T':
                LOGGER.info('Directory %s is a %s bundle and data type is %s', path, bundle.get_name(), bundle.get_datatype())
                fmask_image_paths_l1t.append(bundle)
            else:
                if not bundle:
                    LOGGER.info('No bundle was able to identify the directory: %s.', path)
                if not bundle.get_datatype() == 'L1T':
                    LOGGER.info('The folder %s was dropped because of data type of metadata', bundle.path)
                    bundle = None
        
        if len(sr_image_paths_l1t) == len(fmask_image_paths_l1t):
            LOGGER.info('Starting harmonize process of all sr images')
            list_data_class_objects_sr = _get_class_method(sr_image_paths_l1t, 'get_raster')
            extents_dictionary =  harmonize_images(list_data_class_objects_sr)#, list_data_class_objects[0].get_attribute(raster.PROJECTION), list_data_class_objects[0].get_attribute(raster.DATA_SHAPE))
            list_data_class_objects_sr = None
            LOGGER.info('Result of harmonize process: %s' % extents_dictionary)
            LOGGER.info('Starting calculation of spectral features of every band')
            LOGGER.info('Identifying landmask %s' % landmask_path)
            bundle = _get_bundle_from_path(landmask_path)
            if bundle:
                LOGGER.info('Directory %s is a %s bundle', landmask_path, bundle.get_name())
                LOGGER.info('Rasterizing vector shape')
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), 1), {})
                dataset_landmask_rasterized = create_raster_tiff_from_reference(extents_dictionary, '', None, options_to_create)
                bundle.rasterize(dataset_landmask_rasterized, [1], [1]) #the rasterized process changes the dataset
                #we don't have to write the data in disk, if we do, then uncomment the next two lines and the one after TODO
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
                image = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/rasterize3.tif'
                #TODO: check why using this option doesn't write the image to disk: new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, dataset_landmask_rasterized, options_to_create)
                create_raster_tiff_from_reference(extents_dictionary, image, dataset_landmask_rasterized.ReadAsArray(), options_to_create)
                LOGGER.info('Finished rasterizing vector shape')
            else:
                LOGGER.info('No bundle was able to identify the directory: %s.', landmask_path)
            LOGGER.info('Resizing all fmask images according to harmonize process')
            #list_data_class_objects_fmask = _get_class_method(fmask_image_paths_l1t, 'get_raster')         
            subset_counter = 0
            list_fmask_arrays_resized_and_boolean = []
            values = [FMASK_CLOUD, FMASK_CLOUD_SHADOW, FMASK_OUTSIDE]
            #the next for can be parallelized and extracted to a general function
            for bundle in fmask_image_paths_l1t:
                yoffset = extents_dictionary['y_offset'][subset_counter]
                xoffset = extents_dictionary['x_offset'][subset_counter]
                y_range = extents_dictionary['y_range']
                x_range = extents_dictionary['x_range']
                data_array_resized = get_image_subset(yoffset, xoffset, y_range, x_range, bundle.get_raster().read_data_file_as_array())
                data_array_resized_and_masked = mask_values(data_array_resized, values)
                list_fmask_arrays_resized_and_boolean.append(data_array_resized_and_masked)
                subset_counter+=1
            #The next lines just for checking, uncomment if want to write in disk the last image of fmask
            #file_masked = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/fmask_mask.tif'
            #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
            #create_raster_tiff_from_reference(extents_dictionary, file_masked, data_array_resized_and_masked, options_to_create)
            data_array_resized = None
            data_array_resized_and_masked = None
            LOGGER.info('Finished resizing and booleanizing all fmask images according to harmonize process')
            folder_results =  getattr(SETTINGS, 'BIG_FOLDER')
            LOGGER.info('Creating empty stacks for bands in path: %s' % folder_results)
            number_of_sr_bands = len(FILES)

            LOGGER.info('Number of bands of hdf array: %s' % str(number_of_sr_bands))
            options_to_create_empty_stacks = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), len(sr_image_paths_l1t)), {})
            #new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], options_to_create_empty_stacks)
            new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], options_to_create_empty_stacks) 
            output_file_stack_bands_list = []
            datasets_stack_bands_list = []
            for i in range(0, number_of_sr_bands):
                output_file = folder_results + 'band' + str(i+1)
                #We keep the dataset output of create_raster_tiff_from_reference for stacking purposes
                datasets_stack_bands_list.append(create_raster_tiff_from_reference(extents_dictionary, output_file, None, options_to_create_empty_stacks))
                output_file_stack_bands_list.append(output_file)
            LOGGER.info('Created empty stacks for bands')
            LOGGER.info('Creating empty stacks for indexes in path: %s' % folder_results)
            options_to_create_empty_indexes_stacks = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), len(sr_image_paths_l1t)), {})
            #new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], options_to_create_empty_indexes_stacks)
            new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], options_to_create_empty_indexes_stacks)                
            output_file_stack_indexes_list = []
            datasets_stack_indexes_list = []
            list_of_indexes = ['NDVI', 'SR', 'EVI', 'ARVI', 'TC']
            list_of_indexes_functions = [calculate_ndvi_2, calculate_sr, calculate_evi, calculate_arvi, calculate_tasseled_caps]
            number_of_indexes = len(list_of_indexes)
            for i in range(number_of_indexes):
                if list_of_indexes[i] == 'TC':
                    for k in range(number_of_sr_bands):
                        output_file = folder_results + list_of_indexes[i] + str(k+1) 
                        #We keep the dataset output of create_raster_tiff_from_reference for stacking purposes
                        datasets_stack_indexes_list.append(create_raster_tiff_from_reference(extents_dictionary, output_file, None, options_to_create_empty_indexes_stacks))
                        output_file_stack_indexes_list.append(output_file)
                else:
                    output_file = folder_results + list_of_indexes[i]  # + str(i+1)
                    #We keep the dataset output of create_raster_tiff_from_reference for stacking purposes
                    datasets_stack_indexes_list.append(create_raster_tiff_from_reference(extents_dictionary, output_file, None, options_to_create_empty_indexes_stacks))
                    output_file_stack_indexes_list.append(output_file)

            LOGGER.info('Created empty stacks for indexes')
            landmask_array = dataset_landmask_rasterized.ReadAsArray()
            LOGGER.info('Calculating mask from fmask result over all images')
            #this is with landmask: index_masked_pixels_over_all_images = numpy.array((numpy.invert(ndarray.all(numpy.array(list_fmask_arrays_resized_and_boolean)==0,axis=0))*landmask_array) == 0, dtype = bool)
            
            index_fmask_over_all_images = numpy.array((numpy.invert(ndarray.all(numpy.array(list_fmask_arrays_resized_and_boolean)==0,axis=0))) == 0, dtype = bool)
            #TODO: consider
                    #using and 'or' operator instead of 'ndarray.all' for getting index_fmask_over_all_images: ndarray.all
            
            
            #The next lines just for checking, uncomment if want to write in disk the last image of fmask
            #file_masked_overall = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/fmask_mask_overall_images.tif'
            #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
            #create_raster_tiff_from_reference(extents_dictionary, file_masked_overall, index_masked_pixels_over_all_images, options_to_create)
            #LOGGER.info('Calculating mask from no data values over all images') #is too restrictive this line
            #index_NaNs_over_all_images = numpy.zeros([y_range, x_range])
            subset_counter = 0
            for bundle in sr_image_paths_l1t:
                if bundle.FORMAT == 'HDF4':
                    LOGGER.info('Reading arrays of sr images')
                    bundle.read_hdf_data_file_as_array()
                    data_array_resized = numpy.zeros((number_of_sr_bands, y_range, x_range))
                    LOGGER.info('Starting stacking of sr images for every band')
                    LOGGER.info('Processing image %s' % bundle.path)
                    new_options_for_create_raster_from_reference(extents_dictionary, raster.CREATE_STACKING, True, options_to_create_empty_stacks)
                    LOGGER.info('Number of offset in writing of stack: %s' % str(subset_counter))
                    yoffset = extents_dictionary['y_offset'][subset_counter]
                    xoffset = extents_dictionary['x_offset'][subset_counter]
                    new_options_for_create_raster_from_reference(extents_dictionary, raster.STACK_OFFSET, subset_counter, options_to_create_empty_stacks)
                    array_for_masking = list_fmask_arrays_resized_and_boolean[subset_counter]*landmask_array
                    index_masked_pixels = numpy.array(array_for_masking==0, dtype = bool)
                    for i in range(number_of_sr_bands):
                        LOGGER.info('Resizing bands of %s' % bundle.path)
                        data_array_resized[i,:,:] = get_image_subset(yoffset, xoffset, y_range, x_range, bundle.get_raster().hdf_data_array[i,:,:])
                        LOGGER.info('Applying landmask and fmask, value of mask of -9999 to each band of %s' % bundle.path)
                        #data_array_resized[i,:,:][index_masked_pixels] = 0
                        data_array_resized[i,:,:][index_masked_pixels] = -9999
                        LOGGER.info('Writing band %s of file %s in the stack: %s' % (str(i+1), bundle.path, output_file_stack_bands_list[i]))
                        new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_bands_list[i], options_to_create_empty_stacks)
                        create_raster_tiff_from_reference(extents_dictionary, output_file_stack_bands_list[i], data_array_resized[i, :, :], options_to_create_empty_stacks)
                    index_NaNs = numpy.array(data_array_resized== -9999, dtype = bool)
                    index_NaNs_2d = numpy.array(ndarray.all(data_array_resized==-9999,axis=0), dtype = bool)
                    #index_NaNs_over_all_images[index_NaNs_2d] = -9999
                    LOGGER.info('Shape of hdf data array resized and masked  %s %s %s'  % (data_array_resized.shape[0], data_array_resized.shape[1], data_array_resized.shape[2]))
                    LOGGER.info('Starting calculation of indexes for hdf data array resized and masked')
                    LOGGER.info('Starting stacking of sr images for every index')                
                    if bundle.get_name() == 'Landsat 8 surfaces reflectances':
                        new_options_for_create_raster_from_reference(extents_dictionary, raster.CREATE_STACKING, True, options_to_create_empty_indexes_stacks)
                        new_options_for_create_raster_from_reference(extents_dictionary, raster.STACK_OFFSET, subset_counter, options_to_create_empty_indexes_stacks)
                        for j in range(number_of_indexes):
                            LOGGER.info('Calculating index: %s' % list_of_indexes[j])
                            array = list_of_indexes_functions[j](data_array_resized, bundle.get_name())
                            if list_of_indexes[j] == 'TC':    
                                for k in range(number_of_sr_bands):
                                    LOGGER.info('Masking Tasseled caps result: %s with fmask and landmask, value of -9999' %  output_file_stack_indexes_list[j+k])
                                    #array[k,:,:][index_masked_pixels] = 0
                                    array[k,:,:][index_masked_pixels] = -9999
                                    LOGGER.info('Masking Tasseled caps result: %s with Nan values' %  output_file_stack_indexes_list[j+k])
                                    array[k,:,:][index_NaNs[k,:,:]] = -9999
                                    new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_indexes_list[j+k], options_to_create_empty_indexes_stacks)
                                    create_raster_tiff_from_reference(extents_dictionary, output_file_stack_indexes_list[j+k], array[k, :, :], options_to_create_empty_indexes_stacks)
                            else:
                                LOGGER.info('Masking index: %s with fmask and landmask, value of -9999' %  output_file_stack_indexes_list[j])
                                #array[index_masked_pixels] = 0
                                array[index_masked_pixels] = -9999
                                LOGGER.info('Masking index result: %s with Nan values' %  output_file_stack_indexes_list[j])
                                array[index_NaNs_2d] = -9999
                                new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_indexes_list[j], options_to_create_empty_indexes_stacks)
                                create_raster_tiff_from_reference(extents_dictionary, output_file_stack_indexes_list[j], array, options_to_create_empty_indexes_stacks)
                            array = None
                        
                    subset_counter+=1
                data_array_resized = None
            #file_masked_NaNs_over_all_images = folder_results + 'mask_NaNs_over_all_images.tif'
            #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
            #create_raster_tiff_from_reference(extents_dictionary, file_masked_NaNs_over_all_images, index_NaNs_over_all_images, options_to_create)
                     
            
            LOGGER.info('Starting calculation of temporal metrics for images stacked bands')
            output_file_stack_bands_list_metrics = []
            for i in range(len(output_file_stack_bands_list)):
                LOGGER.info('Reading image: %s' % output_file_stack_bands_list[i])
                array = datasets_stack_bands_list[i].ReadAsArray()
                LOGGER.info('Calculating statistics: average, minimum, maximum, standard deviation, range of file %s' % output_file_stack_bands_list[i])
                #LOGGER.info('Changing value of fmask and landmask to array_metrics from zero to -9999 of file: %s' % output_file_stack_bands_list[i])
                #for j in range(array.shape[0]):
                    #array[j,:,:][index_masked_pixels_over_all_images] = -9999
                array_metrics = calculate_statistics_metrics(array, [-9999])
                #array_metrics = calculate_statistics_metrics(array, [0,-9999])
                #The masking value for array_metrics is -9999
                #LOGGER.info('Applying fmask and landmask to array_metrics of file: %s' % output_file_stack_bands_list[i])
                LOGGER.info('Shape of array metrics: %s %s %s' % (array_metrics.shape[0], array_metrics.shape[1], array_metrics.shape[2]))
                #TODO: Is necessary the masking with 0 or we leave the -9999 ? ? ?     
                #for j in range(array_metrics.shape[0]):
                    #array_metrics[j,:,:][index_masked_pixels_over_all_images] = 0
                image_result = output_file_stack_bands_list[i] + 'metrics' + 'band' + str(i+1)
                #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
                create_raster_tiff_from_reference(extents_dictionary, image_result, array_metrics, options_to_create)
                output_file_stack_bands_list_metrics.append(image_result)
            LOGGER.info('Starting calculation of temporal metrics for images stacked indexes')
            output_file_stack_indexes_list_metrics = []
            for i in range(len(output_file_stack_indexes_list)):
                LOGGER.info('Reading image: %s' % output_file_stack_indexes_list[i])
                array = datasets_stack_indexes_list[i].ReadAsArray()
                #LOGGER.info('Changing value of fmask and landmask to array_metrics from zero to -9999 of file: %s' % output_file_stack_indexes_list[i])
                #for j in range(array.shape[0]):
                    #array[j,:,:][index_masked_pixels_over_all_images] = -9999
                array_metrics = calculate_statistics_metrics(array, [-9999])
                LOGGER.info('Calculating statistics: average, minimum, maximum, standard deviation, range of file %s' % output_file_stack_indexes_list[i])
                #array_metrics = calculate_statistics_metrics(array, [0, -9999])
                #The masking value for array_metrics is -9999
                #LOGGER.info('Applying fmask and landmask to array_metrics of file: %s' % output_file_stack_indexes_list[i])
                LOGGER.info('Shape of array metrics: %s %s %s' % (array_metrics.shape[0], array_metrics.shape[1], array_metrics.shape[2]))
                #TODO: Is necessary the masking with 0 or we leave the -9999 ? ? ?     
                #for j in range(array_metrics.shape[0]):
                    #array_metrics[j,:,:][index_masked_pixels_over_all_images] = 0
                if i == 0:
                    #TODO: Next line for flag 'fill_holes'
                    #TODO: value of 9999 or what value do we use ???
                    LOGGER.info('Changing value of fmask of -9999 to 9999 for ndvi metrics to pass to segmentation')
                    index_fmask_for_ndvi_metrics = numpy.array( index_fmask_over_all_images == 1, dtype = bool)#TODO: consider
                    #using and 'or' operator instead of 'ndarray.all' for getting index_fmask_over_all_images
                    index_landmask_for_ndvi_metrics = numpy.array(landmask_array == 1, dtype = bool)
                    index_ndvi_metrics_overall_bands_minus_9999 =numpy.array(ndarray.all(array==-9999,axis=0), dtype=bool)                      
                    for j in range(array_metrics.shape[0]):
                        #array_for_masking = list_fmask_arrays_resized_and_boolean[j]
                        index_fmask_and_landmask_for_ndvi_metrics = numpy.logical_and(index_fmask_for_ndvi_metrics, index_landmask_for_ndvi_metrics)
                        array_metrics[j, :, :][index_fmask_and_landmask_for_ndvi_metrics] = 9999
                        array_ndvi_metrics = array_metrics
                    #just testing purposes:
                    options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
                    image = folder_results + 'rasterize_fmask_last_image_without_landmask.tif'
                    #TODO: check why using this option doesn't write the image to disk: new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, dataset_landmask_rasterized, options_to_create)
                    create_raster_tiff_from_reference(extents_dictionary,image, index_fmask_and_landmask_for_ndvi_metrics, options_to_create)   
                                         
                image_result = output_file_stack_indexes_list[i] + 'metrics'     
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
                create_raster_tiff_from_reference(extents_dictionary, image_result, array_metrics, options_to_create)
                output_file_stack_indexes_list_metrics.append(image_result)
            array = None
            array_metrics = None
            datasets_stack_bands_list = None
            datasets_stack_indexes_list = None
            LOGGER.info('Starting segmentation with: %s' % output_file_stack_indexes_list_metrics[0])   
            val_t = 3
            val_s = 0.2
            val_c = 0.8
            val_xt = 1
            val_rows = 1000
            val_nodata = -9999
            val_tile = False
            val_mp = False
            #folder_and_bind_segmentation = '/LUSTRE/MADMEX/staging/2016_tasks/redisenio_madmex/segmentation/git_segmentation/segmentation:/segmentation'
            #folder_and_bind_license = '/LUSTRE/MADMEX/staging/2016_tasks/redisenio_madmex/segmentation/license/license.txt:/segmentation/license.txt'
            #folder_and_bind_ndvimetrics = get_parent(output_file_stack_indexes_list_metrics[0]) + ':/results'
            #ndvimetrics = '/results/' + get_basename_of_file(output_file_stack_indexes_list_metrics[0])
            #TODO: remove the following lines, right now just for testing purposes. The lines before TODO fix them if necessary
            folder_and_bind_segmentation = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/segmentation/segmentation:/segmentation'
            folder_and_bind_license = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/segmentation/license/license.txt:/segmentation/license.txt '
            #output_file_stack_indexes_list_metrics = ['/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/metrics/NDVImetrics_mod.tif']        
            folder_and_bind_ndvimetrics = get_parent(output_file_stack_indexes_list_metrics[0]) + ':/results'
            ndvimetrics = '/results/' +  get_basename_of_file(output_file_stack_indexes_list_metrics[0])
            LOGGER.info('starting segmentation')
            command = 'segmentation_mac'
            hosts_from_command = get_host_from_command(command)
            LOGGER.info('The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname))
            remote = RemoteProcessLauncher(hosts_from_command[0])
            arguments = 'docker  run --rm -v ' + folder_and_bind_segmentation + ' -v ' + folder_and_bind_license + ' -v ' + folder_and_bind_ndvimetrics + ' segmentation/segmentation:v1 python /segmentation/segment.py ' + ndvimetrics
            arguments+=  ' -t ' + str(val_t) + ' -s ' + str(val_s) + ' -c ' + str(val_c) + ' --tile ' + str(val_tile) + ' --mp ' + str(val_mp) + ' --xt ' + str(val_xt) + ' --rows ' + str(val_rows) + ' --nodata ' + str(val_nodata)
            remote.execute(arguments)
            LOGGER.info('Finished segmentation')
            #TODO: Do we need to have separate values for  the mask of zeros and  Nans values to segmentation tif ??
            #Right now the segmentation tif have the value of zero as the no data value

            #TODO: next lines for flag 'fill_holes'
            LOGGER.info('Changing value of fmask of 9999 to -9999 overall images in %s for segmentation for consistency with other indexes' % output_file_stack_indexes_list_metrics[0])  
            #output_file_stack_indexes_list_metrics[0][index_masked_pixels_over_all_images] = -9999
            LOGGER.info('Rewriting %s' %output_file_stack_indexes_list_metrics[0] )
            for j in range(array_ndvi_metrics.shape[0]):
                array_ndvi_metrics[j, :, :][index_fmask_and_landmask_for_ndvi_metrics] = -9999
            image_result = output_file_stack_indexes_list[0] + 'metrics'     
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
            create_raster_tiff_from_reference(extents_dictionary, image_result, array_ndvi_metrics, options_to_create)
            array_ndvi_metrics = None
                
            

            #The first entry of output_file_stack_indexes_list_metrics is NDVImetrics
            image_segmentation_file =  output_file_stack_indexes_list_metrics[0] + '_' + str(val_t) + '_' + ''.join(str(val_s).split('.'))+ '_' + ''.join(str(val_c).split('.')) + '.tif'
            LOGGER.info('Starting vectorization of segmentation file: %s' % image_segmentation_file)
            image_segmentation_shp = image_segmentation_file + '.shp'
            vectorize_raster(image_segmentation_file, 1, image_segmentation_shp, 'objects', 'id')
            LOGGER.info('Finished vectorization: %s' % image_segmentation_shp)
            LOGGER.info('Preparation for classification')
            #LOGGER.info('Reading raster of segmentation file: %s' % image_segmentation_file)
            #array_sg_raster = get_array_from_image_path(image_segmentation_file)
            LOGGER.info('Extracting infomation of raster segmentation file: %s' % image_segmentation_file)
            gdal_format = "GTiff"
            #TODO: instead of the next line we could use extents_dictionary for metadata creation of files
            image_segmentation_file_class = raster.Data(image_segmentation_file, gdal_format)
            array_sg_raster = image_segmentation_file_class.read_data_file_as_array()
            width_sg_raster, height_sg_raster, bands_sg_raster = image_segmentation_file_class.get_attribute(raster.DATA_SHAPE)
            unique_labels_for_objects = numpy.unique(array_sg_raster)

            
            LOGGER.info('Starting calculation of zonal statistics for stacking of temporal metrics indexes')
            dataframe_list_stack_indexes_list_metrics = []
            for i in range(len(output_file_stack_indexes_list_metrics)):
                LOGGER.info('Reading image: %s' % output_file_stack_indexes_list_metrics[i])
                array = get_array_from_image_path(output_file_stack_indexes_list_metrics[i])
                LOGGER.info('calculating zonal statistics for file: %s' % output_file_stack_indexes_list_metrics[i])
                array_zonal_statistics = calculate_zonal_statistics(array, array_sg_raster, unique_labels_for_objects)
                LOGGER.info('finished zonal statistics')
                array_zonal_statistics_labeled = append_labels_to_array(array_zonal_statistics, unique_labels_for_objects)
                LOGGER.info('Shape of array of zonal statistics labeled %s %s' % (array_zonal_statistics_labeled.shape[0], array_zonal_statistics_labeled.shape[1]))
                LOGGER.info('Building data frame')
                dataframe_list_stack_indexes_list_metrics.append(create_names_of_dataframe_from_filename(build_dataframe_from_array(array_zonal_statistics_labeled.T), array_zonal_statistics_labeled.shape[0], get_basename_of_file(output_file_stack_indexes_list_metrics[i])))
                #LOGGER.info('Changing value of fmask overall images to numpy.NaN for dataframe of: %s' %output_file_stack_indexes_list_metrics[i])
                LOGGER.info('Changing value of fmask overall images to zero for dataframe')
                #index_fmask_dataframe = dataframe_list_stack_indexes_list_metrics[i]['id'] == 9999 #this is id of fmask objects
                #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
                #dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(dataframe_list_stack_indexes_list_metrics[i].median())
                #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = 0
                #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
                LOGGER.info('Filling NaN with zeros')
                #dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(dataframe_list_stack_indexes_list_metrics[i].median())
                dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(0)

                
            array = None
            LOGGER.info('Joining feature dataframes for stack indexes list metrics')
            dataframe_joined_stack_indexes_metrics = join_dataframes_by_column_name(dataframe_list_stack_indexes_list_metrics, 'id')
            dataframe_list_stack_indexes_list_metrics = None
            #The next two lines are just for checking 
            file_name = folder_results + 'dataframe_joined_for_stack_indexes'
            dataframe_joined_stack_indexes_metrics.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
            dataframe_joined_stack_indexes_metrics = None
            dataframe_joined_stack_indexes_metrics = pandas.read_csv(file_name, sep='\t')
            
            
            
            
            LOGGER.info('Starting calculation of zonal statistics for stacking of temporal metrics bands')
            dataframe_list_stack_bands_list_metrics = []
            for i in range(len(output_file_stack_bands_list_metrics)):
                LOGGER.info('Reading image: %s' % output_file_stack_bands_list_metrics[i])
                array = get_array_from_image_path(output_file_stack_bands_list_metrics[i])
                LOGGER.info('calculating zonal statistics for file: %s' % output_file_stack_bands_list_metrics[i])
                array_zonal_statistics = calculate_zonal_statistics(array, array_sg_raster, unique_labels_for_objects)
                LOGGER.info('finished zonal statistics')
                array_zonal_statistics_labeled = append_labels_to_array(array_zonal_statistics, unique_labels_for_objects)
                LOGGER.info('Shape of array of zonal statistics labeled %s %s' % (array_zonal_statistics_labeled.shape[0], array_zonal_statistics_labeled.shape[1]))
                LOGGER.info('Building data frame')
                dataframe_list_stack_bands_list_metrics.append(create_names_of_dataframe_from_filename(build_dataframe_from_array(array_zonal_statistics_labeled.T), array_zonal_statistics_labeled.shape[0], get_basename_of_file(output_file_stack_bands_list_metrics[i])))

                #LOGGER.info('Changing value of fmask overall images to numpy.NaN for dataframe of: %s' %output_file_stack_indexes_list_metrics[i])
                LOGGER.info('Changing value of fmask overall images to zero for dataframe')
                #index_fmask_dataframe = dataframe_list_stack_bands_list_metrics[i]['id'] == 9999 #this is id of fmask objects
                #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
                #dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(dataframe_list_stack_indexes_list_metrics[i].median())
                #dataframe_list_stack_bands_list_metrics[i].loc[index_fmask_dataframe, 1:] = 0
                #dataframe_list_stack_bands_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN 
                LOGGER.info('Filling NaN with zeros')
                dataframe_list_stack_bands_list_metrics[i] = dataframe_list_stack_bands_list_metrics[i].fillna(0)
                
            
            array = None
            LOGGER.info('Joining feature dataframes for stack bands list metrics')
            dataframe_joined_stack_bands_metrics = join_dataframes_by_column_name(dataframe_list_stack_bands_list_metrics, 'id')
            dataframe_list_stack_bands_list_metrics = None
            file_name = folder_results + 'dataframe_joined_for_stack_bands'
            dataframe_joined_stack_bands_metrics.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
            dataframe_joined_stack_bands_metrics = None
            
            dataframe_joined_stack_bands_metrics = pandas.read_csv(file_name, sep='\t')
          
       
            LOGGER.info('Working with auxiliary files')
            dem_file = getattr(SETTINGS, 'DEM')
            aspect_file = getattr(SETTINGS, 'ASPECT')
            slope_file = getattr(SETTINGS, 'SLOPE')
            LOGGER.info('File of dem: %s' % dem_file)
            LOGGER.info('File of aspect: %s' % aspect_file)
            LOGGER.info('File of slope: %s' % slope_file)
            list_of_aux_files = [dem_file, aspect_file, slope_file]
            #dataset_landmask_rasterized = get_dataset(folder_results + 'rasterize3.tif')
            landmask_folder = folder_results  + 'landmask_from_rasterize/'
            LOGGER.info('Polygonizing the landmask rasterized array for clipping the aux files')
            layer_landmask = 'landmask'
            #TODO: the next line requires we have in disk the rasterized file, instead change the 
            #function vectorize_raster for using a dataset
            vectorize_raster(folder_results + 'rasterize3.tif', 1, landmask_folder, layer_landmask, 'id')
            #vectorize_raster(dataset_landmask_rasterized, 1, landmask_folder, layer_landmask, 'id')
            LOGGER.info('Folder of polygon: %s' % landmask_folder)
            output_file_aux_files_warped = []
            for aux_file in list_of_aux_files:
                landmask_file = landmask_folder + layer_landmask + '.shp'
                LOGGER.info('Clipping aux_file: %s with: %s' % (aux_file, landmask_file))
                aux_file_clipped = folder_results  + get_basename_of_file(aux_file) + '_cropped_subprocess_call.tif'
                command = [
                       'gdalwarp', '-cutline', landmask_file,
                       '-crop_to_cutline', '-of', 'GTiff', '-co', 'compress=lzw', '-co', 'tiled=yes','-ot', 'Int32','-dstnodata', '-9999', aux_file, aux_file_clipped
                       ]
                subprocess.call(command)
                LOGGER.info('Finished clipping of aux file')
                LOGGER.info('Starting warping of file: %s according to %s ' % (aux_file_clipped, image_segmentation_file))
                #dataset_warped_aux_file = warp_raster_from_reference(aux_file_clipped, image_segmentation_file, None)
                dataset_warped_aux_file = warp_raster_from_reference(aux_file_clipped, image_segmentation_file_class.data_file, None)
                LOGGER.info('Starting resizing of array of auxiliary file: %s' % aux_file)
                array_resized_and_warped_aux_file = get_array_resized_from_reference_dataset(dataset_warped_aux_file, image_segmentation_file_class.data_file)
                #The next lines of creation just for testing purposes:
                aux_file_resized_and_warped =  folder_results + get_basename_of_file(aux_file) + '_resized_and_warped.tif'
                #options_to_create = new_options_for_create_raster_from_reference(image_segmentation_file_class.metadata,  raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary,  raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
                #create_raster_tiff_from_reference(image_segmentation_file_class.metadata, aux_file_resized_and_warped, array_resized_and_warped_aux_file, options_to_create)
                create_raster_tiff_from_reference(extents_dictionary, aux_file_resized_and_warped, array_resized_and_warped_aux_file, options_to_create)
                LOGGER.info('Starting resampling')
                array = resample_numpy_array(array_resized_and_warped_aux_file, width_sg_raster, height_sg_raster, interpolation = 'nearest')
                aux_file_resampled = folder_results + get_basename_of_file(aux_file) + '_resampled_from_resized_and_warped.tif'
                #LOGGER.info('Masking auxiliary file: %s with fmask and NaNs of NDVI segmentation raster' % aux_file_resampled)
                #index_nodata_value_pixels_ndvi = numpy.array(array_sg_raster==0, dtype = bool)
                #array[index_nodata_value_pixels_ndvi] = -9999
                #The next lines of creation just for testing purposes:
                #create_raster_tiff_from_reference(image_segmentation_file_class.metadata, aux_file_resampled, array, options_to_create)
                create_raster_tiff_from_reference(extents_dictionary, aux_file_resampled, array, options_to_create)
                output_file_aux_files_warped.append(aux_file_resampled)
            LOGGER.info('Starting calculation of zonal statistics for auxiliary files warped')
            dataframe_list_aux_files_warped = []
            for i in range(len(output_file_aux_files_warped)):
                LOGGER.info('Reading image: %s' % output_file_aux_files_warped[i])
                array = get_array_from_image_path(output_file_aux_files_warped[i])
                LOGGER.info('calculating zonal statistics for file: %s' % output_file_aux_files_warped[i])
                array_zonal_statistics = calculate_zonal_statistics(array, array_sg_raster, unique_labels_for_objects)
                LOGGER.info('finished zonal statistics')
                array_zonal_statistics_labeled = append_labels_to_array(array_zonal_statistics, unique_labels_for_objects)
                LOGGER.info('Shape of array of zonal statistics labeled %s %s' % (array_zonal_statistics_labeled.shape[0], array_zonal_statistics_labeled.shape[1]))
                LOGGER.info('Building data frame')
                dataframe_list_aux_files_warped.append(create_names_of_dataframe_from_filename(build_dataframe_from_array(array_zonal_statistics_labeled.T), array_zonal_statistics_labeled.shape[0], get_basename_of_file(output_file_aux_files_warped[i])))
                #Instead of dropping rows because contains no data:
                #dataframe_list_aux_files_warped[i] = dataframe_list_aux_files_warped[i].dropna(how='any')
                #use: http://stackoverflow.com/questions/33573408/python-pandas-replace-na-with-the-median-or-mean-of-a-group-in-dataframe,
                #http://pandas.pydata.org/pandas-docs/stable/missing_data.html#missing-data
                #LOGGER.info('Filling no data values of aux file: %s with median' % output_file_aux_files_warped[i])
                #dataframe_list_aux_files_warped[i] = dataframe_list_aux_files_warped[i].fillna(dataframe_list_aux_files_warped[i].median())

                #LOGGER.info('Changing value of fmask overall images to numpy.NaN for dataframe of: %s' %output_file_stack_indexes_list_metrics[i])
                #LOGGER.info('Changing value of fmask overall images to zero for dataframe')
                #index_fmask_dataframe = dataframe_list_aux_files_warped[i]['id'] == 9999 #this is id of fmask objects
                #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
                #dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(dataframe_list_stack_indexes_list_metrics[i].median())
                #dataframe_list_aux_files_warped[i].loc[index_fmask_dataframe, 1:] = 0
                #dataframe_list_aux_files_warped[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
                LOGGER.info('Filling NaN with zeros')
                dataframe_list_aux_files_warped[i] = dataframe_list_aux_files_warped[i].fillna(0)
                
                
            array = None
            LOGGER.info('Joining feature dataframes for aux files')
            dataframe_joined_aux_files = join_dataframes_by_column_name(dataframe_list_aux_files_warped, 'id')
            dataframe_list_aux_files_warped = None
            #The next two lines are just for checking 
            file_name = folder_results + 'dataframe_joined_for_aux_files'
            dataframe_joined_aux_files.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
            dataframe_joined_aux_files = None
            dataframe_joined_aux_files = pandas.read_csv(file_name, sep='\t')
            array_sg_raster = None
            
            
            LOGGER.info('Getting gradient texture features of file %s' % output_file_stack_indexes_list_metrics[0])
            array_ndvi_metrics = get_array_from_image_path(output_file_stack_indexes_list_metrics[0])            
            output_file_texture_sobel = output_file_stack_indexes_list_metrics[0] + 'gradient.tif'
            array_ndvi_metrics_texture = get_gradient_of_image(array_ndvi_metrics[3,:,:])
            LOGGER.info('Masking array of ndvi metrics texture with fmask and NaNs values of segmentation raster')
            array_sg_raster = get_array_from_image_path(image_segmentation_file)
            #index_nodata_value_pixels_ndvi = numpy.array(array_sg_raster==0, dtype = bool)
            #array_ndvi_metrics_texture[:, :] [index_nodata_value_pixels_ndvi] = -9999 
            index_nodata_value_pixels_ndvi = index_ndvi_metrics_overall_bands_minus_9999
            array_ndvi_metrics_texture[:, :] [index_nodata_value_pixels_ndvi] = -9999 
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
            create_raster_tiff_from_reference(extents_dictionary, output_file_texture_sobel, array_ndvi_metrics_texture, options_to_create)       
            LOGGER.info('Finished gradient texture features')    
            LOGGER.info('Calculating zonal stats for :%s' % output_file_texture_sobel)
            array_zonal_statistics = calculate_zonal_statistics(array_ndvi_metrics_texture, array_sg_raster, unique_labels_for_objects)
            LOGGER.info('finished zonal statistics')
            array_zonal_statistics_labeled = append_labels_to_array(array_zonal_statistics, unique_labels_for_objects)
            LOGGER.info('Shape of array of zonal statistics labeled %s %s' % (array_zonal_statistics_labeled.shape[0], array_zonal_statistics_labeled.shape[1]))
            LOGGER.info('Building data frame')
            dataframe_texture_features = create_names_of_dataframe_from_filename(build_dataframe_from_array(array_zonal_statistics_labeled.T), array_zonal_statistics_labeled.shape[0], get_basename_of_file(output_file_texture_sobel))

            #index_fmask_dataframe = dataframe_texture_features['id'] == 9999 #this is id of fmask objects
            #dataframe_list_stack_indexes_list_metrics[i].loc[index_fmask_dataframe, 1:] = numpy.NaN
            #dataframe_list_stack_indexes_list_metrics[i] = dataframe_list_stack_indexes_list_metrics[i].fillna(dataframe_list_stack_indexes_list_metrics[i].median())
            #dataframe_texture_features.loc[index_fmask_dataframe, 1:] = 0            
            #dataframe_texture_features.loc[index_fmask_dataframe, 1:] = numpy.NaN
            LOGGER.info('Filling NaN with zeros')            
            dataframe_texture_features = dataframe_texture_features.fillna(0)
            
            file_name = folder_results + 'dataframe_texture_features'
            dataframe_texture_features.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
            array_zonal_statistics_labeled = None
            dataframe_texture_features = None
            array_sg_raster = None
            dataframe_texture_features = pandas.read_csv(file_name, sep='\t')
        
            
            
            LOGGER.info('Working with the training data')

            training_data_file = getattr(SETTINGS, 'TRAINING_DATA')
            array_sg_raster = get_array_from_image_path(image_segmentation_file)

            LOGGER.info('Clipping training_data_file: %s with: %s' % (training_data_file, landmask_file))
            training_data_file_clipped = folder_results  + get_basename_of_file(training_data_file) + '_cropped_subprocess_call.tif'
            command = [
                    'gdalwarp', '-cutline', landmask_file,
                    '-crop_to_cutline', '-of', 'GTiff','-co', 'compress=lzw', '-co', 'tiled=yes','-ot', 'Int32', '-dstnodata', '-9999', training_data_file, training_data_file_clipped
                    ]
            subprocess.call(command)
            LOGGER.info('Finished clipping of training data file')
            
            LOGGER.info('Starting warping of file: %s according to %s ' % (training_data_file_clipped, image_segmentation_file))
            dataset_warped_training_data_file = warp_raster_from_reference(training_data_file_clipped, image_segmentation_file_class.data_file, None)
            LOGGER.info('Starting resizing of array of training file: %s' % training_data_file_clipped)
            array_resized_and_warped_training_data_file = get_array_resized_from_reference_dataset(dataset_warped_training_data_file, image_segmentation_file_class.data_file)


            #The next lines of creation just for testing purposes:
            import gdal
            training_data_file_resized_and_warped =  folder_results + get_basename_of_file(training_data_file) + '_resized_and_warped.tif'
            options_to_create = new_options_for_create_raster_from_reference(extents_dictionary,  raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
            create_raster_tiff_from_reference(extents_dictionary, training_data_file_resized_and_warped, array_resized_and_warped_training_data_file, options_to_create, data_type = gdal.GDT_Int32)
            LOGGER.info('Starting resampling')
            #width_sg_raster, height_sg_raster, bands_sg_raster = image_segmentation_file_class.get_attribute(raster.DATA_SHAPE)
            array_training_data_resampled = resample_numpy_array(array_resized_and_warped_training_data_file, width_sg_raster, height_sg_raster, interpolation = 'nearest')
            training_data_file_resampled = folder_results + get_basename_of_file(training_data_file) + '_resampled_from_resized_and_warped.tif'
            #LOGGER.info('Masking training data file: %s with fmask and NaNs of NDVI segmentation raster' % training_data_file_resampled)
            #index_nodata_value_pixels_ndvi = numpy.array(array_sg_raster==0, dtype = bool)
            #array_training_data_resampled[index_nodata_value_pixels_ndvi] = -9999
            LOGGER.info('Changing  value of nodata 0 to -9999 for training data: %s' % training_data_file_resampled) #TODO: This only to training data ???
            index_zeros_training_data = numpy.array(array_training_data_resampled == 0, dtype = bool)
            array_training_data_resampled[index_zeros_training_data] = -9999
            #The next lines of creation just for testing purposes:
            create_raster_tiff_from_reference(extents_dictionary, training_data_file_resampled, array_training_data_resampled, options_to_create, data_type = gdal.GDT_Int32)
            LOGGER.info('Applying chipping to training data file %s:' % training_data_file_resampled)
            geotransform = raster._get_attribute(raster.GEOTRANSFORM, extents_dictionary)
            malla = get_grid(array_training_data_resampled.shape, geotransform[1] , 5000,1000,diagonal=True)
            array_training_data_resampled = array_training_data_resampled*malla
            training_data_file_resampled_grid = training_data_file_resampled +'grid.tif'
            create_raster_tiff_from_reference(extents_dictionary, training_data_file_resampled_grid, array_training_data_resampled, options_to_create, data_type = gdal.GDT_Int32)
            LOGGER.info('Calculating zonal histograms for file: %s according to: %s' % (training_data_file_resampled_grid, image_segmentation_file))
            unique_classes = numpy.unique(array_training_data_resampled)
            array_of_distribution_of_classes_per_object_segmentation = calculate_zonal_histograms(array_training_data_resampled, unique_classes, array_sg_raster, unique_labels_for_objects)
            array_training_data_resampled = None
            LOGGER.info('Getting objects that have no mixture of classes within zonal histogram')
            dataframe_of_pure_objects_of_training_data = get_pure_objects_from_raster_as_dataframe(array_of_distribution_of_classes_per_object_segmentation, unique_labels_for_objects, unique_classes, ["id", "given"])
            #Just checking
            file_name = folder_results + 'dataframe_pure_objects_of_training_data'
            dataframe_of_pure_objects_of_training_data.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
            
            array_of_distribution_of_classes_per_object_segmentation = None
            dataframe_of_pure_objects_of_training_data = None
            dataframe_of_pure_objects_of_training_data = pandas.read_csv(file_name, sep='\t')
            
            
            outlier = True
            if outlier:
                LOGGER.info('Starting outlier elimination with dataframe of stack bands metrics and dataframe of pure objects of training data')
                LOGGER.info('Number of rows and columns of dataframe of stack bands metrics %s %s' % (len(dataframe_joined_stack_bands_metrics.index), len(dataframe_joined_stack_bands_metrics.columns) ))
                LOGGER.info('Number of rows and columns of dataframe of pure objects of training data %s %s' % (len(dataframe_of_pure_objects_of_training_data.index), len(dataframe_of_pure_objects_of_training_data.columns) ))        
                LOGGER.info('Joining dataframe of stack bands metrics and dataframe of pure objects of training data')
                dataframe_joined_stack_bands_metrics_and_pure_objects = join_dataframes_by_column_name([dataframe_joined_stack_bands_metrics, dataframe_of_pure_objects_of_training_data], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_joined_stack_bands_metrics_and_pure_objects.index), len(dataframe_joined_stack_bands_metrics_and_pure_objects.columns)))
                LOGGER.info('Starting principal component analysis')
                array_reduced_pca = reduce_dimensionality(dataframe_joined_stack_bands_metrics_and_pure_objects, .95, ['id', 'given'])
                LOGGER.info('Shape of reduced array of stack bands metrics and pure objects of training data by pca: %s %s' %(array_reduced_pca.shape[0], array_reduced_pca.shape[1]) )
                labels_of_objects_reduced_dataframe = dataframe_joined_stack_bands_metrics_and_pure_objects['id'].values
                LOGGER.info('Appending labels')
                array_reduced_pca_labeled = append_labels_to_array(array_reduced_pca.T, labels_of_objects_reduced_dataframe)
                LOGGER.info('Shape of array reduced by pca and labeled: %s %s' %(array_reduced_pca_labeled.shape[0], array_reduced_pca_labeled.shape[1]))
                LOGGER.info('Building data frame')
                dataframe_reduced_pca_file = folder_results + 'dataframe_joined_for_stack_bands_metrics_and_pure_objects_of_training_data_reduced_by_pca'
                dataframe_reduced_pca = create_names_of_dataframe_from_filename(build_dataframe_from_array(array_reduced_pca_labeled.T), array_reduced_pca_labeled.shape[0], get_basename_of_file(dataframe_reduced_pca_file))
                #TODO: Just checking:
                dataframe_reduced_pca.to_csv(dataframe_reduced_pca_file, sep=',', encoding='utf-8', index = False)
                LOGGER.info('Starting with elimination of outliers')
                LOGGER.info('Joining reduced dataframe by pca with object ids and dataframe of pure objects of training data')
                dataframe_reduced_pca_with_classes= join_dataframes_by_column_name([dataframe_reduced_pca, dataframe_of_pure_objects_of_training_data], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_reduced_pca_with_classes.index), len(dataframe_reduced_pca_with_classes.columns)))
                #Just testing purposes:
                dataframe_reduced_pca_with_classes.to_csv(dataframe_reduced_pca_file + 'classes', sep = ',', encoding = 'utf8', index = False)
                unique_classes = numpy.unique(dataframe_of_pure_objects_of_training_data['given'].values)
                object_ids_outlier_elimination = outlier_elimination_for_dataframe(dataframe_reduced_pca_with_classes, 'id', 'given', 'id', 3, unique_classes, 0.15)
                #Just testing purposes:
                object_ids_outlier_elimination_file = folder_results + 'dataframe_object_ids_outlier_elimination'
                object_ids_outlier_elimination.to_csv(object_ids_outlier_elimination_file, sep = ',', encoding = 'utf-8', index = False)
                LOGGER.info('Joining all dataframes according to ids of outlier elimination ')
                dataframe_all_joined_classified = join_dataframes_by_column_name([object_ids_outlier_elimination, dataframe_joined_stack_bands_metrics, dataframe_joined_stack_indexes_metrics, dataframe_joined_aux_files, dataframe_texture_features, dataframe_of_pure_objects_of_training_data], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_all_joined_classified.index), len(dataframe_all_joined_classified.columns)))
            else:
                LOGGER.info('Joining all dataframes without outlier elimination')
                dataframe_all_joined_classified = join_dataframes_by_column_name([dataframe_joined_stack_bands_metrics, dataframe_joined_stack_indexes_metrics, dataframe_joined_aux_files, dataframe_texture_features, dataframe_of_pure_objects_of_training_data], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_all_joined_classified.index), len(dataframe_all_joined_classified.columns)))

            
            LOGGER.info('Joining all dataframes for classifying')
            dataframe_all_joined_for_classifying = join_dataframes_by_column_name([dataframe_joined_stack_bands_metrics, dataframe_joined_stack_indexes_metrics, dataframe_joined_aux_files, dataframe_texture_features], 'id')
            dataframe_all_joined_for_classifying['given'] = '?'
            LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_all_joined_for_classifying.index), len(dataframe_all_joined_for_classifying.columns)))
            index_of_objects_not__id_zero = dataframe_all_joined_for_classifying['id'] > 0
            dataframe_all_joined_for_classifying = dataframe_all_joined_for_classifying[index_of_objects_not__id_zero]
            LOGGER.info('Number of rows and columns of dataframe joined after removing object with id zero: (%s,%s)' %(len(dataframe_all_joined_for_classifying.index), len(dataframe_all_joined_for_classifying.columns)))
            
            LOGGER.info('Generating data file')
            dataframe_all_joined_classified_file = folder_results + 'C5.data'
            dataframe_all_joined_classified.to_csv(dataframe_all_joined_classified_file, sep = ',', encoding = 'utf-8', index = False, header = False)
            LOGGER.info('Generating cases file')
            dataframe_all_joined_for_classifying_file = folder_results + 'C5.cases'
            dataframe_all_joined_for_classifying.to_csv(dataframe_all_joined_for_classifying_file, sep = ',', encoding = 'utf-8', index = False, header = False)
            LOGGER.info('Generating names file')
            unique_classes = numpy.unique(dataframe_all_joined_classified['given'].values)
            name_namesfile = folder_results + 'C5.names'
            generate_namesfile(dataframe_all_joined_classified.columns, unique_classes,name_namesfile, 'id', 'given')
            
            #Running C5 classification:
            #/usr/local/bin/c5.0 -b -f C5
            #/usr/local/bin/predict -f C5|tail -n +4|sed -nE 's/\s{2,}/,/g;p'|cut -d',' -f1,3,4|sed -n 's/\[//;p'|sed -n 's/\]//;p'|sed -n '1s/^/id,predicted,confidence\n/;p' > C5.result          

            command = 'segmentation_mac'
            hosts_from_command = get_host_from_command(command)
            LOGGER.info('The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname))
            remote = RemoteProcessLauncher(hosts_from_command[0])
            folder_and_bind_c5 = folder_results + ':/datos'
                
            arguments = 'docker  run --rm -v ' + folder_and_bind_c5  + ' c5/c5_execution:v1 ' + 'c5.0 -b -f /datos/C5'
            LOGGER.info('Beginning C5') 
            remote.execute(arguments)
    
            LOGGER.info('Begining predict')
            arguments = 'docker  run --rm -v ' + folder_and_bind_c5  + ' c5/c5_execution:v1 ' + 'predict -f /datos/C5'
            remote = RemoteProcessLauncher(hosts_from_command[0])
            output = remote.execute(arguments, True)
            LOGGER.info('Writing C5 result to csv')
            C5_result = write_C5_result_to_csv(output, folder_results)  
            LOGGER.info('Using result of C5: %s for generating land cover shapefile and raster image' % C5_result)

            LOGGER.info('Using result of C5 for generating land cover shapefile and raster image')        
            C5_result = folder_results + 'C5_result.csv'
            image_segmentation_shp_file = folder_results + 'NDVImetrics_3_02_08.tif.shp'
            dataframe_c5_result = pandas.read_csv(C5_result)
            FORMAT =  'ESRI Shapefile'
            image_segmentation_shp_class = vector.Data(image_segmentation_shp_file,  FORMAT)
            LOGGER.info('Joining dataframe %s to %s' %(C5_result, image_segmentation_shp_file))
            dataframe_joined_shp_segmentation_and_c5_result = join_C5_dataframe_and_shape(image_segmentation_shp_class, 'id', dataframe_c5_result, 'id')
            LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_joined_shp_segmentation_and_c5_result.index), len(dataframe_joined_shp_segmentation_and_c5_result.columns)))
            dataframe_joined_shp_segmentation_and_c5_result_file = folder_results + 'dataframe_joined_shp_segmentation_and_c5_result.csv'
            LOGGER.info('Writing csv of join between c5 result and segmentation shape: %s' % dataframe_joined_shp_segmentation_and_c5_result_file)            
            dataframe_joined_shp_segmentation_and_c5_result.to_csv(dataframe_joined_shp_segmentation_and_c5_result_file, sep =',', encoding = 'utf8', index = False)
            LOGGER.info('Writing C5 result joined with segmentation shape to shapefile')
            #segmentation_and_c5_result_file_vectorized_file = folder_results +'segmentation_and_c5_result_file_vectorized_vectorized.shp'
            #write_C5_dataframe_to_shape(dataframe_joined_shp_segmentation_and_c5_result, image_segmentation_shp_class, segmentation_and_c5_result_file_vectorized_file)        
            segmentation_and_c5_result_file_vectorized_folder = folder_results + 'segmentation_and_c5_result_vectorized/'
            create_directory_path(segmentation_and_c5_result_file_vectorized_folder)
            sql = "SELECT a.id, a.predicted, a.confidence, st_geomfromtext(a.geom," + image_segmentation_shp_class.srid+ ") as geometry "
            sql+= "from dataframe_joined_shp_segmentation_and_c5_result a"
            shp_result = segmentation_and_c5_result_file_vectorized_folder + '/C5_result_joined_segmentation_shape.shp'
            command = [
                    'ogr2ogr', shp_result,
                    dataframe_joined_shp_segmentation_and_c5_result_file,
                    '-dialect', 'sqlite', '-sql', sql
                    ]
            subprocess.call(command)       
            LOGGER.info('Rasterizing segmentation and c5 result shape of folder %s' % segmentation_and_c5_result_file_vectorized_folder)
            LOGGER.info('Identifying segmentation and c5 shape folder %s' % segmentation_and_c5_result_file_vectorized_folder)
            bundle = _get_bundle_from_path(segmentation_and_c5_result_file_vectorized_folder)
            if bundle:
                LOGGER.info('Directory %s is a %s bundle', segmentation_and_c5_result_file_vectorized_folder, bundle.get_name())
                LOGGER.info('Rasterizing vector shape to get land cover tif')
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.DATA_SHAPE, (int(extents_dictionary['x_range']), int(extents_dictionary['y_range']), 1), {})
                dataset_shape_sg_and_c5_rasterized = create_raster_tiff_from_reference(extents_dictionary, '', None, options_to_create)
                bundle.rasterize(dataset_shape_sg_and_c5_rasterized, [1], None, ["ATTRIBUTE=predicted" ]) #the rasterized process changes the dataset
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
                image =folder_results + 'madmex_lcc_prueba.tif'
                #TODO: check why using this option doesn't write the image to disk: new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, dataset_landmask_rasterized, options_to_create)
                create_raster_tiff_from_reference(extents_dictionary, image, dataset_shape_sg_and_c5_rasterized.ReadAsArray(), options_to_create, data_type = gdal.GDT_Int32)
                LOGGER.info('Finished rasterizing vector shape')
                LOGGER.info('Rasterizing vector shape to get confidence tif')
                bundle.rasterize(dataset_shape_sg_and_c5_rasterized, [1], None, ["ATTRIBUTE=confidence" ])
                image =folder_results + 'madmex_lcc_confidence_prueba.tif'
                #TODO: check why using this option doesn't write the image to disk: new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, dataset_landmask_rasterized, options_to_create)
                create_raster_tiff_from_reference(extents_dictionary, image, dataset_shape_sg_and_c5_rasterized.ReadAsArray(), options_to_create)
                LOGGER.info('Finished rasterizing vector shape')
        
        LOGGER.info('Finished workflow classification :)')
