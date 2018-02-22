#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tools_deployer.py
# by Tomás Poveda
# ______________________________________________________________________
# Tool that generates a new version of the tools ready to be updated
# deployed to all artists
# NOTE: This tool only works on Windows systems
# ______________________________________________________________________
# ==================================================================="""

# import win32gui
# from win32com.shell import shell, shellcon
import compileall
import subprocess
import tempfile
import shutil
import json
import os
import re
from string import zfill
from distutils.dir_util import copy_tree
numbers = re.compile('\d+')

def deploySolsticeTools():
    folderPath = getSolsticeToolsFolder()
    if not os.path.exists(folderPath):
        print 'ERROR: Path {} does not exists! Aborting deployment ...'.format(folderPath)
        return
    settingsFile = os.path.join(folderPath, 'settings.json')
    if not os.path.isfile(settingsFile):
        print 'ERROR: File {} does not exists. Aborting deployment ...!'.format(settingsFile)
        return

    moduleFile = os.path.join(folderPath, 'modules', 'solstice_tools.mod')
    if not os.path.isfile(moduleFile):
        print 'ERROR: Module {} does not exists. Abortin deployment ...!'.format(moduleFile)
        return

    tempPath = tempfile.mkdtemp()
    if not os.path.exists(tempPath):
        print 'ERROR: Error when creating temp folder {}. Aborting deployment ...!'.format(tempPath)

    solsticeToolsTempPath = os.path.join(tempPath, 'solstice_tools')
    if not os.path.exists(solsticeToolsTempPath):
        os.makedirs(solsticeToolsTempPath)

    with open(settingsFile, 'r') as fl:
        setupInfo = json.loads(fl.read())
    currVersion = setupInfo.get('version')
    if not currVersion:
        print 'ERROR: settings.json is not accessible. Aborting deployment ...!'

    if not copySolsticeContentsToFolder(folderPath, solsticeToolsTempPath):
        print 'ERROR: Impossible to copy solstice_tools from {0} to solstice_tools temp folder {1}. Aborting deployment ...!'.format(folderPath, solsticeToolsTempPath)
        return

    newSettingsPath = os.path.join(solsticeToolsTempPath, 'settings.json')
    if not os.path.isfile(newSettingsPath):
        print 'ERROR: File {} does not exists. Aborting deployment ...!'.format(solsticeToolsTempPath)

    newModulesPath = os.path.join(solsticeToolsTempPath, 'modules')
    if not os.path.exists(newModulesPath):
        print 'ERROR: File {} does not exists. Aborting deployment ...!'.format(newModulesPath)

    shutil.move(newModulesPath, tempPath)

    newVersion = incrementVersion(currVersion)
    with open(newSettingsPath, 'wb') as fl:
        fl.write(json.dumps({'version': newVersion}, ensure_ascii=False))

    compilePythonFiles(tempPath)
    cleanPythonFiles(tempPath)
    for root, dirs, files in os.walk(tempPath):
        for dir in dirs:
            if '.idea' in dir:
                shutil.rmtree(os.path.join(root, dir))

    zipFile = zipDir('solstice_tools', tempPath)
    with open(os.path.join(os.path.dirname(zipFile), 'setup.json'), 'wb') as fl:
        fl.write(json.dumps({'lastVersion':newVersion}, ensure_ascii=False))

    versionFolderPath = os.path.join(os.path.dirname(zipFile), newVersion)
    if not os.path.exists(versionFolderPath):
        os.makedirs(versionFolderPath)
    shutil.move(zipFile, os.path.join(versionFolderPath, os.path.basename(zipFile)))

    print 'Solstice_tools deployed succesfully with version {}'.format(newVersion)

    try:
        subprocess.check_call(['explorer', os.path.dirname(zipFile)])
    except:
        pass

def getSolsticeToolsFolder():
    solstice_tools_pidl, flags = shell.SHILCreateFromPath("E:\Solstice\solstice\solstice_tools\solstice_tools", 0)
    pidl, display_name, image_list = shell.SHBrowseForFolder (
      win32gui.GetDesktopWindow (),
        solstice_tools_pidl,
      "Choose solstice_tools folder",
      0,
      None,
      None
    )
    return shell.SHGetPathFromIDList (pidl)

def incrementVersion(s):
    """ look for the last sequence of number(s) in a string and increment """
    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        lastoccr_incr = str(int(lastoccr) + 1)
        if len(lastoccr) > len(lastoccr_incr):
            lastoccr_incr = zfill(lastoccr_incr, len(lastoccr))
        return s[:lastoccr_sre.start()]+lastoccr_incr+s[lastoccr_sre.end():]
    return s

def copySolsticeContentsToFolder(source, destination):
    try:
        copy_tree(source, destination, update=True)
        return True
    except:
        return

def compilePythonFiles(path):
    if os.path.exists(path):
        compileall.compile_dir(path, force=True)


def cleanPythonFiles(path):
    if os.path.exists(path):
        for parent, dirnames, filenames in os.walk(path):
            for fn in filenames:
                if fn.lower().endswith('.py') and 'userSetup' not in fn:
                    print 'Removing file: {}'.format(fn)
                    os.remove(os.path.join(parent, fn))

def zipDir(outputFilename, dirName):
    return shutil.make_archive(outputFilename, 'zip', dirName)

if __name__ == '__main__':
    deploySolsticeTools()
