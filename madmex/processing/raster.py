'''
Created on 19/04/2016

@author: erickpalacios
'''
import numexpr
import numpy
from numpy import NaN
from scipy.stats import nanstd, nanmean
#from scipy import  ndimage
import scipy.ndimage
from madmex.mapper.data._gdal import get_projection, get_dataset, get_band,\
    _get_geotransform, get_geotransform, get_datashape_from_dataset
from madmex.mapper.data.vector import create_empty_layer
import gdal
import ogr
from pandas.core.frame import DataFrame
from numpy import ndarray
from scipy.misc import imresize
import logging
from scipy.ndimage.filters import sobel
import pandas
from sklearn.decomposition import PCA

LOGGER = logging.getLogger(__name__)
AEROSOL_L8 = 1
BLUE_L8 = 2
GREEN_L8 = 3
RED_L8 = 4
NIR_L8 = 5
SWIR_L8 = 6
LANDSAT_5_DN = 'Landsat 5 DN'
LANDSAT_5 = 'Landsat 5'
LANDSAT_7 = 'Landsat 7'
LANDSAT_8 = 'Landsat 8 surfaces reflectances' #Defined according to get_name() function of module bundle landsat8sr
OVERFLOW_LEVEL = 1.e309
tc_coefficents = {LANDSAT_5:None,
                            LANDSAT_7:None,
                            LANDSAT_8:None
                            }
tc_coefficents[LANDSAT_5_DN] = numpy.array([[ 0.2909, 0.2493, 0.4806, 0.5568, 0.4438, 0.1706, 10.3695],
                             [-0.2728, -0.2174, -0.5508, 0.7221, 0.0733, -0.1648, -0.7310],
                             [ 0.1446, 0.1761, 0.3322, 0.3396, -0.6210, -0.4186, -3.3828],
                             [ 0.8461, -0.0731, -0.4640, -0.0032, -0.0492, -0.0119, 0.7879],
                             [ 0.0549, -0.0232, 0.0339, -0.1937, 0.4162, -0.7823, -2.4750],
                             [ 0.1186, -0.8069, 0.4094, 0.0571, -0.0228, 0.0220, -0.0336]])
        
tc_coefficents[LANDSAT_5] = numpy.array([[0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863],
                             [-0.2848, -0.2435, -0.5436, 0.7243, 0.0840, -0.1800],
                             [ 0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572],
                             [ -0.8242, 0.0849, 0.4392, -0.0580, -0.2012, -0.2768],
                             [ -0.3280, 0.0549, 0.1075, 0.1855, -0.4357, 0.8085],
                             [ 0.1084, -0.9022, 0.4120, -0.0573, -0.0251, 0.0238]])

tc_coefficents[LANDSAT_7] = numpy.array([[ 0.3561, 0.3972, 0.3904, 0.6966, 0.2286, 0.1596],
                             [-0.3344, -0.3544, -0.4556, 0.6966, -0.0242, -0.2630],
                             [ 0.2626, 0.2141, 0.0926, 0.0656, -0.7629, -0.5388],
                             [ 0.0805, -0.0498, 0.1950, -0.1327, 0.5752, -0.7775],
                             [ -0.7252, -0.0202, 0.6683, 0.0631, -0.1494, -0.0274],
                             [ 0.4000, -0.8172, 0.3832, 0.0602, -0.1095, 0.0985]])

# according to https://geonet.esri.com/docs/DOC-1868
# valid for bands 2-3-4-5-6-7
tc_coefficents[LANDSAT_8] = numpy.array([[ 0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872],
                             [-0.2941, -0.243, -0.5424, 0.7276, -0.0713, -0.1608],
                             [ 0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559],
                             [ -0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773],
                             [ -0.3294, 0.0557, 0.1056, 0.1855, -0.4349, -0.8085],
                             [ 0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252]])


def calculate_ndvi(band4, band3, mode=numpy.int16):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    Returns an image of two bands
    '''
    spectralindex = numexpr.evaluate("100 * (1.*(band4 - band3) / (band4 + band3))")
    spectralindex[numpy.where(band4 - band3 == 0)] = 0
    spectralindex[numpy.where(numpy.logical_and(band4 == 0, band3 == 0))] = None
    return spectralindex.astype(mode)

def calculate_ndvi_2(array, type_satellite):
    '''
    Calculate the normalized differenced vegetation index of a raster image using the third
    and fourth band. 
    band_a is the fourth and band_b is the third in the case of landsat7
    Returns an image of two bands
    '''
    if type_satellite == LANDSAT_8:
        band_a = array[NIR_L8-1, :, :]
        band_b = array[RED_L8-1, :, :]
    spectral_index = numexpr.evaluate("1.0 * (band_a - band_b) / (band_a + band_b)")
    spectral_index[numpy.where(numpy.logical_and(band_a == 0, band_b == 0))] = -9999
    index_inf_values = abs(spectral_index) >= OVERFLOW_LEVEL
    spectral_index[index_inf_values] = -9999
    return spectral_index
def calculate_sr(array, type_satellite):
    '''
    Calculates the Simple Ratio (Fourth band / Third band) of a raster image
    band_a is the fourth and band_b is the third in the case of landsat7
    '''
    if type_satellite == LANDSAT_8:
        band_a = array[NIR_L8-1, :, :]
        band_b = array[RED_L8-1, :, :]
    spectralindex = numexpr.evaluate("1.0 * (1.*band_a / band_b)")
    index_zeros = numpy.where(band_b == 0)
    index_inf_values  = abs(spectralindex) >= OVERFLOW_LEVEL
    spectralindex[index_zeros] = -9999
    spectralindex[index_inf_values] = -9999
    return spectralindex
def calculate_evi(array, type_satellite):
    '''
    Calculate the EVI (Enhanced Vegetation Index) of a raster image using the one, third and fourth band
    band_a is the fourth, band_b is the third and band_c is one in the case of landsat7
    '''
    if type_satellite == LANDSAT_8:
        band_a = array[NIR_L8-1, :, :]
        band_b = array[RED_L8-1, :, :]
        band_c = array[BLUE_L8-1, :, :]
    spectralindex = numexpr.evaluate("1.0 * (2.5 * (band_a - band_b) / (band_a + 6.0 * band_b - 7.5 * band_c + 1))")
    index_zeros_denominator = band_a+6.0*band_b-7.5*band_c+1 == 0
    index_inf_values  = abs(spectralindex) >= OVERFLOW_LEVEL
    spectralindex[index_inf_values] = -9999
    spectralindex[index_zeros_denominator] = -9999
    return spectralindex
def calculate_arvi(array, type_satellite):
    '''
    Calculate the ARVI (Atmospherically Resistant Vegetation Index) of a raster image
    band_a is the fourth, band_b is the third and band_c is one in the case of landsat7    
    '''
    if type_satellite == LANDSAT_8:
        band_a = array[NIR_L8-1, :, :]
        band_b = array[RED_L8-1, :, :]
        band_c = array[BLUE_L8-1, :, :]
    spectralindex = numexpr.evaluate("1.0 * (1.*(band_a - (2 * band_b - band_c)) / (band_a + (2 * band_b - band_c)))")
    index_zeros_denominator = band_a + (2 * band_b - band_c) == 0
    spectralindex[index_zeros_denominator] = -9999
    index_inf_values  = abs(spectralindex) >= OVERFLOW_LEVEL
    spectralindex[index_inf_values] = -9999
    return spectralindex
def calculate_tasseled_caps(array, type_satellite):
    number_of_bands, height, width = array.shape
    bands = numpy.zeros((number_of_bands, width * height))
    for i in range(number_of_bands):
        bands[i, :] = numpy.ravel(array[i, :, :])
        bands[i,:] = numpy.nan_to_num(bands[i,:]) #This is an option to handle the entries with value of -9999
    tc3d = numpy.zeros((number_of_bands, height, width))
    tc2d = numpy.dot(tc_coefficents[type_satellite], bands)
    for i in range(number_of_bands):
        tc3d[i, :, :] = tc2d[i, :].reshape(1, height, width)
    index_inf_values  = abs(tc3d) >= OVERFLOW_LEVEL
    tc3d[index_inf_values] = -9999
    return tc3d
def calculate_index(band_a, band_b):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    Returns an image of two bands
    '''
    spectral_index = numexpr.evaluate("1.0 * (band_a - band_b) / (band_a + band_b)")
    spectral_index[numpy.where(band_a - band_b == 0)] = 0.00000001
    spectral_index[numpy.where(numpy.logical_and(band_a + band_b < 0.1, band_a + band_b > -0.1))] = -9999
    spectral_index[numpy.where(numpy.logical_and(band_a == -9999, band_b == -9999))] = -9999
    return spectral_index

def orig(band_a, band_b, mode=numpy.int16):
    '''
    Calculate the normalized differenced vegetation index of a raster image
    Returns an image of two bands
    '''
    spectralindex = numexpr.evaluate("(band_a - band_b) / (band_a + band_b)")
    spectralindex[numpy.where(band_a - band_b == 0)] = 0
    spectralindex[numpy.where(numpy.logical_and(band_a == -9999, band_b == -9999))] = -9999
    return spectralindex.astype(mode)
def mask_values(data, values):
    '''
    Return a boolean array of 0's and 1's 
    The 0's are the values in the list values
    '''
    #base = numpy.zeros((data.shape), numpy.int8)
    masked = numpy.zeros((data.shape), numpy.int8)
    for no_data in values:
        numpy.putmask(masked, data == no_data , 1)
    #base = base + masked
    return numpy.invert(numpy.array(masked, dtype = bool)).astype(numpy.int8)
def calculate_statistics_metrics(array, no_data_values):
    for no_data_value in no_data_values:
        numpy.putmask(array, array == no_data_value, NaN)
    zonalstats = []
    statsmin = numpy.nanmin(array, axis = 0)
    statsmax = numpy.nanmax(array, axis = 0)
    statsrange = statsmax-statsmin
    #The resulting metrics have no data value of -9999:
    numpy.putmask(statsmin, numpy.isnan(statsmin), -9999)
    index_inf_values  = abs(statsmin) >= OVERFLOW_LEVEL
    statsmin[index_inf_values] = -9999
    zonalstats.append(statsmin)
    statsmin = None    
    numpy.putmask(statsmax, numpy.isnan(statsmax), -9999)
    index_inf_values  = abs(statsmax) >= OVERFLOW_LEVEL
    statsmax[index_inf_values] = -9999
    zonalstats.append(statsmax)
    statsmax =None
    numpy.putmask(statsrange, numpy.isnan(statsrange), -9999)
    index_inf_values  = abs(statsrange) >= OVERFLOW_LEVEL
    statsrange[index_inf_values] = -9999
    zonalstats.append(statsrange)
    statsrange = None
    #statsmean = nanmean(array, axis = 0)
    statsmean = numpy.nanmean(array, axis = 0)
    numpy.putmask(statsmean, numpy.isnan(statsmean), -9999)
    index_inf_values  = abs(statsmean) >= OVERFLOW_LEVEL
    statsmean[index_inf_values] = -9999
    zonalstats.append(statsmean)
    statsmean = None    
    #statsstd = nanstd(array, axis = 0)
    statsstd = numpy.nanstd(array, axis = 0)
    numpy.putmask(statsstd, numpy.isnan(statsstd), -9999)
    index_inf_values  = abs(statsstd) >= OVERFLOW_LEVEL
    statsstd[index_inf_values] = -9999
    zonalstats.append(statsstd)
    statsstd = None
    array_stats = numpy.array(zonalstats)
    zonalstats = None
    return array_stats
def vectorize_raster(source, gdal_band_number, target_vector_layer_filename, layer_name, field_name_of_layer):
    import os
    if os.path.isfile(source):
        ds = get_dataset(source)
    else:
        #TODO: test if is dataset
        LOGGER.info('dataset')
    projection_reference = ds.GetProjection()
    data_layer, ds_layer=create_empty_layer(target_vector_layer_filename, layer_name, projection_reference)
    band = ds.GetRasterBand(gdal_band_number)
    field = ogr.FieldDefn(field_name_of_layer, ogr.OFTInteger)
    data_layer.CreateField(field)
    return gdal.Polygonize(band, None, data_layer, 0, [])
def calculate_zonal_statistics(array, array_labeled, labels):
    function_min_zonal = lambda x: scipy.ndimage.measurements.minimum(x, labels = array_labeled, index= labels)
    function_max_zonal =lambda x: scipy.ndimage.measurements.maximum(x, labels = array_labeled, index= labels)
    function_mean_zonal =lambda x: scipy.ndimage.measurements.mean(x, labels = array_labeled, index= labels)
    function_std_zonal =lambda x: scipy.ndimage.measurements.standard_deviation(x, labels = array_labeled, index= labels)
    if len(array.shape) == 3:
        #TODO: Instead of the next two lines, why don't we create segmentations files based
        #on each of the indexes so we can use them as the argument array_labeled of this function 
        #and it's corresponding labels argument ???
        index_NaNs_2d = numpy.array(ndarray.all(array==-9999,axis=0), dtype = bool) #The arguments  
        #array_labeled and labels are based on the NDVI index, so it's possible that no data values 
        #of the ARVI index (for example) are present in the argument array and these values are labeled 
        #different in the NDVI index, that's the reason of this line and the next one 
        array_labeled[index_NaNs_2d] = 0 #we re-labeled the array_labeled according of the array
        #of the index
        LOGGER.info('Calculating zonal minimum')
        arr_min = map(function_min_zonal,array)
        LOGGER.info('Calculating zonal maximum')
        arr_max = map(function_max_zonal,array)
        LOGGER.info('Calculating zonal mean')
        arr_mean = map(function_mean_zonal,array)
        LOGGER.info('Calculating zonal standard deviation')
        arr_std = map(function_std_zonal,array)
        return numpy.concatenate((arr_min, arr_max, arr_mean, arr_std), axis=0)
    else:
        index_NaNs_2d = numpy.array(array == -9999, dtype =bool)
        array_labeled[index_NaNs_2d] = 0
        LOGGER.info('Calculating zonal minimum')
        arr_min = function_min_zonal(array)
        LOGGER.info('Calculating zonal maximum')
        arr_max = function_max_zonal(array)
        LOGGER.info('Calculating zonal mean')
        arr_mean = function_mean_zonal(array)
        LOGGER.info('Calculating zonal standard deviation')
        arr_std = function_std_zonal(array)
    #return numpy.concatenate((map(function_min_zonal,array),map(function_max_zonal,array), map(function_mean_zonal,array), map(function_std_zonal,array)),axis=0)
        return numpy.array((arr_min, arr_max, arr_mean, arr_std))
    #number_of_bands = array.shape[0]
    #fmin_zonal = lambda dim: numpy.array([numpy.nanmin(array[dim,array_labeled == x]) for x in labels])
    #fmax_zonal = lambda dim: numpy.array([numpy.nanmax(array[dim,array_labeled == x]) for x in labels])
    #fmean_zonal = lambda dim: numpy.array([numpy.nanmean(array[dim,array_labeled == x]) for x in labels])
    #fstd_zonal= lambda dim: numpy.array([numpy.nanstd(array[dim,array_labeled == x]) for x in labels])
    #return numpy.concatenate((map(fmin_zonal, [dim for dim in range(number_of_bands)]), map(fmax_zonal, [dim for dim in range(number_of_bands)]), map(fmean_zonal, [dim for dim in range(number_of_bands)]), map(fstd_zonal, [dim for dim in range(number_of_bands)]) ),axis=0)
    #return numpy.array([numpy.array([numpy.nanmin(array[:,array_labeled==x],axis=1), numpy.nanmax(array[:,array_labeled==x],axis=1), numpy.nanmean(array[:,array_labeled==x],axis=1), numpy.nanstd(array[:,array_labeled==x],axis=1)]).flatten() for x in labels]).T
 
def append_labels_to_array(array, labels):
    return numpy.concatenate((labels.reshape(1, len(labels)), array), axis = 0)
    #return numpy.concatenate((labels.reshape(len(labels), 1), array), axis = 1)
def build_dataframe_from_array(array):
    return pandas.DataFrame(array)
def resample_numpy_array(array, width, height, interpolation = None, mode = 'F'):
    if len(array.shape) == 3:
        bands, y, x= array.shape
        LOGGER.info('Resampling using width %s and height %s' %(width, height))
        data_resampled = numpy.zeros([bands, height, width])
        for band in bands:
            data_resampled[band, :, :] = imresize(array[band, :, :], [height, width], interp = interpolation, mode = mode)
    else:
        LOGGER.info('Resampling using width %s and height %s' %(width, height))
        data_resampled = imresize(array, [height, width], interp = interpolation, mode = mode)
    LOGGER.info('Array resampled')
    if len(array.shape) == 3:
        LOGGER.info('Shape of array resampled: %s %s %s' %(data_resampled.shape[0], data_resampled.shape[1], data_resampled.shape[2]))
    else:
        LOGGER.info('Shape of array resampled: %s %s' %(data_resampled.shape[0], data_resampled.shape[1]))
    return data_resampled
def get_gradient_of_image(array):
    return calculate_filter_Sobel(array)
def calculate_filter_Sobel(array, mode_type = "constant"):
    sx = sobel(array, axis = 0, mode = mode_type)
    sy = sobel(array, axis = 1, mode = mode_type)
    return numpy.hypot(sx,sy)
def get_grid(dimension, resolution,griddistance,chipsize,diagonal=True):
    '''
    Calculates a binary mask array of sample chips for a given input image dimension
    #TODO: Do we need to rewrite this function??... right now is a copy-paste from old madmex, works ok
    dimension: image/array dimension (as result of numpy shape). must be 2-dimensional.
    resolution: pixel size in image map projection units        
    griddistance: distance between nodal points in sample grid in image map projection unit
    chipsize: Size (length) of the quadratic chips in the image map projection unit
    diagonal: whether or not to also fill diagonal in between the grid    
    ''' 
 
    data = numpy.zeros(dimension)
    xsize = int(data.shape[1])
    ysize =int(data.shape[0])

    blocksize = int(numpy.round(chipsize/resolution))
    distsize = int(numpy.round(griddistance/resolution))
    firstblock = numpy.zeros((blocksize,xsize))
    xhalfoffset = int(numpy.round(blocksize/2))
    
    for x in range(xhalfoffset,xsize,distsize):
        firstblock[:,x:x+blocksize] = 1
        
    for y in range(xhalfoffset,ysize,distsize):
        dy = data.shape[0]-y
        if dy < blocksize:
            data[y:,:] = firstblock[:dy,:]
        else:
            data[y:y+blocksize,:] = firstblock     

    if diagonal:
        secondblock = numpy.zeros((blocksize,xsize))
        for x in range(xhalfoffset+numpy.round(distsize/2),xsize,distsize):
            secondblock[:,x:x+blocksize] = 1
            
        for y in range(xhalfoffset+numpy.round(distsize/2),ysize,distsize):
            dy = data.shape[0]-y
            if dy < blocksize:
                data[y:,:] = secondblock[:dy,:]
            else:
                data[y:y+blocksize,:] = secondblock         
    return data
def calculate_zonal_histograms(array, classes, array_labeled, labels):
    '''
    Calculates zonal histogram of a discrete raster image (e.g. classification result) over objects in a label raster
    '''
    zonal_histogram = scipy.ndimage.measurements.histogram(array, 0, max(classes), max(classes) + 1, labels=array_labeled, index=labels)
    return numpy.vstack(zonal_histogram)
def get_pure_objects_from_raster_as_dataframe(array_histogram_of_objects, unique_objects, unique_classes, names_of_columns):
    '''
    Remove mixed objects (those which have more than one class) and keep the pure ones
    '''
    n_objects, n_classes = array_histogram_of_objects.shape
    n_zeros = numpy.sum(array_histogram_of_objects == 0, axis = 1) 
    one_class_in_histogram_index = n_zeros == n_classes-1 #get the indexes of pure objects
    subset_objects = unique_objects[one_class_in_histogram_index]
    subset_histogram = array_histogram_of_objects[one_class_in_histogram_index,:]
    LOGGER.info("Shape of array with histogram of pure objects, number_of_objects: %s, number_of classes: %s" % (subset_histogram.shape[0], subset_histogram.shape[1]))
    class_list = numpy.zeros(subset_histogram.shape[0]) 
    class_range = numpy.arange(max(unique_classes)+1)
    for o in range(subset_histogram.shape[0]):
        idx = subset_histogram[o,:] > 0 #Get the index of class for object "o"
        if sum(idx) > 0: # if class index has been found
            a_class = class_range[idx] # get the class value
            class_list[o] = a_class # add class value to list
    nonzero_classes =  class_list > 0 # index of classes with value greater 0 (we ignore the zero class, cause is nodata: fmask or NaN's values)
    class_list = class_list[nonzero_classes] # all non zero class labels
    subset_objects = subset_objects[nonzero_classes] # final object 
    df = pandas.DataFrame(numpy.vstack([subset_objects,class_list]).T) # stack and create dataframe
    df.columns = [names_of_columns[0], names_of_columns[1]]
    return df
def get_objects_by_relative_proportion_from_raster_as_dataframe(array_histogram_of_objects, unique_objects, unique_classes, names_of_columns, proportion):
    '''
    Get objects which at least have a proportion of a class inside them
    '''
    print unique_classes
    #if 0 in unique_classes:
        #index_of_class_nonzero_numbered = [k for k in range(0,len(unique_classes)) if unique_classes[k] > 0]
        #print index_of_class_nonzero_numbered
        #array_histogram_of_objects = array_histogram_of_objects[:, index_of_class_nonzero_numbered]
        #array_histogram_of_objects = array_histogram_of_objects[:, 1:]
    #LOGGER.info("Shape of array histogram removing class zero, number_of_objects: %s, number_of classes: %s" % (array_histogram_of_objects.shape[0], array_histogram_of_objects.shape[1]))
    #index_of_class_nonzero = numpy.array(unique_classes > 0, dtype = bool)
    #unique_classes = unique_classes[index_of_class_nonzero]
    #print unique_classes
    n_sum = numpy.sum(array_histogram_of_objects, axis = 1)
    indexes_of_objects_with_a_class_label = n_sum > 0
    subset_objects = unique_objects[indexes_of_objects_with_a_class_label]
    subset_histogram = array_histogram_of_objects[indexes_of_objects_with_a_class_label, :]
    LOGGER.info("Shape of array histogram with at least a class per object, number_of_objects: %s, number_of classes: %s" % (array_histogram_of_objects.shape[0], array_histogram_of_objects.shape[1]))
    class_list = numpy.zeros(subset_histogram.shape[0]) 
    class_range = numpy.arange(max(unique_classes)+1) 
    LOGGER.info("Class range %s" % str(class_range))
    i=0
    for o in range(subset_histogram.shape[0]):
        nr = numpy.sum(subset_histogram[o,:]) 
        rel = subset_histogram[o,:]*1.0/nr*1.0        
        max_class = numpy.max(subset_histogram[o,:]) #TODO: this is different in old code of madmex
        if i < 5:
            print max_class
        idx = subset_histogram[o,:] == max_class
        if sum(idx) == 1 and rel[idx] >= proportion: #The object needs to have at least a given proportion
            class_list[o] = class_range[idx]
        else:
            class_list[o] = 0
        i+=1
    nonzero_classes =  class_list > 0 # index of classes with value greater 0 (we ignore the zero class, cause is nodata: fmask or NaN's values)
    class_list = class_list[nonzero_classes] # all non zero class labels
    subset_objects = subset_objects[nonzero_classes] # final object 
    df = pandas.DataFrame(numpy.vstack([subset_objects,class_list]).T) # stack and create dataframe
    df.columns = [names_of_columns[0], names_of_columns[1]]
    return df