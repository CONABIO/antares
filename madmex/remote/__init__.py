'''
madmex.remote
'''
import base64
import json
import logging
import os
import sys

from madmex.util import create_file_name, is_file
from six.moves import urllib
from web.settings import USGS_USER, USGS_PASSWORD


logger = logging.getLogger(__name__)

def maybe_download_and_extract(target_directory, scene_url):
    
    filename = scene_url.split('/')[-1]
    filepath = create_file_name(target_directory, filename)
    if not is_file(filepath):
        def _progress(count, block_size, total_size):
            sys.stdout.write('\rDownloading %s %.1f%%' %
                       (filename,
                        float(count * block_size) / float(total_size) * 100.0))
            sys.stdout.flush()

        filepath, _ = urllib.request.urlretrieve(scene_url,
                                             filepath,
                                             _progress)
        sys.stdout.write('')
        sys.stdout.flush()
        statinfo = os.stat(filepath)
        logger.info('Successfully downloaded: %s %s bytes' % (filename, statinfo.st_size))

class UsgsApi():
    def __init__(self):
        if USGS_USER != None and USGS_PASSWORD != None:
            
            self.username = USGS_USER
            self.password = USGS_PASSWORD
            self.host = 'https://espa.cr.usgs.gov'
        else:
            logger.error('Please add the usgs credentials to the .env file.')
            sys.exit(-1)
        
    def _consume_api(self, endpoint, arg=None):
        raw = "%s:%s" % (USGS_USER, USGS_PASSWORD)
        authorization = 'Basic %s' % base64.b64encode(raw).strip()
        url = self.host + '/api' + endpoint
        request = urllib.request.Request(url)
        logger.info(url)
        request.add_header('Authorization', authorization)
        response = urllib.request.urlopen(request)
        data = json.load(response.fp)
        return data
    def get_functions(self):
        data = self._consume_api('/v1')
        for key, value in data['operations'].iteritems():
            print key
        
    def get_projections(self):
        return self._consume_api('/v1/projections')
    
    def get_available_products(self):
        return self._consume_api('/v1/available-products')
    
    def get_formats(self):
        return self._consume_api('/v1/formats')
    
    def get_orders(self):
        return self._consume_api('/v1/order')
    
    def get_list_orders(self):
        return self._consume_api('/v1/list-orders')
    def get_resampling_methods(self):
        return self._consume_api('/v1/resampling-methods')
        
    def list_order(self, order_id):
        raw = "%s:%s" % (USGS_USER, USGS_PASSWORD)
        authorization = 'Basic %s' % base64.b64encode(raw).strip()
        url = self.host + '/api/v1/item-status/' + order_id
        logger.debug('Retrieving order from %s.' % url)
        request = urllib.request.Request(url)
        request.add_header('Authorization', authorization)
        response = urllib.request.urlopen(request)
        data = json.load(response.fp)
        
        for scene in data[order_id]:
            if scene['status'] == 'complete':
                pass
                #maybe_download_and_extract('/Users/agutierrez/Documents/scene026036', scene['product_dload_url'])
           
        print json.dumps(data, indent=4, sort_keys=True)
        
        