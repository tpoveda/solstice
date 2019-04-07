#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_browser_utils.py
# by Tomas Poveda
# Module that includes utilities related with files and folders
# ______________________________________________________________________
# ==================================================================="""

import os

# region Constants
SEPARATOR = '/'
BAD_SEPARATOR = '\\'
PATH_SEPARATOR = '//'
SERVER_PREFIX = '\\'
RELATIVE_PATH_PREFIX = './'
BAD_RELATIVE_PATH_PREFIX = '../'

# We use one separator depending if we are working on Windows (nt) or other operative system
NATIVE_SEPARATOR = (SEPARATOR, BAD_SEPARATOR)[os.name=='nt']
# endregion

def get_sub_folders(root_folder, sort=True):
    """
    Return a list with all the sub folders names on a directory
    :param root_folder: str, folder we want to search sub folders for
    :param sort: bool, True if we want sort alphabetically the returned folders or False otherwise
    :return: list<str>, sub folders names
    """

    if not os.path.exists(root_folder):
        raise RuntimeError('Folder {0} does not exists!'.format(root_folder))
    file_names = os.listdir(root_folder)
    result = list()
    for f in file_names:
        if os.path.isdir(os.path.join(os.path.abspath(root_folder), f)):
            result.append(f)
    if sort:
        result.sort()

    return result


def normalize_path(path):
    """
    Normalize a path to solve problems with \\ and // on paths
    :param path: str, path to normalize
    :return: str, normalized path
    """

    return path.replace(BAD_SEPARATOR, SEPARATOR).replace(PATH_SEPARATOR, SEPARATOR)


def clean_path(path):
    """
    Cleans a path. Useful to resolve problems with slashes
    :param path: str
    :return: str, clean path
    """

    # We convert '~' Unix character to user's home directory
    path = os.path.expanduser(str(path))

    # Remove spaces from path and fixed bad slashes
    path = normalize_path(path.strip())

    # Fix server paths
    is_server_path = path.startswith(SERVER_PREFIX)
    while SERVER_PREFIX in path:
        path = path.replace(SERVER_PREFIX, PATH_SEPARATOR)
    if is_server_path:
        path = PATH_SEPARATOR + path

    return path


def get_relative_path(path, start):
    """
    Gets a relative path from a start path
    :param path: str, path to get relative path
    :param start: str, Start path to calculate the relative path from
    """

    if os.path.splitext(start)[-1]:
        start = clean_path(os.path.dirname(start))
    relpath = clean_path(os.path.relpath(path, start))

    # TODO: Check if this is correct
    if not relpath.startswith('../'):
        relpath = './' + relpath

    return relpath


def get_absolute_path(path, start):
    """
    Gets an absolute path from a start path
    :param path: str, path to get absolute path
    :param start: str, Start path to calculate the absolute path from
    """

    path = path.replace('\\', '/')
    if not os.path.isdir(start):
        start = os.path.dirname(start).replace('\\', '/')
    else:
        start = start.replace('\\', '/')
    return os.path.abspath(os.path.join(start, path)).replace('\\', '/')


def get_absolute_file_paths(root_directory):
    """
    Returns a generator with all absolute paths on a folder (and sub folders)
    :param root_directory: str, directory to start looking
    """

    for dir, _, files in os.walk(root_directory):
        for f in files:
            yield os.path.abspath(os.path.join(dir, f))


def get_immediate_subdirectories(root_directory):
    """
   Returns a list with intermediate subdirectories of root directory
   :param root_directory: str, directory to start looking
   """

    return [os.path.join(root_directory, name) for name in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, name))]