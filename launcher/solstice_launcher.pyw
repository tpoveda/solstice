#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_launcher.py
# by Tomas Poveda
# Application that setup Maya to work on Solstice Short Film
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import time
import shutil
import argparse
import platform
import traceback
import subprocess

import solstice_artella_utils as artella
import solstice_config as cfg
import solstice_console
import solstice_updater
import solstice_resources
import solstice_launcher_utils
import solstice_maya_utils
import solstice_houdini_utils
import solstice_nuke_utils

from PySide.QtGui import *
from PySide.QtCore import *

# ==============================================

MAYA_VERSION = 2019

# ==============================================


class SolsticeDccs(object):
    Maya = 'Maya'
    Houdini = 'Houdini'
    Nuke = 'Nuke'


class SolsticeLauncher(QObject, object):

    def __init__(self):
        super(SolsticeLauncher, self).__init__()

        self.selected_dcc = None

    @staticmethod
    def get_executables(versions):
        """
        Return available Maya releases
        :param versions:
        :return:
        """

        return [k for k in versions if not k.startswith(cfg.SolsticeConfig.DEFAULTS)]

    def main(self):
        """
        Main launcher function
        """

        maya_location = solstice_launcher_utils.get_maya_installation(2019)
        houdini_location = solstice_launcher_utils.get_houdini_installation()
        nuke_location = solstice_launcher_utils.get_nuke_installation()
        # if maya_location and not houdini_location and not nuke_location:
        #     self.selected_dcc = SolsticeDccs.Maya
        # elif houdini_location and not maya_location and not nuke_location:
        #     self.selected_dcc = SolsticeDccs.Houdini
        # elif nuke_location and not maya_location and not houdini_location:
        #     self.selected_dcc = SolsticeDccs.Nuke

        console = solstice_console.SolsticeConsole()
        console.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        dcc_config = cfg.create_config(window=self, dcc_install_path=None, console=console)

        # if self.selected_dcc is None:
        dcc_selector = DCCSelector(dcc_config)
        dcc_selector.exec_()
        self.selected_dcc = dcc_selector.selected_dcc

        if self.selected_dcc is None:
            QMessageBox.information(None, 'Maya and Houdini installations not found', 'Solstice Launcher cannot launch non supported DCC. Closing it ...!')
            sys.exit()

        dcc_install_path = None
        if self.selected_dcc == SolsticeDccs.Maya:
            dcc_install_path = maya_location
        elif self.selected_dcc == SolsticeDccs.Houdini:
            dcc_install_path = houdini_location
        elif self.selected_dcc == SolsticeDccs.Nuke:
            dcc_install_path = nuke_location

        self.setup_ui()

        console.move(self._splash.geometry().center())
        console.move(300, 405)
        console.show()

        config = cfg.create_config(window=self, dcc_install_path=dcc_install_path, console=console)

        if config is None:
            console.write('Maya location not found! Solstice Launcher will not launch Maya!')
            self._splash.close()
            return

        parser = argparse.ArgumentParser(
            description="Solstice Launcher allows to setup a custom initialization for "
                        "Maya. This allows to setup specific Solstice paths in a very easy way"
        )

        parser.add_argument(
            '-e', '--edit',
            action='store_true',
            help="""
                    Edit configuration file
                    """
        )

        args = parser.parse_args()
        if args.edit:
            console.write('Opening Configuration File to edit ...')
            return config.edit()

        console.write('Creating Solstice Launcher Configuration ...')
        exec_ = config.value('executable')

        self.progress_bar.setValue(1)
        app.processEvents()
        time.sleep(1)

        # Close already working Artella processes
        console.write('Updating Artella Paths ...')
        app.processEvents()
        artella.update_artella_paths(console)
        app.processEvents()

        console.write('Closing Artella App instances ...')
        app.processEvents()
        self._progress_text.setText('Closing Artella App instances ...')
        artella.close_all_artella_app_processes(console)
        self.progress_bar.setValue(2)
        app.processEvents()
        time.sleep(1)

        # Launch Artella App
        self._progress_text.setText('Launching Artella App ...')
        console.write('Launching Artella App ...')
        app.processEvents()
        artella.launch_artella_app(console)
        self.progress_bar.setValue(3)
        app.processEvents()
        time.sleep(1)

        # We need to import this here because this path maybe is not available until we update Artella paths
        try:
            import spigot
        except ImportError as e:
            console.write_error('Impossible to import Artella Python modules! Maybe Artella is not installed properly. Contact TD please!')
            return

        install_path = config.value('solstice_pipeline_install')
        if install_path:
            install_path = os.path.join(install_path)
        if install_path is None or not os.path.exists(install_path):
            console.write('Current installation path does not exists: {}. Reinstalling Solstice Tools ...'.format(install_path))
            config.setValue('solstice_pipeline_install', os.path.abspath(solstice_updater.SolsticeTools.set_installation_path(console=console)))

        # Setup Solstice Environment variables
        console.write('Setting DCC Environment Variables ...')
        self._progress_text.setText('Setting DCC Environment Variables ...')
        self.progress_bar.setValue(5)
        app.processEvents()

        console.write('Added environment variable: solstice_install_path --> {}'.format(install_path))
        if os.environ.get('PYTHONPATH'):
            os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ';' + config.value('solstice_pipeline_install')
            os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ';' + os.path.join(config.value('solstice_pipeline_install'), 'solstice', 'pipeline')
            os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ';' + os.path.join(os.path.join(config.value('solstice_pipeline_install'), 'solstice', 'pipeline'), 'externals')
        else:
            os.environ['PYTHONPATH'] = config.value('solstice_pipeline_install')
            os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ';' + os.path.join(config.value('solstice_pipeline_install'), 'solstice', 'pipeline')
            os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ';' + os.path.join(os.path.join(config.value('solstice_pipeline_install'), 'solstice', 'pipeline'), 'externals')

        # Check Solstice Tools version ...
        self._progress_text.setText('Checking Solstice Tools Version ...')
        self.progress_bar.setValue(4)
        console.write('Checking Solstice Tools Version ...')
        updater = solstice_updater.SolsticeUpdater(config=config, parent=self._splash)
        self.main_layout.addWidget(updater)
        updater.show()
        updater.raise_()
        app.processEvents()

        need_to_update = solstice_updater.check_solstice_tools_version(console=console, updater=updater)
        os.environ['SOLSTICE_PIPELINE_SHOW'] = 'show'

        app.processEvents()
        time.sleep(1)
        updater.close()
        updater._progress_bar.setValue(0)
        app.processEvents()

        # Download Solstice Tools ...
        if need_to_update:
            self._progress_text.setText('Updating Solstice Tools ...')
            console.write('Updating Solstice Tools Solstice Tools ')
            updater.show()
            app.processEvents()
            valid_download = solstice_updater.update_solstice_tools(console=console, updater=updater)
            time.sleep(1)
            updater.close()
            updater._progress_bar.setValue(0)
            app.processEvents()

            self._splash.close()

            # if valid_download:
            #     QMessageBox.information(None, 'Solstice Pipeline Updated', 'Solstice Pipeline installed successfully!')
            # else:
            #     QMessageBox.critical(None, 'Contact Solstice Pipeline Team!',
            #                          'Pipeline Tools Download server is not working" Please contact Solstice Pipeline Team!')

        # TODO: Show changelog

        self._splash.show()
        app.processEvents()

        console.write('Solstice Maya setup completed, launching: {}'.format(exec_))
        app.processEvents()

        time.sleep(1)

        self.launch(exec_=exec_, console=console, install_path=os.path.join(config.value('solstice_pipeline_install'), 'solstice', 'pipeline'))

    def setup_ui(self):
        """
        Sets launcher UI
        """

        if self.selected_dcc == SolsticeDccs.Maya:
            ba = QByteArray.fromBase64(solstice_resources.maya_splash_code)
        elif self.selected_dcc == SolsticeDccs.Houdini:
            ba = QByteArray.fromBase64(solstice_resources.houdini_splash_code)
        elif self.selected_dcc == SolsticeDccs.Nuke:
            ba = QByteArray.fromBase64(solstice_resources.nuke_splash_code)
        else:
            QMessageBox.information(None, 'No supported DCC found!', 'Solstice Launcher cannot launch non supported DCC. Closing it ...!')
            return

        image = QImage.fromData(ba, 'PNG')
        splash_pixmap = QPixmap.fromImage(image)

        self._splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        self._splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._splash.setEnabled(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 2, 5, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignBottom)

        self._splash.setLayout(self.main_layout)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }")
        self.main_layout.addWidget(self.progress_bar)
        self.progress_bar.setMaximum(6)
        self.progress_bar.setTextVisible(False)

        self._progress_text = QLabel('Loading Solstice Tools ...')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        self.main_layout.addWidget(self._progress_text)

        self.main_layout.addItem(QSpacerItem(0, 20))

        self._splash.show()

        # Create Solstice Configuration
        self._progress_text.setText('Creating Solstice Launcher Configuration ...')

    def launch(self, exec_, console, install_path):
        """
        Function that ready to use Maya for being used in Solstice Short Film
        """

        if self.selected_dcc == SolsticeDccs.Maya:
            solstice_maya_utils.launch_maya(exec_=exec_, console=console)
        elif self.selected_dcc == SolsticeDccs.Houdini:
            script_path = os.path.join(install_path, 'userSetup.py')
            if not os.path.isfile(script_path):
                QMessageBox.information(None, 'No valid init script for Houdini found!',
                                        'Solstice Launcher cannot launch Houdini. Init Script not found: {}!'.format(script_path))
                return None

            houdini_path = os.path.join(install_path, 'dcc', 'houdini')
            if not os.path.isdir(houdini_path):
                QMessageBox.information(None, 'No valid Houdini DCC folder found!',
                                        'Solstice Launcher cannot launch Houdini. Houdini DCC folder not found: {}!'.format(
                                            houdini_path))
                return None

            houdini_bootstrap = os.path.join(install_path, houdini_path, 'houdini_bootstrap.bat')
            if not os.path.isfile(houdini_bootstrap):
                QMessageBox.information(None, 'No valid Houdini Bootstrap found!',
                                        'Solstice Launcher cannot launch Houdini. Bootstrap not found: {}!'.format(
                                            houdini_bootstrap))
                return None

            solstice_houdini_utils.launch_houdini(exec_=exec_, console=console, script_path=script_path, houdini_path=houdini_path, bootstrap=houdini_bootstrap)
        elif self.selected_dcc == SolsticeDccs.Nuke:
            script_path = os.path.join(install_path, 'userSetup.py')
            if not os.path.isfile(script_path):
                QMessageBox.information(None, 'No valid init script for Nuke found!',
                                        'Solstice Launcher cannot launch Nuke. Init Script not found: {}!'.format(script_path))
            solstice_nuke_utils.launch_nuke(exec_=exec_, console=console, script_path=script_path)
        else:
            QMessageBox.information(None, 'No supported DCC found!', 'Solstice Launcher cannot launch non supported DCC. Closing it ...!')


class DCCSelector(QDialog, object):
    def __init__(self, config, parent=None):
        super(DCCSelector, self).__init__(parent)

        self._config = config
        self.selected_dcc = None

        self.setWindowTitle('DCC Selector')
        self.setFixedSize(QSize(310, 160))
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        self.setStyleSheet('background-color: rgb(80, 80, 80)')

        dccs_layout = QHBoxLayout()
        self.main_layout.addLayout(dccs_layout)

        maya_ba = QByteArray.fromBase64(solstice_resources.maya_code)
        maya_image = QImage.fromData(maya_ba, 'PNG')
        maya_pixmap = QPixmap.fromImage(maya_image)

        maya_btn = QPushButton()
        maya_btn.setFixedSize(QSize(100, 100))
        maya_btn.setIconSize(QSize(110, 110))
        maya_btn.setIcon(QIcon(maya_pixmap))
        dccs_layout.addWidget(maya_btn)

        houdini_ba = QByteArray.fromBase64(solstice_resources.houdini_code)
        houdini_image = QImage.fromData(houdini_ba, 'PNG')
        houdini_pixmap = QPixmap.fromImage(houdini_image)

        houdini_btn = QPushButton()
        houdini_btn.setFixedSize(QSize(100, 100))
        houdini_btn.setIconSize(QSize(110, 110))
        houdini_btn.setIcon(QIcon(houdini_pixmap))
        dccs_layout.addWidget(houdini_btn)

        nuke_ba = QByteArray.fromBase64(solstice_resources.nuke_code)
        nuke_image = QImage.fromData(nuke_ba, 'PNG')
        nuke_pixmap = QPixmap.fromImage(nuke_image)

        nuke_btn = QPushButton()
        nuke_btn.setFixedSize(QSize(100, 100))
        nuke_btn.setIconSize(QSize(90, 90))
        nuke_btn.setIcon(QIcon(nuke_pixmap))
        dccs_layout.addWidget(nuke_btn)

        extra_buttons_lyt = QHBoxLayout()
        self.main_layout.addLayout(extra_buttons_lyt)
        self.open_folder_btn = QPushButton('Open Solstice Tools folder')
        self.uninstall_btn = QPushButton('Uninstall Solstice Tools')
        self.force_uninstall_btn = QPushButton('Force')
        self.force_uninstall_btn.setMaximumWidth(35)
        extra_buttons_lyt.addWidget(self.open_folder_btn)
        extra_buttons_lyt.addWidget(self.uninstall_btn)
        extra_buttons_lyt.addWidget(self.force_uninstall_btn)

        close_btn = QPushButton('C L O S E')
        self.main_layout.addWidget(close_btn)

        maya_location = solstice_launcher_utils.get_maya_installation(2019)
        if not maya_location:
            maya_btn.setVisible(False)

        houdini_location = solstice_launcher_utils.get_houdini_installation()
        if not houdini_location:
            houdini_btn.setVisible(False)

        nuke_location = solstice_launcher_utils.get_nuke_installation()
        if not nuke_location:
            nuke_btn.setVisible(False)

        if maya_location is None and houdini_location is None and nuke_location is None:
            QMessageBox.information(None, 'Maya, Houdini & Nuke installations not found', 'Solstice Launcher cannot launch non supported DCC. Closing it ...!')
            sys.exit()

        maya_btn.clicked.connect(self._on_maya_selected)
        houdini_btn.clicked.connect(self._on_houdini_selected)
        nuke_btn.clicked.connect(self._on_nuke_selected)
        self.open_folder_btn.clicked.connect(self._on_open_installation_folder)
        self.uninstall_btn.clicked.connect(self._on_uninstall)
        self.force_uninstall_btn.clicked.connect(self._on_force_uninstall)
        close_btn.clicked.connect(sys.exit)

    def _on_maya_selected(self):
        self.selected_dcc = SolsticeDccs.Maya
        self.close()

    def _on_houdini_selected(self):
        self.selected_dcc = SolsticeDccs.Houdini
        self.close()

    def _on_nuke_selected(self):
        self.selected_dcc = SolsticeDccs.Nuke
        self.close()

    def _on_open_installation_folder(self):

        def _open_folder(path):
            """
            Open folder using OS default settings
            :param path: str, folder path we want to open
            """

            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

        install_path = solstice_updater.SolsticeTools.get_installation_path(config=self._config)
        if install_path and os.path.isdir(install_path) and len(os.listdir(install_path)) != 0:
            _open_folder(install_path)
        else:
            QMessageBox.information(self, 'Solstice Tools are not installed!', 'Solstice Tools Installation folder not found!')

    def _on_uninstall(self):
        install_path = solstice_updater.SolsticeTools.get_installation_path(config=self._config)
        if install_path and os.path.isdir(install_path):
            dirs_to_remove = list()
            if os.path.isdir(os.path.join(install_path, 'solstice_pipeline')):
                dirs_to_remove.append(os.path.join(install_path, 'solstice_pipeline'))
            elif os.path.isdir(os.path.join(install_path, 'solstice')) and os.path.isfile(os.path.join(install_path, '__init__.pyc')):
                dirs_to_remove.append(os.path.join(install_path, 'solstice'))
                dirs_to_remove.append(os.path.join(install_path, '__init__.pyc'))

            QMessageBox.information(self, 'Close DCCs', 'Please close any opened DCC (Maya, Houdini or Nuke) before continuing')
            res = QMessageBox.question(self, 'Uninstalling Solstice Tools', 'Are you sure you want to uninstall Solstice Tools?\nFolder/s that will be removed \n\t{}'.format('\n\t'.join(dirs_to_remove)), QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.Yes:
                try:
                    for f in dirs_to_remove:
                        if os.path.isdir(f):
                            shutil.rmtree(f, ignore_errors=True)
                        elif os.path.isfile(f):
                            os.remove(f)
                    self._config.setValue('solstice_pipeline_install', None)
                    QMessageBox.information(self, 'Solstice Tools uninstalled!', 'Solstice Tools uninstalled successfully!')
                except Exception:
                    QMessageBox.critical(self, 'Error during Solstice Tools uninstall', traceback.format_exc())
        else:
            QMessageBox.information(self, 'Solstice Tools are not installed!', 'Impossible to uninstall Solstice Tools!')


    def _on_force_uninstall(self):
        res = QMessageBox.question(self, 'Uninstalling Solstice Tools', 'Are you sure you want to uninstall Solstice Tools?', QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self._config.setValue('solstice_pipeline_install', None)
            QMessageBox.information(self, 'Solstice Tools uninstalled!', 'Solstice Tools uninstalled successfully!')


if __name__ == '__main__':

    app = QApplication(sys.argv)

    SolsticeLauncher().main()
