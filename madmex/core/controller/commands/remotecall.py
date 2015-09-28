'''
Created on Sep 25, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex import _
from madmex.core.controller.base import BaseCommand
from madmex.persistence.database.connection import SESSION_MAKER, Host
from madmex.remote.dispatcher import RemoteProcessLauncher


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--commandpath', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')
        parser.add_argument('--host', nargs='*', help='This is a stub for the, \
            change detection command, right now all it does is sum numbers in \
            the list.')

    def handle(self, **options):
        '''
        In this example command, the values that come from the user input are
        added up and the result is printed in the screen.
        '''
              
        command = ' '.join(options['commandpath'])
        host = options['host'][0]
        
        session = SESSION_MAKER()
        host_object = session.query(Host).filter(Host.alias==host).first()    
        
        print 'The command to be executed is %s in the host %s' % (command, host)
        
        print host_object.hostname
        
        remote = RemoteProcessLauncher(host_object)
        
        remote.execute(command)