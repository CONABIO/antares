'''
Created on Jan 9, 2017

@author: agutierrez
'''


from __future__ import unicode_literals

from madmex.core.controller.base import BaseCommand
from madmex.remote.dispatcher import LocalProcessLauncher
from madmex.util import create_file_name


INV_MASK_VALUE = 2
MAX_GAP = 7
STAT_CLASSES = 14
STAT_MAX = 7
STAT_MIN = 0
THRESHOLD = 30
THRESHOLD_COD = 0.8
THRESHOLD_LOG = 270
WINDOW_SIZE = 5

class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--id', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--output', nargs=1, help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        
        id = options["id"][0]
        output = options["output"][0]
        
        print output
        
        in1 = create_file_name(output, 'overlap_master.tif')
        in2 = create_file_name(output, 'overlap_slave.tif')
        in_invar = create_file_name(output, 'invariantPixelMask.tif')
        result = create_file_name(output, 'crosscorrelation_next.tif')
        
        local = LocalProcessLauncher()
        volume = '%s:%s' % (output, output)
        shell_array = ['docker',
                       'run',
                       '--rm',
                       '-v',
                       volume,
                       'madmex/antares',
                       'correlation',
                       '-in1',
                       in1,
                       '-in2',
                       in2,
                       '-in_invar',
                       in_invar,
                       '-val_invar',
                       '%s' % INV_MASK_VALUE,
                       '-out',
                       result,
                       '-window_size',
                       '%s' % WINDOW_SIZE,
                       '-max_gap',
                       '%s' % MAX_GAP]
        shell_string = ' '.join(shell_array)
        
        print shell_string
        log = local.execute(shell_string)
        
        print log
