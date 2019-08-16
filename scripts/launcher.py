#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella launcher implementation for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import sys
import contextlib

from Qt.QtWidgets import QApplication

@contextlib.contextmanager
def application():
    app = QApplication.instance()

    if not app:
        app = QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        yield app


if __name__ == '__main__':

    with application() as app:

        import tpPyUtils
        tpPyUtils.init()
        import tpDccLib
        tpDccLib.init()
        import tpQtLib
        tpQtLib.init()

        from PySide.QtGui import *

        import artellapipe
        artellapipe.init()
        import artellalauncher
        artellalauncher.init()

        import solstice
        solstice.init(import_libs=False)

        from solstice.launcher import launcher

        launcher = launcher.SolsticeLauncher(project=artellapipe.solstice, resource=solstice.resource)
        launcher.init()
