
'''
JUST AN EXAMPLE REMOVE EVERYTHING FROM HERE
madmex.core.controller
Controller package.
'''
import os
import pkgutil

from madmex.core.controller.base import BaseCommand


COMMANDS_PACKAGE = 'madmex.core.controller.commands'

def find_commands(management_dir):
    '''
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    '''
    command_dir = os.path.join(management_dir, '')
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]

if __name__=='__main__':
    print os.path.dirname(os.path.realpath(__file__))
    print find_commands(os.path.dirname(os.path.realpath(__file__)))


