'''
Created on 15/06/2015

@author: erickpalacios
'''
import os.path


class Processes(object):
    '''
    classdocs
    '''

    def result(self):
        '''
        Type: success or not
        '''
        pass
    def execute(self):
        '''
        execute
        '''
        pass
    def getentries(self, path):
        "return list of entries within a directory"
        return os.listdir(path)
    def getpath(self, path, folder):
        '''
        return path of folder
        '''
        return os.path.join(path, folder)
    def getextension(self, filename):
        '''
        return extension of file given it's name
        '''
        path_name, file_extension = os.path.splitext(filename)
        return file_extension
        
    def createoutputfile(self):
        '''
        create output file
        '''
        pass
     