'''
Created on Nov 25, 2016

@author: agutierrez
'''
from __future__ import unicode_literals

import numpy
import pandas

from madmex.model.base import BaseModel
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_file_name


def save_to_file(data, filename):
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)
    
def save_to_file_cases(data, filename):
    dataframe = pandas.DataFrame(data)
    dataframe['given'] = '?'
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)
    
def create_names_file(target, bands, filename):
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
        self.model_name = 'test'

    def fit(self, X, y):
        train_data = numpy.column_stack((X, y))
        save_to_file(train_data, create_file_name(self.path, '%s.data' % self.model_name))
        create_names_file(numpy.unique(y), X.shape[1],create_file_name(self.path, '%s.names' % self.model_name))
        launcher = LocalProcessLauncher()
        shell_string = 'docker run -v %s:/results madmex/c5_execution c5.0 -f /results/%s' % (self.path, self.model_name)
        print shell_string
        launcher.execute(shell_string)

    def predict(self, X):
        save_to_file_cases(X, create_file_name(self.path, '%s.cases' % self.model_name))
        local = LocalProcessLauncher()
        shell_string = 'docker run -v %s:/results madmex/c5_execution predict -f /results/%s' % (self.path, self.model_name)
        print shell_string        
        output = local.execute(shell_string)
        by_line = output.split('\n')
        y = []
        for line in by_line:
            array_predict = line.split()
            if len(array_predict) == 4:
                y.append(int(float(array_predict[2])))
        return numpy.array(y)

    def save(self, filepath):
        pass
    def load(self, filepath):
        pass
