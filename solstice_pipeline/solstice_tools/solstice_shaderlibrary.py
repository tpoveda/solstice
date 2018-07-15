#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shadermanager.py
# by Tomas Poveda
# Tool used to manage all shaders used by all the assets in the short film
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import json

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_shaderviewer, solstice_shader
from solstice_utils import solstice_maya_utils as utils
from solstice_utils import solstice_image as img
from solstice_utils import solstice_shader_utils, solstice_artella_utils

IGNORE_SHADERS = ['particleCloud1', 'shaderGlow1', 'defaultColorMgtGlobals', 'lambert1']
IGNORE_ATTRS = ['computedFileTextureNamePattern']
SHADER_EXT = 'sshader'


class ShaderIO(object):
    def __init__(self):
        pass

    @staticmethod
    def write(dict, file_dir):
        with open(file_dir, 'w') as f:
            json.dump(dict, f, indent=4, sort_keys=True)

    @staticmethod
    def read(file_dir):
        with open(file_dir, 'r') as f:
            shader_dict = json.load(f)
        return shader_dict


class ShadingNetwork(ShaderIO, object):
    def __init__(self):
        super(ShadingNetwork, self).__init__()

    @classmethod
    def write_network(cls, shaders_path, shaders=None, icon_path=None):
        if not os.path.exists(shaders_path):
            sp.logger.debug('ShaderLibrary: Shaders Path {0} is not valid! Aborting export!'.format(shaders_path))

        if shaders is None:
            shaders = cmds.ls(materials=True)

        exported_shaders = list()
        for shader in shaders:
            if shader not in IGNORE_SHADERS:
                shader_network = cls.get_shading_network(shader, shader)
                shader_network['icon'] = img.image_to_base64(icon_path)
                out_file = os.path.join(shaders_path, shader + '.' + SHADER_EXT)
                sp.logger.debug('Generating Shader {0} in {1}'.format(shader, out_file))
                cls.write(shader_network, out_file)
                exported_shaders.append(out_file)

        return exported_shaders

    @classmethod
    def load_network(cls, shader_file_path, existing_material=None):
        network_dict = cls.read(shader_file_path)
        for key in network_dict:
            if key == 'icon':
                continue

            as_type = network_dict[key]['asType']
            node_type = network_dict[key]['type']
            if existing_material is not None and as_type == 'asShader':
                utils.delete_all_incoming_nodes(node=existing_material)
                continue
            elif as_type == 'asShader':
                node = cls.create_shader_node(node_type=node_type, as_type=as_type, name=key)
                nodeSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=key+'SG')
                cmds.connectAttr(node+'.outColor', nodeSG+'.surfaceShader', force=True)
            else:
                node = cls.create_shader_node(node_type=node_type, as_type=as_type, name=key)

        for key in network_dict:
            if key == 'icon':
                continue

            as_type = network_dict[key]['asType']
            if existing_material is not None and as_type == 'asShader':
                cls._set_attrs(existing_material, network_dict[key], as_type)
            else:
                cls._set_attrs(key, network_dict[key], as_type)

        for key in network_dict:
            if key == 'icon':
                continue

            as_type = network_dict[key]['asType']
            if existing_material is not None and as_type == 'asShader':
                continue
            else:
                name = key+'_'
                name = re.sub('(?<=[A-z])[0-9]+', '', name)
                try:
                    cmds.rename(key, name)
                except Exception:
                    sp.logger.debug('ShaderLibrary: Impossible to rename {0} to {1}'.format(key ,name))

    @classmethod
    def create_shader_node(cls, node_type, as_type, name):
        shader_node = None
        if as_type == 'asShader':
            shader_node = cmds.shadingNode(node_type, asShader=True, name=name)
        elif as_type == 'asUtility':
            shader_node = cmds.shadingNode(node_type, asUtility=True, name=name)
        elif as_type == 'asTexture':
            shader_node = cmds.shadingNode(node_type, asTexture=True, name=name)
        return shader_node

    @classmethod
    def get_shading_network(cls, shader_node, prefix):
        prefix_name = shader_node + '_' + prefix
        shader_network = dict()
        shader_network[prefix_name] = cls._attrs_to_dict(shader_node, prefix)
        connected_nodes = cmds.listConnections(shader_node, source=True, destination=False)
        if connected_nodes:
            for n in connected_nodes:
                shader_network.update(cls.get_shading_network(n, prefix))
            return shader_network
        else:
            return shader_network

    @classmethod
    def _attrs_to_dict(cls, shader_node, prefix):
        attrs = {'asType': None, 'type': None, 'attr': dict(), 'connection':dict()}
        shader_attrs = cmds.listAttr(shader_node, multi=True)
        attrs['type'] = cmds.objectType(shader_node)
        attrs['asType'] = cls._get_shading_node_type(shader_node)
        for attr in shader_attrs:
            if not cmds.connectionInfo('{0}.{1}'.format(shader_node, attr), isDestination=True):
                try:
                    value = cmds.getAttr('{0}.{1}'.format(shader_node, attr))
                    if value is not None:
                        if isinstance(value, list):
                            attrs['attr'][attr] = value[0]
                        else:
                            attrs['attr'][attr] = value
                except Exception:
                    sp.logger.debug('ShaderLibrary: Attribute {0} skipped'.format(attr))
                    continue
            else:
                connected_node, connection = cmds.connectionInfo('{0}.{1}'.format(shader_node, attr), sourceFromDestination=True).split('.')
                new_connection_name = connected_node + '_' + prefix + '.' + connection
                attrs['connection'][attr] = new_connection_name

        return attrs

    @classmethod
    def _set_attrs(cls, shader_node, attrs, as_type):
        for attr in attrs['connection']:
            con_node, con_attr = attrs['connection'][attr].split('.')
            try:
                cmds.connectAttr('{0}.{1}'.format(con_node, con_attr), '{0}.{1}'.format(shader_node, attr), force=True)
            except Exception:
                sp.logger.debug('ShaderLibrary: Attribute Conection {0} skipped!'.format(attr))
                continue

        if 'notes' not in attrs['attr'] and cmds.objExists(shader_node) and cmds.attributeQuery('notes', node=shader_node, exists=True):
            cmds.setAttr('{0}.{1}'.format(shader_node, 'notes'), '', type='string')
        for attr in attrs['attr']:
            attr_type = None
            if attr in IGNORE_ATTRS:
                continue
            if attr in attrs['connection']:
                continue
            if isinstance(attrs['attr'][attr], list):
                if len(attrs['attr'][attr]) == 3:
                    attr_type = 'double3'
                elif len(attrs['attr'][attr]) == 2:
                    attr_type = 'double2'
                attribute = attrs['attr'][attr]
                try:
                    cmds.setAttr('{0}.{1}'.format(shader_node, attr), type=attr_type, *attribute)
                except Exception:
                    sp.logger.debug('ShaderLibrary: setAttr {0} skipped!'.format(attr))
                    continue
            elif isinstance(attrs['attr'][attr], basestring):
                if attr == 'notes' and not cmds.attributeQuery('notes', node=shader_node, exists=True):
                    cmds.addAttr(shader_node, longName='notes', dataType='string')
                try:
                    cmds.setAttr('{}.{}'.format(shader_node, attr), attrs['attr'][attr], type='string')
                except Exception:
                    sp.logger.debug('ShaderLibrary: setAttr {0} skipped!'.format(attr))
                    continue
            else:
                try:
                    cmds.setAttr('{}.{}'.format(shader_node, attr), attrs['attr'][attr])
                except:
                    sp.logger.debug('ShaderLibrary: setAttr {0} skipped!'.format(attr))
                    continue

    @staticmethod
    def _get_shading_node_type(shader_node):
        connections = cmds.listConnections(shader_node, source=False, destination=True)
        if 'defaultTextureList1' in connections:
            return 'asTexture'
        if 'defaultShaderList1' in connections:
            return 'asShader'
        if 'defaultRenderUtilityList1' in connections:
            return 'asUtility'


class ShaderWidget(QWidget, object):
    def __init__(self, shader_name, parent=None):
        super(ShaderWidget, self).__init__(parent=parent)

        self._name = shader_name

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(main_layout)

        if cmds.objExists(shader_name):
            self._shader_swatch = solstice_shader_utils.get_shader_swatch(self._name)
            main_layout.addWidget(self._shader_swatch)

            v_div_w = QWidget()
            v_div_l = QVBoxLayout()
            v_div_l.setAlignment(Qt.AlignLeft)
            v_div_l.setContentsMargins(0, 0, 0, 0)
            v_div_l.setSpacing(0)
            v_div_w.setLayout(v_div_l)
            v_div = QFrame()
            v_div.setMinimumHeight(30)
            v_div.setFrameShape(QFrame.VLine)
            v_div.setFrameShadow(QFrame.Sunken)
            v_div_l.addWidget(v_div)
            main_layout.addWidget(v_div_w)

        shader_lbl = QLabel(shader_name)
        main_layout.addWidget(shader_lbl)

        v_div_w = QWidget()
        v_div_l = QVBoxLayout()
        v_div_l.setAlignment(Qt.AlignLeft)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setMinimumHeight(30)
        v_div.setFrameShape(QFrame.VLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        main_layout.addWidget(v_div_w)

        custom_icon_widget = QWidget()
        custom_icon_palette = custom_icon_widget.palette()
        custom_icon_palette.setColor(QPalette.Background, Qt.red)
        custom_icon_widget.setAutoFillBackground(True)
        custom_icon_widget.setPalette(custom_icon_palette)
        custom_icon_layout = QVBoxLayout()
        custom_icon_layout.setContentsMargins(0, 0, 0, 0)
        custom_icon_layout.setSpacing(0)
        custom_icon_widget.setLayout(custom_icon_layout)
        main_layout.addWidget(custom_icon_widget)

        self._custom_icon_btn = QPushButton('Custom Icon')
        self._custom_icon_btn.setMinimumHeight(75)
        self._custom_icon_btn.setMaximumHeight(75)
        self._custom_icon_btn.setMinimumWidth(75)
        self._custom_icon_btn.setMaximumWidth(75)
        custom_icon_layout.addWidget(self._custom_icon_btn)

        auto_gen_icon = QPushButton('Auto Icon')
        auto_gen_icon.setMaximumHeight(20)
        custom_icon_layout.addWidget(auto_gen_icon)


    def export(self):

        #TODO: Check if a custom icon is setted up and export the correct pixmap depending on it

        shader_library_path = ShaderLibrary.get_shader_library_path()
        if not os.path.exists(shader_library_path):
            sp.logger.debug('Shader Library {0} not found! Aborting shader export! Contact TD!'.format(shader_library_path))
            return

        if not cmds.objExists(self._name):
            sp.logger.debug('Shader {0} does not exists in the scene! Aborting shader export!'.format(self._name))
            return

        px = QPixmap(QSize(100, 100))
        self._shader_swatch.render(px)
        temp_file = os.path.join(ShaderLibrary.get_shader_library_path(), 'tmp.png')
        px.save(temp_file)
        try:
            ShadingNetwork.write_network(shaders_path=shader_library_path, shaders=[self._name], icon_path=temp_file)
        except Exception as e:
            sp.logger.debug('Aborting shader export: {0}'.format(str(e)))
            os.remove(temp_file)
            return
        os.remove(temp_file)



    @property
    def name(self):
        return self._name


class ShaderExporter(QDialog, object):
    def __init__(self, shaders, parent=None):
        super(ShaderExporter, self).__init__(parent=parent)

        self.setWindowTitle('Solstice Tools - Shader Exporter')
        self.setMinimumWidth(370)
        self.setMinimumHeight(350)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self._shaders_list = QListWidget()
        self.main_layout.addWidget(self._shaders_list)

        export_btn = QPushButton('Export')
        self.main_layout.addWidget(export_btn)

        for shader in shaders:
            if shader in IGNORE_SHADERS:
                continue
            shader_item = QListWidgetItem()
            shader_widget = ShaderWidget(shader_name=shader)
            shader_item.setSizeHint(QSize(120, 120))
            shader_widget.setMinimumWidth(100)
            shader_widget.setMinimumHeight(100)
            self._shaders_list.addItem(shader_item)
            self._shaders_list.setItemWidget(shader_item, shader_widget)

        export_btn.clicked.connect(self._export_shaders)

    def _export_shaders(self):
        exported_shaders = list()
        for i in range(self._shaders_list.count()):
            item = self._shaders_list.item(i)
            item_widget = self._shaders_list.itemWidget(item)
            exported_shader = item_widget.export()
            exported_shaders.append(exported_shader)

        return exported_shaders


class ShaderViewerWidget(QWidget, object):
    def __init__(self, shader_name, parent=None):
        super(ShaderViewerWidget, self).__init__(parent=parent)

        self._name = shader_name

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        main_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        shader_btn = QPushButton()
        shader_btn.setMinimumWidth(110)
        shader_btn.setMaximumHeight(110)
        shader_btn.setMaximumWidth(110)
        shader_btn.setMinimumHeight(110)
        shader_btn.setIconSize(QSize(100, 100))
        shader_lbl = QLabel(self._name)
        shader_lbl.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        main_layout.addLayout(button_layout)
        button_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        button_layout.addWidget(shader_btn)
        button_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        main_layout.addWidget(shader_lbl)

        # =================================================================================================

        shader_path = os.path.join(ShaderLibrary.get_shader_library_path(), shader_name+'.'+SHADER_EXT)
        if not os.path.isfile(shader_path):
            sp.logger.debug('Shader Data Path {0} for shader {1} is not valid!'.format(shader_path, shader_name))
            return

        shader_data = ShaderIO.read(shader_path)
        shader_icon = shader_data['icon']
        if not shader_icon:
            return
        shader_icon = shader_icon.encode('utf-8')
        shader_btn.setIcon(QPixmap.fromImage(img.base64_to_image(shader_icon)))


class ShaderLibrary(solstice_windows.Window, object):

    name = 'Shader Library'
    title = 'Solstice Tools - Shader Manager'
    version = '1.0'
    dock = True

    def __init__(self, name='ShaderManagerWindow', parent=None, **kwargs):

        self._shader_library_path = self.get_shader_library_path()
        if not os.path.exists(self._shader_library_path):
            print('PATH DOES NOT EXISTS!')
            # TODO: Add MessageBox and asks the user if the want to download
            # TODO: from Artella server the shaders folder

        super(ShaderLibrary, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(ShaderLibrary, self).custom_ui()

        self.set_logo('solstice_shaderlibrary_logo')

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(top_layout)
        top_layout.addItem(QSpacerItem(50, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self._export_asset_btn = QToolButton()
        self._export_asset_btn.setText('Export Selected Asset Materials')
        self._export_asset_btn.setMinimumHeight(40)
        self._export_asset_btn.setMaximumHeight(40)
        top_layout.addWidget(self._export_asset_btn)
        self._export_sel_btn = QToolButton()
        self._export_sel_btn.setText('Export Selected Materials')
        self._export_sel_btn.setMinimumWidth(40)
        self._export_sel_btn.setMinimumHeight(40)
        top_layout.addWidget(self._export_sel_btn)
        self._export_all_btn = QToolButton()
        self._export_all_btn.setText('Export All Scene Materials')
        self._export_all_btn.setMinimumWidth(40)
        self._export_all_btn.setMaximumHeight(40)
        top_layout.addWidget(self._export_all_btn)
        top_layout.addItem(QSpacerItem(50, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.shader_viewer = solstice_shaderviewer.ShaderViewer()
        self.main_layout.addLayout(self.shader_viewer)

        # self._export_asset_btn.clicked.connect(self._export_selected_asset)
        self._export_sel_btn.clicked.connect(self._export_selected_shaders)
        self._export_all_btn.clicked.connect(self._export_all_shaders)

        self.update_shader_library()

    def update_shader_library(self):
        sp.logger.debug('Updating Shaders ...')
        for shader_file in os.listdir(self.get_shader_library_path()):
            if not shader_file.endswith('.'+SHADER_EXT):
                continue
            shader_name = os.path.splitext(shader_file)[0]
            # if cmds.objExists(shader_name):
            #     continue
            shader_widget = ShaderViewerWidget(shader_name=shader_name)
            self.shader_viewer.add_widget(shader_widget)

    def load_shader(self, shader_name):
        shader_path = os.path.join(self._shader_library_path, shader_name+'.'+SHADER_EXT)
        if os.path.isfile(shader_path):
            ShadingNetwork.load_network(shader_file_path=shader_path)
        else:
            sp.logger.debug('ShaderLibrary: Shader {0} does not exist! Shader skipped!'.format(shader_path))

    @staticmethod
    def get_shader_library_path():
        return os.path.join(sp.get_solstice_assets_path(), 'Scripts', 'ST_ShaderLibrary', '__working__')

    @staticmethod
    def export_asset(asset=None):
        asset_groups = cmds.ls('*_grp', type='transform')
        if len(asset_groups) <= 0:
            # sp.logger.debug('Asset {} has no valid groups'.format(asset.name()))
            # sp.logger.debug('Asset {} has no valid groups'.format(asset.name()))
            return

        all_shading_groups = list()
        json_data = dict()
        for grp in asset_groups:
            json_data[grp] = dict()
            children = cmds.listRelatives(grp, type='transform', allDescendents=True, fullPath=True)
            for child in children:
                child_shapes = cmds.listRelatives(child, shapes=True, fullPath=True)
                for shape in child_shapes:
                    json_data[grp][shape] = dict()
                    shading_groups = cmds.listConnections(shape, type='shadingEngine')
                    for shading_grp in shading_groups:
                        shading_grp_mat = cmds.ls(cmds.listConnections(shading_grp), materials=True)
                        json_data[grp][shape][shading_grp] = shading_grp_mat
                        all_shading_groups.append(shading_grp)

        asset_materials = list(set(cmds.ls(cmds.listConnections(all_shading_groups), materials=True)))

        # Generate JSON shading file for asset
        asset_shading_path = os.path.join(asset._asset_path, '__working__', 'shading', asset.name+'_SHD')
        asset_shading_file = os.path.join(asset_shading_path, asset.name+'.json')
        if os.path.exists(asset_shading_path):
            with open(asset_shading_file, 'w') as fp:
                json.dump(json_data, fp)

        shader_exporter = ShaderExporter(shaders=asset_materials)
        shaders = shader_exporter._export_shaders()

        if os.path.isfile(asset_shading_file):
            return shaders, asset_shading_file

        return [shaders, '']




    # def _export_selected_asset(self):
    #     shaders = list()
    #
    #     objs = cmds.ls(sl=True)
    #     if len(objs) <= 0:
    #         cmds.warning('Select asset before export shaders please!')
    #         return
    #
    #     obj = objs[0]
    #     if not cmds.objExists(obj) or not obj.endswith('_grp'):
    #         cmds.warning('Select asset is not valid. Please select the main group of the asset in the shading file')
    #
    #     children = cmds.listRelatives(type='transform', allDescendents=True, fullPath=True)
    #     all_shading_groups = list()
    #     for child in children:
    #         child_shapes = cmds.listRelatives(child, shapes=True, fullPath=True)
    #         for shape in child_shapes:
    #             shading_groups = cmds.listConnections(shape, type='shadingEngine')
    #             for shading_grp in shading_groups:
    #                 all_shading_groups.append(shading_grp)
    #     all_shading_groups = list(set(all_shading_groups))
    #
    #     asset_shaders = list(set(cmds.ls(cmds.listConnections(all_shading_groups), materials=True)))

    def _export_selected_shaders(self):
        shaders = cmds.ls(sl=True, materials=True)
        ShaderExporter(shaders=shaders, parent=self).exec_()

    def _export_all_shaders(self):
        shaders = cmds.ls(materials=True)
        ShaderExporter(shaders=shaders, parent=self).exec_()
        pass


# ============================================================================================================

# if not 'shader_library_window' in globals():
shader_library_window = None


def shader_library_window_closed(object=None):
    global shader_library_window
    if shader_library_window is not None:
        shader_library_window.cleanup()
        shader_library_window.parent().setParent(None)
        shader_library_window.parent().deleteLater()
        shader_library_window = None


def shader_library_window_destroyed(object=None):
    global shader_library_window
    shader_library_window = None


def run(restore=False):
    reload(utils)
    reload(solstice_shader_utils)
    reload(solstice_shaderviewer)
    reload(solstice_shader)

    # Check that Artella plugin is loaded and, if not, we loaded it
    solstice_artella_utils.update_artella_paths()
    if not solstice_artella_utils.check_artella_plugin_loaded():
        if not solstice_artella_utils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    sp.update_solstice_project_path()

    global shader_library_window
    if shader_library_window is None:
        shader_library_window = ShaderLibrary()
        shader_library_window.destroyed.connect(shader_library_window_destroyed)
        shader_library_window.setProperty('saveWindowPref', True)

    if restore:
        parent = OpenMayaUI.MQtUtil.getCurrentParent()
        mixin_ptr = OpenMayaUI.MQtUtil.findControl(shader_library_window.objectName())
        OpenMayaUI.MQtUtil.addWidgetToMayaLayout(long(mixin_ptr), long(parent))
    else:
        # shader_library_window.show(dockable=ShaderLibrary.dock, save=True, closeCallback='from solstice_tools import solstice_shaderlibrary\nsolstice_shaderlibrary.shader_library_window_closed()', uiScript='from solstice_tools import solstice_shaderlibrary\nsolstice_shaderlibrary.run(restore=True)')
        shader_library_window.show(dockable=ShaderLibrary.dock, save=True, closeCallback='from solstice_tools import solstice_shaderlibrary\nsolstice_shaderlibrary.shader_library_window_closed()')

    shader_library_window.window().raise_()
    shader_library_window.raise_()
    shader_library_window.isActiveWindow()

    return shader_library_window
