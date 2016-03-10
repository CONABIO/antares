'''
Created on 16/07/2015

@author: erickpalacios
'''

from __future__ import unicode_literals
import datetime
import numpy

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
        irradiance = [1858, 1575, 1047, 234]
    else:
        irradiance = [1858, 1573, 1043, 236]
    toa = rad
    for i in range(number_of_bands):
        toa[i,:,:] = (numpy.pi * rad[i, :, :]) / (sun_distance * sun_distance * irradiance[i] * numpy.cos((90 - sun_elevation) * numpy.pi / 180))
    return toa
def calculate_distance_sun_earth_spot5(datestr):
    '''
    Returns distance between sun and earth.
    '''
    day = datestr.timetuple().tm_yday
    sun_distance = 1 / (1 - 0.016729 * numpy.cos((0.9856 * (day - 4)) * numpy.pi / 180))
    return sun_distance
def calculate_toa_spot6(rad, sun_distance, sun_elevation, irradiance, number_of_bands):
    '''
    Calculates top of atmosphere for spot 6.
    '''
    irrad = irradiance
    toa = rad
    for i in range(number_of_bands):
        toa[i,:,:] = (numpy.pi * rad[i,:,:]) / (sun_distance * irrad[i] * numpy.cos(sun_elevation))
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
    rad = calculate_rad_spot5(data.astype(numpy.float), gain, offset)
    sun_distance = calculate_distance_sun_earth_spot5(imaging_date)
    return calculate_toa_spot5(rad, sun_distance, sun_elevation, hrg, number_of_bands)
def calculate_rad_toa_spot6(data, gain, offset, imaging_date, sun_elevation, irradiance, number_of_bands):
    '''
    Calculates top of atmosphere for spot 6.
    '''
    rad = calculate_rad_spot5(data.astype(numpy.float), gain, offset)
    sun_distance = calculate_distance_sun_earth_spot5(imaging_date)
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
    bands = 5
    solar_zenit = 90 - sun_elevation
    irradiance = [1997.8, 1863.5, 1560.4, 1395.0, 1124.4]  # Exo-Atmospheric Irradiance in 
    toa = rad
    for i in range(bands):
        toa[i, :, :] = rad[i, :, :] * (numpy.pi * (sun_distance * sun_distance)) / (irradiance[i] * numpy.cos(numpy.pi * solar_zenit / 180)) 
    return toa
