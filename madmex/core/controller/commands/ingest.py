'''
Created on Jun 3, 2015

@author: agutierrez
'''

#import os

from madmex.core.controller.base import BaseCommand
#from madmex.core.controller import find_commands

from madmex.processes import Manager


class Command(BaseCommand):
    '''
    classdocs
    '''
    
    def add_arguments(self, parser):
        parser.add_argument('--spot5',nargs='*')

        parser.add_argument('--newregister', nargs='*', help='This is a stub for the, \
            ingest command')

    def handle(self,**options):
        #options is a dictionary with the process as a key and arguments as values 
        arguments=['newregister','spot5']
        print options
        process=dict((k,v) for k,v in options.iteritems() if k in arguments and v)
        #enviar process que es un diccionario al paquete processes q llama a newsensor
        obj=Manager(process)
        obj.execute()
        
        #ingest=Ingest(options)
        #ingest.run
        
        
        
    '''
        print options
        
        arguments=options['newregister']
        
        
        if arguments[0]=='newregister':
            nuevo=Newregister(arguments[1])
            #print nuevo._str_()
            print nuevo

    '''         



