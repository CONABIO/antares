'''
Created on Jun 3, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.core.controller.commands import get_bundle_from_path


def _get_bundle_from_path(path):
    '''
    This method tries to instance every bundle using the given directory. When
    a bundle is able to identify the files present in the directory the instance
    of that bundle is returned to the caller.
    '''
    return get_bundle_from_path(path, '../../../mapper')

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--ima', nargs='*', help='This argument represents'
            ' the first image to be processed.')
        parser.add_argument('--imb', nargs='*', help='This argument represents'
            ' the second image to be processed.')
        parser.add_argument('--output', nargs='*', help='The output filename')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
        image_a = options['ima'][0]
        image_b = options['imb'][0]
        output_image = options['output'][0]
        
        bundle_a = _get_bundle_from_path(image_a)
        bundle_b = _get_bundle_from_path(image_a)
        
        print 'Image %s will be compared against image %s. Output will be available' \
              ' at %s.' % (image_a, image_b, output_image)
