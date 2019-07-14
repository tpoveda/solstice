#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used to show assets related with Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys
import weakref
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import messagehandler, stack
from solstice.pipeline.utils import decorators, qtutils, outliner as utils
from solstice.pipeline.resources import resource

if sp.is_maya():
    import maya.cmds as cmds
    import maya.OpenMaya as OpenMaya
    from solstice.pipeline.utils import mayautils
    undo_decorator = mayautils.undo
else:
    undo_decorator = decorators.empty


global solstice_outliner_window
try:
    # We do this to remove callbacks when we reload the module
    # Only during DEV
    solstice_outliner_window.remove_callbacks()
except Exception:
    pass


class OutlinerAssetItem(utils.OutlinerAssetItem, object):
    viewToggled = Signal(QObject, bool)
    viewSolo = Signal(QObject, bool)

    def __init__(self, asset, parent=None):
        super(OutlinerAssetItem, self).__init__(asset=asset, parent=parent)

    def get_display_widget(self):
        return utils.AssetDisplayButtons()

    def add_asset_attributes_change_callback(self):
        obj = self.asset.get_mobject()
        vis_callback = OpenMaya.MNodeMessage.addAttributeChangedCallback(obj, partial(self._update_asset_attributes))
        return vis_callback

    def _update_asset_attributes(self, msg, plug, otherplug, *client_data):

        if self.block_callbacks is False:
            if msg & OpenMaya.MNodeMessage.kAttributeSet:
                if 'visibility' in plug.name():
                    self.asset_buttons.view_btn.setChecked(plug.asBool())
                elif 'type' in plug.name():
                    model_widget = self.get_file_widget(category='model')
                    if model_widget is None:
                        sys.solstice.logger.warning('Impossible to update type attribute because model wigdet is available!')
                        return
                    model_widget.model_buttons.proxy_hires_cbx.setCurrentIndex(plug.asInt())

    def create_menu(self, menu):
        replace_menu = QMenu('Replace by', self)
        menu.addMenu(replace_menu)
        replace_abc = replace_menu.addAction('Alembic')
        replace_rig = replace_menu.addAction('Rig')
        replace_standin = replace_menu.addAction('Standin')
        remove_act = menu.addAction('Delete')
        menu.addSeparator()
        sync_shaders_act = menu.addAction('Sync Shaders')
        unload_shaders_act = menu.addAction('Unload Shaders')

        replace_abc.triggered.connect(self._on_replace_alembic)
        replace_rig.triggered.connect(self._on_replace_rig)
        sync_shaders_act.triggered.connect(self._on_sync_shaders)
        unload_shaders_act.triggered.connect(self._on_unload_shaders)

    def is_rig(self):
        """
        Returns whether current asset is a rig or not
        :return: bool
        """

        valid_tag_data = False
        main_group_connections = cmds.listConnections(self.asset.node, source=True)
        for connection in main_group_connections:
            attrs = cmds.listAttr(connection, userDefined=True)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        return valid_tag_data

    def is_alembic(self):
        """
        Returns whether current asset is an alembic or not
        :return: bool
        """

        valid_tag_data = False
        main_group_connections = cmds.listConnections(self.asset.node, source=True)
        for connection in main_group_connections:
            attrs = cmds.listAttr(connection, userDefined=True)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_info':
                        valid_tag_data = True
                        break

        return valid_tag_data

    def is_standin(self):
        """
        Returns whether current asset is an standin or not
        :return: bool
        """

        pass

    @undo_decorator
    def _on_replace_alembic(self):
        abc_file = self.asset.get_alembic_files()
        is_referenced = sys.solstice.dcc.node_is_referenced(self.asset.node)
        if is_referenced:
            if self.is_rig():
                main_group_connections = cmds.listConnections(self.asset.node, source=True)
                for connection in main_group_connections:
                    attrs = cmds.listAttr(connection, userDefined=True)
                    if attrs and type(attrs) == list:
                        if not 'root_ctrl' in attrs:
                            sys.solstice.logger.warning('Asset Rig is not ready for replace functionality yet!')
                            return
                        print('come onnnn')

                # ref_node = sys.solstice.dcc.reference_node(self.asset.node)
                # if not ref_node:
                #     return
                # sys.solstice.dcc.unload_reference(ref_node)
            elif self.is_standin():
                pass
            else:
                sys.solstice.logger.warning('Impossible to replace {} by Alembic!'.format(self.name))
        else:
            sys.solstice.logger.warning('Imported asset cannot be replaced!')

        # if self.asset.node != hires_group:
        #     is_referenced = cmds.referenceQuery(asset.node, isNodeReferenced=True)
        #     if is_referenced:
        #         namespace = cmds.referenceQuery(asset.node, namespace=True)
        #         if not namespace or not namespace.startswith(':'):
        #             sys.solstice.logger.error('Node {} has not a valid namespace!. Please contact TD!'.format(asset.node))
        #             continue
        #         else:
        #             namespace = namespace[1:] + ':'

    def _on_replace_rig(self):
        is_referenced = sys.solstice.dcc.node_is_referenced(self.asset.node)
        if not is_referenced:
            valid_refs = True
            children = sys.solstice.dcc.node_children(self.asset.node, all_hierarchy=False, full_path=True)
            for child in children:
                is_child_ref = sys.solstice.dcc.node_is_referenced(child)
                if not is_child_ref:
                    valid_refs = False
                    break
            if not valid_refs:
                sys.solstice.logger.warning('Impossible to replace {} by rig file ...'.format(self.asset.node))
                return
            rig_ref = self.asset.reference_asset_file('rig')
            print(rig_ref)

    def _on_sync_shaders(self):
        self.asset.sync_shaders()

    def _on_unload_shaders(self):
        self.asset.unload_shaders()


class OutlinerModelItem(utils.OutlinerFileItem, object):

    proxyHiresToggled = Signal(QObject, int)

    def __init__(self, parent=None):
        super(OutlinerModelItem, self).__init__(category='model', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return resource.pixmap('cube', category='icons').scaled(18, 18, Qt.KeepAspectRatio)

    def custom_ui(self):
        super(OutlinerModelItem, self).custom_ui()

        self.model_buttons = ModelDisplayButtons()
        self.item_layout.addWidget(self.model_buttons, 0, 3, 1, 1)

    # def setup_signals(self):
    #     self.model_buttons.proxy_hires_cbx.currentIndexChanged.connect(partial(self.proxyHiresToggled.emit, self))


class OutlinerShadingItem(utils.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerShadingItem, self).__init__(category='shading', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return  resource.pixmap('shader', category='icons').scaled(18, 18, Qt.KeepAspectRatio)


class OutlinerGroomItem(utils.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerGroomItem, self).__init__(category='groom', parent=parent)


class OutlinerArtellaItem(utils.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerArtellaItem, self).__init__(category='artella', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return resource.pixmap('artella', category='icons').scaled(18, 18, Qt.KeepAspectRatio)


class ModelDisplayButtons(utils.DisplayButtonsWidget, object):
    def __init__(self, parent=None):
        super(ModelDisplayButtons, self).__init__(parent=parent)

    def custom_ui(self):
        self.setMinimumWidth(25)

        self.proxy_hires_cbx = QComboBox()
        self.proxy_hires_cbx.addItem('proxy')
        self.proxy_hires_cbx.addItem('hires')
        self.proxy_hires_cbx.addItem('both')
        self.main_layout.addWidget(self.proxy_hires_cbx)


class ArtellaDisplayButtons(utils.DisplayButtonsWidget, object):
    def __init__(self, parent=None):
        super(ArtellaDisplayButtons, self).__init__(parent=parent)

    def custom_ui(self):
        self.setMinimumWidth(25)


class SolsticeBaseOutliner(utils.BaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeBaseOutliner, self).__init__(parent=parent)

    @staticmethod
    def get_file_widget_by_category(category, parent=None):
        if category == 'model':
            file_widget = OutlinerModelItem(parent=parent)
        elif category == 'shading':
            file_widget = OutlinerShadingItem(parent=parent)
        elif category == 'groom':
            file_widget = OutlinerGroomItem(parent=parent)
        elif category == 'artella':
            file_widget = OutlinerArtellaItem(parent=parent)
        else:
            return None

        return file_widget

    def init_ui(self):
        allowed_types = self.allowed_types()
        assets = sp.get_assets(allowed_types=allowed_types)
        for asset in assets:
            asset_widget = OutlinerAssetItem(asset)
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()

            asset_widget.clicked.connect(self._on_item_clicked)
            asset_widget.viewToggled.connect(self._on_toggle_view)
            self.callbacks.append(mayautils.MCallbackIdWrapper(asset_widget.add_asset_attributes_change_callback()))

            asset_files = asset.get_asset_files()
            asset_files['artella'] = None
            for cat, file_path in asset_files.items():
                file_widget = self.get_file_widget_by_category(category=cat, parent=asset_widget)
                if file_widget is not None:
                    asset_widget.add_child(file_widget, category=cat)
                    self.widget_tree[asset_widget].append(file_widget)
                    if cat == 'model':
                        file_widget.proxyHiresToggled.connect(self._on_toggle_proxy_hires)
                    elif cat == 'shading':
                        pass
                    elif cat == 'groom':
                        pass
                    elif cat == 'artella':
                        pass

    def _on_toggle_view(self, widget, state):
        node_name = widget.asset.node
        if cmds.objExists(node_name):
            main_control = widget.asset.get_main_control()
            if main_control:
                if not cmds.objExists(main_control):
                    return
            # if not main_control or not cmds.objExists(main_control):
            #     if state:
            #
            #     return
            if state is True:
                cmds.showHidden(node_name)
            else:
                cmds.hide(node_name)

    def _on_toggle_proxy_hires(self, widget, item_index):
        node_name = widget.parent.asset.node
        if cmds.objExists(node_name):
            if cmds.attributeQuery('type', node=node_name, exists=True):
                widget.parent.block_callbacks = True
                try:
                    cmds.setAttr('{}.type'.format(node_name), item_index)
                except Exception:
                    widget.parent.block_callbacks = False
                widget.parent.block_callbacks = False


class SolsticeAssetsOutliner(SolsticeBaseOutliner, object):

    def __init__(self, parent=None):
        super(SolsticeAssetsOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['prop']

    def add_callbacks(self):
        pass
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('NameChanged', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneOpened', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneImported', self._on_refresh_outliner)))
        # # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Undo', self._on_refresh_outliner)))
        # # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Redo', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MDGMessage.addNodeRemovedCallback(self._on_refresh_outliner)))

class SolsticeCharactersOutliner(SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCharactersOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['character']


class SolsticeLightsOutliner(SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeLightsOutliner, self).__init__(parent=parent)


class SolsticeCamerasOutliner(SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCamerasOutliner, self).__init__(parent=parent)


class SolsticeFXOutliner(SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeFXOutliner, self).__init__(parent=parent)


class SolsticeOutlinerSettings(QWidget, object):

    settingsSaved = Signal()

    def __init__(self, parent=None):
        super(SolsticeOutlinerSettings, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.save_btn = QPushButton('Save')
        self.save_btn.setIcon(resource.icon('save'))
        self.main_layout.addWidget(self.save_btn)

    def setup_signals(self):
        self.save_btn.clicked.connect(self.settingsSaved.emit)


class SolsticeTabs(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeTabs, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.assets_outliner = SolsticeAssetsOutliner()
        self.characters_outliner = SolsticeCharactersOutliner()
        self.lights_outliner = SolsticeLightsOutliner()
        self.fx_outliner = SolsticeFXOutliner()
        self.cameras_outliner = SolsticeCamerasOutliner()

        self.tab_widget.addTab(self.assets_outliner, 'Assets')
        self.tab_widget.addTab(self.characters_outliner, 'Characters')
        self.tab_widget.addTab(self.lights_outliner, 'Lights')
        self.tab_widget.addTab(self.fx_outliner, 'FX')
        self.tab_widget.addTab(self.cameras_outliner, 'Cameras')

    def setup_signals(self):
        pass

    def get_count(self):
        return self.tab_widget.count()

    def get_widget(self, index):
        return self.tab_widget.widget(index)


class SolsticeOutliner(QWidget, object):

    name = 'SolsticeOutliner'
    title = 'Solstice Tools - Solstice Outliner'
    version = '1.2'

    instances = list()

    def __init__(self, parent=mayautils.get_maya_window()):
        super(SolsticeOutliner, self).__init__(parent=parent)

        SolsticeOutliner._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        cmds.select(clear=True)

        self.io = messagehandler.MessageHandler()

        self.custom_ui()
        self.init_ui()
        self.setup_signals()

        global solstice_outliner_window
        solstice_outliner_window = self

    @staticmethod
    def _delete_instances():
        for ins in SolsticeOutliner.instances:
            try:
                ins.remove_callbacks()
                ins.setParent(None)
                ins.deleteLater()
            except Exception:
                pass

            SolsticeOutliner.instances.remove(ins)
            del ins

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.parent().layout().addLayout(self.main_layout)

        self.toolbar = QToolBar()
        self.setup_toolbar()
        self.main_layout.addWidget(self.toolbar)

        self.stack = stack.SlidingStackedWidget(self)
        self.main_layout.addWidget(self.stack)

        self.tabs = SolsticeTabs(self)
        self.settingswidget = SolsticeOutlinerSettings()

        self.stack.addWidget(self.tabs)
        self.stack.addWidget(self.settingswidget)

    def setup_signals(self):
        self.settingswidget.settingsSaved.connect(self.open_tabs)

    def setup_toolbar(self):
        load_scene_shaders_action = QToolButton(self)
        load_scene_shaders_action.setText('Load Shaders')
        load_scene_shaders_action.setToolTip('Load and Apply All Scene Shaders')
        load_scene_shaders_action.setStatusTip('Load and Apply All Scene Shaders')
        load_scene_shaders_action.setIcon(resource.icon('apply_shaders'))
        load_scene_shaders_action.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        unload_scene_shaders_action = QToolButton(self)
        unload_scene_shaders_action.setText('Unload Shaders')
        unload_scene_shaders_action.setToolTip('Unload All Scene Shaders')
        unload_scene_shaders_action.setStatusTip('Unload All Scene Shaders')
        unload_scene_shaders_action.setIcon(resource.icon('unload_shaders'))
        unload_scene_shaders_action.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        update_refs_action = QToolButton(self)
        update_refs_action.setText('Sync Assets')
        update_refs_action.setToolTip('Updates all asset references to the latest published version')
        update_refs_action.setStatusTip('Updates all asset references to the latest published version')
        update_refs_action.setIcon(resource.icon('download'))
        update_refs_action.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        settings_action = QToolButton(self)
        settings_action.setText('Settings')
        settings_action.setToolTip('Outliner Settings')
        settings_action.setStatusTip('Outliner Settings')
        settings_action.setIcon(resource.icon('settings'))
        settings_action.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.toolbar.addWidget(load_scene_shaders_action)
        self.toolbar.addWidget(unload_scene_shaders_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(update_refs_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(settings_action)

        load_scene_shaders_action.clicked.connect(sp.load_shaders)
        unload_scene_shaders_action.clicked.connect(sp.unload_shaders)
        settings_action.clicked.connect(self.open_settings)

    def init_ui(self):
        for outliner in self.get_outliner_widgets():
            outliner.init_ui()

    def add_callbacks(self):
        for outliner in self.get_outliner_widgets():
            outliner.add_callbacks()

    def remove_callbacks(self):
        for outliner in self.get_outliner_widgets():
            outliner.remove_callbacks()

    def refresh_outliner(self):
        for outliner in self.get_outliner_widgets():
            outliner.refresh_outliner()

    def open_tabs(self):
        self.stack.slide_in_index(0)

    def open_settings(self):
        self.stack.slide_in_index(1)

    def closeEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def hideEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def deleteLater(self):
        self.remove_callbacks()
        super(SolsticeOutliner, self).deleteLater()

    def get_outliner_widgets(self):
        outliner_widgets = list()
        for i in range(self.tabs.get_count()):
            outliner_widgets.append(self.tabs.get_widget(i))

        return outliner_widgets

    def run(self):
        self.add_callbacks()
        return self


def run():
    qtutils.dock_window(SolsticeOutliner, min_width=350)
