#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_update_utils.py
# by Tomás Poveda
# ______________________________________________________________________
# Utilities functions for updater
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import urllib2
import shutil
import zipfile
import tempfile
import os
import json
import time

try:
    import maya.cmds as cmds
except:
    pass

numbers = re.compile('\d+')

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def downloadFile(filename, destination, progress_bar=None):
    print(sLog('Downloading file {} to temporary folder -> {}'.format(os.path.basename(filename), destination)))
    try:
        dstFolder = os.path.dirname(destination)
        if not os.path.exists(dstFolder):
            print(sLog('Creating downloaded folders ...'))
            os.makedirs(dstFolder)
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        req = urllib2.Request(filename, headers=hdr)
        data = urllib2.urlopen(req)
        # with open(destination, 'ab') as dstFile:
        #     dstFile.write(data.read())
        chunk_read(response=data, destination=destination, report_hook=chunk_report, progress_bar=progress_bar)


    except Exception as e:
        raise e
    if os.path.exists(destination):
        print(sLog('Files downloaded succesfully!'))
        return True
    else:
        print(sLog('Error when downloading files.'))
        return False


def chunk_report(bytes_so_far, chunk_size, total_size, progres_bar=None):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    if progres_bar:
        try:
            cmds.progressBar(progres_bar, edit=True, progress=percent)
        except:
            pass
    print("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))
    if bytes_so_far >= total_size:
        print('\n')


def chunk_read(response, destination, chunk_size=8192, report_hook=None, progress_bar=None):

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
                report_hook(bytes_so_far, chunk_size, total_size, progress_bar)
    dst_file.close()
    return bytes_so_far

def unzipFile(filename, destination, removeFirst=True, removeSubfolders=None):
    print(sLog('Unzipping file {} to --> {}'.format(filename, destination)))
    try:
        if removeFirst and removeSubfolders:
            print(sLog('Remove old installation ...'))
            for subfolder in removeSubfolders:
                p = os.path.join(destination, subfolder)
                print(sLog('\t{}'.format(p)))
                if os.path.exists(p):
                    shutil.rmtree(p)
        if not os.path.exists(destination):
            print(sLog('Creating destination folders ...'))
            os.makedirs(destination)
        zipRef = zipfile.ZipFile(filename, 'r')
        zipRef.extractall(destination)
        zipRef.close()
        print(sLog('Unzip completed!'))
    except Exception as e:
        raise e

def getVersion(s):
    """ look for the last sequence of number(s) in a string and increment """
    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr
    return None

def updateTools(get_versions=False, progress_bar=None):

    temp_path = tempfile.mkdtemp()
    maya_path = os.path.join(os.path.expanduser("~/"), 'maya')
    if not os.path.exists(maya_path):
        maya_path = os.path.join(os.path.expanduser("~/Documents"), 'maya')
    if not os.path.exists(maya_path):
        print(sLog('ERROR: Maya Documents Path {} does not exist. Check that Maya is installed on your system!'.format(maya_path)))
        return
    tools_file = 'solstice_tools.zip'
    repo_url = 'http://cgart3d.com/solstice_tools/'
    setup_file = '{}setup.json'.format(repo_url)
    setup_path = os.path.join(temp_path, 'setup.json')
    if not downloadFile(setup_file, setup_path, progress_bar=progress_bar):
        raise Exception(sLog('ERROR: setup.json is not accessible. It was nos possible to install solstice_tools. Check your internet connection and retry'))
    with open(setup_path, 'r') as fl:
        setup_info = json.loads(fl.read())
    last_version = setup_info.get('lastVersion')
    if not last_version:
        raise Exception(sLog('ERROR: Last version uploaded is not available. Try again later!'))
    last_version_value = getVersion(last_version)
    print(sLog('Last solstice_tools deployed version is {}'.format(last_version)))
    solstice_tools_path = os.path.join(maya_path, 'solstice_tools', 'settings.json')
    # print(sLog('Checking current solstice_tools installed version on: {}'.format(solstice_tools_path)))
    try:
        if os.path.isfile(solstice_tools_path):
            with open(solstice_tools_path, 'r') as fl:
                install_info = json.loads(fl.read())
            install_version = install_info.get('version')
            if not install_version:
                raise Exception(sLog('ERROR: Installed version impossible to get ...'))
            print(sLog('Current installed version: {}'.format(install_version)))

            installed_version = getVersion(install_version)

            if installed_version and last_version_value <= installed_version:
                print(sLog('Current installed tools {0} are up-to-date (version in server {1}!)').format(install_version, last_version))
                return last_version_value, installed_version

            if get_versions:
                return last_version_value, installed_version
        else:
            if get_versions:
                return last_version_value, None
    except Exception as e:
        print(sLog('Error while retriving solstice_tools version. Check your Internet connection or contact Solstice TD!'))
        print(e)
        return False

    print '=' * 150
    print(sLog('Current installed tools are outdated! Installing new version tools ... {0}!').format(last_version))
    print '=' * 150

    solstice_tools_zip_file = '{}{}/{}'.format(repo_url, last_version, tools_file)
    solstice_tools_install_path = os.path.join(temp_path, last_version, tools_file)
    print '----------> ', solstice_tools_zip_file
    if not downloadFile(solstice_tools_zip_file, solstice_tools_install_path, progress_bar=progress_bar):
        raise Exception(sLog(
            'ERROR: Impossible to access solstice_tools.zip. It was nos possible to install solstice_tools. Check your internet connection and retry'))
    print(sLog('Installing solstice_tools on: {}'.format(maya_path)))
    time.sleep(1)
    unzipFile(solstice_tools_install_path, maya_path, removeSubfolders=['solstice_tools'])

    print '=' * 150
    print(sLog('solstice_tools {} installed succesfully!'.format(last_version)))
    print '=' * 150

    try:
        cmds.confirmDialog(title='Solstice Tools', message='Solstice Tools installed successfully! Please restart Maya')
    except:
        pass

    return None, None