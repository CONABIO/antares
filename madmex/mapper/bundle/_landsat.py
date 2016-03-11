'''
Created on Aug 26, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

from madmex.configuration import SETTINGS
from madmex.mapper.base import BaseBundle
from madmex.mapper.data import raster


_BASE = r'L%s[0-9]?[0-9]{3}[0-9]{3}_[0-9]{3}[0-9]{4}[0-9]{2}[0-9]{2}_%s'

class LandsatBaseBundle(BaseBundle):
    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        
        self.output_directory = None
        self.file_dictionary = None
        self.get_landsat_files()
        
        print self.file_dictionary
        
        self._look_for_files()
    def get_landsat_files(self):
        '''
        This method prepares the dictonary that holds the regular expressions
        to identify the files that this bundle represent.
        '''
        mission = self.get_mission()
        if not self.file_dictionary:
            band_1 = _BASE % (mission, 'B1[0-9].TIF')
            band_2 = _BASE % (mission, 'B2[0-9].TIF')
            band_3 = _BASE % (mission, 'B3[0-9].TIF')
            band_4 = _BASE % (mission, 'B4[0-9].TIF')
            band_5 = _BASE % (mission, 'B5[0-9].TIF')
            band_6 = _BASE % (mission, 'B6[0-9].TIF')
            band_61 = _BASE % (mission, 'B61.TIF')
            band_62 = _BASE % (mission, 'B62.TIF')
            band_7 = _BASE % (mission, 'B7[0-9].TIF')
            band_8 = _BASE % (mission, 'B7[0-9].TIF')
            gcp = _BASE % (mission, 'GCP.txt')
            metadata = _BASE % (mission, 'MTL.txt')
            
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
                                        band_1:None,
                                        band_2:None,
                                        band_3:None,
                                        band_4:None,
                                        band_5:None,
                                        band_61:None,
                                        band_62:None,
                                        band_7:None,
                                        band_8:None,
                                        gcp:None,
                                        metadata:None
                                        }
            if mission == '8':
                self.file_dictionary = {
                                        band_1:None
                                        }
    def get_mission(self):
        '''
        Implementers should override this method to provide access to the mission
        number of the particular Landsat implementation.
        '''
        raise NotImplementedError('Subclasses of SpotBaseBundle must provide a get_mission() method.')
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
