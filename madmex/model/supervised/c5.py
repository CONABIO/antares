'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import logging

import numpy
import pandas

from madmex.model.base import BaseModel
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_filename


LOGGER = logging.getLogger(__name__)

def save_to_file(data, filename):
    '''
    This method creates a file that will use the train method.
    '''
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)

def save_to_file_cases(data, filename):
    '''
    This method creates a file that will use the predict method.
    '''
    dataframe = pandas.DataFrame(data)
    dataframe['given'] = '?'
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)

def create_names_file(target, bands, filename):
    '''
    This method creates a file that defines the features that will be used in the training
    stage.
    '''
    with open(filename,'w') as names:
        names.write('target.\n')
        for band in range(bands):
            names.write('band%s:\tcontinuous.\n' % band)
        names.write('target:\t%s\n' % ','.join(map(lambda x: '%s.0' % str(x), target)))

class Model(BaseModel):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.path = path
        self.model_name = 'c5'

    def fit(self, X, y):
        '''
        This method creates the necessary files to train a c5 model with the
        c5.0 executable. It creates only the names and data files.
        '''
        train_data = numpy.column_stack((X, y))
        save_to_file(train_data, create_filename(self.path, '%s.data' % self.model_name))
        create_names_file(numpy.unique(y), X.shape[1],create_filename(self.path, '%s.names' % self.model_name))
        launcher = LocalProcessLauncher()
        shell_string = 'docker run --rm -v %s:/results madmex/c5_execution c5.0 -f /results/%s' % (self.path, self.model_name)
        LOGGER.debug('Docker command: %s', shell_string)
        launcher.execute(shell_string)

    def predict(self, X):
        '''
        The c5 model creates a file with the tree extension and it
        will be loaded by the predict executable.
        '''
        save_to_file_cases(X, create_filename(self.path, '%s.cases' % self.model_name))
        local = LocalProcessLauncher()
        shell_string = 'docker run --rm -v %s:/results madmex/c5_execution predict -f /results/%s' % (self.path, self.model_name)
        LOGGER.debug('Docker command: %s', shell_string)     
        output = local.execute(shell_string)
        by_line = output.split('\n')
        y = []
        for line in by_line:
            array_predict = line.split()
            if len(array_predict) == 4:
                y.append(int(float(array_predict[2])))
        return numpy.array(y)

    def save(self, filepath):
        '''
        This method will do nothing in the case of a C5 model. The model is persisted
        by default.
        '''
        pass

    def load(self, filepath):
        '''
        This methid will do nothing in the case of a C5 model.
        '''
        pass
