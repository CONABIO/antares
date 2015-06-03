'''
madmex.core.controller
Controller package.
'''
from datetime import date
from importlib import import_module
import os
import pkgutil
import sys

from madmex.core.controller.base import BaseCommand, CommandError


COMMANDS_PACKAGE = 'madmex.core.controller.commands'

def find_commands(management_dir):
    '''
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    '''
    command_dir = os.path.join(management_dir, 'commands')
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]


def load_command_class(name):
    '''
    Given a command name and an application name, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    '''
    module = import_module('%s.%s' % (COMMANDS_PACKAGE, name))
    return module.Command()

def fetch_command(subcommand):
    '''
    This method retrieves the command name to be loaded.
    Parameters
    ----------
    subcommand : str
                 Name of the command to be used.
    '''
    commands = find_commands(__path__[0])
    if subcommand in commands:
        klass = load_command_class(subcommand)
    else:
        raise CommandError("Command not found.")
    return klass

class CommandLineLauncher(object):
    '''
    This class creates an object to launch processes using the command line
    interface. The command line arguments are passed via the constructor, and
    the command to be execuded is identified as the second argument in the
    arguments list.
    '''
    def __init__(self, argv=None):
        """
        Constructor for the CommandLineLauncher class, it keeps a reference
        for the argument list and holds the name of the script that is being
        executed.
        """
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
    def execute(self):
        '''
        Executes the command given by the user and represented
        by this object. In case no command is given, it shows a help
        message.
        '''
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'
        fetch_command(subcommand).run_from_argv(self.argv)

def madmex_copyright():
    '''
    Copyright legend for the MADMex system.
    '''
    return "MADMex 2009-%s" % date.today().year

def execute(argv=None):
    '''
    Main entry point for the MADMex system.
    '''
    print madmex_copyright()
    launcher = CommandLineLauncher(argv)
    launcher.execute()
