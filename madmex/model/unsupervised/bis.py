'''
Created on Dec 2, 2017

@author: agutierrez
'''
import logging

import numpy
from rasterio import features
import rasterio

from madmex.model.base import BaseModel
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import get_basename, get_parent, get_basename_of_file, \
    create_filename
from web.settings import TEMP_FOLDER, BIS_LICENSE


OPTIONS = {'t':100,
           's':0.7,
           'c':0.3,
           'mp':True,
           'xt':40,
           'rows':1000
          }

LOGGER = logging.getLogger(__name__)

class Model(BaseModel):
    '''
    classdocs
    '''


    def __init__(self, options=None):
        '''
        Constructor
        '''
        if not options:
            self.t = OPTIONS['t']
            self.s = OPTIONS['s']
            self.c = OPTIONS['c']
            self.mp = OPTIONS['mp']
            self.xt = OPTIONS['xt']
            self.rows = OPTIONS['rows']
    
    def predict(self, image_path):
        local = LocalProcessLauncher()
        image_name = get_basename_of_file(image_path)
        image_folder = get_parent(image_path)
        license_file = create_filename(TEMP_FOLDER, 'license.txt')
        with open(license_file, 'w') as the_file:
            the_file.write(BIS_LICENSE)
        shell_string_template = 'docker run -v %s:/data -v %s:/segmentation/license.txt madmex/segmentation python /segmentation/segment.py /data/%s -t %g -s %g -c %g --mp %s --xt %g --rows %g' 
        shell_string = shell_string_template % (image_folder, license_file, image_name, self.t, self.s, self.c, self.mp, self.xt, self.rows)
        LOGGER.debug('Docker command: %s', shell_string)
        local.execute(shell_string)
        segmented_file = '%s_%s_%s_%s.tif' % (image_path, self.t, ''.join(str(self.s).split('.')), ''.join(str(self.c).split('.')))
        with rasterio.open(segmented_file) as src:
            meta = src.meta
            transform = src.transform    
            segments = src.read(1)
        shapes = features.shapes(segments.astype(numpy.uint16), transform=transform)
        return shapes, transform, meta