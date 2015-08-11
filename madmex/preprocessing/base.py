'''
Created on 16/07/2015

@author: erickpalacios
'''

import numpy as np

def calculate_rad_spot5(data,gain,offset):
    b = 0
    rad = data
    for g in gain:
        rad[b,:,:] = data[b,:,:]/g+offset[b]
        b = b+1
    return rad
def calculate_toa_spot5(rad, sun_distance, sun_elevation, hrg, number_of_bands):
    if hrg == 'SCENE HRG2 J':
        E = [1858, 1575, 1047, 234]
    else:
        E = [1858, 1573, 1043, 236]
    print E
    BANDS = number_of_bands
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:])/(sun_distance*sun_distance*E[i]*np.cos((90-sun_elevation)*np.pi/180))
    return toa
def calculate_distance_Sun_Earth_spot5(datestr):
    """
    returns distance between sun and earth
    """
    day = datestr.timetuple().tm_yday
    sun_distance = 1/(1-0.016729*np.cos((.9856*(day-4))*np.pi/180))
    return sun_distance
def calculate_toa_spot6(rad, sun_distance, sun_elevation, irradiance, number_of_bands):
    E = irradiance
    BANDS = number_of_bands
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:])/(sun_distance*E[i]*np.cos(sun_elevation))
    return toa
def calculate_distance_Sun_Earth_spot6(datestr):
    """
    returns distance between sun and earth in AU for a given date. Date needs to be a string using format YYYY-MM-DD or datetime object from metadata
    """
    import ephem
    import datetime
    sun = ephem.Sun()  # @UndefinedVariable
    if isinstance(datestr, str):
        sun.compute(datetime.datetime.strptime(datestr, '%Y-%m-%d').date())
    elif isinstance(datestr, datetime.datetime ):
        sun.compute(datestr)
    sun_distance = sun.earth_distance  # needs to be between 0.9832898912 AU and 1.0167103335 AU
    return sun_distance
def calculate_rad_toa_spot5(data, gain, offset, imaging_date, sun_elevation, hrg, number_of_bands):
    rad = calculate_rad_spot5(data.astype(np.float), gain, offset)
    sun_distance = calculate_distance_Sun_Earth_spot5(imaging_date)
    return calculate_toa_spot5(rad, sun_distance, sun_elevation, hrg, number_of_bands)
def calculate_rad_toa_spot6(data, gain, offset, imaging_date, sun_elevation, irradiance, number_of_bands):
    rad = calculate_rad_spot5(data.astype(np.float), gain, offset)
    sun_distance = calculate_distance_Sun_Earth_spot5(imaging_date)
    return calculate_toa_spot6(rad, sun_distance, sun_elevation,irradiance, number_of_bands)
def calculate_rad_rapideye(data, radiometricScaleFactor=0.009999999776482582, radiometricOffsetValue=0.0):
    """
    Convert DN into RAD according to RE documentation
    returns sensor radiance of that pixel in watts per steradian per square meter.
    """
    rad = data * radiometricScaleFactor + radiometricOffsetValue
    rad[rad == radiometricOffsetValue] = 0
    return rad
def calculate_toa_rapideye(rad, sun_distance, sun_elevation):
    """
    Calculates TOA from RAD according to RE documentation
    needs Sun earth distance and sun elevation
    """  
    BANDS = 5
    solar_zenit = 90 - sun_elevation
    EAI = [1997.8, 1863.5, 1560.4, 1395.0, 1124.4]  # Exo-Atmospheric Irradiance in 
    toa = rad
    for i in range(BANDS):
        toa[i, :, :] = rad[i, :, :] * (np.pi * (sun_distance * sun_distance)) / (EAI[i] * np.cos(np.pi * solar_zenit / 180)) 
    return toa