'''
Created on Jun 10, 2015

@author: agutierrez
'''
from __future__ import unicode_literals

import re

from madmex.mapper.base import BaseBundle
from madmex.persistence.database.connection import RawProduct
from madmex.util import create_file_name, get_files_from_folder


class Bundle(BaseBundle):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.file_dictionary = {
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}\.tif$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_browse\.tif$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_license\.txt$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_metadata\.xml$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_readme\.txt$':None,
                           r'^\d{7}_\d{4}-\d{2}-\d{2}_RE\d_3A_\d{6}_udm\.tif$':None
                           }
        self._look_for_files()

    def _look_for_files(self):
        for key in self.file_dictionary.iterkeys():
            for name in get_files_from_folder(self.path):
                if re.match(key, name):
                    self.file_dictionary[key] = create_file_name(self.path, name)
    def is_consistent(self):
        '''
        Check if this bundle is consistent.
        '''
        pass

    def can_identify(self):
        return len(self.get_files()) == len(self.file_dictionary)
    
    def get_name(self):
        return 'RapidEye'
    
    
    def get_files(self):
        return [file_path for file_path in self.file_dictionary.itervalues() if file_path]
    
    def get_database_object(self):
        return RawProduct (
                uuid='1235345f',
                acquisition_date=None,
                ingest_date=None,
                path='/my/path',
                legend=None,
                geometry='self.my_geometry',
                information=None,
                product_type=None,
                type='raw'
                )
    
if __name__ == '__main__':
    path = '/LUSTRE/MADMEX/staging/rapideye/2014cov2/entrega/1350406_2014-05-18_RE5_3A_243522'
    res = Bundle(path)
    if res.can_identify():
        print 'Hurray! identified.'
        print 'Files are:'
        for f in res.get_files():
            print f
    else:
        print 'Buhuu, this directory sucks.'
    
