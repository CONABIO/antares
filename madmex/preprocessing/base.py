'''
Created on 16/07/2015

@author: erickpalacios
'''

import numpy as np

def calculate_spot_rad(data,gain,offset):
    b = 0
    rad = data
    for g in gain:
        rad[b,:,:] = data[b,:,:]/g+offset[b]
        b = b+1
    return rad
def calculate_spot5_toa(rad, sun_distance, sun_elevation):
    E = [1843,1568,1052,233]
    BANDS = 4
    toa = rad
    for i in range(BANDS):
        toa[i,:,:] = (np.pi*rad[i,:,:]*sun_distance)/(E[i]*np.cos(sun_elevation))
        
    return toa
def calculate_distance_Sun_Earth(datestr):
    """
    returns distance between sun and earth in AU for a given date. Date needs to be a string using format YYYY-MM-DD or datetime object from metadata
    """
    import datetime
    import ephem
    sun = ephem.Sun()   # @UndefinedVariable
    if isinstance(datestr, str):
        sun.compute(datetime.datetime.strptime(datestr, '%Y-%m-%d').date())
    elif isinstance(datestr, datetime.datetime ):
        sun.compute(datestr)
    sun_distance = sun.earth_distance  # needs to be between 0.9832898912 AU and 1.0167103335 AU
    return sun_distance
def calculate_rad_ref(data, gain, offset, imaging_date, sun_elevation):
    rad = calculate_spot_rad(data.astype(np.float), gain, offset)
    sun_distance = calculate_distance_Sun_Earth(str(imaging_date))
    return calculate_spot5_toa(rad, sun_distance, sun_elevation)
def calculate_rapideye_rad(data, radiometricScaleFactor=0.009999999776482582, radiometricOffsetValue=0.0):
    """
    Convert DN into RAD according to RE documentation
    returns sensor radiance of that pixel in watts per steradian per square meter (W/m2/sr/μm).
    """
    
    rad = data * radiometricScaleFactor + radiometricOffsetValue
    rad[rad == radiometricOffsetValue] = 0
    return rad

    
def calculate_rapideye_toa(rad, sun_distance, sun_elevation):
    """
    Calculates TOA from RAD according to RE documentation
    needs Sun earth distance and sun elevation
    """  
    BANDS = 5
    solar_zenit = 90 - sun_elevation
    EAI = [1997.8, 1863.5, 1560.4, 1395.0, 1124.4]  # Exo-Atmospheric Irradiance in W/m2/μm
    toa = rad
    for i in range(BANDS):
        toa[i, :, :] = rad[i, :, :] * (np.pi * (sun_distance * sun_distance)) / (EAI[i] * np.cos(np.pi * solar_zenit / 180))
        
    return toa