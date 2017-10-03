'''
Created on Jul 10, 2015

@author: agutierrez
madmex.util
This package contains several useful classes and methods.
'''

from __future__ import unicode_literals

import json
import math
import os
from os.path import isdir
import re
from shutil import rmtree
import shutil
import sys
import time
import unicodedata
import urllib
import urllib2

from psycopg2._psycopg import AsIs

from madmex import LOGGER
from madmex.configuration import SETTINGS


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
    
def remove_directory(path):
    '''
    Removes the directory in the given path recursively.
    '''
    shutil.rmtree(path)

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
def get_basename_of_file(filename):
    ''''
    Get base name of file
    '''
    return os.path.basename(filename)
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

def adapt_numpy_float(numpy_float):
    return AsIs(numpy_float)

def check_if_file_exists(filename):
    return os.path.isfile(filename)

def json_to_file(filename, json_dict):
    '''
    This method dumps the given json into a file.
    '''
    with open(filename, 'w') as f:
        f.write(json.dumps(json_dict, indent=4))
def json_from_file(filename):
    '''
    This method loads a json object from a file.
    '''
    print filename
    return json.loads(filename)

def size_of_fmt(num):
    '''
    Lookup table that is used as helper for download chunks.
    '''
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
def download_chunks(url, rep, nom_fic):
    '''
    This method downloads a file in chunks.
    '''
    req = urllib2.urlopen(url)
    downloaded = 0
    CHUNK = 1024 * 1024 *8
    total_size = int(req.info().getheader('Content-Length').strip())
    total_size_fmt = size_of_fmt(total_size)
    with open(rep+'/'+nom_fic, 'wb') as fp:
        start = time.clock()
        LOGGER.info('Downloading %s %s:' % (nom_fic, total_size_fmt))
        while True:
            chunk = req.read(CHUNK)
            downloaded += len(chunk)
            done = int(50 * downloaded / total_size)
            sys.stdout.write('\r[{1}{2}]{0:3.0f}% {3}ps'.format(math.floor((float(downloaded)/ total_size) * 100),'=' * done,' ' * (50 - done),size_of_fmt((downloaded // (time.clock() - start)) / 8)))
            sys.stdout.flush()
            if not chunk: break
            fp.write(chunk)

def download_landsat_scene(url, directory, filename):
    '''
    This method downloads a scene directly from usgs. In order to do so, it
    pretends to be a browser to build a request that is accepted by the server.
    We added the headers so we don't get banned when the server detects that we
    are doing lots of requests. This idea is based on the landsat downloader:
    https://github.com/olivierhagolle/LANDSAT-Download
    '''
    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)
    data=urllib2.urlopen("https://ers.cr.usgs.gov").read()
    token_group = re.search(r'<input .*?name="csrf_token".*?value="(.*?)"', data)
    if token_group:
        token = token_group.group(1)
    else:
        LOGGER.error('The cross site request forgery token was not found.')
        sys.exit(1)
    usgs = {'account':getattr(SETTINGS, 'USGS_USER'), 'passwd':getattr(SETTINGS, 'USGS_PASSWORD')}
    params = urllib.urlencode(dict(username=usgs['account'], password=usgs['passwd'], csrf_token=token))
    request = urllib2.Request("https://ers.cr.usgs.gov/login", params, headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})
    f = urllib2.urlopen(request)
    data = f.read()
    f.close()    
    download_chunks(url, directory, filename)



if __name__ == '__main__':
    print get_base_name('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_extension('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/myawesomefile.ext.json')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a/')
    print get_parent('/LUSTRE/MADMEX/eodata/rapideye/1447720/2013/2013-02-11/l3a')
    print relative_path('/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-15/sr', '/LUSTRE/MADMEX/eodata/oli_tirs/21048/2015/2015-01-15/sr/LC80210482015015LGN00_MTL.txt' )
    print get_basename_of_file('/LUSTRE/MADMEX/eodata/oli_tirs/21048/2015/2015-01-15/sr/LC80210482015015LGN00_MTL.txt')
    print create_file_name('/LUSTRE/MADMEX/staging/antares_test/oli_tirs/21048/2015/2015-01-15/sr', get_basename_of_file('/LUSTRE/MADMEX/eodata/oli_tirs/21048/2015/2015-01-15/sr/LC80210482015015LGN00_MTL.txt'))
    print check_if_file_exists('/LUSTRE/MADMEX/eodata/oli_tirs/21048/2015/2015-01-15/sr/LC80210482015015LGN00_MTL.txt')