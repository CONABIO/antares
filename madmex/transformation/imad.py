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
        self.chisqr = None
        self.MAD = None
    def preprocessing(self):
        '''
        Function to extract valid pixels and paremeters for imad transformation
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
        self.wt = numpy.ones(int(self.index_sum))
        self.delta = 1.0
        self.iteration = 0
        self.max_iterations = (self.bands + 1) * (self.bands+1)
        self.flag = True
    def processing(self):
        '''
        The imad transformation of two images
        '''

        self.outcorrlist = []
        MIN_DELTA = 0.02
        LOGGER.info('Starting iMAD iterations.')  
        oldrho = numpy.zeros(self.bands)
        while (self.delta > MIN_DELTA) and (self.iteration < self.max_iterations) and self.flag:
            try:
                LOGGER.info("iMAD iteration: %d", self.iteration)
                sumw = numpy.sum(self.wt)
                means = numpy.average(self.image_bands_flattened, axis=1, weights=self.wt)
                dmc = self.image_bands_flattened - means[:, numpy.newaxis]
                dmc = numpy.multiply(dmc, numpy.sqrt(self.wt))
                sigma = numpy.dot(dmc, dmc.T) / sumw
                s11 = sigma[0:self.bands, 0:self.bands]
                s22 = sigma[self.bands:, self.bands:]
                s12 = sigma[0:self.bands, self.bands:]
                s21 = sigma[self.bands:, 0:self.bands]
                aux1=linalg.solve(s22,s21)
                lama,a=linalg.eig(numpy.dot(s12,aux1),s11)
                aux2=linalg.solve(s11,s12)
                lamb,b=linalg.eig(numpy.dot(s21,aux2),s22)
                #sort a
                idx = numpy.argsort(lama)
                a = a[:, idx]
                #sort b        
                idx = numpy.argsort(lamb)
                b = b[:, idx]          
                #canonical correlations        
                rho = numpy.sqrt(numpy.real(lamb[idx])) 
                self.delta = numpy.sum(numpy.abs(rho - oldrho))
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
                    self.chisqr = numpy.sum(numpy.multiply(self.MAD, self.MAD) / var_mad, 0)
                    self.wt = numpy.squeeze(1 - numpy.array(stats.chi2._cdf(self.chisqr, self.bands))) 
                    oldrho = rho
                    LOGGER.info('Processing of iteration %d finished [%f] ...', self.iteration, numpy.max(self.delta))
                    self.iteration += 1
                else:
                    self.flag=False
                    LOGGER.warning("Processing in iteration %d produced error. Taking last MAD of iteration %d", self.iteration, (self.iteration - 1))
            except Exception, error:
                self.flag = False
                LOGGER.error('iMAD transform failed with error: %s', str(repr(error))) 
                LOGGER.error('Processing in iteration %d produced error. Taking last MAD of iteration %d' % (self.iteration, self.iteration - 1))
    def postprocessing(self):
        '''
        Reshape to original image size, by including nodata pixels    
        '''
        print 'The number of bands is: %s' % self.bands
        MADout = numpy.zeros((int(self.bands + 1), self.columns * self.rows))
        MADout[0:self.bands, self.index] = self.MAD
        MADout[self.bands:(self.bands + 1), self.index] = self.chisqr
        # close
        self.MAD = None
        self.chisqr = None
        # return to multidimensional array structure (multispectral image)
        LOGGER.info('Reshaping structure of MAD components')
        self.output = numpy.zeros((self.bands + 1, self.rows, self.columns))
        for b in xrange(self.bands + 1):
                self.output[b, :, :] = (numpy.resize(MADout[b, :], (self.rows, self.columns)))
        # close
        MADout = None

        
        