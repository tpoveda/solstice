#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Solstice Pipeline tool to smooth the workflow between Maya and Artella
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import weakref
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.core import asset, assetviewer
from solstice.pipeline.gui import window, stack, spinner, splitters, console
from solstice.pipeline.utils import image, qtutils
from solstice.pipeline.tools.sanitycheck.checks import checkgroups, assetchecks


class SanityCheckWaiting(QFrame, object):
    def __init__(self, parent=None):
        super(SanityCheckWaiting, self).__init__(parent)

        self.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.wait_spinner = spinner.WaitSpinner()
        self.wait_spinner.bg.setFrameShape(QFrame.NoFrame)
        self.wait_spinner.bg.setFrameShadow(QFrame.Plain)

        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
        main_layout.addWidget(self.wait_spinner)
        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))


class SanityCheck(window.Window, object):
    name = 'Solstice_SanityCheck'
    title = 'Solstice Tools - Sanity Check'
    version = '1.1'

    def __init__(self):
        super(SanityCheck, self).__init__()

        self._current_asset = None

    def custom_ui(self):
        super(SanityCheck, self).custom_ui()

        self.set_logo('solstice_sanitycheck_logo')
        self.resize(1000, 850)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        categories_widget.setLayout(categories_layout)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        main_splitter.addWidget(categories_widget)

        main_categories_menu_layout = QHBoxLayout()
        main_categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        main_categories_menu_layout.setSpacing(0)
        categories_layout.addLayout(main_categories_menu_layout)

        categories_menu = QWidget()
        categories_menu_layout = QVBoxLayout()
        categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        categories_menu_layout.setSpacing(0)
        categories_menu_layout.setAlignment(Qt.AlignTop)
        categories_menu.setLayout(categories_menu_layout)
        main_categories_menu_layout.addWidget(categories_menu)

        self.stack = stack.SlidingStackedWidget(parent=self)
        main_categories_menu_layout.addWidget(self.stack)

        asset_splitter = QSplitter(Qt.Horizontal)
        asset_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.addWidget(asset_splitter)

        self._asset_viewer = assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=self.show_check_menu,
            column_count=3,
            parent=self)
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        asset_splitter.addWidget(self._asset_viewer)

        log_splitter = QSplitter(Qt.Horizontal)
        log_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_splitter.addWidget(log_splitter)

        self.sanity_widget = QWidget()
        self.sanity_widget.setMinimumWidth(300)
        self.sanity_layout = QVBoxLayout()
        self.sanity_widget.setLayout(self.sanity_layout)
        self.sanity_widget.setVisible(False)
        self._log = console.SolsticeConsole()
        self._log.write_ok('>>> SANITY CHECKER LOG <<<\n')
        self._log.write('\n')
        log_splitter.addWidget(self.sanity_widget)
        log_splitter.addWidget(self._log)

        self._check_asset_widget = QWidget()
        self._check_asset_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._check_asset_widget.setVisible(False)
        check_asset_layout = QVBoxLayout()
        check_asset_layout.setContentsMargins(5, 5, 5, 5)
        check_asset_layout.setSpacing(5)
        self._check_asset_widget.setLayout(check_asset_layout)
        self._check_asset_widget.setMinimumWidth(200)
        asset_splitter.addWidget(self._check_asset_widget)

        self._categories_btn_group = QButtonGroup(self)
        self._categories_btn_group.setExclusive(True)
        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            new_btn = QPushButton(category)
            new_btn.toggled.connect(partial(self._change_category, category))
            categories_buttons[category] = new_btn
            categories_buttons[category].setCheckable(True)
            categories_menu_layout.addWidget(new_btn)
            self._categories_btn_group.addButton(new_btn)
        categories_buttons['All'].setChecked(True)

        self.asset_name = splitters.Splitter('')
        check_asset_layout.addWidget(self.asset_name)
        icon_layout = QHBoxLayout()
        check_asset_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.asset_icon = QLabel()
        self.asset_icon.setFixedSize(QSize(200, 200))
        self.asset_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(self.asset_icon)
        icon_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        check_asset_layout.addLayout(splitters.SplitterLayout())
        self.check_general_btn = QPushButton('Check General')
        self.check_general_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.check_textures_btn = QPushButton('Check Textures')
        self.check_textures_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.check_model_btn = QPushButton('Check Model')
        self.check_model_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.check_shading_btn = QPushButton('Check Shading')
        self.check_shading_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.check_grooming_btn = QPushButton('Check Grooming')
        self.check_grooming_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.check_grooming_btn.setVisible(False)
        check_asset_layout.addWidget(self.check_general_btn)
        check_asset_layout.addLayout(splitters.SplitterLayout())
        check_asset_layout.addWidget(self.check_textures_btn)
        check_asset_layout.addLayout(splitters.SplitterLayout())
        check_asset_layout.addWidget(self.check_model_btn)
        check_asset_layout.addLayout(splitters.SplitterLayout())
        check_asset_layout.addWidget(self.check_shading_btn)
        check_asset_layout.addLayout(splitters.SplitterLayout())
        check_asset_layout.addWidget(self.check_grooming_btn)

        wait_widget = SanityCheckWaiting()
        self.stack.addWidget(wait_widget)

        self.check_textures_btn.clicked.connect(partial(self._do_check, 'textures'))
        self.check_model_btn.clicked.connect(partial(self._do_check, 'model'))
        self.check_shading_btn.clicked.connect(partial(self._do_check, 'shading'))
        self.check_grooming_btn.clicked.connect(partial(self._do_check, 'grooming'))

    def show_check_menu(self, asset_to_show=None, *args, **kwargs):
        self._current_asset = None
        if not asset_to_show:
            self._check_asset_widget.setVisible(False)
            return

        if isinstance(asset_to_show, asset.CharacterAsset):
            self.check_grooming_btn.setVisible(True)
        else:
            self.check_grooming_btn.setVisible(False)

        self._current_asset = weakref.ref(asset_to_show)

        self.asset_name.set_text(asset_to_show.name)
        self.asset_icon.setPixmap(QPixmap.fromImage(image.base64_to_image(asset_to_show._icon, image_format=asset_to_show._icon_format)).scaled(200, 200, Qt.KeepAspectRatio))
        self._check_asset_widget.setVisible(True)

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)

    def _do_check(self, check_type):
        self.stack.setCurrentIndex(1)
        QCoreApplication.processEvents()

        qtutils.clear_layout_widgets(self.sanity_layout)
        self._log.clear()

        self.sanity_widget.setVisible(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_widget.setLayout(scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll_widget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.sanity_layout.addWidget(scroll)

        if check_type == 'textures':
            textures_check = TexturesSanityCheck(asset=self._current_asset, log=self._log, auto_fix=False, stop_on_error=True)
            textures_check.check_btn.setVisible(False)
            scroll_layout.addWidget(textures_check)
            textures_check._on_do_check()
        if check_type == 'model':
            model_check = ModelSanityCheck(asset=self._current_asset, log=self._log, auto_fix=False, stop_on_error=True)
            model_check.check_btn.setVisible(False)
            scroll_layout.addWidget(model_check)
            model_check._on_do_check()
        if check_type == 'shading':
            shading_check = ShadingSanityCheck(asset=self._current_asset, log=self._log, auto_fix=False, stop_on_error=True)
            shading_check.check_btn.setVisible(False)
            scroll_layout.addWidget(shading_check)
            shading_check._on_do_check()

        self.stack.setCurrentIndex(0)

        return True


class TexturesSanityCheck(checkgroups.SanityCheckGroup, object):
    def __init__(self, asset, log, auto_fix=False, stop_on_error=False, parent=None):
        super(TexturesSanityCheck, self).__init__(name='Textures', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        self.add_check(assetchecks.ValidTexturesPath(asset=asset, status='working', log=log))
        self.add_check(assetchecks.TexturesFolderIsEmpty(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CleanModelUnknownNodes(asset=asset, status='working', log=log))
        self.add_check(assetchecks.TextureFileSize(asset=asset, status='working', log=log))
    # self.add_check(solstice_assetchecks.TextureFilesLocked(asset=asset, status='working', log=log))


class ModelSanityCheck(checkgroups.SanityCheckGroup, object):
    def __init__(self, asset, log, auto_fix=False, stop_on_error=False, parent=None):
        super(ModelSanityCheck, self).__init__(name='Textures', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        self.add_check(assetchecks.ValidModelPath(asset=asset, status='working', log=log))
        self.add_check(assetchecks.ModelFileIsLocked(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CleanModelUnknownNodes(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CheckModelMainGroup(asset=asset, status='working', log=log))
        self.add_check(assetchecks.ModelHasNoShaders(asset=asset, status='working', log=log))
        self.add_check(assetchecks.RigProxyHiresGroups(asset=asset, status='working', log=log))
        # self.add_check(solstice_assetchecks.ValidTagDataNode(asset=asset, status='working', log=log))
        # self.add_check(solstice_assetchecks.SetupTagDataNode(asset=asset, status='working', log=log))


class ShadingSanityCheck(checkgroups.SanityCheckGroup, object):
    def __init__(self, asset, log, auto_fix=False, stop_on_error=False, parent=None):
        super(ShadingSanityCheck, self).__init__(name='Textures', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        self.add_check(assetchecks.ValidModelPath(asset=asset, status='working', log=log))
        self.add_check(assetchecks.ValidShadingPath(asset=asset, status='working', log=log))
        self.add_check(assetchecks.ModelFileIsLocked(asset=asset, status='working', log=log))
        self.add_check(assetchecks.ShadingFileIsLocked(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CleanModelUnknownNodes(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CleanShadingUnknownNodes(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CheckModelMainGroup(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CheckShadingMainGroup(asset=asset, status='working', log=log))
        self.add_check(assetchecks.CheckShadingShaders(asset=asset, status='working', log=log))


def run():
    SanityCheck().show()
