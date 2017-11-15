'''
madmex.remote
'''
import base64
import json
import logging
import os
import sys

import requests

from madmex.util import create_filename, is_file
from six.moves import urllib
from web.settings import USGS_USER, USGS_PASSWORD


logger = logging.getLogger(__name__)

version = 'v1'

def maybe_download_and_extract(target_directory, scene_url):
    '''
    This method will try to download the requested url, if 
    a file with the url name has already been downloaded it
    will not proceed.
    '''
    filename = scene_url.split('/')[-1]
    filepath = create_filename(target_directory, filename)
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
    else:
        logger.info('%s was already downloaded at %s' % (filename, target_directory))

class UsgsApi():
    def __init__(self):
        '''
        This is the constructor, it creates an object that holds
        credentials to usgs portal. 
        '''
        if USGS_USER != None and USGS_PASSWORD != None:
            self.username = USGS_USER
            self.password = USGS_PASSWORD
            self.host = 'https://espa.cr.usgs.gov'
        else:
            logger.error('Please add the usgs credentials to the .env file.')
            sys.exit(-1)

    def _consume_api_urllib(self, endpoint, data=None):
        '''
        This method hides the complexity of making a request to usgs,
        depending on whether data parameter is given or not, it makes
        a GET or a POST request. It requires an endpoint to query the
        api if an invalid request is given, then the aip will answer
        with a 404 error message.
        '''
        raw = "%s:%s" % (USGS_USER, USGS_PASSWORD)
        authorization = 'Basic %s' % base64.b64encode(raw).strip()
        url = self.host + '/api' + endpoint
        if not data:
            request = urllib.request.Request(url)
        else: # a POST request
            request = urllib.request.Request(url, data=data,
                             headers={'content-type': 'application/json'})
        logger.info(url)
        request.add_header('Authorization', authorization)
        response = urllib.request.urlopen(request)
        data = json.load(response.fp)
        return data
    
    def _consume_api_requests(self, endpoint, data=None):
        '''
        This method hides the complexity of making a request to usgs,
        depending on whether data parameter is given or not, it makes
        a GET or a POST request. It requires an endpoint to query the
        api if an invalid request is given, then the aip will answer
        with a 404 error message.
        '''
        url = self.host + '/api' + endpoint
        logger.info(url)
        if not data:
            response = requests.get(url, auth=(USGS_USER,USGS_PASSWORD))
        else: # a POST request
            response = requests.post(url, data = data, auth=(USGS_USER,USGS_PASSWORD))
        data = response.json()
        return data

    def get_functions(self):
        '''
        Will query the api for the valid functions that it exposes.
        '''
        return self._consume_api_requests('/%s' % version)

    def get_projections(self):
        '''
        Returns the available projections that the api supports.
        '''
        return self._consume_api_requests('/%s/projections' % version)

    def get_available_products(self, scene_id):
        '''
        Given a scene id, this method returns the available products
        that can be requested in an order.
        '''
        return self._consume_api_requests('/%s/available-products/%s' % (version, scene_id))
    
    def get_formats(self):
        '''
        Returns the available formats in which the data can be requested.
        '''
        return self._consume_api_requests('/%s/formats' % version)
    
    def order(self, collection, inputs, products):
        '''
        This is the only method implementing a post request. Data about which
        scenes are requested and which products are needed is required on 
        this method calling. More complex querying is supported, we are keeping
        this simple for now.
        '''
        request_json = {'format':'gtiff',
                        'note':'testing',
                        collection:{
                                'inputs':inputs,
                                'products':products
                            }
                        } 
        payload = json.dumps(request_json).encode('utf8')
        print payload
        return self._consume_api_requests('/%s/order' % version, payload)
    
    def get_list_orders(self):
        '''
        This methos returns the status of the orders that have been posted.
        '''
        return self._consume_api_requests('/%s/list-orders' % version)

    def get_resampling_methods(self):
        '''
        Returns the resampling methods available when the products are
        requested in a different resolution that the standard one. Default
        value will be nearest neighbors.
        '''
        return self._consume_api_requests('/%s/resampling-methods' % version)

    def get_user_info(self):
        '''
        Returns information about the user that the credentials that this
        object holds.
        '''
        return self._consume_api_requests('/%s/user' % version)

    def get_list_order(self, order_id):
        '''
        Returns the status of the given order.
        '''
        url = '/%s/item-status/%s' % (version, order_id)
        return self._consume_api_requests(url)
