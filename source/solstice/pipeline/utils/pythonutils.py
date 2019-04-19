#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities related with Python
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import re
import ast
import sys
import json
import stat
import getpass
import platform
import subprocess
import webbrowser
from tempfile import mkstemp
from shutil import move

iters = [list, tuple, set, frozenset]
class _hack(tuple): pass
iters = _hack(iters)
iters.__doc__ = """
A list of iterable items (like lists, but not strings). Includes whichever
of lists, tuples, sets, and Sets are available in this version of Python.
"""


class classproperty(object):
    """
    Simplified way of creating getter and setters in Python
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


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
        config_directory = os.getenv('APPDATA') or os.path.expanduser('~')
    elif platform.system().lower() == 'darwin':
        config_directory = os.path.join(os.path.expanduser('~'), 'Library', 'Preferences')
    else:
        config_directory = os.getenv('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')

    return config_directory


def open_folder(path):
    """
    Open folder using OS default settings
    :param path: str, folder path we want to open
    """

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def open_file(file_path):
    """
    Open file using OS default settings
    :param file_path: str, file path we want to open
    """

    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file_path))
    elif os.name == 'nt':
        os.startfile(file_path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file_path))
    else:
        raise NotImplementedError('OS not supported: {}'.format(os.name))


def file_has_info(file_path):
    """
    Check if the given file size is bigger than 1.0 byte
    :param file_path: str, ful file path of the file to check
    :return: bool
    """

    file_stats = os.stat(file_path)
    if file_stats.st_size < 1:
        return False

    return True


def load_json(file_path):
    """
    Open and read JSON and return readed values
    :param file_path:  str
    :return: dict
    """

    with open(file_path, 'r') as f:
        return json.load(f)


def is_dir(directory):
    """
    Checks if the given directory is a directory or not
    :param directory: str
    :return: bool
    """

    if not directory:
        return False

    try:
        mode = os.stat(directory)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
            return True
    except Exception:
        return False

    return False


def is_file(file_path):
    """
    Checks if the given path is an existing file
    :param file_path: str
    :return: bool
    """

    if not file_path:
        return False

    try:
        mode = os.stat(file_path)[stat.ST_MODE]
        if stat.S_ISREG(mode):
            return True
    except Exception:
        return False

    return False


def get_file_text(file_path):
    """
    Get the text stored in a file in a unique string (without parsing)
    :param file_path: str
    :return: str
    """

    open_file = open(file_path, 'r')
    lines = ''

    try:
        lines = open_file.read()
        open_file.close()
    except Exception:
        open_file.close()

    return lines


def get_file_size(filepath, round_value=2):
    """
    Returns the size of the given file
    :param filepath: str
    :param round_value: int, value to round size to
    :return: str
    """

    size = os.path.getsize(filepath)
    size_format = round(size * 0.000001, round_value)

    return size_format


def get_folder_size(directory, round_value=2):
    """
    Returns the size of the given folder
    :param directory: str
    :param round_value: int, value to round size to
    :return: str
    """

    size = 0
    for root, dirs, files in os.walk(directory):
        for name in files:
            size += get_file_size(os.path.join(root, name), round_value)

    return size


def get_size(path, round_value=2):
    """
    Return the size of the given directory or file path
    :param path: str
    :param round_value: int, value to round size to
    :return: int
    """

    size = 0
    if is_dir(path):
        size = get_folder_size(path, round_value)
    if is_file(path):
        size = get_file_size(path, round_value)

    return size


def add_unique_postfix(fn):
    if not os.path.exists(fn):
        return fn

    path, name = os.path.split(fn)
    name, ext = os.path.splitext(name)

    make_fn = lambda i: os.path.join(path, '%s_%d%s' % (name, i, ext))

    for i in xrange(2, sys.maxint):
        uni_fn = make_fn(i)
        if not os.path.exists(uni_fn):
            return uni_fn

    return None


def open_web(url):
    """
    Open given web URL in user web browser
    :param url: str
    """

    webbrowser.open(url)


def force_list(var):
    """
    Returns the given variable as list
    :param var: variant
    :return: list
    """

    if var is None:
        return []

    if type(var) is not list:
        if type(var) in [tuple]:
            var = list(var)
        else:
            var = [var]

    return var


def user():
    """
    Returns the current user name in lowercase
    :return: str
    """

    return getpass.getuser().lower()


def system():
    """
    Returns the current platform in lowercase
    :return: str
    """

    return platform.system().lower()


def is_mac():
    """
    Returns whether current OS is MAC or not
    :return: bool
    """

    return system().startswith('os') or system().startswith('mac') or system().startswith('darwin')


def is_linux():
    """
    Returns whether current OS is Linux or not
    :return: bool
    """

    return system().lower().startswith('lin')


def is_windows():
    """
    Returns whether current OS is Windows or not
    :return: bool
    """

    return system().lower().startswith('win')


def norm_path(path):
    """
    Returns a normalized path containing only forward slashes
    :param path: str
    :return: str
    """

    path = path.replace("\\", "/")
    # path = six.u(path)
    return path.rstrip("/")


def norm_paths(paths):
    """
    Normalize all the given paths to a consitent format
    :param paths: list(str)
    :return: list(str)
    """

    return [norm_path(p) for p in paths]


def rel_path(data, start):
    """
    Returns a relative version of all the pats in data from the start path
    :param data: str
    :param start: str
    :return: str
    """

    rpath = start

    for i in range(0, 3):

        rpath = os.path.dirname(rpath)
        token = os.path.relpath(rpath, start)

        rpath = norm_path(rpath)
        token = norm_path(token)

        if rpath.endswith("/"):
            rpath = rpath[:-1]

        data = data.replace(rpath, token)

    return data


def abs_path(data, start):
    """
    Returns an absolute version of all the pats in data using the start path
    :param data: str
    :param start: str
    :return: str
    """

    rel_path1 = norm_path(os.path.dirname(start))
    rel_path2 = norm_path(os.path.dirname(rel_path1))
    rel_path3 = norm_path(os.path.dirname(rel_path2))

    if not rel_path1.endswith("/"):
        rel_path1 += "/"

    if not rel_path2.endswith("/"):
        rel_path2 += "/"

    if not rel_path3.endswith("/"):
        rel_path3 += "/"

    data = data.replace('../../../', rel_path3)
    data = data.replace('../../', rel_path2)
    data = data.replace('../', rel_path1)

    return data


def real_path(path):
    """
    Returns the given path eliminating any symbolic link
    :param path: str
    :return: str
    """

    path = os.path.realpath(path)
    path = os.path.expanduser(path)

    return norm_path(path)


def split_path(path):
    """
    Slit the given path into directory, basename and extension
    :param path: str
    :return: list(str)
    """

    path = norm_path(path)
    filename, extension = os.path.splitext(path)
    return os.path.dirname(filename), os.path.basename(filename), extension
