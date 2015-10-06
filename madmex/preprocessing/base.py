'''
Created on 16/07/2015

@author: erickpalacios
'''

from __future__ import unicode_literals
import datetime
import numpy as np
from scipy import ndimage
from scipy import signal
from scipy import stats 
import matplotlib.pylab as pylab
from skimage import io, color
from madmex import LOGGER
FMASK_LAND = 0
FMASK_WATER = 1
FMASK_SNOW = 3
FMASK_OUTSIDE = 255
FMASK_CLOUD_SHADOW = 2
FMASK_CLOUD = 4
MORPHING_SIZE = 10
MORPHING_SIZES = [250,150,50] # pixel sizes of structure elements

def calculate_rad_spot5(data,gain,offset):
    '''
    Calculates radiance for spot 5.
    '''
    b = 0
    rad = data
    for g in gain:
        rad[b,:,:] = data[b,:,:] / g + offset[b]
        b = b+1
    return rad
def calculate_toa_spot5(rad, sun_distance, sun_elevation, hrg, number_of_bands):
    '''
    Calculates top of atmosphere for spot 5.
    '''
    if hrg == 'SCENE HRG2 J':
        E = [1858, 1575, 1047, 234]
    else:
        E = [1858, 1573, 1043, 236]
    BANDS = number_of_bands
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:]) / (sun_distance * sun_distance * E[i] * np.cos((90 - sun_elevation) * np.pi / 180))
    return toa
def calculate_distance_Sun_Earth_spot5(datestr):
    '''
    Returns distance between sun and earth.
    '''
    day = datestr.timetuple().tm_yday
    sun_distance = 1 / (1 - 0.016729 * np.cos((0.9856 * (day - 4)) * np.pi / 180))
    return sun_distance
def calculate_toa_spot6(rad, sun_distance, sun_elevation, irradiance, number_of_bands):
    E = irradiance
    BANDS = number_of_bands
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:])/(sun_distance*E[i]*np.cos(sun_elevation))
    return toa
def calculate_distance_sun_earth(datestr):
    '''
    Calculates distance between sun and earth in astronomical unints for a given
    date. Date needs to be a string using format YYYY-MM-DD or datetime object
    from metadata.
    '''
    import ephem
    sun = ephem.Sun()  # @UndefinedVariable
    if isinstance(datestr, str):
        sun.compute(datetime.datetime.strptime(datestr, '%Y-%m-%d').date())
    elif isinstance(datestr, datetime.datetime ):
        sun.compute(datestr)
    sun_distance = sun.earth_distance  # needs to be between 0.9832898912 AU and 1.0167103335 AU
    return sun_distance
def calculate_rad_toa_spot5(data, gain, offset, imaging_date, sun_elevation, hrg, number_of_bands):
    '''
    Calculates top of atmosphere for spot 5.
    '''
    rad = calculate_rad_spot5(data.astype(np.float), gain, offset)
    sun_distance = calculate_distance_Sun_Earth_spot5(imaging_date)
    return calculate_toa_spot5(rad, sun_distance, sun_elevation, hrg, number_of_bands)
def calculate_rad_toa_spot6(data, gain, offset, imaging_date, sun_elevation, irradiance, number_of_bands):
    '''
    Calculates top of atmosphere for spot 6.
    '''
    rad = calculate_rad_spot5(data.astype(np.float), gain, offset)
    sun_distance = calculate_distance_Sun_Earth_spot5(imaging_date)
    return calculate_toa_spot6(rad, sun_distance, sun_elevation,irradiance, number_of_bands)
def calculate_rad_rapideye(data, radiometricScaleFactor=0.009999999776482582, radiometricOffsetValue=0.0):
    '''
    Convert digital number into radiance according to rapideye documentation. Returns 
    sensor radiance of that pixel in watts per steradian per square meter.
    '''
    rad = data * radiometricScaleFactor + radiometricOffsetValue
    rad[rad == radiometricOffsetValue] = 0
    return rad
def calculate_toa_rapideye(rad, sun_distance, sun_elevation):
    '''
    Calculates top of atmosphere from radiance according to RE documentation
    needs sun-earth distance and sun elevation.
    '''
    BANDS = 5
    solar_zenit = 90 - sun_elevation
    EAI = [1997.8, 1863.5, 1560.4, 1395.0, 1124.4]  # Exo-Atmospheric Irradiance in 
    toa = rad
    for i in range(BANDS):
        toa[i, :, :] = rad[i, :, :] * (np.pi * (sun_distance * sun_distance)) / (EAI[i] * np.cos(np.pi * solar_zenit / 180)) 
    return toa
def filter_median(input_image_raster, filter_size):
    '''
    Median filtering of raster
    '''    
    return ndimage.median_filter(input_image_raster, filter_size)
def morph_dilation(input_image_raster, filter_size):
    '''
    Morphological dilation of raster
    '''
    ndim = 3
    if input_image_raster.ndim == 2:
        input_image_raster = np.expand_dims(input_image_raster, axis=0)
        ndim = 2
    if input_image_raster.ndim != 3:
        raise Exception("Input array has to be 3D")
    if ndim == 3:
        return ndimage.grey_dilation(input_image_raster, (1, filter_size, filter_size))
    else:
        return ndimage.grey_dilation(input_image_raster, (1, filter_size, filter_size))[0]
def morphing(image_mask_array, image_array, inbetween, clouds):
    np.putmask(image_mask_array, image_array[0, :, :] == 0, FMASK_OUTSIDE)
    m = len(MORPHING_SIZES)
    for MORPHING_SIZE in MORPHING_SIZES:
        np.putmask(image_mask_array, morph_dilation(clouds, MORPHING_SIZE) == 1, FMASK_CLOUD*10+m)
        m = m-1
        np.putmask(image_mask_array, inbetween == 1, FMASK_CLOUD_SHADOW)
        np.putmask(image_mask_array, clouds == 1, FMASK_CLOUD)
    return image_mask_array
def base_masking(top_of_atmosphere_data, output, solar_zenith, solar_azimuth, geotransform):
        cloud_mask = convert_to_fmask(extract_extremes(top_of_atmosphere_data, output))
        clouds = np.where(cloud_mask==FMASK_CLOUD, 1, 0)
        shadows= np.where(cloud_mask==FMASK_CLOUD_SHADOW, 1, 0)
        resolution = geotransform[1]
        shadow_mask = calculate_cloud_shadow(clouds, shadows, cloud_mask.shape, solar_zenith, solar_azimuth, resolution) * FMASK_CLOUD_SHADOW
        water_mask = convert_water_to_fmask(calculate_water(top_of_atmosphere_data))
        return combine_mask(cloud_mask, shadow_mask, water_mask)
def extract_extremes(data, image_file, steps=1000):
    CENTER = 50

    watermask = calculate_water(data)

    result_matrix = np.zeros((data.shape), dtype=float)
    
    xtiles = 5000 / steps
    ytiles = 5000 / steps
    counter = 0
    
    f, axarr = pylab.subplots(xtiles, ytiles)
    
    b = 0
    global_quant = list()
        
    for ycount in range(0, 5000, steps):
        for xcount in range(0, 5000, steps):
            subset = data[:, ycount:ycount + steps, xcount:xcount + steps]
            LOGGER.info("Extent: %dx%d"% (xcount,ycount))
            z, y, x = subset.shape
            
            rgb = np.zeros((y, x, z))
            for i in range(0, z):
                rgb[:, :, i] = subset[i, :, :] / np.max(data[i, :, :])
            
            col_space1 = color.rgb2lab(rgb[:, :, 0:3])
        
            # col_space = color.rgb2hsv(rgb[:,:,0:3])
            
            subset_result = np.zeros((steps, steps), dtype=np.float)
        
            quant = calculate_quantiles(col_space1[ :, :, 0])
            if len(quant) > 0:
                points = calculate_breaking_points(quant)
                # print points
            
                break_points = np.array(calculate_continuity(points.keys()))
            else:
                break_points = []
            
            subset = data[b, ycount:ycount + steps, xcount:xcount + steps] 
            pylab.subplot(xtiles, ytiles, counter + 1)
            fig = pylab.plot(quant, c="k", alpha=0.5)
                    
            if len(break_points) > 1:
                for p in points.keys():
                    pylab.plot(p, np.array(quant)[p], 'r.')
                    
                if len(break_points[break_points < CENTER]) > 0:
                    min_bp = max(break_points[break_points < CENTER])
                if len(break_points[break_points > CENTER]) > 0:
                    max_bp = min(break_points[break_points > CENTER])
                
                if np.min(subset) != 0.0 or np.max(subset) != 0.0:
                    LOGGER.info("%d, %3.2f, %3.2f, %3.2f * %d, %3.2f, %3.2f, %3.2f" % (min_bp, quant[min_bp], np.min(subset), quant[0] / np.min(subset), max_bp, quant[99] , np.max(subset), quant[99] / np.max(subset)))
                

                for i, q in enumerate(range(max_bp, 100, 1)):
                    modelled = f_lin(q, points[max_bp]["slope"], points[max_bp]["offset"])
                    diff = abs(quant[q] - modelled)
                    global_quant.append((q, quant[q], diff))
                    
                    # subset_result = np.where(col_space1[ :, :,0] > quant[q], 10 + col_space1[ :, :,0] -modelled, subset_result)
                
                for i, q in enumerate(range(0, min_bp,)):
                    modelled = f_lin(q, points[max_bp]["slope"], points[max_bp]["offset"])
                    diff = abs(quant[q] - modelled)
                    global_quant.append((q, quant[q], diff))
                    # subset_result = np.where(col_space1[ :, :,0] < quant[q], 1 + col_space1[ :, :,0] -modelled, subset_result)
            

                result_matrix[b, ycount:ycount + steps, xcount:xcount + steps] = subset_result
            counter += 1
            fig = pylab.gcf()
            fig.set_size_inches(18.5, 10.5)
            name = image_file.replace(".tif", "_local.png")
            fig.savefig(name, bbox_inches='tight', dpi=150)
    
    z, y, x = data.shape
    rgb = np.zeros((y, x, z))
    for i in range(0, z):
        rgb[:, :, i] = data[i, :, :] / np.max(data[i, :, :])
    
    col_space1 = color.rgb2lab(rgb[:, :, 0:3])
    subset_result = np.zeros((3, y, x), dtype=np.float)
    total_q = len(global_quant)

    for counter, item in enumerate(global_quant):
        LOGGER.info("%d: %d, %s" % ( counter, total_q, str(item)))
        q, value, diff = item
        MAX_ERROR = 10
        if diff > MAX_ERROR:
            if q < 50.0:
                subset_result[0, :, :] = np.where(col_space1[ :, :, 0] < value, 1 + col_space1[ :, :, 0] - diff, subset_result[0, :, :])
                subset_result[1, :, :] = np.where(col_space1[ :, :, 0] < value, subset_result[1, :, :] + diff, subset_result[1, :, :])
                subset_result[2, :, :] = np.where(col_space1[ :, :, 2] < value, subset_result[2, :, :] - 1, subset_result[2, :, :])
            else:
                subset_result[0, :, :] = np.where(col_space1[ :, :, 0] > value, 100. + col_space1[ :, :, 0] - diff, subset_result[0, :, :])
                subset_result[1, :, :] = np.where(col_space1[ :, :, 0] > value, subset_result[1, :, :] + diff, subset_result[1, :, :])
                subset_result[2, :, :] = np.where(col_space1[ :, :, 2] > value, subset_result[2, :, :] + 1, subset_result[2, :, :])
    
    return subset_result
def calculate_water(data):
    z,y,x = data.shape
    pot_water = np.zeros((y,x))
    
    for b in range(z-1,1,-1):
        pot_water[:,:] = np.where(data[b,:,:]<data[b-1,:,:],pot_water+b*1,pot_water)
        
    for b in range(z-1,1,-1):
        pot_water[:,:] = np.where(data[b,:,:]>data[b-1,:,:],pot_water-b*1,pot_water)
    
    # NDWI bands
    b=4
    pot_water[:,:] = np.where(data[b,:,:]>data[b-3,:,:],pot_water-1,pot_water) 
    
    #NIR-RE diff to  R-RE aka sun glid
    dark_nir = np.where(data[b,:,:]<0.12,data, data*0 )

    pot_water[:,:] = np.where(np.abs(dark_nir[b,:,:]-dark_nir[b-1,:,:]) < abs(dark_nir[b-1,:,:]-dark_nir[b-2,:,:]),pot_water+1.5,pot_water-1.5) 
    

    pot_water = signal.medfilt2d(pot_water,kernel_size=5)
    pot_water = np.where(data[0,:,:]==0, -999, pot_water)
    return pot_water
def calculate_quantiles(band, NA=0):
    quant = list()
    na_free_data = band[band > NA]
    if len(na_free_data) > 100:
        for i in range(0, 100, 1):
            p = np.percentile(na_free_data, i)
            quant.append(p)
    else:
        quant = []
        
    return np.array(quant)
def calculate_breaking_points(quant_list):
    MAX_ERROR = 5
    RANGE = 5
    CENTER = 50
    BRAKE_POINTS = dict()
    
    # right to left window
    for x_iter in range(100, CENTER, -1):
        x_proj = range(x_iter - RANGE, x_iter)

        # pylab.plot(x_proj, quant[x-RANGE:x], 'k',alpha=0.5)
        y_subset = quant_list[x_iter - RANGE:x_iter]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_proj, y_subset) 
        g, l = calculate_error(slope, intercept, x_proj, y_subset)


        # print x-RANGE,x, slope, intercept, y[0], f(x, slope, intercept), l,r
        if l > MAX_ERROR:
            BRAKE_POINTS[x_iter - RANGE / 2] = {"error":l, "slope":slope, "offset":intercept}
       
    # left to right window
    for x_iter in range(0, CENTER, 1):
        x_proj = range(x_iter, x_iter + RANGE)
        # pylab.plot(x_proj, quant_list[x_iter:x_iter + RANGE], 'k', alpha=0.3)
        y_subset = quant_list[x_iter:x_iter + RANGE]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_proj, y_subset) 
        g, l = calculate_error(slope, intercept, x_proj, y_subset)


        # print x,x+RANGE, slope, intercept, y[0], f(x, slope, intercept), l,r
        if l > MAX_ERROR:
            if ((x_iter - RANGE + x_iter) / 2) not in BRAKE_POINTS.keys():
                BRAKE_POINTS[x_iter + (RANGE / 2)] = {"error":l, "slope":slope, "offset":intercept}

        # pylab.plot([x_iter, x_iter + RANGE, ], [ f(x_iter, slope, intercept), f(x_iter + RANGE, slope, intercept)], "b", alpha=0.3)
    return BRAKE_POINTS
def calculate_error(slope, offset, x_val, y_val):
    CENTER = 50.0000001
    err_sum_total = 0.0
    err_sum_local = 0.0

    for i, x in enumerate(x_val):
            err_sum_local += ((f_lin(x, slope, offset) - y_val[i]) ** 2) * (CENTER - x) ** 2
            err_sum_total += ((f_lin(x, slope, offset) - y_val[i]) ** 2) * (CENTER - x) ** 2
        
    return err_sum_total, err_sum_local
def calculate_continuity(point_list):
    breaks = list()
    point_list.sort()
    
    for i in range(1, len(point_list)):
        if point_list[i] - point_list[i - 1] != 1:
            breaks.append(point_list[i - 1])
            breaks.append(point_list[i])
        
    
    return breaks
def f_lin(x, scale, off):
    return x * scale + off
def convert_to_fmask(raster):
    from numpy.core.numerictypes import byte
    z, y, x = raster.shape
    fmask = np.zeros((y, x)).astype(byte)  # FMASK_LAND
    fmask = np.where (raster[0, :, :] > 100, FMASK_CLOUD, fmask)
    fmask = np.where (raster[0, :, :] < 100, FMASK_CLOUD_SHADOW, fmask)
    fmask = np.where (raster[0, :, :] == 0, FMASK_LAND, fmask)
    fmask = np.where (raster[0, :, :] == -999.0, FMASK_OUTSIDE, fmask)
    return fmask
def calculate_cloud_shadow(clouds, shadows, solarzenith, solarazimuth, resolution):
    cloudrowcol = np.column_stack(np.where(clouds == 1))
    cloudheight = np.arange(1000, 3100, 100)
    cloud_mask_shape = clouds.shape
    cloudsproj = np.zeros(cloud_mask_shape)  
    
    for h in cloudheight:    
        dist = h / resolution * np.tan(np.deg2rad(90 - solarzenith))
        ydiff = dist * np.sin(np.deg2rad(360-solarazimuth))
        xdiff = dist * np.cos(np.deg2rad(360-solarazimuth))     
        if solarazimuth < 180:
            rows = cloudrowcol[:, 0] - ydiff #/ 5
            cols = cloudrowcol[:, 1] - xdiff #/ 5
        else:
            rows = cloudrowcol[:, 0] + ydiff #/ 5
            cols = cloudrowcol[:, 1] + xdiff #/ 5
        rows = rows.astype(np.int)
        cols = cols.astype(np.int)
        np.putmask(rows, rows < 0, 0)
        np.putmask(cols, cols < 0, 0)
        np.putmask(rows, rows >= cloud_mask_shape[0] - 1, cloud_mask_shape[0]  - 1)
        np.putmask(cols, cols >= cloud_mask_shape[1]  - 1, cloud_mask_shape[1]  - 1)
        cloudsproj[rows, cols] = 1  
    inbetween = shadows * cloudsproj
    return inbetween
def combine_mask(cloudmask, shadowmask, watermask):
    watermask = np.where(watermask == FMASK_CLOUD_SHADOW, FMASK_CLOUD_SHADOW, watermask)
    watermask = np.where(cloudmask == FMASK_CLOUD, FMASK_CLOUD, watermask)
    watermask = np.where(shadowmask == FMASK_CLOUD_SHADOW, FMASK_CLOUD_SHADOW, watermask)
    return watermask
def convert_cloud_to_fmask(raster):
    from numpy.core.numerictypes import byte
    z, y, x = raster.shape
    fmask = np.zeros((y, x)).astype(byte)  # FMASK_LAND
    fmask = np.where (raster[0, :, :] > 100, FMASK_CLOUD, fmask)
    fmask = np.where (raster[0, :, :] < 100, FMASK_CLOUD_SHADOW, fmask)
    fmask = np.where (raster[0, :, :] == 0, FMASK_LAND, fmask)
    fmask = np.where (raster[0, :, :] == -999.0, FMASK_OUTSIDE, fmask)
    fmask = signal.medfilt2d(fmask*1.0, kernel_size=3)
    fmask = signal.medfilt2d(fmask*1.0, kernel_size=5)    
    return fmask
def convert_water_to_fmask(raster):
    from numpy.core.numerictypes import byte
    y, x = raster.shape
    fmask = np.zeros((y, x)).astype(byte)  # FMASK_LAND
    fmask = np.where (raster > 1, FMASK_WATER, fmask)
    fmask = np.where (raster <= 1, FMASK_LAND, fmask)
    fmask = np.where (raster == -999.0, FMASK_OUTSIDE, fmask)
    return fmask

