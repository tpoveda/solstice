#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_python_utils.py
# by Tomas Poveda
# Utilities related with Python
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import ast
import json
import platform
import subprocess
from tempfile import mkstemp
from shutil import move

from pathlib2 import Path

iters = [list, tuple, set, frozenset]
class _hack(tuple): pass
iters = _hack(iters)
iters.__doc__ = """
A list of iterable items (like lists, but not strings). Includes whichever
of lists, tuples, sets, and Sets are available in this version of Python.
"""


def string_to_dictionary(string):
    """
    Converts a dictionary string representation into a dictionary
    :param string: str
    :return: dict
    """

    return ast.literal_eval(string)


def path_to_dictionary(path):
    """
    Returns the tree hierarchy of the given path as a Python dictionary
    :param path: str
    :return: dict
    """

    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = 'directory'
        d['children'] = [path_to_dictionary(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d['type'] = 'file'

    return d


def replace(file_path, pattern, subst):
    """
    Replaces one string from another string in a given file
    :param file_path: str, path to the file
    :param pattern: search to be replaced
    :param subst: string that will replace the old one
    """

    fh, abs_path = mkstemp()
    with os.fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                # TODO: This gives when working with non ascii codecs, solve this without try/except
                try:
                    new_file.write(line.replace(pattern, subst))
                except Exception:
                    pass
    os.remove(file_path)
    move(abs_path, file_path)


def _strips(direction, text, remove):
    if isinstance(remove, iters):
        for subr in remove:
            text = _strips(direction, text, subr)
        return text

    if direction == 'l' or direction == 'L':
        if text.startswith(remove):
            return text[len(remove):]
    elif direction == 'r' or direction == 'R':
        if text.endswith(remove):
            return text[:-len(remove)]
    else:
        raise ValueError("Direction needs to be r or l.")
    return text


def rstrips(text, remove):

    """
    Removes the string `remove` from the right of `text`
        >>> rstrips("foobar", "bar")
        'foo'
    """
    return _strips('r', text, remove)


def lstrips(text, remove):

    """
    Removes the string `remove` from the left of `text`
        >>> lstrips("foobar", "foo")
        'bar'
        >>> lstrips('http://foo.org/', ['http://', 'https://'])
        'foo.org/'
        >>> lstrips('FOOBARBAZ', ['FOO', 'BAR'])
        'BAZ'
        >>> lstrips('FOOBARBAZ', ['BAR', 'FOO'])
        'BARBAZ'
    """
    return _strips('l', text, remove)


def strips(text, remove):

    """
    removes the string `remove` from the both sides of `text`
        >>> strips("foobarfoo", "foo")
        'bar'
    """
    return rstrips(lstrips(text, remove), remove)


def get_folders_from_path(path):
    """
    Gets a list of sub folders in the given path
    :param path: str
    :return: list<str>
    """

    folders = list()
    while True:
        path, folder = os.path.split(path)
        if folder != '':
            folders.append(folder)
        else:
            if path != '':
                folders.append(path)
            break
    folders.reverse()

    return folders


def read_json(filename):
    """
    Loads data of JSON as dict
    :param filename: str, name of the JSON file to load
    """

    data = dict()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    return data


def write_json(filename, data):
    """
    Writes data into JSON file
    :param filename: str, name of the JSON file to write
    :param data: str, data to write into JSON file
    """

    if not data:
        return
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def camel_case_to_string(camel_case_string):
    """
    Converts a camel case string to a normal one
    testPath --> test Path
    :param camel_case_string: str
    :return: str
    """

    return re.sub("([a-z])([A-Z])", "\g<1> \g<2>", camel_case_string)


def string_to_camel_case(string):
    """
    Converts a string to a camel case one
    test path --> TestPath
    :param string: str
    :return: str
    """

    return ''.join(x for x in string.title() if not x.isspace())


def get_system_config_directory():
    """
    Returns platform specific configuration directory
    """

    if platform.system().lower() == 'windows':
        config_directory = Path(os.getenv('APPDATA') or '~')
    elif platform.system().lower() == 'darwin':
        config_directory = Path('~', 'Library', 'Preferences')
    else:
        config_directory = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config')

    return config_directory


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])