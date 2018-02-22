import os
import sys
import glob
import importlib
import pkgutil
try:
    reload
except NameError:
    try:
        from importlib import reload
    except ImportError:
        from imp import reload

root_path = os.path.dirname(os.path.abspath(__file__))
extra_paths = [os.path.join(root_path, 'externals'), os.path.join(root_path, 'icons')]
for path in extra_paths:
    if os.path.exists(path):
        if path not in sys.path:
            sys.path.append(path)

def get_module_names():
    root_name = os.path.basename(root_path)
    ret = list()
    for subdir, dirs, files in os.walk(root_path):
        file_names = glob.glob(os.path.split(subdir)[0] + '/*/__init__.py')
        for file_path in file_names:
            directories = file_path.split(os.sep)
            subdirectory = str.join(os.sep, directories[:directories.index(root_name)])
            package_path = file_path.split(subdirectory)[1].replace('\\', '.')[1:].replace('.__init__.py', '').replace('.__init__.pyc', '')
            ret.append(package_path)
    return ret

def reload_all():
    for mod_name in get_module_names():
        try:
            mod = sys.modules[mod_name]
            reload(mod)
        except:
            continue

def init_solstice_tools():
    mod_names = list(set(get_module_names()))
    for mod_name in mod_names:

        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            print('Impossible to import {} module'.format(mod_name))
            print(e)
        # try:
        mod = sys.modules[mod_name]
        imported_mods = list()
        for importer, mod_name, is_pkg in pkgutil.iter_modules(mod.__path__):
            mod_name = '{0}.{1}'.format(mod.__name__, mod_name)
            imported_mod = importlib.import_module(mod_name)
            imported_mods.append(imported_mod)
        print('Module {} initialized'.format(mod_name))
        # except:
        #     continue

def init():
    reload_all()
    init_solstice_tools()
    # from solstice_tools.scripts import userSetup
    # reload(userSetup)