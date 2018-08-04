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

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_shaderviewer, solstice_sync_dialog, solstice_assetviewer
from solstice_utils import solstice_maya_utils as utils
from solstice_utils import solstice_image as img
from solstice_utils import solstice_python_utils, solstice_shader_utils, solstice_artella_utils, solstice_qt_utils


IGNORE_SHADERS = ['particleCloud1', 'shaderGlow1', 'defaultColorMgtGlobals', 'lambert1']
IGNORE_ATTRS = ['computedFileTextureNamePattern']
SHADER_EXT = 'sshader'


class ShadingNetwork(object):
    def __init__(self):
        super(ShadingNetwork, self).__init__()

    @staticmethod
    def write(shader_dict, file_dir):
        """
        Writes given shader dict to the given JSON file
        :param shader_dict: dict
        :param file_dir: str
        """

        with open(file_dir, 'w') as f:
            json.dump(shader_dict, f, indent=4, sort_keys=True)

    @staticmethod
    def read(file_dir):
        """
        Reads shader info from given JSON file
        :param file_dir: str
        :return: dict
        """

        with open(file_dir, 'r') as f:
            shader_dict = json.load(f)
        return shader_dict

    @classmethod
    def write_network(cls, shaders_path, shaders=None, icon_path=None):
        """
        Writes shader network info to the given path
        :param shaders_path: str, path where we want to store the shader
        :param shaders: list<str>, list of shaders we want to store
        :param icon_path: str, icon we want to show in the shader viewer
        :return: list<str>, list of exported shaders
        """
        if not os.path.exists(shaders_path):
            sp.logger.debug('ShaderLibrary: Shaders Path {0} is not valid! Aborting export!'.format(shaders_path))

        if shaders is None:
            shaders = cmds.ls(materials=True)

        exported_shaders = list()
        for shader in shaders:
            if shader not in IGNORE_SHADERS:
                # Get dict with all the info of the shader
                shader_network = cls.get_shading_network(shader, shader)

                # Store shader icon in base64 format
                shader_network['icon'] = img.image_to_base64(icon_path)

                # Export the shader in the given path and with the proper format
                out_file = os.path.join(shaders_path, shader + '.' + SHADER_EXT)
                sp.logger.debug('Generating Shader {0} in {1}'.format(shader, out_file))

                upload_new_version = True
                # if os.path.isfile(out_file):
                #     temp_file, temp_filename = tempfile.mkstemp()
                #     cls.write(shader_network, temp_filename)
                #     if filecmp.cmp(out_file, temp_filename):
                #         sp.logger.debug('Shader file already exists and have same size. No new shader file will be generated!')
                #         result = solstice_qt_utils.show_question(None, 'New Shader File Version', 'Shader File {} already exists with same file size! Do you want to upload it to Artella anyways?'.format(shader))
                #         if result == QMessageBox.No:
                #             upload_new_version = False
                #     else:
                #         sp.logger.debug('Writing shader file: {}'.format(out_file))
                #         cls.write(shader_network, out_file)
                # else:
                solstice_artella_utils.lock_file(out_file, force=True)
                sp.logger.debug('Writing shader file: {}'.format(out_file))
                cls.write(shader_network, out_file)

                if upload_new_version:
                    sp.logger.debug('Creating new shader version in Artella: {}'.format(out_file))
                    solstice_artella_utils.upload_new_asset_version(out_file, comment='New Shader {} version'.format(shader))
                    solstice_artella_utils.unlock_file(out_file)

                exported_shaders.append(out_file)

        return exported_shaders

    @classmethod
    def load_network(cls, shader_file_path, existing_material=None):
        """
        Loads given shader file and creates a proper shader
        :param shader_file_path: str, JSON shader file
        :param existing_material:
        """

        # Get JSON dict from JSON shader file
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
                cls.create_shader_node(node_type=node_type, as_type=as_type, name=key)

        for key in network_dict:
            if key == 'icon':
                continue
            as_type = network_dict[key]['asType']
            if existing_material is not None and as_type == 'asShader':
                cls._set_attrs(existing_material, network_dict[key])
            else:
                cls._set_attrs(key, network_dict[key])

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
        """
        Function that get all necessary attributes from shading node and stores them in dict
        :param shader_node: str
        :param prefix: str
        :return: dict
        """

        attrs = {'asType': None, 'type': None, 'attr': dict(), 'connection': dict()}
        shader_attrs = cmds.listAttr(shader_node, multi=True)

        # Shader object type
        attrs['type'] = cmds.objectType(shader_node)

        # Shading node type
        attrs['asType'] = solstice_shader_utils.get_shading_node_type(shader_node)
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
    def _set_attrs(cls, shader_node, attrs):
        for attr in attrs['connection']:
            con_node, con_attr = attrs['connection'][attr].split('.')
            try:
                cmds.connectAttr('{0}.{1}'.format(con_node, con_attr), '{0}.{1}'.format(shader_node, attr), force=True)
            except Exception:
                sp.logger.debug('ShaderLibrary: Attribute Connection {0} skipped!'.format(attr))
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


class ShaderWidget(QWidget, object):
    def __init__(self, shader_name, layout='horizontal', parent=None):
        super(ShaderWidget, self).__init__(parent=parent)

        self._name = shader_name

        if layout == 'horizontal':
            main_layout = QHBoxLayout()
        else:
            main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(main_layout)

        if cmds.objExists(shader_name):
            self._shader_swatch = solstice_shader_utils.get_shader_swatch(self._name)
            main_layout.addWidget(self._shader_swatch)

            if layout == 'horizontal':
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
        if layout == 'vertical':
            main_layout.setAlignment(Qt.AlignCenter)
            shader_lbl.setAlignment(Qt.AlignCenter)
            shader_lbl.setStyleSheet('QLabel {background-color: rgba(50, 50, 50, 200); border-radius:5px;}')

    def export(self):
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
            network = ShadingNetwork.write_network(shaders_path=shader_library_path, shaders=[self._name], icon_path=temp_file)
            exported_shaders = network
        except Exception as e:
            sp.logger.debug('Aborting shader export: {0}'.format(str(e)))
            os.remove(temp_file)
            return
        os.remove(temp_file)

        return exported_shaders

    @property
    def name(self):
        return self._name


class ShaderExporter(QDialog, object):

    exportFinished = Signal()

    def __init__(self, shaders, parent=None):
        super(ShaderExporter, self).__init__(parent=parent)

        self._shaders = shaders

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

        self.widgets_to_export = list()
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

            shader_export_widget = ShaderWidget(shader_name=shader, layout='vertical')
            shader_export_widget.setMinimumWidth(100)
            shader_export_widget.setMinimumHeight(100)
            self.widgets_to_export.append(shader_export_widget)

        export_btn.clicked.connect(self._on_export_shaders)

    def _export_shaders(self):

        exported_shaders = list()
        if len(self._shaders) <= 0:
            sp.logger.error('No Shaders To Export. Aborting ....')
            return exported_shaders

        exporter = solstice_sync_dialog.SolsticeShaderExport(shaders=self.widgets_to_export)
        exporter.sync()
        exported_shaders = exporter.exported_shaders

        return exported_shaders

    def _on_export_shaders(self):
        self._export_shaders()
        self.exportFinished.emit()


class ShaderViewerWidget(QWidget, object):

    clicked = Signal()

    def __init__(self, shader_name, parent=None):
        super(ShaderViewerWidget, self).__init__(parent=parent)

        self._name = shader_name
        self._menu = None

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

        self.shader_path = os.path.join(ShaderLibrary.get_shader_library_path(), shader_name+'.'+SHADER_EXT)
        if not os.path.isfile(self.shader_path):
            sp.logger.debug('Shader Data Path {0} for shader {1} is not valid!'.format(self.hader_path, shader_name))
            return

        shader_data = ShadingNetwork.read(self.shader_path)
        shader_icon = shader_data['icon']
        if not shader_icon:
            return
        shader_icon = shader_icon.encode('utf-8')
        shader_btn.setIcon(QPixmap.fromImage(img.base64_to_image(shader_icon)))

        # =================================================================================================

        shader_btn.clicked.connect(self.clicked.emit)

    def contextMenuEvent(self, event):
        self._generate_context_menu()
        if not self._menu:
            return
        self._menu.exec_(event.globalPos())

    def open_shader_in_editor(self):
        solstice_python_utils.open_file(self.shader_path)

    def _generate_context_menu(self):
        self._menu = QMenu(self)
        open_in_editor = self._menu.addAction('Open Shader in external editor')
        self._menu.addAction(open_in_editor)

        open_in_editor.triggered.connect(self.open_shader_in_editor)


class ShaderLibrary(solstice_windows.Window, object):

    name = 'Solstice_ShaderLibrary'
    title = 'Solstice Tools - Shader Manager'
    version = '1.0'
    dock = True

    def __init__(self, name='ShaderManagerWindow', parent=None, **kwargs):

        self._valid_state = True
        self._shader_library_path = self.get_shader_library_path()
        if not os.path.exists(self._shader_library_path):
            result = solstice_qt_utils.show_question(None, 'Shading Library Path not found!', 'Shaders Library Path is not sync! To start using this tool you should sync this folder first. Do you want to do it?')
            if result == QMessageBox.Yes:
                sp.logger.debug('Solstice Shader Library Path not found! Trying to sync through Artella!')
                self.update_shaders_from_artella()
                if not os.path.exists(self._shader_library_path):
                    sp.logger.debug('Solstice Shader not found after sync. Something is wrong, please contact TD!')
                    self._valid_state = False
            else:
                self._valid_state = False

        super(ShaderLibrary, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(ShaderLibrary, self).custom_ui()

        self.set_logo('solstice_shaderlibrary_logo')

        self.main_layout.setAlignment(Qt.AlignTop)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(top_layout)

        top_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

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
        self._sync_shaders_btn = QToolButton()
        self._sync_shaders_btn.setText('Sync Shaders from Artella')
        self._sync_shaders_btn.setMinimumWidth(40)
        self._sync_shaders_btn.setMaximumHeight(40)
        top_layout.addWidget(self._sync_shaders_btn)
        self._open_shaders_path_btn = QToolButton()
        self._open_shaders_path_btn.setText('Open Shaders Library Path')
        self._open_shaders_path_btn.setMinimumWidth(40)
        self._open_shaders_path_btn.setMaximumHeight(40)
        top_layout.addWidget(self._open_shaders_path_btn)

        top_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # ===========================================================================================

        shader_splitter = QSplitter(Qt.Horizontal)
        shader_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(shader_splitter)

        shader_widget = QWidget()
        self.shader_viewer = solstice_shaderviewer.ShaderViewer()
        self.shader_viewer.setAlignment(Qt.AlignTop)
        shader_widget.setLayout(self.shader_viewer)

        self._asset_viewer = solstice_assetviewer.CategorizedAssetViewer(
            item_pressed_callback=self._on_asset_click
        )

        shader_splitter.addWidget(self._asset_viewer)
        shader_splitter.addWidget(shader_widget)

        self._export_sel_btn.clicked.connect(self._export_selected_shaders)
        self._export_all_btn.clicked.connect(self._export_all_shaders)
        self._sync_shaders_btn.clicked.connect(self.update_shaders_from_artella)
        self._open_shaders_path_btn.clicked.connect(self._open_shaders_path)

        if self._valid_state:
            self.update_shader_library()

    def update_shaders_from_artella(self):
        """
        Connects to Artella and synchronize all the content located in the Shader Library path
        """

        solstice_sync_dialog.SolsticeSyncFile(files=[self._shader_library_path]).sync()

    def update_shader_library(self):
        sp.logger.debug('Updating Shaders ...')

        self.shader_viewer.clear()

        for shader_file in os.listdir(self.get_shader_library_path()):
            if not shader_file.endswith('.'+SHADER_EXT):
                continue
            shader_name = os.path.splitext(shader_file)[0]
            # if cmds.objExists(shader_name):
            #     continue
            shader_widget = ShaderViewerWidget(shader_name=shader_name)
            shader_widget.clicked.connect(lambda: self.load_shader(shader_name=shader_name))
            self.shader_viewer.add_widget(shader_widget)

    def load_shader(self, shader_name):
        shader_path = os.path.join(self._shader_library_path, shader_name+'.'+SHADER_EXT)
        if os.path.isfile(shader_path):
            ShadingNetwork.load_network(shader_file_path=shader_path)
        else:
            sp.logger.debug('ShaderLibrary: Shader {0} does not exist! Shader skipped!'.format(shader_path))

    @staticmethod
    def get_shader_library_path():
        """
        Returns path where Solstice shaders JSON files are located
        :return: str
        """

        return os.path.join(sp.get_solstice_assets_path(), 'Scripts', 'PIPELINE', '__working__', 'ShadersLibrary')

    @staticmethod
    def get_asset_shader_file_path(asset):
        """
        Returns shaders JSON file path of the given asset
        If does not ensures that the file already exists
        :param asset:
        :return: str
        """

        asset_shading_path = os.path.join(asset._asset_path, '__working__', 'shading')
        asset_shading_file = os.path.join(asset_shading_path, asset.name + '_SHD.json')

        return asset_shading_file

    @staticmethod
    def export_asset(asset=None, shading_meshes=None, comment='New Shaders version'):
        """
        Export all shaders info for the given asset
        Generates 2 files:
            1) Shader JSON files which will be stored inside Shaders Library Path
            2) Asset Shader Description file which maps the asset geometry to their respective shader
               This file is stored in the asset folder.
        :param asset: SolsticeAsset
        :return: list
        """

        if asset is None:
            sp.logger.debug('Given Asset to export is not valid! Aborting operation ...')
            return

        try:
            asset.open_asset_file(file_type='shading', status='working')
        except Exception:
            sp.logger.debug('Impossible to open Working Shading file for asset: {}'.format(asset.name))
            return

        all_shading_groups = list()
        json_data = dict()
        if shading_meshes:
            for mesh in shading_meshes:
                json_data[mesh] = dict()
                shapes = cmds.listRelatives(mesh, shapes=True, fullPath=True)
                for shape in shapes:
                    json_data[mesh][shape] = dict()
                    shading_groups = cmds.listConnections(shape, type='shadingEngine')
                    for shading_grp in shading_groups:
                        shading_grp_mat = cmds.ls(cmds.listConnections(shading_grp), materials=True)
                        json_data[mesh][shape][shading_grp] = shading_grp_mat
                        all_shading_groups.append(shading_grp)
        else:
            asset_groups = cmds.ls('*_grp', type='transform')
            if len(asset_groups) <= 0:
                return
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
        upload_new_version = True
        asset_shading_file = ShaderLibrary.get_asset_shader_file_path(asset=asset)
        if os.path.isfile(asset_shading_file):
            with open(asset_shading_file, 'r') as f:
                current_data = json.load(f)
            if current_data is not None:
                if current_data != json_data:
                    solstice_artella_utils.lock_file(file_path=asset_shading_file, force=True)
                    with open(asset_shading_file, 'w') as fp:
                        json.dump(json_data, fp)
                else:
                    result = solstice_qt_utils.show_question(None, 'New JSON Shader File Version','Shaders JSON File {} already exists with same file size! Do you want to upload it to Artella anyways?'.format(asset_shading_file))
                    if result == QMessageBox.No:
                        upload_new_version = False
        else:
            with open(asset_shading_file, 'w') as fp:
                json.dump(json_data, fp)

        # Upload new version of JSON shading file if necessary
        if upload_new_version:
            valid_version = solstice_artella_utils.upload_new_asset_version(asset_shading_file, comment=comment)
            if not valid_version:
                solstice_qt_utils.show_info(None, 'New Shaders JSON file version', 'Error while creating new version of JSON shaders version: {} Create it manaully later through Artella!'.format(asset_shading_file))

        # To export shaders file we need to use ShaderLibrary Tool
        # shader_exporter = ShaderExporter(shaders=asset_materials)
        # shaders = shader_exporter._export_shaders()

        if os.path.isfile(asset_shading_file):
            return asset_shading_file

        return ''

    def _export_selected_shaders(self):
        shaders = cmds.ls(sl=True, materials=True)
        exporter = ShaderExporter(shaders=shaders, parent=self)
        exporter.exportFinished.connect(self.update_shader_library)
        exporter.exec_()

    def _export_all_shaders(self):
        shaders = cmds.ls(materials=True)
        exporter = ShaderExporter(shaders=shaders, parent=self)
        exporter.exportFinished.connect(self.update_shader_library)
        exporter.exec_()

    def _open_shaders_path(self):
        solstice_python_utils.open_folder(self.get_shader_library_path())

    def _on_asset_click(self, asset):
        sp.logger.debug('Generating Shading info for asset: {}'.format(asset.name))
        self.export_asset(asset=asset)
        self.update_shader_library()


def run():
    reload(utils)
    reload(solstice_shader_utils)
    reload(solstice_shaderviewer)
    reload(solstice_assetviewer)

    # Check that Artella plugin is loaded and, if not, we loaded it
    solstice_artella_utils.update_artella_paths()
    if not solstice_artella_utils.check_artella_plugin_loaded():
        if not solstice_artella_utils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    sp.update_solstice_project_path()

    ShaderLibrary.run()
