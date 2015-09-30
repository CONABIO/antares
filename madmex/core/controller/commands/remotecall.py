'''
Created on Sep 25, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex import _
from madmex.core.controller.base import BaseCommand, CommandParser
from madmex.persistence.database.connection import SESSION_MAKER, Host
import madmex.persistence.database.connection as connection
from madmex.persistence.driver import query_host_configurations, \
    get_host_from_command
from madmex.remote.dispatcher import RemoteProcessLauncher
from madmex.remote.manager import CommandManager


class Command(BaseCommand):
    '''
    classdocs
    '''
    def add_arguments(self, parser):
        '''
        Adds the sum argument for this command, of course this will change in
        the final implementation.
        '''
        parser.add_argument('--command', nargs='*', help='<command name> <command \
            line arguments>')
        parser.add_argument('--register', nargs='*', help='<type of registry host/command> \
            <registre arguments (hostname, alias, user, password, port, configuration) \
            or (host_configuration, command, queue)>')

    def handle(self, **options):
        '''
        This command lets the user launch a process in a remote host. It also lets
        the user to register new hosts and new commands in the database.
        '''
        register = options['register']
        if register:
            manager = CommandManager()
            register_type = register[0]
            if register_type == 'host':
                hostname = register[1]
                alias = register[2]
                user = register[3]
                password = register[4]
                port = int(register[5])
                configuration = register[6]
                manager.register_hostname(hostname, alias, user, password, port, configuration)
            elif register_type == 'command':
                hosts = query_host_configurations()
                command = register[2]
                queue = register[3]
                host_configuration = register[1]
                for host in hosts:
                    if host_configuration == host['configuration']:
                        host_id = host['pk_id']
                        manager.register_command(host_id, command, queue)
        else:
            command = options['command'][0]
            arguments = ' '.join(options['command'][1:])
            hosts_from_command = get_host_from_command(command)
            print 'The command to be executed is %s in the host %s' % (command, hosts_from_command[0].hostname)
            remote = RemoteProcessLauncher(hosts_from_command[0])
            remote.execute(arguments)
