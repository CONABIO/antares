'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import numpy

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
from madmex.mapper.data import raster
from madmex.mapper.data._gdal import create_raster, JPEG
from madmex.mapper.data.raster import GDAL_TIFF
from madmex.util import get_parent, create_directory_path, create_filename


#_BASE = r'L%s[0-9]?[0-9]{3}[0-9]{3}_[0-9]{3}[0-9]{4}[0-9]{2}[0-9]{2}_%s'
_BASE = r'L%s?0%s.*_%s'
_BASE_SR = r'lndsr.L%s?%s.*%s'

class LandsatBaseBundle(BaseBundle):
    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        
        self.output_directory = None
        self.file_dictionary = None
        self.get_landsat_files()
        self._look_for_files()
    def get_landsat_files(self):
        '''
        This method prepares the dictionary that holds the regular expressions
        to identify the files that this bundle represent.
        '''
        mission = self.get_mission()
        processing_level = self.get_processing_level()
        letter = self.get_letter()
        if not self.file_dictionary:
            ang = _BASE % (letter, mission, 'ANG.txt')
            band_1 = _BASE % (letter, mission, 'B1.TIF')
            band_2 = _BASE % (letter, mission, 'B2.TIF')
            band_3 = _BASE % (letter, mission, 'B3.TIF')
            band_4 = _BASE % (letter, mission, 'B4.TIF')
            band_5 = _BASE % (letter, mission, 'B5.TIF')
            band_6 = _BASE % (letter, mission, 'B6.TIF')
            band_61 = _BASE % (letter, mission, 'B6_VCID_1.TIF')
            band_62 = _BASE % (letter, mission, 'B6_VCID_2.TIF')
            band_7 = _BASE % (letter, mission, 'B7.TIF')
            band_8 = _BASE % (letter, mission, 'B8.TIF')
            band_9 = _BASE % (letter, mission, 'B9.TIF')
            band_10 =  _BASE % (letter, mission, 'B10.TIF')
            band_11 = _BASE % (letter, mission , 'B11.TIF')
            band_BQA = _BASE % (letter, mission, 'BQA.TIF')
            gcp = _BASE % (letter, mission, 'GCP.txt')
            metadata = _BASE % (letter, mission, 'MTL.txt')
            band_1_sr_img= _BASE % (letter, mission, 'sr_band1_hdf.img')
            band_2_sr_img= _BASE % (letter, mission, 'sr_band2_hdf.img')
            band_3_sr_img= _BASE % (letter, mission, 'sr_band3_hdf.img')
            band_4_sr_img= _BASE % (letter, mission, 'sr_band4_hdf.img')
            band_5_sr_img= _BASE % (letter, mission, 'sr_band5_hdf.img')
            band_6_sr_img= _BASE % (letter, mission, 'sr_band6_hdf.img')
            band_7_sr_img= _BASE % (letter, mission, 'sr_band7_hdf.img')    
            band_sr_hdf = _BASE_SR % (letter, mission, '.hdf$')
            band_sr_hdf_xml = _BASE_SR% (letter, mission, '_hdf.xml')  
            band_sr_cloud_img = _BASE % (letter, mission, 'sr_cloud_hdf.img')
            band_sr_ipflag_img = _BASE % (letter, mission, 'sr_ipflag_hdf.img')
            image_fmask = _BASE % (letter, mission, 'MTLFmask$')
            image_fmask_hdr =  _BASE % (letter, mission, 'MTLFmask.hdr')
            image_fmask_xml =  _BASE % (letter, mission, 'MTLFmask.aux.xml')
            self.file_dictionary = {}
            if mission == '5':
                self.file_dictionary = {
                                        band_1:None,
                                        band_2:None,
                                        band_3:None,
                                        band_4:None,
                                        band_5:None,
                                        band_6:None,
                                        band_7:None,
                                        metadata:None
                                        }
            if mission == '7':
                self.file_dictionary = {
                                        ang:None,
                                        band_1:None,
                                        band_2:None,
                                        band_3:None,
                                        band_4:None,
                                        band_5:None,
                                        band_61:None,
                                        band_62:None,
                                        band_7:None,
                                        band_8:None,
                                        band_BQA:None,
                                        gcp:None,
                                        metadata:None
                                        }
            if mission == '8' and processing_level == 'L1T':
                self.file_dictionary = {
                                        band_1:None,
                                        band_2:None,
                                        band_3:None,
                                        band_4:None,
                                        band_5:None,
                                        band_6:None,
                                        band_7:None,
                                        band_8:None,
                                        band_9:None,
                                        band_10:None,
                                        band_11:None,
                                        band_BQA:None,
                                        metadata:None
                                        }
            if mission == '8' and processing_level == 'SR':
                self.file_dictionary ={
                                        band_1_sr_img:None,
                                        band_2_sr_img:None,
                                        band_3_sr_img:None,
                                        band_4_sr_img:None,
                                        band_5_sr_img:None,
                                        band_6_sr_img:None,
                                        band_7_sr_img:None,
                                        band_sr_hdf:None,
                                        band_sr_hdf_xml:None,
                                        band_sr_cloud_img:None,
                                        band_sr_ipflag_img:None,
                                        metadata:None   
                                        }
            if mission == '8' and processing_level == 'FMASK':
                self.file_dictionary={
                                      image_fmask:None,
                                      image_fmask_hdr:None,
                                      image_fmask_xml:None,
                                      metadata:None,
                                      }
        #self._look_for_files()
        #self.get_thumbnail()
    def get_mission(self):
        '''
        Implementers should override this method to provide access to the mission
        number of the particular Landsat implementation.
        '''
        raise NotImplementedError('Subclasses of LandsatBaseBundle must provide a get_mission() method.')
    def get_processing_level(self):
        '''
        Implementers should override this method to provide access to the processing level
        of the particular Landsat implementation.
        '''
        raise NotImplementedError('Subclasses of LandsatBaseBundle must provide a get_processing_level() method.')
    def get_output_directory(self):
        '''
        Creates the output directory where the Landsat files will be persisted in
        the file system.
        '''
        if self.output_directory is None:
            destination = getattr(SETTINGS, 'TEST_FOLDER')
            self.output_directory = destination
        return self.output_directory
    
    def get_image_band_file(self, band):
        '''
        In the particular case of the Landsat missions, the images come in separated
        files, one file for each band. This method will return the file for the
        specified band.
        '''
        return self.file_dictionary[_BASE % (self.get_mission(), 'Bs%[0-9].TIF' % band)]
    
    def get_metadata_file(self):
        '''
        This method is a getter for the file that contains metadata for this image.
        '''
        return self.file_dictionary[_BASE % (self.get_mission(), 'MTL.txt')]
    def get_raster(self):
        '''
        Lazily creates and returns a raster object for this bundle.
        '''
        if self.raster is None:
            self.raster = raster.Data(self.file_dictionary[self.get_image_file()], self.get_format_file())
        return self.raster
    def get_thumbnail(self):
        '''
        Creates a thumbnail for the scene in true color.
        '''
        from subprocess import call
        file_1 = self.file_dictionary[_BASE % (self.get_mission(), 'B1[0-9].TIF')]
        file_2 = self.file_dictionary[_BASE % (self.get_mission(), 'B2[0-9].TIF')]
        file_3 = self.file_dictionary[_BASE % (self.get_mission(), 'B3[0-9].TIF')]
        parent_directory = get_parent(self.path)
        thumnail_directory = create_filename(parent_directory, 'thumbnail')
        create_directory_path(thumnail_directory)
        parent_directory
        filename = create_filename(thumnail_directory, 'vrt.tif')
        merge_command = ['/Library/Frameworks/GDAL.framework/Programs/gdalbuildvrt', '-separate', '-o', filename, file_3, file_2, file_1]
        call(merge_command)
        thumbnail = create_filename(thumnail_directory, 'thumbnail.jpg')
        resize_command = ['/Library/Frameworks/GDAL.framework/Programs/gdal_translate', filename, '-of', 'JPEG', '-outsize', '5%', '5%', thumbnail]
        call(resize_command)
