'''
Created on 24/08/2015

@author: erickpalacios
'''

from __future__ import unicode_literals
from madmex.transformation.base import BaseTransformation
from madmex import LOGGER
import numpy
from scipy import linalg, stats
import math
class Transformation(BaseTransformation):
    '''
    classdocs
    '''
    def __init__(self, image1_array, image2_array):
        '''
        Constructor
        '''
        self.output = None
        self.execute(image1_array, image2_array)
    def preprocessing(self, image1_array, image2_array):
        '''
        Function to extract valid pixels and paremeters for imad transformation
        '''
        bands, rows, cols = image1_array.shape
        image_bands_flattened = numpy.zeros((2*bands, cols*rows))
        for k in xrange(bands):
            image_bands_flattened[k, :] = numpy.ravel(image1_array[k, :, :])
            image_bands_flattened[bands+k, :] = numpy.ravel(image2_array[k, :, :])
        no_data_value = 0 # TODO: every image needs to have nodata value set to 0
        index1_no_data = image_bands_flattened[0, :] == no_data_value
        index2_no_data = image_bands_flattened[bands, :] == no_data_value
        index_no_data = index1_no_data | index2_no_data
        index = index_no_data == False
        image_bands_flattened = image_bands_flattened[:, index]
        index_sum = numpy.sum(index)
        return (image_bands_flattened, bands, rows, cols, index, index_sum, numpy.ones(int(index_sum)), 1.0, numpy.zeros(bands), 0, (bands+1)*(bands+1), True)
    def execute(self, image1_array, image2_array, MIN_DELTA = 0.02):
        '''
        The imad transformation of two images
        '''
        image_bands_flattened, bands, rows, cols, index, index_sum, wt, delta, oldrho, iteration, max_iterations, flag = self.preprocessing(image1_array, image2_array)
        self.outcorrlist = []
        MIN_DELTA = 0.02
        print("Starting iMAD iterations")  
        while (delta > MIN_DELTA) and (iteration < max_iterations) and flag:
            try:
                print("iMAD iteration: %d" % iteration)
                sumw = numpy.sum(wt)
                means = numpy.average(image_bands_flattened, axis=1, weights=wt)
                dmc = image_bands_flattened - means[:, numpy.newaxis]
                dmc = numpy.multiply(dmc, numpy.sqrt(wt))
                sigma = numpy.dot(dmc, dmc.T) / sumw
                s11 = sigma[0:bands, 0:bands]
                s22 = sigma[bands:, bands:]
                s12 = sigma[0:bands, bands:]
                s21 = sigma[bands:, 0:bands]
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
                delta = numpy.sum(numpy.abs(rho - oldrho))
                if(not math.isnan(delta)):
                    self.outcorrlist.append(rho)
                    #normalize dispersions  
                    tmp1 = numpy.dot(numpy.dot(a.T, s11), a)
                    tmp2 = 1. / numpy.sqrt(numpy.diag(tmp1))
                    tmp3 = numpy.tile(tmp2, (bands, 1))
                    a = numpy.multiply(a, tmp3)
                    b = numpy.mat(b)
                    tmp1 = numpy.dot(numpy.dot(b.T, s22), b)
                    tmp2 = 1. / numpy.sqrt(numpy.diag(tmp1))
                    tmp3 = numpy.tile(tmp2, (bands, 1))
                    b = numpy.multiply(b, tmp3)
                    #assure positive correlation
                    tmp = numpy.diag(numpy.dot(numpy.dot(a.T, s12), b))
                    b = numpy.dot(b, numpy.diag(tmp / numpy.abs(tmp)))
                    #canonical and MAD variates
                    U = numpy.dot(a.T , (image_bands_flattened[0:bands, :] - means[0:bands, numpy.newaxis]))    
                    V = numpy.dot(b.T , (image_bands_flattened[bands:, :] - means[bands:, numpy.newaxis]))          
                    MAD = U - V  
                    #new weights        
                    var_mad = numpy.tile(numpy.mat(2 * (1 - rho)).T, (1, index_sum))    
                    chisqr = numpy.sum(numpy.multiply(MAD, MAD) / var_mad, 0)
                    wt = numpy.squeeze(1 - numpy.array(stats.chi2._cdf(chisqr, bands))) 
                    oldrho = rho
                    print("Processing of iteration %d finished [%f] ..." % (iteration, numpy.max(delta)))  
                    iteration += 1
                else:
                    flag=False
                    LOGGER.warning("Processing in iteration %d produced error. Taking last MAD of iteration %d" % (iteration,iteration-1))
            except Exception, error:
                flag = False
                #iteration = max_iterations  
                print("iMAD transform failed with error: %s" % str(repr(error))) 
                LOGGER.warning("Processing in iteration %d produced error. Taking last MAD of iteration %d" % (iteration,iteration-1))
        self.postprocessing(rows, cols, bands, index, chisqr, MAD)
    def postprocessing(self, rows, cols, bands, index, chisqr, MAD): 
        '''
        Reshape to original image size, by including nodata pixels    
        '''
        MADout = numpy.zeros((int(bands + 1), cols * rows))
        MADout[0:bands, index] = MAD
        MADout[bands:(bands + 1), index] = chisqr
        # close
        MAD = None
        chisqr = None
        # return to multidimensional array structure (multispectral image)
        print("Reshaping structure of MAD components")
        self.output = numpy.zeros((bands + 1, rows, cols))
        for b in xrange(bands + 1):
                self.output[b, :, :] = (numpy.resize(MADout[b, :], (rows, cols)))
        # close
        MADout = None

        
        