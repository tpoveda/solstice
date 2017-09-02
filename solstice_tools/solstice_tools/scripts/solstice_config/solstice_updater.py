#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_autoUpdater.py
# by Tomás Poveda
# ______________________________________________________________________
# Auto Updater script for solstice_tools
# ______________________________________________________________________
# ==================================================================="""

import tempfile
import os
import urllib
import json
import time
import shutil
import zipfile


def sLog(text):
    return '| Solstice Tools | => {}'.format(text)


def updateTools(ui=False):
    tempPath = tempfile.mkdtemp()
    mayaPath = os.path.join(os.path.expanduser("~"), 'maya')
    if not os.path.exists(mayaPath):
        print(sLog('ERROR: Maya Documents Path {} does not exist. Check that Maya is installed on your system!'))
    toolsFile = 'solstice_tools.zip'
    repoUrl = 'http://cgart3d.com/solstice_tools/'
    setupFile = '{}setup.json'.format(repoUrl)
    setupPath = os.path.join(tempPath, 'setup.json')
    if not downloadFile(setupFile, setupPath):
        raise Exception(sLog(
            'ERROR: setup.json is not accessible. It was nos possible to installa solstice_tools. Check your internet connection and retry'))
    with open(setupPath, 'r') as fl:
        setupInfo = json.loads(fl.read())
    lastVersion = setupInfo.get('lastVersion')
    if not lastVersion:
        raise Exception(sLog('ERROR: Last version uploaded is not available. Try again later!'))
    print(sLog('Last solstice_tools uplodaded version is {}'.format(lastVersion)))
    solsticeToolsPath = os.path.join(mayaPath, 'solstice_tools', 'settings.json')
    print(sLog('Checking current solstice_tools installed version on: {}'.format(solsticeToolsPath)))
    if os.path.exists(solsticeToolsPath):
        print 'Tools are already installed'
    else:
        print '=' * 150
        print(sLog('solstice_tools are not installed!'))
        print '=' * 150

        solsticeToolsZipFile = '{}{}/{}'.format(repoUrl, lastVersion, toolsFile)
        solsticeToolsInstallPath = os.path.join(tempPath, lastVersion, toolsFile)
        print '----------> ', solsticeToolsZipFile
        if not downloadFile(solsticeToolsZipFile, solsticeToolsInstallPath):
            raise Exception(sLog(
                'ERROR: Impossible to access solstice_tools.zip. It was nos possible to install solstice_tools. Check your internet connection and retry'))
        print(sLog('Installing solstice_tools on: {}'.format(mayaPath)))
        time.sleep(1)
        unzipFile(solsticeToolsInstallPath, mayaPath, removeSubfolders=['solstice_tools'])


# ====================================================================================================================

def downloadFile(filename, destination):
    print(sLog('Downloading file {} to temporary folder -> {}'.format(os.path.basename(filename), destination)))
    try:
        dstFolder = os.path.dirname(destination)
        if not os.path.exists(dstFolder):
            print(sLog('Creating downloaded folders ...'))
            os.makedirs(dstFolder)
        urlopen = urllib.URLopener()
        urlopen.retrieve(filename, destination)
    except Exception as e:
        raise e
    if os.path.exists(destination):
        print(sLog('Files installed succesfully!'))
        return True
    else:
        print(sLog('Error when downloaded files.'))
        return False


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


if __name__ == '__main__':
    updateTools()