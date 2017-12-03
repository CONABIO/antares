'''
Created on Dec 2, 2017

@author: agutierrez
'''
from skimage import segmentation

from madmex.model.base import BaseModel


class Model(BaseModel):
    '''
    classdocs
    '''


    def __init__(self, options):
        '''
        Constructor
        ''' 
        self.model_name = 'slic'
        self.compactness = options['compactness']
        self.avg_segment_size_ha = options['avg_segment_size_ha']
        self.area_ha = options['area_ha']
        
    def predict(self, X):

        n_segments = int(self.area_ha / self.avg_segment_size_ha)
        segments = segmentation.slic(X, 
                          compactness = self.compactness,
                          n_segments = n_segments, 
                          multichannel = True,
                          enforce_connectivity=True)
        return segments