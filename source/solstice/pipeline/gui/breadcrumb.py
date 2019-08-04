#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains classes to create breadcrubms widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


import os

from Qt.QtWidgets import *

from solstice.pipeline.gui import label
from solstice.pipeline.utils import pythonutils as utils


class Breadcrumb(object):
    def __init__(self, label):
        """
        Constructor
        :param label: QLabel, label used in this breadcrumb
        """

        self._label = label

    @property
    def label(self):
        return self._label


class BreadcrumbWidget(QWidget, object):
    def __init__(self, parent=None):
        super(BreadcrumbWidget, self).__init__(parent=parent)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self._path_label = label.ElidedLabel()
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(self._path_label.sizePolicy().hasHeightForWidth())
        self._path_label.setSizePolicy(sp)
        main_layout.addWidget(self._path_label)

    def set(self, breadcrumbs):
        """
        Populates the breadcrumb control with a list of breadcrumbs
        :param breadcrumbs: each breadcrumb should derive from Breadcrumb class
        """

        path = "<span style='color:#E2AC2C'> &#9656; </span>".join([crumb.label for crumb in breadcrumbs])
        path = "<big>%s</big>" % path

        self._path_label.setText(path)

    def set_from_path(self, path):
        """
        Creates a proper Breadcrumb list for given path and sets the text
        """

        path = os.path.dirname(path)
        folders = utils.get_folders_from_path(path)
        breadcrumbs = [Breadcrumb(f) for f in folders]
        self.set(breadcrumbs)
