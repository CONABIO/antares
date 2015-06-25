'''
Created on 18/06/2015

@author: erickpalacios
'''
class Basebundle(object):
    '''
    This class serves as a base shell for a bundle. A bundle is a set of files
    that represent a working piece of information. The implementation of this
    class is in charge of looking for the needed files and throw an error in
    case any of the given files is missing or is incorrect.
    '''

    def scan(self):
        '''
        This method will traverse through the list of files in the given
        directory using the given regex dictionary, creating a map for the
        founded files.
        '''
        raise NotImplementedError('subclasses of BaseBundle must provide a scan() method')
    def is_consistent(self):
        '''
        Subclasses must implement this method.
        '''
        raise NotImplementedError(
            'subclasses of BaseBundle must provide a '
            'is_consistent() method')
        