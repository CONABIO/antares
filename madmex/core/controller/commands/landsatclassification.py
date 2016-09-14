'''
Created on 26/08/2016

@author: erickpalacios
'''
from madmex.core.controller.base import BaseCommand
import logging
from madmex.core.controller.commands import get_bundle_from_path
from madmex.persistence.driver import find_datasets, get_host_from_command
from datetime import datetime
from madmex.mapper.data import raster
from madmex.mapper.data.harmonized import harmonize_images, get_image_subset
from madmex.mapper.data.raster import create_raster_tiff_from_reference,\
    new_options_for_create_raster_from_reference
from madmex.processing.raster import mask_values, \
    calculate_ndvi_2, calculate_sr, calculate_evi, calculate_arvi,\
    calculate_tasseled_caps, calculate_statistics_metrics
from madmex.configuration import SETTINGS
import numpy
from madmex.mapper.bundle.landsat8sr import FILES
from madmex.mapper.data._gdal import get_dataset, get_array_from_image_path
from numpy import ndarray
import subprocess
from madmex.remote.dispatcher import RemoteProcessLauncher
from madmex.util import get_parent, get_base_name, get_basename_of_file
from madmex import LOGGER
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
                #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
                #image = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/rasterize3.tif'
                #TODO: check why using this option doesn't write the image to disk: new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, dataset_landmask_rasterized, options_to_create)
                #create_raster_tiff_from_reference(extents_dictionary, image, dataset_landmask_rasterized.ReadAsArray(), options_to_create)
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
                        datasets_stack_indexes_list.append(create_raster_tiff_from_reference(extents_dictionary, output_file, None, options_to_create_empty_indexes_stacks))
                        output_file_stack_indexes_list.append(output_file)
                else:
                    output_file = folder_results + list_of_indexes[i]  # + str(i+1)
                    datasets_stack_indexes_list.append(create_raster_tiff_from_reference(extents_dictionary, output_file, None, options_to_create_empty_indexes_stacks))
                    output_file_stack_indexes_list.append(output_file)

            LOGGER.info('Created empty stacks for indexes')
            landmask_array = dataset_landmask_rasterized.ReadAsArray()
            LOGGER.info('Calculating mask from fmask result over all images')
            index_masked_pixels_over_all_images = numpy.array((numpy.invert(ndarray.all(numpy.array(list_fmask_arrays_resized_and_boolean)==0,axis=0))*landmask_array) == 0, dtype = bool)
            #The next lines just for checking, uncomment if want to write in disk the last image of fmask
            #file_masked_overall = '/Users/erickpalacios/Documents/CONABIO/Tareas/Redisenio_MADMEX/clasificacion_landsat/landsat8/classification/fmask_mask_overall_images.tif'
            #options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})
            #create_raster_tiff_from_reference(extents_dictionary, file_masked_overall, index_masked_pixels_over_all_images, options_to_create)
 
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
                        LOGGER.info('Applying landmask and fmask')
                        data_array_resized[i,:,:][index_masked_pixels] = 0
                        LOGGER.info('Writing band %s of file %s in the stack: %s' % (str(i+1), bundle.path, output_file_stack_bands_list[i]))
                        new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_bands_list[i], options_to_create_empty_stacks)
                        create_raster_tiff_from_reference(extents_dictionary, output_file_stack_bands_list[i], data_array_resized[i, :, :], options_to_create_empty_stacks)
                    index_NaNs = numpy.array(data_array_resized== -9999, dtype = bool)
                    index_NaNs_2d = numpy.array(ndarray.all(data_array_resized==-9999,axis=0), dtype = bool)
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
                                    LOGGER.info('Masking Tasseled caps result: %s with fmask and landmask' %  output_file_stack_indexes_list[j+k])
                                    array[k,:,:][index_masked_pixels] = 0
                                    LOGGER.info('Masking Tasseled caps result: %s with Nan values' %  output_file_stack_indexes_list[j+k])
                                    array[k,:,:][index_NaNs[k,:,:]] = -9999
                                    new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_indexes_list[j+k], options_to_create_empty_indexes_stacks)
                                    create_raster_tiff_from_reference(extents_dictionary, output_file_stack_indexes_list[j+k], array[k, :, :], options_to_create_empty_indexes_stacks)
                            else:
                                LOGGER.info('Masking index: %s with fmask and landmask' %  output_file_stack_indexes_list[j])
                                array[index_masked_pixels] = 0
                                LOGGER.info('Masking index result: %s with Nan values' %  output_file_stack_indexes_list[j])
                                array[index_NaNs_2d] = -9999
                                new_options_for_create_raster_from_reference(extents_dictionary, raster.DATASET, datasets_stack_indexes_list[j], options_to_create_empty_indexes_stacks)
                                create_raster_tiff_from_reference(extents_dictionary, output_file_stack_indexes_list[j], array, options_to_create_empty_indexes_stacks)
                            array = None
                        
                    subset_counter+=1
                data_array_resized = None         
            
            LOGGER.info('Starting calculation of temporal metrics for images stacked bands')
            output_file_stack_bands_list_metrics = []
            for i in range(len(output_file_stack_bands_list)):
                LOGGER.info('Reading image: %s' % output_file_stack_bands_list[i])
                array = datasets_stack_bands_list[i].ReadAsArray()
                LOGGER.info('Calculating statistics: average, minimum, maximum, standard deviation, range of file %s' % output_file_stack_bands_list[i])
                array_metrics = calculate_statistics_metrics(array, [0,-9999])
                LOGGER.info('Applying fmask and landmask to array_metrics of file: %s' % output_file_stack_bands_list[i])
                LOGGER.info('Shape of array metrics: %s %s %s' % (array_metrics.shape[0], array_metrics.shape[1], array_metrics.shape[2]))     
                for j in range(array_metrics.shape[0]):
                    array_metrics[j,:,:][index_masked_pixels_over_all_images] = 0
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
                LOGGER.info('Calculating statistics: average, minimum, maximum, standard deviation, range of file %s' % output_file_stack_indexes_list[i])
                array_metrics = calculate_statistics_metrics(array, [0, -9999])
                LOGGER.info('Applying fmask and landmask to array_metrics of file: %s' % output_file_stack_indexes_list[i])
                LOGGER.info('Shape of array metrics: %s %s %s' % (array_metrics.shape[0], array_metrics.shape[1], array_metrics.shape[2]))
                #TODO: Is necessary the masking with 0 or we leave the -9999 ? ? ?     
                #for j in range(array_metrics.shape[0]):
                    #array_metrics[j,:,:][index_masked_pixels_over_all_images] = 0
                image_result = output_file_stack_indexes_list[i] + 'metrics'     
                options_to_create = new_options_for_create_raster_from_reference(extents_dictionary, raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
                create_raster_tiff_from_reference(extents_dictionary, image_result, array_metrics, options_to_create)
                output_file_stack_indexes_list_metrics.append(image_result)
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
            LOGGER.info('starging segmentation')
            command = 'segmentation_mac'
            hosts_from_command = get_host_from_command(command)
            LOGGER.info('The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname))
            remote = RemoteProcessLauncher(hosts_from_command[0])
            arguments = 'docker  run --rm -v ' + folder_and_bind_segmentation + ' -v ' + folder_and_bind_license + ' -v ' + folder_and_bind_ndvimetrics + ' segmentation/segmentation:v1 python /segmentation/segment.py ' + ndvimetrics
            arguments+=  ' --t ' + str(val_t) + ' -s ' + str(val_s) + ' -c ' + str(val_c) + ' --tile ' + str(val_tile) + ' --mp ' + str(val_mp) + ' --xt ' + str(val_xt) + ' --rows ' + str(val_rows) + ' --nodata ' + str(val_nodata)
            remote.execute(arguments)
            LOGGER.info('Finished segmentation')
            