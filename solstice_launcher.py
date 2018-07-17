import os
import shutil
import subprocess

# Get installer path
solstice_launcher_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solstice_launcher')
installer_bat = os.path.join(solstice_launcher_path, 'generate_executable.bat')

# PyInstaller will generate spec fild, build folder and dst folder in the current working directory
os.chdir(solstice_launcher_path)

# Generate executable
p = subprocess.Popen(installer_bat, shell=True, stdout=subprocess.PIPE)
stdout, stderr = p.communicate()

if p.returncode == 0:

    # Clean PyInstaller spec generated file
    spec_file = os.path.join(solstice_launcher_path, 'solstice_launcher.spec')
    if os.path.isfile(spec_file):
        print('Removing PyInstaller spec file: {}'.format(spec_file))
        os.remove(spec_file)

    # Remove build temporary folder used by PyInstaller
    temp_build_folder = os.path.join(solstice_launcher_path, 'build')
    if os.path.exists(temp_build_folder):
        print('Removing PyInstaller build foler: {}'.format(temp_build_folder))
        shutil.rmtree(temp_build_folder)

    # Move exe file to the root
    exe_file = os.path.join(solstice_launcher_path, 'dist', 'solstice_launcher.exe')
    if os.path.isfile(exe_file):
        to_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.isfile(os.path.join(to_dir, 'solstice_launcher.exe')):
            print('Removing Current Generated Solstice Launcher EXE file')
            os.remove(os.path.join(to_dir, 'solstice_launcher.exe'))
        print('Moving Solstice Launcher EXE file from: {0} to {1}'.format(exe_file, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        shutil.move(exe_file, to_dir)

    # Remove PyInstaller dst folder
    dist_folder = os.path.join(solstice_launcher_path, 'dist')
    if os.path.exists(dist_folder):
        print('Removing PyInstaller dist foler: {}'.format(dist_folder))
        shutil.rmtree(dist_folder)

    print(' ===> Solstice Launcher Executable generated successfully! <===')

else:
    print('Error while generating Solstice Launcher executable!')