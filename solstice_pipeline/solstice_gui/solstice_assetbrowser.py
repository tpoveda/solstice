#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetbrowser.py
# by Tomas Poveda
# Module that contains a QWidget to browse assets
# The browser can be based on real folder structure or JSON dict folder
# structure
# ______________________________________________________________________
# ==================================================================="""

import os

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

from resources import solstice_resource
import solstice_breadcrumb
import solstice_navigationwidget
import solstice_filelistwidget

class AssetBrowserListBase(QWidget, object):

    clicked = Signal(QWidget)
    double_clicked = Signal(QWidget)

    def __init__(self, app, worker, parent=None):
        super(AssetBrowserListBase, self).__init__(parent=parent)

        self._app = app
        self._worker = worker
        self._ui = self._setup_ui()

    def support_selection(self):
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(self)

    def set_selected(self, status):
        pass

    def is_selected(self):
        return False

    def set_title(self, title):
        pass

    def set_details(self, text):
        pass

    def get_title(self):
        return None

    def get_details(self):
        return None

    def _setup_ui(self):
        raise NotImplementedError


class AssetBrowserHeader(AssetBrowserListBase, object):
    def __init__(self, app, worker, parent=None):
        super(AssetBrowserHeader, self).__init__(app=app, worker=worker, parent=parent)

        self.ui.line.setFrameShadow(QFrame.Plain)
        txt_color = QApplication.palette().text().color()
        self.ui.line.setStyleSheet("#line{color: rgb(%d,%d,%d);}" % (txt_color.red(), txt_color.green(), txt_color.blue()))

    def set_title(self, title):
        self.ui.label.setText("<big>%s</big>" % title)

    def get_title(self):
        return self.ui.label.text()

    def _setup_ui(self):
        ui = solstice_resource.gui('browser_header')
        return ui


class AssetBrowser(QWidget, object):

    selection_changed = Signal()
    item_clicked = Signal()
    list_modified = Signal()

    def __init__(self, title='Asset Browser', root_path=None, parent=None):
        super(AssetBrowser, self).__init__(parent=parent)

        self._directory = None
        self._root_path = root_path

        # ============================================================================

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(5, 5, 5, 5)
        title_layout.setSpacing(2)
        main_layout.addLayout(title_layout)
        title = QLabel(title)
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)

        base_grid = QGridLayout()
        base_grid.setContentsMargins(2, 2, 2, 2)
        base_grid.setSpacing(2)
        base_grid.setRowStretch(1, 2)
        base_grid.setColumnStretch(1, 2)
        main_layout.addLayout(base_grid)

        self.navigation_widget = solstice_navigationwidget.NavigationWidget()
        self.breadcrumb_widget = solstice_breadcrumb.BreadcrumbWidget()

        self._items_list = solstice_filelistwidget.FileListWidget(self)
        self._items_list.setWrapping(True)
        self._items_list.setFocusPolicy(Qt.StrongFocus)
        self._items_list.setFlow(QListView.TopToBottom)
        # self._items_list.setGridSize(QSize(65, 65))
        self._items_list.setUniformItemSizes(True)
        self._items_list.setViewMode(QListView.IconMode)
        self._items_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._items_list.setIconSize(QSize(80, 80))

        base_grid.addWidget(self.navigation_widget, 0, 0, Qt.AlignLeft)
        base_grid.addWidget(self.breadcrumb_widget, 0, 1, Qt.AlignLeft)
        base_grid.addWidget(self._items_list, 1, 0, 2, 2)

        # ============================================================================

        if root_path:
            self.set_directory(os.path.expanduser(root_path))


    def set_directory(self, path):
        """
        Sets the directory that you want to explore
        :param path: str, valid path
        """

        self._directory = os.path.realpath(path)
        self.breadcrumb_widget.set_from_path(path)

        self.update_items()


    def update_items(self):
        """
        Updates items view
        """

        self._items_list.clear()
        qdir = QDir(self._directory)
        filters = QDir.Dirs | QDir.AllDirs | QDir.Files | QDir.NoDot | QDir.NoDotDot

        entries = qdir.entryInfoList()
        for info in entries:
            icon = QFileIconProvider().icon(info)
            suf = info.completeSuffix()
            name, tp = (info.fileName(), 0) if info.isDir() else (
                '%s%s' % (info.baseName(), '.%s' % suf if suf else ''), 1)
            new_item = QListWidgetItem(icon, name, self._items_list, tp)
        self._items_list.setFocus()


    #     asset_browser_widget = solstice_resource.gui('browser')
    #     main_layout.addWidget(asset_browser_widget)
    #
    #     asset_browser_widget.main_pages.setCurrentWidget(asset_browser_widget.loading_page)
    #
    #     self._spin_icons = list()
    #     self._spin_icons.append(solstice_resource.pixmap('progress_bar_1'))
    #     self._spin_icons.append(solstice_resource.pixmap('progress_bar_2'))
    #     self._spin_icons.append(solstice_resource.pixmap('progress_bar_3'))
    #     self._spin_icons.append(solstice_resource.pixmap('progress_bar_4'))
    #     self._timer = QTimer(self)
    #     self._timer.timeout.connect(self._update_spinner)
    #     self._current_spinner_index = 0
    #
    #     asset_browser_widget.search.textEdited.connect(self._on_search_box_input)
    #
    #     asset_browser_widget.load_all_top.clicked.connect(self._on_load_all_clicked)
    #     asset_browser_widget.load_all_bottom.clicked.connect(self._on_load_all_clicked)
    #
    #     self._title_base_style = {
    #         "border": "none",
    #         "border-color": "rgb(32,32,32)",
    #         "border-top-left-radius": "3px",
    #         "border-top-right-radius": "3px",
    #         "border-bottom-left-radius": "0px",
    #         "border-bottom-right-radius": "0px"
    #     }
    #     self._title_styles = {
    #         "gradient": {
    #             "background": "qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97, 97, 97, 255), stop:1 rgba(49, 49, 49, 255));"},
    #         "none": {}
    #     }
    #     self._title_margins = {
    #         "gradient": [12, 3, 12, 3],
    #         "none": [3, 3, 3, 3]
    #     }
    #
    #     self._current_title_style = "none"
    #     self.title_style = "gradient"
    #
    # def _update_spinner(self):
    #     pass
    #
    # def _on_search_box_input(self):
    #     print('Hello')
    #
    # def _on_load_all_clicked(self):
    #     pass