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
import traceback
from functools import partial

import maya.cmds as cmds

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_shaderviewer, solstice_sync_dialog, solstice_assetviewer
from solstice_utils import solstice_maya_utils as utils
from solstice_utils import solstice_image as img
from solstice_utils import solstice_python_utils, solstice_shader_utils, solstice_artella_utils, solstice_qt_utils
from resources import solstice_resource


IGNORE_SHADERS = ['particleCloud1', 'shaderGlow1', 'defaultColorMgtGlobals', 'lambert1']
IGNORE_ATTRS = ['computedFileTextureNamePattern']
SHADER_EXT = 'sshader'


class SolsticeShaderExportSplash(QSplashScreen, object):
    def __init__(self, *args, **kwargs):
        super(SolsticeShaderExportSplash, self).__init__(*args, **kwargs)

        self.mousePressEvent = self.MousePressEvent
        self._canceled = False

    def MousePressEvent(self, event):
        pass


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
    def write_network(cls, shaders_path, shaders=None, icon_path=None, publish=False):
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
                shader_network = cls.get_shading_network(shader)

                # Store shader icon in base64 format
                shader_network['icon'] = img.image_to_base64(icon_path)

                # Export the shader in the given path and with the proper format
                out_file = os.path.join(shaders_path, shader + '.' + SHADER_EXT)
                sp.logger.debug('Generating Shader {0} in {1}'.format(shader, out_file))

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

                if publish:
                    sp.logger.debug('Creating new shader version in Artella: {}'.format(out_file))
                    solstice_artella_utils.upload_new_asset_version(out_file, comment='New Shader {} version'.format(shader), skip_saving=True)
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
                shader_name = os.path.splitext(os.path.basename(shader_file_path))[0]

                # if key == shader_name and not cmds.objExists(shader_name):
                if key == shader_name:
                    name = key
                else:
                    name = key+'_'
                name = re.sub('(?<=[A-z])[0-9]+', '', name)
                try:
                    cmds.rename(key, name)
                except Exception:
                    sp.logger.debug('ShaderLibrary: Impossible to rename {0} to {1}'.format(key, name))

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
    def get_shading_network(cls, shader_node, prefix=None):

        if prefix is not None:
            prefix_name = shader_node + '_' + prefix
        else:
            prefix_name = shader_node
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
    def _attrs_to_dict(cls, shader_node, prefix=None):
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

                if prefix:
                    new_connection_name = connected_node + '_' + prefix + '.' + connection
                else:
                    new_connection_name = connected_node + '.' + connection

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
            shader_lbl.setStatusTip(self.name)
            shader_lbl.setToolTip(self.name)

        do_export_layout = QVBoxLayout()
        do_export_layout.setAlignment(Qt.AlignCenter)
        self.do_export = QCheckBox()
        self.do_export.setChecked(True)
        do_export_layout.addWidget(self.do_export)
        main_layout.addLayout(do_export_layout)

    def export(self, publish=False):

        if self.do_export.isChecked():
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
                network = ShadingNetwork.write_network(shaders_path=shader_library_path, shaders=[self._name], icon_path=temp_file, publish=publish)
                exported_shaders = network
            except Exception as e:
                sp.logger.debug('Aborting shader export: {0}'.format(str(e)))
                os.remove(temp_file)
                return
            os.remove(temp_file)

            return exported_shaders
        else:
            return None

    @property
    def name(self):
        return self._name


class ShaderExporter(QDialog, object):

    exportFinished = Signal()

    def __init__(self, shaders, parent=None):
        super(ShaderExporter, self).__init__(parent=parent)

        self.setWindowTitle('Solstice Tools - Shader Exporter')

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        splash_pixmap = solstice_resource.pixmap('solstice_shaders_splash')
        splash = SolsticeShaderExportSplash(splash_pixmap)
        self._splash_layout = QVBoxLayout()
        self._splash_layout.setAlignment(Qt.AlignBottom)
        splash.setLayout(self._splash_layout)
        self.main_layout.addWidget(splash)

        shaders_layout = QVBoxLayout()
        shaders_layout.setAlignment(Qt.AlignBottom)
        self._splash_layout.addLayout(shaders_layout)
        self._shaders_list = QListWidget()
        self._shaders_list.setMaximumHeight(170)
        self._shaders_list.setFlow(QListWidget.LeftToRight)
        self._shaders_list.setSelectionMode(QListWidget.NoSelection)
        self._shaders_list.setStyleSheet('background-color: rgba(50, 50, 50, 150);')
        shaders_layout.addWidget(self._shaders_list)

        self.export_btn = QPushButton('Export')
        self.publish_btn = QPushButton('Export and Publish')
        self.cancel_btn = QPushButton('Cancel')
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addWidget(self.publish_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.setAlignment(Qt.AlignBottom)
        self._splash_layout.addLayout(buttons_layout)

        progress_layout = QHBoxLayout()
        self._splash_layout.addLayout(progress_layout)

        self._progress_text = QLabel('Exporting and uploading shaders to Artella ... Please wait!')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        self._progress_text.setVisible(False)
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)

        progress_layout.addWidget(self._progress_text)

        for shader in shaders:
            if shader in IGNORE_SHADERS:
                continue
            shader_item = QListWidgetItem()
            shader_widget = ShaderWidget(shader_name=shader, layout='vertical')
            shader_item.setSizeHint(QSize(120, 120))
            shader_widget.setMinimumWidth(100)
            shader_widget.setMinimumHeight(100)
            self._shaders_list.addItem(shader_item)
            self._shaders_list.setItemWidget(shader_item, shader_widget)

        self.export_btn.clicked.connect(partial(self._on_export_shaders, False))
        self.publish_btn.clicked.connect(partial(self._on_export_shaders, True))
        self.cancel_btn.clicked.connect(self.close)

        self.setFixedSize(splash_pixmap.size())

    def export_shaders(self, publish=False):

        exported_shaders = list()

        if self._shaders_list.count() <= 0:
            sp.logger.error('No Shaders To Export. Aborting ....')
            return exported_shaders

        try:
            for i in range(self._shaders_list.count()):
                shader_item = self._shaders_list.item(i)
                shader = self._shaders_list.itemWidget(shader_item)
                self._progress_text.setText('Exporting shader: {0} ... Please wait!'.format(shader.name))
                self.repaint()
                exported_shader = shader.export(publish=publish)
                if exported_shader is not None:
                    if type(exported_shader) == list:
                        exported_shaders.extend(exported_shader)
                    else:
                        exported_shaders.append(exported_shader)
                else:
                    sp.logger.error('Error while exporting shader: {}'.format(shader.name))
        except Exception as e:
            sp.logger.debug(str(e))
            sp.logger.debug(traceback.format_exc())

        return exported_shaders

    def _on_export_shaders(self, publish=False):
        self.cancel_btn.setVisible(False)
        self.export_btn.setVisible(False)
        self.publish_btn.setVisible(False)
        self._progress_text.setVisible(True)
        self.repaint()
        self.export_shaders(publish=publish)
        self.exportFinished.emit()
        sp.logger.debug('Shaders exported successfully!')
        self.close()


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
            # show_only_published_assets=True
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
            shader_widget.clicked.connect(partial(self.load_shader, shader_name))
            self.shader_viewer.add_widget(shader_widget)

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
    def load_shader(shader_name):

        shader_library_path = ShaderLibrary.get_shader_library_path()
        if not os.path.exists(shader_library_path):
            # TODO: If folder is not sync, sync automatically?
            sp.logger.debug('Solstice Shaders Library folder is not synchronized in your PC. Syncronize it please!')
            return False

        shader_path = os.path.join(shader_library_path, shader_name + '.' + SHADER_EXT)
        if os.path.isfile(shader_path):
            if cmds.objExists(shader_name):
                sp.logger.warning('ShaderLibrary: Shader {} already exists! Shader skipped!'.format(shader_name))
                return False
            else:
                ShadingNetwork.load_network(shader_file_path=shader_path)
        else:
            sp.logger.warning('ShaderLibrary: Shader {0} does not exist! Shader skipped!'.format(shader_path))
            return False

        return True

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
                    if shading_groups is None:
                        sp.logger.warning('Shading Mesh {} has not a shader applied to it, applying default shader ...'.format(shape))
                        shading_groups = ['initialShadingGroup']
                    for shading_grp in shading_groups:
                        shading_grp_mat = cmds.ls(cmds.listConnections(shading_grp), materials=True)
                        json_data[mesh][shape][shading_grp] = shading_grp_mat
                        all_shading_groups.append(shading_grp)
        else:
            asset_groups = cmds.ls(asset.name, type='transform')
            if len(asset_groups) <= 0 or len(asset_groups) > 1:
                return
            grp = asset_groups[0]
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

        # Generate JSON shading file for asset
        asset_shading_file = ShaderLibrary.get_asset_shader_file_path(asset=asset)
        solstice_artella_utils.lock_file(asset_shading_file, force=True)

        try:
            with open(asset_shading_file, 'w') as fp:
                json.dump(json_data, fp)

            # Upload new version of JSON shading file
            valid_version = solstice_artella_utils.upload_new_asset_version(asset_shading_file, comment=comment)
            if not valid_version:
                solstice_qt_utils.show_info(None, 'New Shaders JSON file version', 'Error while creating new version of JSON shaders version: {} Create it manaully later through Artella!'.format(asset_shading_file))
            solstice_artella_utils.unlock_file(asset_shading_file)
        except Exception as e:
            sp.logger.error(str(e))
            solstice_artella_utils.unlock_file(asset_shading_file)

        # To export shaders file we need to use ShaderLibrary Tool
        # asset_materials = list(set(cmds.ls(cmds.listConnections(all_shading_groups), materials=True)))
        # shader_exporter = ShaderExporter(shaders=asset_materials)
        # shaders = shader_exporter._export_shaders()

        if os.path.isfile(asset_shading_file):
            return asset_shading_file

        return ''

    def export_asset_shaders(self, asset):
        if asset is None:
            sp.logger.debug('Given Asset to export is not valid! Aborting operation ...')
            return

        asset.sync(sync_type='shading', status='published')
        shading_path = asset.get_asset_file(file_type='shading', status='published')
        if not os.path.isfile(shading_path):
            sp.logger.error('Last published shading file {} is not sync in your computer!'.format(shading_path))
            return

        cmds.file(shading_path, o=True, f=True)

        all_shading_groups = list()
        json_data = dict()

        asset_group = cmds.ls(asset.name, type='transform')
        if len(asset_group) <= 0:
            sp.logger.error('No asset shader group found in the scene ... Aborting exporting process ...')
            return
        if len(asset_group) > 1:
            sp.logger.error('More than one asset shader group found in the scene ... Aborting exporting process ...')
            return

        grp = asset_group[0]
        json_data[grp] = dict()
        children = cmds.listRelatives(grp, type='transform', allDescendents=True, fullPath=True)
        for child in children:
            child_shapes = cmds.listRelatives(child, shapes=True, fullPath=True)
            for shape in child_shapes:
                json_data[grp][shape] = dict()
                shading_groups = cmds.listConnections(shape, type='shadingEngine')
                if shading_groups is None:
                    shading_groups = ['initialShadingGroup']
                for shading_grp in shading_groups:
                    shading_grp_mat = cmds.ls(cmds.listConnections(shading_grp), materials=True)
                    json_data[grp][shape][shading_grp] = shading_grp_mat
                    all_shading_groups.append(shading_grp)

        asset_materials = list(set(cmds.ls(cmds.listConnections(all_shading_groups), materials=True)))
        exporter = ShaderExporter(shaders=asset_materials)
        exporter.exportFinished.connect(self.update_shader_library)
        exporter.exec_()

    @staticmethod
    def load_scene_shaders():
        """
        Loops through all tag data scene nodes and loads all necessary shaders into the current scene
        If a specific shader is already loaded, that shader is skipeed
        :return: list<str>, list of loaded shaders
        """

        from solstice_pipeline.solstice_tools import solstice_outliner
        reload(solstice_outliner)
        
        tag_nodes = solstice_outliner.SolsticeOutliner.get_tag_data_nodes()
        if not tag_nodes or len(tag_nodes) <= 0:
            sp.logger.error('No tag nodes found in the current scene. Aborting shaders loading ...')
            return []

        for tag in tag_nodes:
            shaders = tag.get_shaders()
            if not shaders:
                sp.logger.error('No shaders found for asset: {}'.format(tag.get_asset()))
                continue

            hires_group = tag.get_hires_group()
            if not hires_group or not cmds.objExists(hires_group):
                sp.logger.error('No Hires group found for asset: {}'.format(tag.get_asset()))
                continue

            hires_meshes = [obj for obj in cmds.listRelatives(hires_group, children=True, type='transform', shapes=False, noIntermediate=True, fullPath=True) if cmds.objExists(obj) and cmds.listRelatives(obj, shapes=True)]
            if not hires_meshes or len(hires_meshes) <= 0:
                sp.logger.error('No Hires meshes found for asset: {}'.format(tag.get_asset()))
                continue

            node = tag.get_asset()
            is_referenced = cmds.referenceQuery(node, isNodeReferenced=True)
            if not is_referenced:
                sp.logger.error('Node {} is not referenced! All scene assets should be referenced (not imported). Please contact TD!'.format(node))
                continue

            namespace = cmds.referenceQuery(node, namespace=True)
            if not namespace or not namespace.startswith(':'):
                sp.logger.error('Node {} has not a valid namespace!. Please contact TD!'.format(node))
                continue
            else:
                namespace = namespace[1:] + ':'

            valid_meshes = list()
            for mesh in hires_meshes:
                mesh_no_namespace = mesh.replace(namespace, '')
                asset_group = mesh_no_namespace.split('|')[1]
                asset_mesh = mesh_no_namespace.split('|')[-1]
                group_mesh_name = '|{0}|{1}'.format(asset_group, asset_mesh)
                for shader_mesh in shaders.keys():
                    if shader_mesh == group_mesh_name:
                        valid_meshes.append(mesh)
            if len(valid_meshes) <= 0:
                sp.logger.error('No valid meshes found on asset. Please contact TD!'.format(tag.get_asset()))
                continue

            meshes_shading_groups = list()
            for mesh in valid_meshes:
                mesh_shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True)
                if not mesh_shapes or len(mesh_shapes) <= 0:
                    sp.logger.error('Mesh {} has not valid shapes!'.format(mesh))
                    continue
                for shape in mesh_shapes:
                    shape_name = shape.split(':')[-1]
                    for shader_mesh, shader_data in shaders.items():
                        for shader_shape, shader_group in shader_data.items():
                            shader_shape_name = shader_shape.split('|')[-1]
                            if shape_name == shader_shape_name:
                                meshes_shading_groups.append([mesh, shader_group])
            if len(meshes_shading_groups) <= 0:
                sp.logger.error('No valid shading groups found on asset. Please contact TD!'.format(tag.get_asset()))
                continue

            for mesh_info in meshes_shading_groups:
                mesh = mesh_info[0]
                shading_info = mesh_info[1]
                for shading_grp, materials in shading_info.items():
                    if not materials or len(materials) <= 0:
                        sp.logger.error('No valid materials found on mesh {0} of asset {1}'.format(mesh, tag.get_asset()))
                        continue

                    for mat in materials:

                        # TODO: This check is already done in load shader function. Remove?
                        if not mat or cmds.objExists(mat):
                            sp.logger.warning('Shader {} already exists on scene. Skipping creation ...'.format(mat))
                            continue

                        sp.logger.debug('Loading Shader: {}'.format(mat))
                        valid_shader = ShaderLibrary.load_shader(mat)
                        if not valid_shader:
                            sp.logger.error('Error while loading shader {}'.format(mat))

                # After materials are created we try to apply to the meshes
                # mesh_transform = cmds.listRelatives(mesh, parent=True, fullPath=True)
                # if mesh_transform:
                #     mesh_transform = mesh_transform[0]
                #     if not cmds.objExists(mesh_transform):
                #         sp.logger.error('Mesh Transform {} does not exists in the scene!'.format(mesh_transform))
                # else:
                #     sp.logger.error('Mesh Shape {} has not a valid transform!'.format(mesh))
                #     continue

                try:
                    for shading_grp, materials in shading_info.items():
                        if not cmds.objExists(shading_grp):
                            for mat in materials:
                                if not materials or len(materials) <= 0:
                                    continue
                                sp.logger.error('Shading group {}  loaded from shader info does not exists!'.format(shading_grp))
                                shading_grp = mat + 'SG'
                                sp.logger.error('Applying shading group based on nomenclature: {}'.format(shading_grp))
                                if cmds.objExists(shading_grp):
                                    sp.logger.error('Impossible to set shading group {0} to mesh {1}'.format(shading_grp, mesh))
                                    break
                        cmds.sets(mesh, edit=True, forceElement=shading_grp)
                        sp.logger.debug('Shading set {0} applied to mesh {1}'.format(shading_grp, mesh))
                except Exception as e:
                    sp.logger.error('Impossible to set shading group {0} to mesh {1}'.format(shading_grp, mesh))
                    sp.logger.error(str(e))

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
        self.export_asset_shaders(asset=asset)


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
