#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tools_installer.py
# by Tomás Poveda
# ______________________________________________________________________
# Tool that generates a executable version of the solstice_tools
# NOTE: This tool depends on the pyinstaller package (pip install pyinstaller)
# ______________________________________________________________________
# ===================================================================""

# import win32gui
# from win32com.shell import shell, shellcon
from subprocess import check_call
from subprocess import check_output
import shutil
import os

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def generateInstaller():
    folderPath = getSolsticeToolsFolder()
    if not os.path.exists(folderPath):
        print 'ERROR: Path {} does not exists! Aborting installation generation ...'.format(folderPath)
        return

    updaterFile = os.path.join(folderPath, 'scripts', 'solstice_config', 'solstice_updater.py')
    if not os.path.isfile(updaterFile):
        print 'ERROR: Solstice_tools Updater file {} does not exists! Aborting installation generation ...'.format(updaterFile)

    print '=' * 100
    print(sLog("Generating Solstice Tools installer..."))
    print '=' * 100
    check_output("pyinstaller {}".format(updaterFile))

    distFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dist')
    if not os.path.exists(distFolder):
        print 'ERROR: Distributable folder {} doest not exists! Aborting installation generation ...'.format(distFolder)
        return

    zipFile = zipDir('solstice_tools_installer', distFolder)

    cleanInstallation()

    try:
        check_call(['explorer', os.path.dirname(zipFile)])
    except:
        pass

    print '=' * 100
    print(sLog("Solstice Tools installer generated succesfully!"))
    print '=' * 100

def cleanInstallation():

    print '=' * 100
    print(sLog("Cleaning Solstice Tools installer files ...!"))
    print '=' * 100

    distFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dist')
    if not os.path.exists(distFolder):
        print 'ERROR: Distributable folder {} doest not exists! Aborting installation cleanup ...'.format(distFolder)
        return

    buildFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build')
    if not os.path.exists(buildFolder):
        print 'ERROR: Build folder {} doest not exists! Aborting installation cleanup ...'.format(buildFolder)
        return

    specFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'solstice_updater.spec')
    if not os.path.isfile(specFile):
        print 'ERROR: Spec file {} does not exists! Aborting installation cleanup ...'.format(specFile)

    shutil.rmtree(distFolder)
    shutil.rmtree(buildFolder)
    os.remove(specFile)

    print '=' * 100
    print(sLog("Solstice Tools installer files cleaned succesfully!"))
    print '=' * 100


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

def zipDir(outputFilename, dirName):
    return shutil.make_archive(outputFilename, 'zip', dirName)


if __name__ == '__main__':
    generateInstaller()