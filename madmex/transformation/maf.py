'''
Created on 03/09/2015

@author: erickpalacios
'''
from madmex.transformation.base import BaseTransformation
import logging
import numpy
from scipy import linalg

LOGGER = logging.getLogger(__name__)

class Transformation(BaseTransformation):
    '''
    classdocs
    '''
    
    def __init__(self, image_array):
        '''
        Constructor
        '''
        self.image_array = image_array
        self.output = None
        self.bands, self.rows, self.cols = image_array.shape
    def preprocessing(self):
        '''
        Preprare data for maf transformation
        '''
        self.no_data_value = 0 # TODO: every image needs to have nodata "NA" value set to 0 <-----Discuss if 0 is an appropiate value for NA values
        self.number_of_maf_variates = self.bands - 1
        variates_stack = numpy.zeros((self.cols*self.rows, self.number_of_maf_variates), dtype = float)
        # coavariance matrix from image and itself shifted by 1 pixel
        # (vertically and horizontally)
        rows_1 = self.rows - 1
        cols_1 = self.cols - 1
        self.H = numpy.zeros((rows_1 * cols_1, self.number_of_maf_variates), float)
        self.V = numpy.zeros((rows_1 * cols_1, self.number_of_maf_variates), float)
        LOGGER.info("Reading input bands for MAF transformation")
        for b in range(self.number_of_maf_variates):
            variates = self.image_array[b, :, :]
            self.H[:, b] = numpy.ravel(variates[0:rows_1, 0:cols_1] - variates[0:rows_1, 1:self.cols])
            self.V[:, b] = numpy.ravel(variates[0:rows_1, 0:cols_1] - variates[1:self.rows, 0:cols_1])
            variates_stack[:, b] = numpy.ravel(variates)
        # close useless image data
        self.image_array= None
        # band_data = None
        # label data considered as NA
        nodataidx = variates_stack[:, :] == self.no_data_value
        #variates_stack = numpy.ma.array(variates_stack, mask=self.no_data_value)
        variates_stack = numpy.ma.masked_values(variates_stack, self.no_data_value)
        self.gooddataidx = nodataidx[:, 0] == False
        self.variates_stack = numpy.array(variates_stack.data[self.gooddataidx, :]) 
    def processing(self):
        '''
        Perform the maf transformation
        '''
        # covariance of original bands
        sigma = numpy.ma.cov(self.variates_stack.T, allow_masked=True)
        # covariance for horizontal and vertical shifts
        sigmadh = numpy.ma.cov(self.H.T, allow_masked=True)
        sigmadv = numpy.ma.cov(self.V.T, allow_masked=True)
        # simple pooling of shifts
        sigmad = 0.5 * (numpy.array(sigmadh) + numpy.array(sigmadv))
        #evalues, vec1 = scipy.linalg.eig(sigmad, sigma)
        evalues, vec1 = linalg.eig(sigmad, sigma)

        # Sort eigen values from smallest to largest and apply this order to
        # eigen vector matrix
        sort_index = evalues.argsort()  
        evalues = evalues[sort_index]
        vec1 = vec1[:, sort_index]
        # autocorrelation
        # ac= 1-0.5*vec1
        HH = 1 / numpy.std(self.variates_stack, 0, ddof=1)
        diagvariates = numpy.diag(HH)
        invstderrmaf = numpy.diag((1 / numpy.sqrt(numpy.diag(vec1.T * sigma * vec1))))
        HHH = numpy.zeros((self.number_of_maf_variates), float)
        for b in range(self.number_of_maf_variates):  
            # logger.info("Calculating component %d of MAF transformation" % b)  
            HHH[b] = cmp(numpy.sum((diagvariates * sigma * vec1 * invstderrmaf)[b]), 0)
        sgn = numpy.diag(HHH)  # assure positiviy
        v = numpy.dot(vec1, sgn)
        N = numpy.shape(self.variates_stack)[0]
        X = self.variates_stack - numpy.tile(numpy.mean(self.variates_stack, 0), (N, 1))
        # scale v to give MAFs with unit variance
        aux1 = numpy.dot(numpy.dot(v.T, sigma), v)# dispersion of MAFs
        aux2 = 1 / numpy.sqrt(numpy.diag(aux1))
        aux3 = numpy.tile(aux2.T, (self.number_of_maf_variates, 1))
        v = v * aux3  # now dispersion is unit matrix
        self.mafs = numpy.dot(X, v)
    def postprocessing(self):
        '''
         Reshape to original image size, by including nodata pixels 
        '''
        #    reshape to original image size, by including nodata pixels    
        maf_output = numpy.zeros((self.cols * self.rows, self.number_of_maf_variates))
        maf_output[self.gooddataidx, :] = self.mafs
        #   close mafs
        self.mafs = None
        # return to multidimensional array structure (multispectral image)
        self.output = numpy.zeros((self.number_of_maf_variates, self.rows, self.cols))
        for b in xrange(self.number_of_maf_variates):
            self.output[b, :, :] = (numpy.reshape(maf_output[:, b], (self.rows, self.cols)))
        # close
        maf_output = None
        