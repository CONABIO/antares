'''
Created on Jun 3, 2015

@author: agutierrez
'''

from madmex.core.controller.base import BaseCommand
#from madmex.database.insert import i_person, i_address, i_company, i_engineer

from madmex.processes import Manager


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        add
        '''
        parser.add_argument('--spot5', nargs='*')

        parser.add_argument('--newregister', nargs='*', help='This is a stub for the, \
            ingest command')

    def handle(self, **options):
        '''
        handle
        '''
        #options is a dictionary with the process as a key and arguments as values 
        arguments = ['newregister', 'spot5']
        print options
        process = dict((k, v) for k, v in options.iteritems() if k in arguments and v)
        obj = Manager(process)
        obj.execute()
        #ingest=Ingest(options)
        #ingest.run
        