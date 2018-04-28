#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Initiailzer class for solstice_pipeline
# ==================================================================="""

import os
import sys
import importlib
import pkgutil
from types import ModuleType
from collections import OrderedDict
if sys.version_info[:2] > (2, 7):
    from importlib import reload
else:
    from imp import reload

from maya import OpenMaya

import solstice_pipeline

root_path = os.path.dirname(os.path.abspath(__file__))
loaded_modules = OrderedDict()
reload_modules = list()
logger = None

def update_paths():
    extra_paths = [os.path.join(root_path, 'externals'), os.path.join(root_path, 'icons')]
    for path in extra_paths:
        if os.path.exists(path) and path not in sys.path:
                sys.path.append(path)

    for subdir, dirs, files in os.walk(root_path):
        if subdir not in sys.path:
            sys.path.append(subdir)


def import_module(package_name):
    try:
        mod = importlib.import_module(package_name)
        solstice_pipeline.logger.debug('Imported: {}'.format(package_name))
        if mod and isinstance(mod, ModuleType):
            return mod
        return None
    except (ImportError, AttributeError) as e:
        solstice_pipeline.logger.debug('FAILED IMPORT: {} -> {}'.format(package_name, str(e)))
        pass


def import_modules(module_name, only_packages=False, order=[]):
    names, paths = explore_package(module_name=module_name, only_packages=only_packages)
    ordered_names = list()
    ordered_paths = list()
    temp_index = 0
    i = -1
    for o in order:
        for n, p in zip(names, paths):
            if str(n) == str(o):
                i += 1
                temp_index = i
                ordered_names.append(n)
                ordered_paths.append(p)
            elif n.endswith(o):
                ordered_names.insert(temp_index+1, n)
                ordered_paths.insert(temp_index+1, n)
                temp_index += 1
            elif str(o) in str(n):
                ordered_names.append(n)
                ordered_paths.append(p)

    ordered_names.extend(names)
    ordered_paths.extend(paths)

    names_set = set()
    paths_set = set()
    module_names = [x for x in ordered_names if not (x in names_set or names_set.add(x))]
    module_paths = [x for x in ordered_paths if not (x in paths_set or paths_set.add(x))]

    reloaded_names = list()
    reloaded_paths = list()
    for n, p in zip(names, paths):
        reloaded_names.append(n)
        reloaded_paths.append(p)

    for name, _ in zip(module_names, module_paths):
        if name not in loaded_modules.keys():
            mod = import_module(name)
            if mod:
                if isinstance(mod, ModuleType):
                    loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                    reload_modules.append(mod)

    for name, path in zip(module_names, module_paths):
        order = list()
        if name in loaded_modules.keys():
            mod = loaded_modules[name][1]
            if hasattr(mod, 'order'):
                order = mod.order
        import_modules(module_name=path, only_packages=False, order=order)


def reload_all():
    """
    Loops through all solstice_tools modules and reload them ane by one
    Used to increase iteration times
    """

    for mod in reload_modules:
        try:
            solstice_pipeline.logger.debug('Reloading module {0} ...'.format(mod))
            reload(mod)
        except Exception as e:
            solstice_pipeline.logger.debug('Impossible to import {0} module : {1}'.format(mod, str(e)))


def explore_package(module_name, only_packages=False):
    """
    Load module iteratively
    :param module_name: str, name of the module
    :return: list<str>, list<str>, list of loaded module names and list of loaded module paths
    """

    module_names = list()
    module_paths = list()

    def foo(name, only_packages):
        for importer, m_name, is_pkg in pkgutil.iter_modules([name]):
            mod_path = name + "//" + m_name
            mod_name = 'solstice_pipeline.' + os.path.relpath(mod_path, solstice_pipeline.__path__[0]).replace('\\', '.')
            if only_packages:
                if is_pkg:
                    module_paths.append(mod_path)
                    module_names.append(mod_name)
            else:
                module_paths.append(mod_path)
                module_names.append(mod_name)
    foo(module_name, only_packages)

    return module_names, module_paths


def create_solstice_logger():
    """
    Creates and initializes solstice logger
    """

    from solstice_utils import solstice_logger
    global logger
    logger = solstice_logger.Logger(name='solstice', level=solstice_logger.LoggerLevel.DEBUG)
    logger.debug('Initializing Solstice Tools ...')


def init():
    # update_paths()
    create_solstice_logger()
    import_modules(solstice_pipeline.__path__[0], only_packages=True, order=['solstice_pipeline.solstice_utils', 'solstice_pipeline.solstice_gui', 'solstice_pipeline.solstice_tools'])
    reload_all()
