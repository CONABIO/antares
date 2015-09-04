'''
Created on 24/08/2015

@author: erickpalacios
'''

from __future__ import unicode_literals

import logging
import math
from scipy import linalg, stats

import numpy

from madmex.transformation.base import BaseTransformation


LOGGER = logging.getLogger(__name__)

MIN_DELTA = 0.02

class Transformation(BaseTransformation):
    '''
    classdocs
    '''
    def __init__(self, image1_array, image2_array):
        '''
        Constructor
        '''
        self.image1_array = image1_array
        self.image2_array = image2_array
        self.output = None
        self.bands, self.rows, self.columns = image1_array.shape
        self.image_bands_flattened = None
        self.index = None
        self.index_sum = None
        self.weights = None
        self.chi_squared = None
        self.MAD = None
    def preprocessing(self):
        '''
        Function to extract valid pixels and parameters in order to prepare things
        for the imad transformation.
        '''
        image_bands_flattened = numpy.zeros((2 * self.bands, self.columns * self.rows))
        for k in xrange(self.bands):
            image_bands_flattened[k, :] = numpy.ravel(self.image1_array[k, :, :])
            image_bands_flattened[self.bands + k, :] = numpy.ravel(self.image2_array[k, :, :])
        no_data_value = 0 # TODO: every image needs to have nodata value set to 0
        index1_no_data = image_bands_flattened[0, :] == no_data_value
        index2_no_data = image_bands_flattened[self.bands, :] == no_data_value
        index_no_data = index1_no_data | index2_no_data
        self.index = index_no_data == False
        self.image_bands_flattened = image_bands_flattened[:, self.index]
        self.index_sum = numpy.sum(self.index)
        self.weights = numpy.ones(int(self.index_sum))
        self.delta = 1.0
        self.max_iterations = (self.bands + 1) * (self.bands+1)
        
    def processing(self):
        '''
        The iteratively Multivariate Alteration Detection (MAD) transformation of two
        images. Taking the difference between the canonical variates from a
        canonical correlation analysis we obtain the MAD components.
        '''
        self.outcorrlist = []
        iteration = 0
        flag = True
        MIN_DELTA = 0.02
        LOGGER.info('Starting iMAD iterations.')  
        old_rho = numpy.zeros(self.bands)
        while (self.delta > MIN_DELTA) and (iteration < self.max_iterations) and flag:
            try:
                LOGGER.info('iMAD iteration: %d', iteration)
                weighted_sum = numpy.sum(self.weights)
                means = numpy.average(self.image_bands_flattened, axis=1, weights=self.weights)
                dmc = self.image_bands_flattened - means[:, numpy.newaxis]
                dmc = numpy.multiply(dmc, numpy.sqrt(self.weights))
                sigma = numpy.dot(dmc, dmc.T) / weighted_sum
                s11 = sigma[0:self.bands, 0:self.bands]
                s22 = sigma[self.bands:, self.bands:]
                s12 = sigma[0:self.bands, self.bands:]
                s21 = sigma[self.bands:, 0:self.bands]
                aux_1 = linalg.solve(s22,s21)
                lamda_a,a = linalg.eig(numpy.dot(s12,aux_1),s11)
                aux_2 = linalg.solve(s11,s12)
                lamda_b,b = linalg.eig(numpy.dot(s21,aux_2),s22)
                #sort a
                sorted_indexes = numpy.argsort(lamda_a)
                a = a[:, sorted_indexes]
                #sort b        
                sorted_indexes = numpy.argsort(lamda_b)
                b = b[:, sorted_indexes]          
                #canonical correlations        
                rho = numpy.sqrt(numpy.real(lamda_b[sorted_indexes])) 
                self.delta = numpy.sum(numpy.abs(rho - old_rho))
                if(not math.isnan(self.delta)):
                    self.outcorrlist.append(rho)
                    #normalize dispersions  
                    tmp1 = numpy.dot(numpy.dot(a.T, s11), a)
                    tmp2 = 1. / numpy.sqrt(numpy.diag(tmp1))
                    tmp3 = numpy.tile(tmp2, (self.bands, 1))
                    a = numpy.multiply(a, tmp3)
                    b = numpy.mat(b)
                    tmp1 = numpy.dot(numpy.dot(b.T, s22), b)
                    tmp2 = 1. / numpy.sqrt(numpy.diag(tmp1))
                    tmp3 = numpy.tile(tmp2, (self.bands, 1))
                    b = numpy.multiply(b, tmp3)
                    #assure positive correlation
                    tmp = numpy.diag(numpy.dot(numpy.dot(a.T, s12), b))
                    b = numpy.dot(b, numpy.diag(tmp / numpy.abs(tmp)))
                    #canonical and MAD variates
                    U = numpy.dot(a.T, (self.image_bands_flattened[0:self.bands, :] - means[0:self.bands, numpy.newaxis]))    
                    V = numpy.dot(b.T, (self.image_bands_flattened[self.bands:, :] - means[self.bands:, numpy.newaxis]))          
                    self.MAD = U - V  
                    #new weights        
                    var_mad = numpy.tile(numpy.mat(2 * (1 - rho)).T, (1, self.index_sum))    
                    self.chi_squared = numpy.sum(numpy.multiply(self.MAD, self.MAD) / var_mad, 0)
                    self.weights = numpy.squeeze(1 - numpy.array(stats.chi2._cdf(self.chi_squared, self.bands))) 
                    old_rho = rho
                    LOGGER.info('Processing of iteration %d finished [%f] ...', iteration, numpy.max(self.delta))
                    iteration += 1
                else:
                    flag=False
                    LOGGER.warning("Processing in iteration %d produced error. Taking last MAD of iteration %d", iteration, (iteration - 1))
            except Exception, error:
                flag = False
                LOGGER.error('iMAD transform failed with error: %s', str(repr(error))) 
                LOGGER.error('Processing in iteration %d produced error. Taking last MAD of iteration %d' % (iteration, iteration - 1))
    def postprocessing(self):
        '''
        Reshape to original image size, by including nodata pixels.   
        '''
        print 'The number of bands is: %s' % self.bands
        mad_output = numpy.zeros((int(self.bands + 1), self.columns * self.rows))
        mad_output[0:self.bands, self.index] = self.MAD
        mad_output[self.bands:(self.bands + 1), self.index] = self.chi_squared
        # close
        self.MAD = None
        self.chi_squared = None
        # return to multidimensional array structure (multispectral image)
        LOGGER.info('Reshaping structure of MAD components')
        self.output = numpy.zeros((self.bands + 1, self.rows, self.columns))
        for b in xrange(self.bands + 1):
                self.output[b, :, :] = (numpy.resize(mad_output[b, :], (self.rows, self.columns)))
        # close
        mad_output = None

        
        