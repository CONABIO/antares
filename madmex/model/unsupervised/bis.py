'''
Created on Dec 2, 2017

@author: agutierrez
'''
import logging

from madmex.model.base import BaseModel
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import get_basename, get_parent, get_basename_of_file, \
    create_filename
from web.settings import TEMP_FOLDER, BIS_LICENSE


OPTIONS = {'t':50,
           's':0.7,
           'c':0.3,
           'mp':True,
           'xt':40,
           'rows':625
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
        print shell_string
        LOGGER.debug('Docker command: %s', shell_string)
        #output = local.execute(shell_string)
        #print output