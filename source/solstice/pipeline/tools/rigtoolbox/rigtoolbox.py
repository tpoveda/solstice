#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Collection of tools for rigging
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import window, splitters, buttons, stack, accordion
from solstice.pipeline.utils import rigutils


class BaseRigToolBoxWidget(QFrame, object):

    emitInfo = Signal(str)
    emitWarning = Signal(str)
    emitError = Signal(str, object)

    def __init__(self, title, parent=None):
        super(BaseRigToolBoxWidget, self).__init__(parent=parent)

        self._title = title

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

    @property
    def title(self):
        return self._title


class GenericToolbox(BaseRigToolBoxWidget, object):
    def __init__(self, parent=None):
        super(GenericToolbox, self).__init__('Generic', parent)


class CharacterRigToolbox(BaseRigToolBoxWidget, object):
    def __init__(self, parent=None):
        super(CharacterRigToolbox, self).__init__('Character', parent)


class PropsRigToolbox(BaseRigToolBoxWidget, object):
    def __init__(self, parent=None):
        super(PropsRigToolbox, self).__init__('Props', parent)

        self.main_layout.setAlignment(Qt.AlignTop)

        self.accordion = accordion.AccordionWidget(parent=self)
        self.accordion.rollout_style = accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.accordion)

        base_prop_rig = QWidget()
        base_prop_asset_rig_lyt = QHBoxLayout()
        base_prop_rig.setLayout(base_prop_asset_rig_lyt)

        basic_group_btn = QPushButton('Create Basic Rig')
        basic_group_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        base_prop_asset_rig_lyt.addWidget(basic_group_btn)
        self.accordion.add_item('Basic Prop Asset Rig', base_prop_rig)
        base_prop_asset_rig_lyt.addWidget(splitters.get_horizontal_separator_widget())

        reduction_layout = QHBoxLayout()
        proxy_lbl = QLabel('Proxy Reduction: ')
        proxy_reduction = QSpinBox()
        proxy_reduction.setValue(80)
        proxy_reduction.setMinimum(50)
        proxy_reduction.setMaximum(100)
        reduction_layout.addWidget(proxy_lbl)
        reduction_layout.addWidget(proxy_reduction)
        base_prop_asset_rig_lyt.addLayout(reduction_layout)

        # =========================================================================================================

        update_meshes_widget = QWidget()
        update_meshes_layout = QHBoxLayout()
        update_meshes_widget.setLayout(update_meshes_layout)

        update_meshes_btn = QPushButton('Update Model Meshes')
        update_meshes_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        update_meshes_layout.addWidget(update_meshes_btn)
        self.accordion.add_item('Update Meshes', update_meshes_widget)

        # =========================================================================================================

        check_shaders_widget = QWidget()
        check_shaders_layout = QHBoxLayout()
        check_shaders_widget.setLayout(check_shaders_layout)

        check_shaders_name_btn = QPushButton('Check Shader Names')
        check_shaders_name_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        check_shaders_layout.addWidget(check_shaders_name_btn)
        check_shaders_layout.addWidget(splitters.get_horizontal_separator_widget())
        update_shaders_name_btn = QPushButton('Update Shader Names')
        update_shaders_name_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        check_shaders_layout.addWidget(update_shaders_name_btn)

        self.accordion.add_item('Check Shaders', check_shaders_widget)

        # =========================================================================================================

        basic_group_btn.clicked.connect(lambda: rigutils.create_basic_asset_rig(reduction=proxy_reduction.value()))
        update_meshes_btn.clicked.connect(lambda: rigutils.update_model_meshes())
        check_shaders_name_btn.clicked.connect(lambda: rigutils.check_shaders_nomenclature())
        update_shaders_name_btn.clicked.connect(lambda: rigutils.rename_shaders())


class RigToolBoxMenu(QFrame, object):
    def __init__(self, parent=None):
        super(RigToolBoxMenu, self).__init__(parent=parent)

        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet('background-color: rgb(50, 50, 50);')

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.title_lbl = QLabel()
        self.left_arrow = buttons.IconButton(icon_name='left_arrow')
        self.right_arrow = buttons.IconButton(icon_name='right_arrow')
        main_layout.addWidget(self.left_arrow)
        main_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        main_layout.addWidget(self.title_lbl)
        main_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        main_layout.addWidget(self.right_arrow)


class RigToolBoxWidget(QFrame, object):
    def __init__(self, parent=None):
        super(RigToolBoxWidget, self).__init__(parent=parent)

        self._toolbox_window = parent
        self.ui()

    @property
    def title(self):
        return self._title

    def ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.slide_widget = stack.SlidingStackedWidget(parent=self)
        self.main_layout.addWidget(self.slide_widget)
        self.toolbox_menu = RigToolBoxMenu(parent=self)
        self.main_layout.addWidget(self.toolbox_menu)

        self.generic = GenericToolbox(parent=self)
        self.character = CharacterRigToolbox(parent=self)
        self.props = PropsRigToolbox(parent=self)
        for w in [self.generic, self.character, self.props]:
            self.slide_widget.addWidget(w)
        self.toolbox_menu.title_lbl.setText(self.generic.title)

        self.toolbox_menu.right_arrow.clicked.connect(self._on_next_widget)
        self.toolbox_menu.left_arrow.clicked.connect(self._on_prev_widget)

    def _on_next_widget(self):
        self.slide_widget.slide_in_next()
        self.toolbox_menu.title_lbl.setText(self.slide_widget.current_widget.title)

    def _on_prev_widget(self):
        self.slide_widget.slide_in_prev()
        self.toolbox_menu.title_lbl.setText(self.slide_widget.current_widget.title)


class SolsticeRigToolbox(window.Window, object):

    name = 'Solstice_RigToolbox'
    title = 'Solstice Tools - Rig ToolBox'
    version = '1.0'

    def __init__(self):
        super(SolsticeRigToolbox, self).__init__()

    def custom_ui(self):
        super(SolsticeRigToolbox, self).custom_ui()

        self.resize(600, 550)

        self.toolbow_widget = RigToolBoxWidget(parent=self)
        self.main_layout.addWidget(self.toolbow_widget)

def run():
    win = SolsticeRigToolbox().show()
