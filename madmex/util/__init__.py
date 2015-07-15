'''
madmex.util
This package contains several useful classes and methods.
'''

from __future__ import unicode_literals

import os
from os.path import isdir

def format_string(string, spaces, size):
    '''
    This function creates a new string of the given size with the number of
    spaces at the beginning and the given string following.
    '''
    output = ""
    chunk = size - spaces - 2
    output += space_string(spaces, " ") + "'" + string[0:chunk] + "'\n"
    indented_chunk = size - (spaces + 4) - 2
    for i in range(chunk, len(string), indented_chunk):
        output += space_string(spaces + 4, " ") + "'" + string[i: i + indented_chunk] + "'\n"
    return output

def space_string(length, character):
    '''
    Creates a string repeating the given string, length times.
    '''
    output = ""
    i = 0
    while i < length:
        output += character
        i += 1
    return output

def is_file(path):
    '''
    Checks if url is a file.
    '''
    return os.path.isfile(path)

def is_directory(path):
    '''
    Checks if url is a directory.
    '''
    return os.path.isdir(path)

def create_directory_path(directory):
    '''
    Creates directories if not existing as subdirectories in a destination folder
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def is_empty(path):
    '''
    Check if directory is empty.
    '''
    return True if not os.listdir(path) else False

def create_file_name(path, file_name):
    '''
    Joins path with filename.
    '''
    return os.path.join(path, file_name)

def remove_file(path):
    '''
    Removes the file in the given path.
    '''
    os.remove(path)
    
def relative_path(path, relative):
    '''
    Joins a base path with a relative one and returns an absoulte representation
    of the path.
    '''
    return os.path.abspath(os.path.join(os.path.dirname(path), relative))

def get_contents_from_folder(path):
    '''
    Returns a list with the files and directories found in the given path.
    '''
    return os.listdir(path)

def get_files_from_folder(path):
    '''
    Returns a list with the files found in the given path.
    '''
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_directories_from_folder(path):
    '''
    Returns a list with the directories found in the given path.
    '''
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def get_path_from_list(paths):
    '''
    Given a list of paths, this method returns a path joining all of them.
    '''    
    my_path = ''
    for path in paths:
        my_path = os.path.join(my_path, path)
    return my_path
