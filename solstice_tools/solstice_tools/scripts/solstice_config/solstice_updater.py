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
import re
import urllib2
import json
import time
import shutil
import zipfile
numbers = re.compile('\d+')

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def updateTools(ui=False, stopAtEnd=False):

    if ui:
        import solstice_updater_ui
        reload(solstice_updater_ui)
        solstice_updater_ui.initUI()
        return

    tempPath = tempfile.mkdtemp()
    mayaPath = os.path.join(os.path.expanduser("~/Documents"), 'maya')
    if not os.path.exists(mayaPath):
        print(sLog('ERROR: Maya Documents Path {} does not exist. Check that Maya is installed on your system!'.format(mayaPath)))
    toolsFile = 'solstice_tools.zip'
    repoUrl = 'http://cgart3d.com/solstice_tools/'
    setupFile = '{}setup.json'.format(repoUrl)
    setupPath = os.path.join(tempPath, 'setup.json')
    if not downloadFile(setupFile, setupPath):
        raise Exception(sLog(
            'ERROR: setup.json is not accessible. It was nos possible to install solstice_tools. Check your internet connection and retry'))
    with open(setupPath, 'r') as fl:
        setupInfo = json.loads(fl.read())
    lastVersion = setupInfo.get('lastVersion')
    if not lastVersion:
        raise Exception(sLog('ERROR: Last version uploaded is not available. Try again later!'))
    print(sLog('Last solstice_tools uplodaded version is {}'.format(lastVersion)))
    solsticeToolsPath = os.path.join(mayaPath, 'solstice_tools', 'settings.json')
    print(sLog('Checking current solstice_tools installed version on: {}'.format(solsticeToolsPath)))

    try:
        with open(solsticeToolsPath, 'r') as fl:
            installInfo = json.loads(fl.read())
        installVersion = installInfo.get('version')
        if not installVersion:
            raise Exception(sLog('ERROR: Installed version impossible to get ...'))
        print(sLog('Current installed version: {}'.format(installVersion)))

        lastVersionValue = getVersion(lastVersion)
        installedVersion = getVersion(installVersion)

        if lastVersionValue <= installedVersion:
            print(sLog('Current installed tools {0} are up-to-date (version in server {1}!)').format(installVersion, lastVersion))
            return
    except:
        pass

    print '=' * 150
    print(sLog('Current installed tools are outdated! Installed new version tools ... {0}!').format(lastVersion))
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

    print '=' * 150
    print(sLog('solstice_tools {} installed succesfully!'.format(lastVersion)))
    print '=' * 150

    if stopAtEnd:
        input('solstice_tools setup is finished! Press a key to continue ...')


# ================================================================================================================================================================

def downloadFile(filename, destination):
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
        with open(destination, 'ab') as dstFile:
            dstFile.write(data.read())
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

def getVersion(s):
    """ look for the last sequence of number(s) in a string and increment """
    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr

if __name__ == '__main__':
    updateTools()