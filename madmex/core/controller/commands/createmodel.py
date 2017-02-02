'''
Created on Nov 21, 2016

@author: agutierrez
'''


from __future__ import unicode_literals

import logging
import traceback

import numpy
import pandas
import scipy
import scipy.ndimage
from sklearn.cross_validation import train_test_split
from sklearn.decomposition.pca import PCA

from madmex import load_class
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.model.unsupervised import pca
from madmex.util import create_file_name, create_directory_path


SUPERVISED_PACKAGE = 'madmex.model.supervised'
LOGGER = logging.getLogger(__name__)

def save_to_file(data, filename):
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(filename, sep=str(','), encoding='utf-8', index = False, header = False)

def load_model(name):
    '''
    Loads the python module with the given name found in the path.
    '''
    try:
        module = load_class(SUPERVISED_PACKAGE, name)
        return module
    except Exception:
        traceback.print_exc()
        LOGGER.debug('No %s model found.', name)
        
def train_model(X_train, X_test, y_train, y_test, output, model_name):
    model = load_model(model_name)
    persistence_directory = create_file_name(output, model_name)
    create_directory_path(persistence_directory)
    model_instance = model.Model(persistence_directory)
    model_instance.fit(X_train, y_train)
    model_instance.save(persistence_directory)
    predicted = model_instance.predict(X_test)
    model_instance.create_report(y_test, predicted, create_file_name(persistence_directory, 'report.txt'))

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--training', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--target', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--index', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--model', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        random_int = 1
        training_template = options['training'][0]
        target_template = options['target'][0]
        index_template = options['index'][0]
        output = options['output'][0]
        models = options['model']
        features = training_template % random_int
        training = target_template % random_int
        index = index_template % random_int
        features_array = open_handle(features)
        training_array = open_handle(training)
        index_array = open_handle(index)
            
        labels = numpy.unique(index_array)


        features_flatten = numpy.ravel(features_array).reshape(10, 200 * 200)
        training_flatten = numpy.ravel(training_array).reshape(200 * 200)
        
        array_aux = []
        for j in range(features_array.shape[0]):
            means = scipy.ndimage.measurements.mean(features_array[j,:,:], index_array, labels) 
            print means.shape
            array_aux.append(means)
        for j in range(features_array.shape[0]):
            std = scipy.ndimage.measurements.standard_deviation(features_array[j,:,:], index_array, labels)
            print std.shape
            array_aux.append(std)
        
        print len(array_aux)
        
        features_final = numpy.concatenate([array_aux], axis=0)
          
        print features_final.shape
          
        label_object = []    
        for id in labels:
            values, counts = numpy.unique(training_array[index_array==id], return_counts=True)
            label_object.append(values[numpy.argmax(counts)])
            
        
        
        features_total = features_final
        training_total = label_object
        
        for i in range(1,53):
            features = training_template % (i + 1)
            training = target_template % (i + 1)
            index = index_template % (i + 1)
            features_array = open_handle(features)
            training_array = open_handle(training)
            index_array = open_handle(index)
            
            labels = numpy.unique(index_array)

            array_aux = []
            for j in range(features_array.shape[0]):
                array_aux.append(scipy.ndimage.measurements.mean(features_array[j,:,:], index_array, labels))
            for j in range(features_array.shape[0]):
                array_aux.append(scipy.ndimage.measurements.standard_deviation(features_array[j,:,:], index_array, labels))
            features_final = numpy.concatenate([array_aux], axis=0)
            
            
            print features_final.shape
            
            label_object = []
            
            for id in labels:
                values, counts = numpy.unique(training_array[index_array==id], return_counts=True)
                #print '********* ', values[numpy.argmax(counts)], counts[numpy.argmax(counts)]
                label_object.append(values[numpy.argmax(counts)])
            
            
            print features_total.shape
            print features_final.shape
            features_total = numpy.concatenate((features_total, features_final), axis=1)
            training_total = numpy.concatenate((training_total, label_object), axis=1)
                
                
            print 'label object', len(label_object)
            
                
            #print scipy.ndimage.measurements.mean(training_array, index_array, labels)
            features_flatten = numpy.concatenate((features_flatten, numpy.ravel(features_array).reshape(10, 200 * 200)), axis=1)
            training_flatten = numpy.concatenate((training_flatten, numpy.ravel(training_array).reshape(200 * 200)), axis=0)
        # Remove the elements that map to None
        #mask = training_flatten!=0
        #features_flatten = features_flatten[:,mask]
        #training_flatten = training_flatten[mask]
        
        mask = training_total!=0
        features_flatten = features_total[:,mask]
        training_flatten = training_total[mask]
        
        
        
        
        print features_flatten.shape
        print training_flatten.shape
        X_train, X_test, y_train, y_test = train_test_split(numpy.transpose(features_flatten), training_flatten, train_size=0.8, test_size=0.2)
        
        
        print X_train[0]
        print y_train[0]
        
        
        unsupervised = pca.Model(5)
        unsupervised.fit(X_train) 
        
        '''
        X_train = unsupervised.transform(X_train)
        X_test = unsupervised.transform(X_test) 
        '''
        
        pca_path = create_file_name(output, 'pca')
        create_directory_path(pca_path)
        unsupervised.save(pca_path)

        import time
        for model_name in models:
            start_time = time.time()
            train_model(X_train, X_test, y_train, y_test, output, model_name)
            print "--- %s seconds training %s model---" % ((time.time() - start_time), model_name)
