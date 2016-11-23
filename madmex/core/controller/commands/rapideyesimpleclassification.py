'''
Created on 17/11/2016

@author: erickpalacios
'''
from madmex.core.controller.base import BaseCommand
import logging
from madmex.core.controller.commands import get_bundle_from_path
from madmex.configuration import SETTINGS
import shutil
from madmex.util import get_basename_of_file, create_directory_path
from madmex.persistence.driver import get_host_from_command
from madmex.remote.dispatcher import RemoteProcessLauncher
from madmex.mapper.data._gdal import \
    get_array_resized_from_reference_dataset, warp_raster_from_reference
from madmex.processing.raster import vectorize_raster, resample_numpy_array,\
    calculate_zonal_histograms, \
    get_objects_by_relative_proportion_from_raster_as_dataframe,\
    calculate_zonal_statistics, append_labels_to_array,\
    build_dataframe_from_array
from madmex.mapper.data.raster import create_raster_tiff_from_reference,\
    new_options_for_create_raster_from_reference
import subprocess
from madmex.mapper.data import raster, vector
import numpy
import pandas
from madmex.mapper.data.dataframe import join_dataframes_by_column_name,\
    reduce_dimensionality, create_names_of_dataframe_from_filename,\
    outlier_elimination_for_dataframe, generate_namesfile,\
    write_C5_result_to_csv, join_C5_dataframe_and_shape

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
        parser.add_argument('--image', nargs='*')
        parser.add_argument('--landmask_path', nargs='*')
        parser.add_argument('--outlier', nargs='*')
        
    def handle(self, **options):
        image_to_be_classified = options['image'][0]
        landmask_path = options['landmask_path'][0]
        outlier = options['outlier'][0]
        folder_results =  getattr(SETTINGS, 'BIG_FOLDER')
        shutil.copy(image_to_be_classified, folder_results)
        image_to_be_classified = folder_results +  get_basename_of_file(image_to_be_classified)
        
        '''
        image_for_segmentation = '/results/' +  get_basename_of_file(image_to_be_classified)
        LOGGER.info('Starting segmentation with: %s' % image_for_segmentation)   
        val_t = 50
        val_s = 0.7
        val_c = 0.3
        val_xt = 40
        val_rows = 625
        val_tile = True
        val_mp = True
        
        folder_and_bind_segmentation = getattr(SETTINGS, 'FOLDER_SEGMENTATION')
        folder_and_bind_license = getattr(SETTINGS, 'FOLDER_SEGMENTATION_LICENSE')
        folder_and_bind_image= folder_results  +  ':/results'
        LOGGER.info('starting segmentation')
        command = 'run_container'
        hosts_from_command = get_host_from_command(command)
        LOGGER.info('The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname))
        remote = RemoteProcessLauncher(hosts_from_command[0])
        arguments = 'docker  run --rm -v ' + folder_and_bind_segmentation + ' -v ' + folder_and_bind_license + ' -v ' + folder_and_bind_image + ' madmex/segmentation python /segmentation/segment.py ' + image_for_segmentation
        arguments+=  ' -t ' + str(val_t) + ' -s ' + str(val_s) + ' -c ' + str(val_c) + ' --tile ' + str(val_tile) + ' --mp ' + str(val_mp) + ' --xt ' + str(val_xt) + ' --rows ' + str(val_rows)
        remote.execute(arguments)
        
        LOGGER.info('Finished segmentation')
        
        
        image_segmentation_file = image_to_be_classified + '_' + str(val_t) + '_' + ''.join(str(val_s).split('.'))+ '_' + ''.join(str(val_c).split('.')) + '.tif'
        LOGGER.info('Starting vectorization of segmentation file: %s' % image_segmentation_file)
        image_segmentation_shp_file = image_segmentation_file + '.shp'
        vectorize_raster(image_segmentation_file, 1, image_segmentation_shp_file, 'objects', 'id')
        LOGGER.info('Finished vectorization: %s' % image_segmentation_shp_file)
        
        gdal_format = 'GTiff'
        image_to_be_classified_class = raster.Data(image_to_be_classified, gdal_format)
        width, height, bands = image_to_be_classified_class.get_attribute(raster.DATA_SHAPE)
        LOGGER.info('Identifying landmask %s' % landmask_path)
        bundle = _get_bundle_from_path(landmask_path)
        if bundle:
            LOGGER.info('Directory %s is a %s bundle', landmask_path, bundle.get_name())
            LOGGER.info('Rasterizing vector shape')
            options_to_create = new_options_for_create_raster_from_reference(image_to_be_classified_class.metadata, raster.DATA_SHAPE, (width,height, 1), {})
            dataset_landmask_rasterized = create_raster_tiff_from_reference(image_to_be_classified_class.metadata, '', None, options_to_create)
            bundle.rasterize(dataset_landmask_rasterized, [1], [1]) #the rasterized process changes the dataset
            options_to_create = new_options_for_create_raster_from_reference(image_to_be_classified_class.metadata, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
            image = folder_results + 'landmask_rasterized.tif'
            create_raster_tiff_from_reference(image_to_be_classified_class.metadata, image, dataset_landmask_rasterized.ReadAsArray(), options_to_create)
            LOGGER.info('Finished rasterizing vector shape')        
        
        LOGGER.info('Polygonizing the landmask rasterized')
        landmask_folder = folder_results  + 'landmask_from_rasterize/'
        layer_landmask = 'landmask'
        landmask_file = landmask_folder + layer_landmask + '.shp'  
        layer_landmask = 'landmask'

        vectorize_raster(folder_results + 'landmask_rasterized.tif', 1, landmask_folder, layer_landmask, 'id')
        LOGGER.info('Folder of polygon: %s' % landmask_folder)
        image_segmentation_file_class = raster.Data(image_segmentation_file, gdal_format)
        LOGGER.info('Reading array of %s' % image_for_segmentation)
        array_sg_raster = image_segmentation_file_class.read_data_file_as_array()
        unique_labels_for_objects = numpy.unique(array_sg_raster)
        LOGGER.info('Calculating zonal stats for :%s' % image_to_be_classified)
        LOGGER.info('Reading array of %s' % image_to_be_classified)
        array_image_to_be_classified = image_to_be_classified_class.read_data_file_as_array()       
        array_zonal_statistics = calculate_zonal_statistics(array_image_to_be_classified, array_sg_raster, unique_labels_for_objects)
        LOGGER.info('finished zonal statistics')

        array_zonal_statistics_labeled = append_labels_to_array(array_zonal_statistics, unique_labels_for_objects)
        LOGGER.info('Shape of array of zonal statistics labeled %s %s' % (array_zonal_statistics_labeled.shape[0], array_zonal_statistics_labeled.shape[1]))
        LOGGER.info('Building data frame')
        dataframe_zonal_statistics = create_names_of_dataframe_from_filename(build_dataframe_from_array(array_zonal_statistics_labeled.T), array_zonal_statistics_labeled.shape[0], get_basename_of_file(image_to_be_classified))
        LOGGER.info('Filling NaN with zeros')            
        dataframe_zonal_statistics = dataframe_zonal_statistics.fillna(0)
        file_name = folder_results + 'dataframe_zonal_statistics'
        dataframe_zonal_statistics.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
        
        
        LOGGER.info('Working with the training data')
        training_data_file = getattr(SETTINGS, 'TRAINING_DATA')
        LOGGER.info('Clipping training_data_file: %s with: %s' % (training_data_file, landmask_file))
        
        training_data_file_clipped = folder_results  + get_basename_of_file(training_data_file) + '_cropped_subprocess_call.tif'
        command = [
                    'gdalwarp', '-cutline', landmask_file,
                    '-crop_to_cutline', '-of', 'GTiff','-co', 'compress=lzw', '-co', 'tiled=yes', training_data_file, training_data_file_clipped
                    ]
        subprocess.call(command)
        LOGGER.info('Finished clipping of training data file')
            
        LOGGER.info('Starting warping of file: %s according to %s ' % (training_data_file_clipped, image_segmentation_file))
        dataset_warped_training_data_file = warp_raster_from_reference(training_data_file_clipped, image_segmentation_file_class.data_file, None)
        LOGGER.info('Starting resizing of array of training file: %s' % training_data_file_clipped)

        array_resized_and_warped_training_data_file = get_array_resized_from_reference_dataset(dataset_warped_training_data_file, image_segmentation_file_class.data_file)

        import gdal
        training_data_file_resized_and_warped =  folder_results + get_basename_of_file(training_data_file) + '_resized_and_warped.tif'
        options_to_create = new_options_for_create_raster_from_reference(image_to_be_classified_class.metadata,  raster.GDAL_CREATE_OPTIONS, ['TILED=YES', 'COMPRESS=LZW', 'INTERLEAVE=BAND'], {})
        create_raster_tiff_from_reference(image_to_be_classified_class.metadata, training_data_file_resized_and_warped, array_resized_and_warped_training_data_file, options_to_create, data_type = gdal.GDT_Int32)
        LOGGER.info('Starting resampling')
        array_training_data_resampled = resample_numpy_array(array_resized_and_warped_training_data_file, width, height, interpolation = 'nearest')
        training_data_file_resampled = folder_results + get_basename_of_file(training_data_file) + '_resampled_from_resized_and_warped.tif'        
        create_raster_tiff_from_reference(image_to_be_classified_class.metadata, training_data_file_resampled, array_training_data_resampled, options_to_create, data_type = gdal.GDT_Int32)
 
        LOGGER.info('Calculating zonal histograms for file: %s according to: %s' % (training_data_file_resampled, image_segmentation_file))
        unique_classes = numpy.unique(array_training_data_resampled)
        array_of_distribution_of_classes_per_object_segmentation = calculate_zonal_histograms(array_training_data_resampled, unique_classes, array_sg_raster, unique_labels_for_objects)
        LOGGER.info('Shape of zonal histogram: %s %s' % (array_of_distribution_of_classes_per_object_segmentation.shape[0], array_of_distribution_of_classes_per_object_segmentation.shape[1]))
        array_training_data_resampled = None
        LOGGER.info('Getting objects that have a class of at least .75 proportion within zonal histogram')
        dataframe_of_objects_for_training_data = get_objects_by_relative_proportion_from_raster_as_dataframe(array_of_distribution_of_classes_per_object_segmentation, unique_labels_for_objects, unique_classes, ["id", "given"], 0.75)
        file_name = folder_results + 'dataframe_of_objects_for_training_data'
        dataframe_of_objects_for_training_data.to_csv(file_name, sep='\t', encoding='utf-8', index = False)
        LOGGER.info('Number of rows and columns of dataframe of pure objects of training data %s %s' % (len(dataframe_of_objects_for_training_data.index), len(dataframe_of_objects_for_training_data.columns) ))        
        array_of_distribution_of_classes_per_object_segmentation = None
        dataframe_of_objects_for_training_data = None
        dataframe_of_objects_for_training_data = pandas.read_csv(file_name, sep='\t')
        LOGGER.info('Joining dataframe of dataframe zonal statistics and dataframe of objects of training data')
        dataframe_all_joined_classified = join_dataframes_by_column_name([dataframe_zonal_statistics, dataframe_of_objects_for_training_data], 'id')
        LOGGER.info('Number of rows and columns of dataframe joined %s %s' % (len(dataframe_all_joined_classified.index), len(dataframe_all_joined_classified.columns) ))        
            
        if outlier == 'True':
                LOGGER.info('Starting outlier elimination with dataframe of zonal statistics and dataframe of pure objects of training data')
                LOGGER.info('Starting principal component analysis')
                array_reduced_pca = reduce_dimensionality(dataframe_all_joined_classified, .95, ['id', 'given'])
                LOGGER.info('Shape of reduced array of zonal statistics and pure objects of training data by pca: %s %s' %(array_reduced_pca.shape[0], array_reduced_pca.shape[1]) )
                labels_of_objects_reduced_dataframe = dataframe_all_joined_classified['id'].values
                LOGGER.info('Appending labels')
                array_reduced_pca_labeled = append_labels_to_array(array_reduced_pca.T, labels_of_objects_reduced_dataframe)
                LOGGER.info('Shape of array reduced by pca and labeled: %s %s' %(array_reduced_pca_labeled.shape[0], array_reduced_pca_labeled.shape[1]))
                LOGGER.info('Building data frame')
                dataframe_reduced_pca_file = folder_results + 'dataframe_joined_for_zonal_statistics_and_pure_objects_of_training_data_reduced_by_pca'
                dataframe_reduced_pca = create_names_of_dataframe_from_filename(build_dataframe_from_array(array_reduced_pca_labeled.T), array_reduced_pca_labeled.shape[0], get_basename_of_file(dataframe_reduced_pca_file))
                dataframe_reduced_pca.to_csv(dataframe_reduced_pca_file, sep=',', encoding='utf-8', index = False)
                LOGGER.info('Starting with elimination of outliers')
                LOGGER.info('Joining reduced dataframe by pca with object ids and dataframe of pure objects of training data')
                dataframe_reduced_pca_with_classes= join_dataframes_by_column_name([dataframe_reduced_pca, dataframe_of_objects_for_training_data], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined: (%s,%s)' %(len(dataframe_reduced_pca_with_classes.index), len(dataframe_reduced_pca_with_classes.columns)))
                dataframe_reduced_pca_with_classes.to_csv(dataframe_reduced_pca_file + 'classes', sep = ',', encoding = 'utf8', index = False)
                unique_classes = numpy.unique(dataframe_of_objects_for_training_data['given'].values)
                object_ids_outlier_elimination = outlier_elimination_for_dataframe(dataframe_reduced_pca_with_classes, 'id', 'given', 'id', 3, unique_classes, 0.15)
                object_ids_outlier_elimination_file = folder_results + 'dataframe_object_ids_outlier_elimination'
                object_ids_outlier_elimination.to_csv(object_ids_outlier_elimination_file, sep = ',', encoding = 'utf-8', index = False)
                LOGGER.info('Joining all dataframes according to ids of outlier elimination ')
                dataframe_all_joined_classified = join_dataframes_by_column_name([object_ids_outlier_elimination, dataframe_all_joined_classified], 'id')
                LOGGER.info('Number of rows and columns of dataframe joined classified: (%s,%s)' %(len(dataframe_all_joined_classified.index), len(dataframe_all_joined_classified.columns)))
            
        dataframe_zonal_statistics['given'] = '?'
        LOGGER.info('Number of rows and columns of dataframe for classifying: (%s,%s)' %(len(dataframe_zonal_statistics.index), len(dataframe_zonal_statistics.columns)))
        index_of_objects_not_id_zero = dataframe_zonal_statistics['id'] > 0
        dataframe_all_joined_for_classifying = dataframe_zonal_statistics[index_of_objects_not_id_zero]
        LOGGER.info('Number of rows and columns of dataframe for classifying after removing object with id zero: (%s,%s)' %(len(dataframe_all_joined_for_classifying.index), len(dataframe_all_joined_for_classifying.columns)))
            
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
        '''
        
        
                
        gdal_format = 'GTiff'
        image_to_be_classified_class = raster.Data(image_to_be_classified, gdal_format)
        image_segmentation_shp_file = folder_results + '1947604_2015-01-05_RE1_3A_298768.tif_50_07_03.tif.shp'
        width, height, bands = image_to_be_classified_class.get_attribute(raster.DATA_SHAPE)
        import gdal
        
        
        command = 'run_container'
        hosts_from_command = get_host_from_command(command)
        LOGGER.info('The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname))
        remote = RemoteProcessLauncher(hosts_from_command[0])
        folder_and_bind_c5 = folder_results + ':/datos'
                
        arguments = 'docker  run --rm -v ' + folder_and_bind_c5  + ' madmex/c5_execution ' + 'c5.0 -b -f /datos/C5'
        LOGGER.info('Beginning C5') 
        remote.execute(arguments)
    
        LOGGER.info('Begining predict')
        arguments = 'docker  run --rm -v ' + folder_and_bind_c5  + ' madmex/c5_execution ' + 'predict -f /datos/C5'
        remote = RemoteProcessLauncher(hosts_from_command[0])
        output = remote.execute(arguments, True)
        LOGGER.info('Writing C5 result to csv')
        C5_result = write_C5_result_to_csv(output, folder_results)  
        LOGGER.info('Using result of C5: %s for generating land cover shapefile and raster image' % C5_result)
        LOGGER.info('Using result of C5 for generating land cover shapefile and raster image')        
        C5_result = folder_results + 'C5_result.csv'
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
            options_to_create = new_options_for_create_raster_from_reference(image_to_be_classified_class.metadata, raster.DATA_SHAPE, (width,height, 1), {})
            dataset_shape_sg_and_c5_rasterized = create_raster_tiff_from_reference(image_to_be_classified_class.metadata, '', None, options_to_create)
            bundle.rasterize(dataset_shape_sg_and_c5_rasterized, [1], None, ["ATTRIBUTE=predicted" ]) #the rasterized process changes the dataset
            options_to_create = new_options_for_create_raster_from_reference(image_to_be_classified_class.metadata, raster.GDAL_CREATE_OPTIONS, ['COMPRESS=LZW'], {})            
            image =folder_results + 'madmex_lcc_prueba.tif'
            create_raster_tiff_from_reference(image_to_be_classified_class.metadata, image, dataset_shape_sg_and_c5_rasterized.ReadAsArray(), options_to_create, data_type = gdal.GDT_Int32)
            LOGGER.info('Finished rasterizing vector shape')
            LOGGER.info('Rasterizing vector shape to get confidence tif')
            bundle.rasterize(dataset_shape_sg_and_c5_rasterized, [1], None, ["ATTRIBUTE=confidence" ])
            image =folder_results + 'madmex_lcc_confidence_prueba.tif'            
            create_raster_tiff_from_reference(image_to_be_classified_class.metadata, image, dataset_shape_sg_and_c5_rasterized.ReadAsArray(), options_to_create)
            LOGGER.info('Finished rasterizing vector shape')
        
        LOGGER.info('Finished workflow classification :)')
 
