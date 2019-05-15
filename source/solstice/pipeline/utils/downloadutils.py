#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities functions for downloading files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import re
import sys
import json
import time
import shutil
import urllib2
import zipfile
import tempfile
import platform

numbers = re.compile('\d+')


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    print("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))
    if bytes_so_far >= total_size:
        print('\n')


def chunk_read(response, destination, chunk_size=8192, report_hook=None):
    with open(destination, 'ab') as dst_file:
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0
        while 1:
            chunk = response.read(chunk_size)
            dst_file.write(chunk)
            bytes_so_far += len(chunk)
            if not chunk:
                break
            if report_hook:
                report_hook(bytes_so_far=bytes_so_far, chunk_size=chunk_size, total_size=total_size)
    dst_file.close()
    return bytes_so_far


def download_file(filename, destination):
    print('Downloading file {0} to temporary folder -> {1}'.format(os.path.basename(filename), destination))
    try:
        dst_folder = os.path.dirname(destination)
        if not os.path.exists(dst_folder):
            print('Creating downloaded folders ...')
            os.makedirs(dst_folder)

        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        req = urllib2.Request(filename, headers=hdr)
        data = urllib2.urlopen(req)
        chunk_read(response=data, destination=destination, report_hook=chunk_report)
    except Exception as e:
        raise e

    if os.path.exists(destination):
        print('Files downloaded succesfully!')
        return True
    else:
        print('ERROR: Error when downloading files. Maybe server is down! Please contact TD!')
        return False


def unzip_file(filename, destination, removeFirst=True, removeSubfolders=None):
    print('Unzipping file {} to --> {}'.format(filename, destination))
    try:
        if removeFirst and removeSubfolders:
            print('Removing old installation ...')
            for subfolder in removeSubfolders:
                p = os.path.join(destination, subfolder)
                print('\t{}'.format(p))
                if os.path.exists(p):
                    shutil.rmtree(p)
        if not os.path.exists(destination):
            print('Creating destination folders ...')
            os.makedirs(destination)
        zip_ref = zipfile.ZipFile(filename, 'r')
        zip_ref.extractall(destination)
        zip_ref.close()
        print('Unzip completed!')
    except Exception as e:
        raise e


def get_version(s):
    """
    Look for the last sequence of number(s) in a string and increment
    """

    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr
    return None


def update_tools(get_versions=False):
    temp_path = tempfile.mkdtemp()

    if sys.platform == 'win32':
        maya_path = os.path.join(os.path.expanduser("~/Documents"), 'maya')
    elif sys.platform == 'darwin':
        maya_path = os.path.join(os.path.expanduser('~/Library/Preferences'), 'maya')
    else:
        print('Solstice Tools are not compatible with your OS {}'.format(sys.platform))
        return
    print('Maya Installation Path found: {}'.format(maya_path))
    if not os.path.exists(maya_path):
        print('Maya path {} does not exists" Check that Maya is installed on your system!'.format(maya_path))
        return
    tools_file = 'solstice_pipeline_mac.zip'
    repo_url = 'http://cgart3d.com/solstice_pipeline/'
    setup_json = 'setup.json'
    setup_file = '{}{}'.format(repo_url, setup_json)
    setup_path = os.path.join(temp_path, setup_json)

    if not download_file(filename=setup_file, destination=setup_path):
        raise Exception('ERROR: setup.json is not accessible. It was nos possible to install solstice_tools. Check your internet connection and retry')
    with open(setup_path, 'r') as f:
        setup_info = json.loads(f.read())
    last_version = setup_info.get('lastVersion')
    if not last_version:
        raise Exception('ERROR: Last version uploaded is not available. Try again later!')
    last_version_value = get_version(last_version)
    print('Last Solstice Pipeline Tools deployed version is {}'.format(last_version))

    if platform.system() == 'Darwin':
        solstice_tools_path = os.path.join(maya_path, 'solstice_pipeline', 'solstice_pipeline', 'settings.json')
    else:
        solstice_tools_path = os.path.join(maya_path, 'solstice_pipeline', 'settings.json')
    try:
        if os.path.isfile(solstice_tools_path):
            with open(solstice_tools_path, 'r') as f:
                install_info = json.loads(f.read())
            install_version = install_info.get('version')
            if not install_version:
                raise Exception('ERROR: Installed version impossible to get ...')
            print('Current installed version: {}'.format(install_version))
            installed_version = get_version(install_version)
            if installed_version and (last_version_value <= installed_version):
                print('Current installed tools {0} are up-to-date (version in server {1}!)'.format(install_version, last_version))
                return last_version_value, installed_version
            if get_versions:
                return last_version_value, installed_version
        else:
            if get_versions:
                return last_version_value, None
    except Exception as e:
        print('Error while retrieving solstice_tools version. Check your Internet connection or contact Solstice TD!')
        print(str(e))
        return False

    print('=' * 150)
    print('Current installed tools are outdated! Installing new version tools ... {0}!'.format(last_version))
    print('=' * 150)

    solstice_tools_zip_file = '{}{}/{}'.format(repo_url, last_version, tools_file)
    solstice_tools_install_path = os.path.join(temp_path, last_version, tools_file)
    print('----------> ', solstice_tools_zip_file)
    if not download_file(filename=solstice_tools_zip_file, destination=solstice_tools_install_path):
        raise Exception('ERROR: Impossible to access solstice_tools.zip. It was nos possible to install solstice_tools. Check your internet connection and retry')
    print('Installing solstice_tools on: {}'.format(maya_path))
    time.sleep(1)
    unzip_file(filename=solstice_tools_install_path, destination=maya_path, removeSubfolders=['solstice_pipeline', 'solstice'])

    # Remove original solstice_tools module
    orig_module_file = os.path.join(maya_path, 'modules', 'solstice_tools.mod')
    if os.path.isfile(orig_module_file):
        os.remove(orig_module_file)

    # Remove original solstice_tools folder
    orig_tools_folder = os.path.join(maya_path, 'solstice_tools')
    if os.path.exists(orig_tools_folder):
        shutil.rmtree(orig_tools_folder)

    print('=' * 150)
    print('Solstice Pipeline Tools {} installed succesfully!'.format(last_version))
    print('=' * 150)

    try:
        import maya.cmds as cmds
        cmds.confirmDialog(title='Solstice Pipeline Tools', message='Solstice Tools installed successfully! Restart Maya please.')
    except Exception as e:
        pass

    return None, None
