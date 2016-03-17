'''
Created on Jul 10, 2015

@author: agutierrez
madmex.util
This package contains several useful classes and methods.
'''

from __future__ import unicode_literals

import os
from os.path import isdir
import unicodedata


def get_last_package_from_name(package):
    '''
    Returns the string after the last instance of a '.'.
    '''
    return package[package.rfind('.') + 1:]

def remove_accents(input_string):
    '''
    Returns a string representation without problematic characters.
    '''
    nfkd_form = unicodedata.normalize('NFKD', input_string)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
def create_filename_from_string(input_string):
    '''
    Returns a formated version of the given string that will not cause
    problems.
    '''
    return remove_accents(input_string
            .replace(',', '_')
            .replace(' ', '_')
            .replace('\'', '_')
            .replace('.', '_')
            .replace('__', '_')
            .replace('___', '_'))
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

def get_base_name(filename):
    '''
    Get base name of a file without its suffix. 
    '''
    return os.path.splitext(os.path.basename(filename))[0]

def get_extension(filename):
    '''
    Get the extension for a file. 
    '''
    return os.path.splitext(os.path.basename(filename))[1]

def get_parent(filename):
    '''
    This method returns the parent folder for the file or directory given.
    '''
    return os.path.abspath(os.path.join(filename, os.pardir))
def create_file_at_home(filename):
    '''
    Given a filename this method will create the path to that path using the home
    directory as base.
    '''
    return os.path.join(os.path.expanduser('~'), filename)

if __name__ == '__main__':
    print get_base_name('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_extension('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a')
