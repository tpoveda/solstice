#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tools_local_installer.py
# by Tomás Poveda
# ______________________________________________________________________
# Tool that is used to copy the contents of solstice_tools in local for
# testing purposes
# ______________________________________________________________________
# ===================================================================""

# import win32gui
# from win32com.shell import shell, shellcon
import os
import shutil
from distutils.dir_util import copy_tree

def copySolsticeTools():

    origFolder = getFolder("E:\Solstice\solstice\solstice_tools\solstice_tools")
    if not os.path.exists(origFolder):
        print 'ERROR: Path {} does not exists! Aborting copy ...'.format(origFolder)
        return

    toFolder = getFolder("C:\\Users\\tomi_\\Documents\\maya\\solstice_tools")
    if not os.path.exists(toFolder):
        print 'ERROR: Path {} does not exists! Aborting copy ...'.format(toFolder)
        return

    copy_tree(origFolder, toFolder, update=True)

def getFolder(path):
    solstice_tools_pidl, flags = shell.SHILCreateFromPath(path, 0)
    pidl, display_name, image_list = shell.SHBrowseForFolder (
      win32gui.GetDesktopWindow (),
        solstice_tools_pidl,
      "Choose solstice_tools folder",
      0,
      None,
      None
    )
    return shell.SHGetPathFromIDList (pidl)

if __name__ == '__main__':
    copySolsticeTools()