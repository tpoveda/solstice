#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_updater.py
# by Tomas Poveda
# Tool that generates a new version of the tools ready to be updated
# deployed to all artists
# NOTE: This tool only works on Windows systems
#  ______________________________________________________________________
# ==================================================================="""

import os
import re
import sys
import win32gui
import compileall
import tempfile
import subprocess
import shutil
import json
from string import zfill
from distutils.dir_util import copy_tree
from win32com.shell import shell, shellcon

pipeline_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solstice_pipeline')
if pipeline_path not in sys.path:
    sys.path.append(pipeline_path)

from solstice_utils import solstice_download_utils

numbers = re.compile('\d+')


def deploy_solstice_pipeline():
    folder_path = get_solstice_pipeline_folder()
    if folder_path is None or not os.path.exists(folder_path):
        print 'ERROR: Path "{}" does not exists! Aborting deployment ...'.format(folder_path)
        return

    temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_path')
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    if not os.path.exists(temp_path):
        print 'ERROR: Error when creating temp folder {}. Aborting deployment ...!'.format(temp_path)
        return

    solstice_pipeline_temp_path = os.path.join(temp_path, 'solstice_pipeline')
    if not os.path.exists(solstice_pipeline_temp_path):
        os.makedirs(solstice_pipeline_temp_path)

    current_version = get_last_solstice_pipeline_version(as_int=False)
    if not current_version:
        print('ERROR: settings.json is not accessible. Aborting deployment ...!')
        return

    if not copy_contents_to_folder(folder_path, solstice_pipeline_temp_path):
        print('ERROR: Impossible to copy solstice_pipeline from {0} to solstice_pipeline temp folder {1}. Aborting deployment ...!'.format(folder_path, solstice_pipeline_temp_path))
        return

    new_settings_path = os.path.join(solstice_pipeline_temp_path, 'settings.json')
    if not os.path.isfile(new_settings_path):
        print('ERROR: New Settings File "{}" doest not exists" Aborting deployment ...'.format(new_settings_path))

    new_version = increment_version(current_version)

    compile_python_files(temp_path)
    clean_python_files(temp_path)
    for root, dirs, files in os.walk(temp_path):
        for d in dirs:
            if '.idea' in d:
                shutil.rmtree(os.path.join(root, d))

    version_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), new_version)
    if not os.path.exists(version_folder_path):
        os.makedirs(version_folder_path)

    mac_folder = os.path.join(version_folder_path, 'mac')
    if not os.path.exists(mac_folder):
        os.makedirs(mac_folder)
    win_folder = os.path.join(version_folder_path, 'win')
    if not os.path.exists(win_folder):
        os.makedirs(win_folder)

    # MAC Version
    mac_pipeline_path = os.path.join(mac_folder, 'solstice_pipeline')
    if not os.path.exists(mac_pipeline_path):
        os.makedirs(mac_pipeline_path)
    shutil.copytree(solstice_pipeline_temp_path, os.path.join(mac_pipeline_path, 'solstice_pipeline'))

    user_setup_file = os.path.join(mac_pipeline_path, 'solstice_pipeline', 'userSetup.py')
    if os.path.isfile(user_setup_file):
        shutil.copy2(user_setup_file, os.path.join(os.path.dirname(os.path.dirname(user_setup_file)), 'userSetup.py'))
    os.remove(user_setup_file)
    os.remove(user_setup_file.replace('.py', '.pyc'))

    modules_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
    if os.path.exists(modules_folder):
        shutil.copytree(modules_folder, os.path.join(os.path.dirname(mac_pipeline_path), 'modules'))

    mac_zip_file = zip_dir('solstice_pipeline_mac', os.path.dirname(mac_pipeline_path))
    with open(os.path.join(os.path.dirname(mac_zip_file), 'setup.json'), 'wb') as f:
        f.write(json.dumps({'lastVersion': new_version}, ensure_ascii=False))

    # Windows Version
    shutil.copytree(solstice_pipeline_temp_path, os.path.join(win_folder, 'solstice_pipeline'))

    win_zip_file = zip_dir('solstice_pipeline', win_folder)
    with open(os.path.join(os.path.dirname(win_zip_file), 'setup.json'), 'wb') as f:
        f.write(json.dumps({'lastVersion': new_version}, ensure_ascii=False))

    # Create settings.json file
    last_version_dict = dict()
    last_version_dict['version'] = new_version
    setup_file = os.path.join(folder_path, 'settings.json')
    with open(setup_file, 'w') as fl:
        json.dump(last_version_dict, fl)
    fl.close()

    shutil.rmtree(temp_path)
    shutil.rmtree(version_folder_path)
    
    # Create folder that will be uploaded to server
    version_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), new_version)
    if not os.path.exists(version_folder_path):
        os.makedirs(version_folder_path)
    shutil.move(mac_zip_file, version_folder_path)
    shutil.move(win_zip_file, version_folder_path)



    print 'Solstice Pipeline deployed successfully with version {}'.format(new_version)

    try:
        subprocess.check_call(['explorer', os.path.dirname(zip_file)])
    except Exception:
        pass


def get_solstice_pipeline_folder():
    solstice_pipeline_default_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'solstice_pipeline')
    solstice_pipeline_pidl, flags = shell.SHILCreateFromPath(solstice_pipeline_default_dir, 0)

    try:
        pidl, display_name, image_list = shell.SHBrowseForFolder(
            win32gui.GetDesktopWindow(),
            solstice_pipeline_pidl,
            "Choose solstice_pipeline folder",
            0,
            None,
            None
        )
        return shell.SHGetPathFromIDList(pidl)
    except Exception:
        return None


def get_version(s):
    """
    Look for the last sequence of number(s) in a string and increment it
    :param s: str
    :return: str
    """

    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr
    return None


def get_last_solstice_pipeline_version(as_int=False):
    temp_path = tempfile.mkdtemp()
    repo_url = 'http://cgart3d.com/solstice_pipeline/'
    setup_json = 'setup.json'
    setup_file = '{}{}'.format(repo_url, setup_json)
    setup_path = os.path.join(temp_path, 'setup.json')
    if not solstice_download_utils.download_file(filename=setup_file, destination=setup_path):
        raise Exception('ERROR: setup.json is not accessible. It was not possible to check last version of solstice tools!')

    with open(setup_path, 'r') as f:
        setup_info = json.loads(f.read())
    last_version = setup_info.get('lastVersion')
    if not last_version:
        raise Exception('ERROR: Last version uploaded is not available. Try again later!')

    if as_int:
        return int(get_version(last_version))
    else:
        return last_version


def copy_contents_to_folder(source, dst):
    try:
        copy_tree(source, dst, update=True)
        return True
    except Exception:
        return None


def increment_version(s):
    """
    Look for the last sequence of number(s) in a string and increment
    """

    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        lastoccr_incr = str(int(lastoccr) + 1)
        if len(lastoccr) > len(lastoccr_incr):
            lastoccr_incr = zfill(lastoccr_incr, len(lastoccr))
        return s[:lastoccr_sre.start()]+lastoccr_incr+s[lastoccr_sre.end():]
    return s


def compile_python_files(path):
    if os.path.exists(path):
        compileall.compile_dir(path, force=True)


def clean_python_files(path):
    if os.path.exists(path):
        for parent, dirnames, filenames in os.walk(path):
            for fn in filenames:
                if fn.lower().endswith('.py') and 'userSetup' not in fn:
                    print('Removing file: {}'.format(fn))
                    os.remove(os.path.join(parent, fn))
                if fn.lower() == 'solstice.log':
                    print('Removing file: {}'.format(fn))
                    os.remove(os.path.join(parent, fn))


def zip_dir(output_filename, dir_name):
    return shutil.make_archive(output_filename, 'zip', dir_name)


if __name__ == '__main__':
    deploy_solstice_pipeline()
