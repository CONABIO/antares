'''
madmex.mapper
Core package.
'''
from madmex import find_in_dir


def find_sensors(management_dir):
    '''
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    '''
    return find_in_dir(management_dir,'sensors')



