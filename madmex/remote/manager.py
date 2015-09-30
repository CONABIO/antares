'''
Created on Sep 28, 2015

@author: agutierrez
'''

from __future__ import unicode_literals

from madmex.persistence.database.connection import Host, Command
from madmex.persistence.driver import persist_host, persist_command


class CommandManager(object):
    '''
    This class is a controller for the commands, it works calls the database to
    query, insert and delete command related objects from it.
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def register_hostname(self, hostname, alias, user, password, port, configuration):
        '''
        This method adds an entry to the database in the host table.
        '''
        host = Host(
            hostname=hostname,
            alias=alias,
            user=user,
            password=password,
            port=port,
            configuration=configuration)
        persist_host(host)
        
    def register_command(self, host_id, command, queue):
        '''
        This method adds an entry to the database in the command table.
        '''
        command = Command(
            host_id=host_id,
            command=command,
            queue=queue
            )
        persist_command(command)
