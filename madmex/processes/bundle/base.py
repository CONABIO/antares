'''
Created on 18/06/2015

@author: erickpalacios
'''
import os

class BaseBundle(object):
    '''
    This class serves as a base shell for a bundle. A bundle is a set of files
    that represent a working piece of information. The implementation of this
    class is in charge of looking for the needed files and throw an error in
    case any of the given files is missing or is incorrect.
    '''
    def scan(self, list_ref, list_test):
        '''
        This method test whether the elements of list_test are in list_ref and if success return the index 
        list_ref is the reference list
        list_test is the list that we want to test
        '''
        val = False
        k = 0
        while k < len(list_ref) and (not val):
            try:
                index = list_test.index(list_ref[k])
                val = True
                result = index
            except ValueError:
                    k = k+1
        if k == len(list_ref) and (not val):
            result = 'not founded'
        return result
    def is_consistent(self):
        '''
        Subclasses must implement this method.
        '''
        raise NotImplementedError(
            'subclasses of BaseBundle must provide a '
            'is_consistent() method')
    def get_entries(self, path):
        "return list of entries within a directory"
        return os.listdir(path)
    def join_path_folder(self, path, folder):
        '''
        return path of folder
        '''
        return os.path.join(path, folder)
    def get_extension(self, filename):
        '''
        return extension of file given it's name
        '''
        path_name, file_extension = os.path.splitext(filename)
        return file_extension.strip('.')
        