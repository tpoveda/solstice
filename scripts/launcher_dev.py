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

import os
import sys
import contextlib

paths_to_add = [
    'D://tomi//deps',
    'D://tomi//tpPyUtils//source',
    'D://tomi//tpQtLib//source',
    'D://tomi//tpDccLib//source',
    'D://tomi//tpMayaLib//source',
    'D://tomi//tpHoudiniLib//source',
    'D://tomi//tpNameIt//source',
    'D://artellapipe//source',
    'D://artellalauncher//source',
    'D://solstice//source'
]
for p in paths_to_add:
    if p not in sys.path:
        if not os.path.isdir(p):
            continue
        sys.path.append(p)

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
        solstice.init()

        from solstice.launcher import launcher
        launcher.run()



        # launcher = launcher.SolsticeLauncher(project=artellapipe.solstice)

