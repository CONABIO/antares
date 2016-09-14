'''
Created on 19/04/2016

@author: erickpalacios
'''
import numexpr
import numpy
from numpy import NaN
from scipy.stats import nanstd, nanmean
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
    statsmean = nanmean(array, axis = 0)
    numpy.putmask(statsmean, numpy.isnan(statsmean), -9999)
    index_inf_values  = abs(statsmean) >= OVERFLOW_LEVEL
    statsmean[index_inf_values] = -9999
    zonalstats.append(statsmean)
    statsmean = None    
    statsstd = nanstd(array, axis = 0)
    numpy.putmask(statsstd, numpy.isnan(statsstd), -9999)
    index_inf_values  = abs(statsstd) >= OVERFLOW_LEVEL
    statsstd[index_inf_values] = -9999
    zonalstats.append(statsstd)
    statsstd = None
    array_stats = numpy.array(zonalstats)
    zonalstats = None
    return array_stats
