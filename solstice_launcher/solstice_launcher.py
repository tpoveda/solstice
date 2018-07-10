#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_launcher.py
# by Tomas Poveda
# Application that setup Maya to work on Solstice Short Film
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import argparse
import time

import solstice_artella_utils as artella
import solstice_config as cfg
import solstice_launcher_utils as utils
import solstice_environment as env
import solstice_updater
import solstice_console
import solstice_updater
import solstice_maya_utils
import tempfile

from PySide.QtGui import *
from PySide.QtCore import *


class SolsticeLauncher(QObject, object):

    def __init__(self):
        super(SolsticeLauncher, self).__init__()

    @staticmethod
    def get_executables(versions):
        """
        Return available Maya releases
        :param versions:
        :return:
        """

        return [k for k in versions if not k.startswith(cfg.SolsticeConfig.DEFAULTS)]


    def setup_maya_environments(config, env=None, arg_paths=None):
        pass

    def launch(self):
        """
        Function that ready to use Maya for being used in Solstice Short Film
        """

        parser = argparse.ArgumentParser(
            description="Solstice Launcher allows to setup a custom initialization for "
                        "Maya. This allows to setup specific Solstice paths in a very easy way"
        )

        parser.add_argument(
            '-console', '--console',
            metavar='console',
            type=str,
            default="True",
            help="""
            If True it will show a console during Solstice and will generate a installation log in your desktop
            """
        )

        splash_pixmap = QPixmap('solstice_splash.png')
        self._splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        self._splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._splash.setEnabled(True)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(2)
        main_layout.setAlignment(Qt.AlignBottom)

        self._splash.setLayout(main_layout)
        progress_bar = QProgressBar()
        main_layout.addWidget(progress_bar)
        progress_bar.setMaximum(6)
        progress_bar.setTextVisible(False)

        self._progress_text = QLabel('Loading Solstice Tools ...')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        main_layout.addWidget(self._progress_text)

        console = solstice_console.SolsticeConsole()
        console.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        console.move(self._splash.geometry().center())
        console.move(300, 405)

        main_layout.addItem(QSpacerItem(0, 20))

        self._splash.show()

        # Create Solstice Configuration
        self._progress_text.setText('Creating Solstice Launcher Configuration ...')

        config = cfg.create_config(console=console)

        if config is None:
            console.write('Maya location not found! Solstice Launcher will not launch Maya!')
            self._splash.close()
            return

        parser.add_argument(
            'file',
            nargs='?',
            default=None,
            help="""
            If this argument is passed, Maya will try to load a scene on start [OPTIONAL]
            """
        )

        parser.add_argument(
            '-env', '--environment',
            metavar='env',
            type=str,
            default=config.get(cfg.SolsticeConfig.DEFAULTS, 'environment'),
            help="""
            Launch Maya with given environment. If no environment is specified Maya
            will try to use default value. If no default value is specified, Maya
            will behave with factory environment setup
            """
        )

        parser.add_argument(
            '-p', '--path',
            metavar='path',
            type=str,
            nargs='+',
            help="""
            Used to pass an unlimited number of paths to use for environment creation
            Useful if you do not want to create a environment variable. Just pass the
            path/paths you want to use in Maya session [OPTIONAL]
            """
        )

        parser.add_argument(
            '-e', '--edit',
            action='store_true',
            help="""
            Edit configuration file
            """
        )

        parser.add_argument(
            '-d', '--debug',
            action='store_true',
            help="""
            Start Maya in Dev mode, autoload on plugins are turned off and console
            is showed during Solstice Launcher execution
            """
        )

        args = parser.parse_args()
        if args.edit:
            console.write('Opening Configuration File to edit ...')
            return config.edit()

        if args.console:
            show_console = utils.str2bool(args.console)
            if show_console:
                console.show()
        if args.debug:
            console.set_debug_level()

        console.write('Creating Solstice Launcher Configuration ...')
        exec_default = config.get(cfg.SolsticeConfig.DEFAULTS, 'executable')
        if not exec_default and config.items(cfg.SolsticeConfig.EXECUTABLES):
            items = dict(config.items(cfg.SolsticeConfig.EXECUTABLES))
            exec_ = items[sorted(items.keys(), reverse=True)[0]]
        else:
            exec_ = exec_default
        progress_bar.setValue(1)
        app.processEvents()
        time.sleep(1)

        # Close already working Artella processes
        console.write('Closing Artella App instances ...')
        app.processEvents()
        self._progress_text.setText('Closing Artella App instances ...')
        artella.close_all_artella_app_processes(console)
        progress_bar.setValue(2)
        app.processEvents()
        time.sleep(1)

        # Launch Artella App
        self._progress_text.setText('Launching Artella App ...')
        console.write('Updating Artella Paths ...')
        app.processEvents()
        artella.update_artella_paths(console)
        app.processEvents()
        console.write('Launching Artella App ...')
        app.processEvents()
        artella.launch_artella_app(console)
        progress_bar.setValue(3)
        app.processEvents()
        time.sleep(1)

        # We need to import this here because this path maybe is not available until we update Artella paths
        try:
            import am.artella.spigot.spigot as spigot
        except ImportError as e:
            console.write_error('Impossible to import Artella Python modules! Maybe Artella is not installed properly. Contact TD please!')
            return

        # Check Solstice Tools version ...
        self._progress_text.setText('Checking Solstice Tools Version ...')
        progress_bar.setValue(4)
        console.write('Checking Solstice Tools Version ...')
        updater = solstice_updater.SolsticeUpdater(config=config, parent=self._splash)
        main_layout.addWidget(updater)
        updater.show()
        app.processEvents()

        need_to_update = solstice_updater.check_solstice_tools_version(console=console, updater=updater)

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

            if valid_download:
                QMessageBox.information(None, 'Solstice Pipeline Updated', 'Solstice Pipeline installed successfully!')
            else:
                QMessageBox.critical(None, 'Contact Solstice Pipeline Team!', 'Pipeline Tools Download server is not working" Please contact Solstice Pipeline Team!')

        # TODO: Show changelog

        self._splash.show()
        app.processEvents()

        console.write('Setting Maya Environment Variables ...')
        self._progress_text.setText('Setting Maya Environment Variables ...')
        progress_bar.setValue(5)
        app.processEvents()

        if not args.environment:
            # args.environment = config.get(cfg.SolsticeConfig.INSTALL, 'install_path')
            args.environment = 'install_path'

        env.MayaEnvironment.build(config=config, console=console, env=args.environment, arg_paths=args.path)
        app.processEvents()

        console.write('Solstice Maya setup completed, launching: {}'.format(exec_))
        app.processEvents()

        time.sleep(1)

        # TODO: Export al console log to a file

        for p in sys.path:
            print(p)

        # TODO: Launch Maya
        solstice_maya_utils.launch_maya(exec_=exec_, args=args, console=console)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    SolsticeLauncher().launch()
