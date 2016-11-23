'''
Created on Nov 21, 2016

@author: agutierrez
'''


from __future__ import unicode_literals

import numpy
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.neural_network.multilayer_perceptron import MLPClassifier
from sklearn.preprocessing.data import MinMaxScaler

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands.indexes import open_handle
from madmex.core.controller.commands.ingest import _get_bundle_from_path
from madmex.mapper.data._gdal import create_raster_from_reference, create_raster
from madmex.util import create_file_name, get_base_name


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
        parser.add_argument('--model', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        
        
        random_int = 1
        
        '/Users/agutierrez/Documents/maestria/machine-learning/proyecto/features/df%s-raster.tif'
        '/Users/agutierrez/Documents/maestria/machine-learning/proyecto/raster/df%s-training.tif'
        
        training_template = options['training'][0]
        target_template = options['target'][0]
        model_path = options['model'][0]
        features = training_template % random_int
        training = target_template % random_int
        features_array = open_handle(features)
        training_array = open_handle(training)
        features_flatten = numpy.ravel(features_array).reshape(10, 200 * 200)
        training_flatten = numpy.ravel(training_array).reshape(200 * 200)
        for i in range(1,52):
            features = training_template % (i + 1)
            training = target_template % (i + 1)
            features_array = open_handle(features)
            training_array = open_handle(training)
            features_flatten = numpy.concatenate((features_flatten, numpy.ravel(features_array).reshape(10, 200 * 200)), axis=1)
            training_flatten = numpy.concatenate((training_flatten, numpy.ravel(training_array).reshape(200 * 200)), axis=0)
        print features_flatten.shape
        print training_flatten.shape
        print 'number of NONE elements' 
        print training_flatten[0:100]
        mask = training_flatten!=0
        print numpy.sum(training_flatten==0)
        print features_flatten.shape
        print len(training_flatten)
        features_flatten = features_flatten[:,mask]
        training_flatten = training_flatten[mask]
        for i in range(10):
            features_flatten[i] = MinMaxScaler().fit_transform(features_flatten[i])
            print '******** ',i
            print 'max:'
            print numpy.max(features_flatten[i])
            print 'min:'
            print numpy.min(features_flatten[i])
        print '---------' 
        print features_flatten.shape
        print len(training_flatten)
        print numpy.unique(training_flatten)
        X_train, X_test, y_train, y_test = train_test_split(numpy.transpose(features_flatten), training_flatten, train_size=0.70)
        import time
        import warnings
        start_time = time.time()
        model = RandomForestClassifier(n_estimators=1000,n_jobs=8)
        #model = svm.LinearSVC(C=10)
        #model = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(100, 7), max_iter=400,verbose=10, random_state=1)
        model.fit(X_train, y_train)
        print("--- %s seconds ---" % (time.time() - start_time))
        
        from sklearn.externals import joblib
        joblib.dump(model, model_path) 
        warnings.filterwarnings('ignore')
        start_time = time.time()
        print model.score(X_test,y_test)
        print("--- %s seconds ---" % (time.time() - start_time))
