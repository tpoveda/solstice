#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for shader files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import json
import logging
import traceback

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import qtutils

import artellapipe
from artellapipe.core import defines, file, assetfile
from artellapipe.utils import shader

if tp.is_maya():
    from tpDcc.dccs.maya.core import shader as maya_shader

LOGGER = logging.getLogger()


class SolsticeShaderFile(file.ArtellaFile, object):
    def __init__(self, project, file_name, file_path=None, file_extension=None):
        self._file_path = file_path
        super(SolsticeShaderFile, self).__init__(
            project=project, file_name=file_name, file_path=file_path, file_extension=file_extension)

    def get_template_dict(self, **kwargs):
        """
        Implements get_template_dict() function
        :return: dict
        """

        file_extension = kwargs.get('extension', None)
        return {
            'project_id': self._project.id,
            'project_id_number': self._project.id_number,
            'shaders': self._file_path,
            'shader_name': self.name,
            'file_extension': file_extension
        }

    def _import_file(self, file_path, *args, **kwargs):
        LOGGER.info('Importing Shader: {}'.format(file_path))
        if not os.path.isfile(file_path):
            LOGGER.warning('Shader File "{}" does not exists. Skip importing ...'.format(file_path))
            return

        if tp.Dcc.object_exists(self.name):
            LOGGER.warning('Shader "{}" already exists in current scene. Skip importing ...'.format(self.name))
            return

        shader.ShadingNetwork.load_network(shader_file_path=file_path)

    def _export_file(self, file_path, *args, **kwargs):

        exported_shader = None
        shader_swatch = kwargs.get('shader_swatch', None)

        if not shader_swatch and tp.is_maya():
            shader_swatch = maya_shader.get_shader_swatch(shader_name=self.name)

        px = QPixmap(QSize(100, 100))
        shader_swatch.render(px)
        temp_file = os.path.join(os.path.dirname(file_path), 'tmp.png')
        px.save(temp_file)
        try:
            exported_shader = shader.ShadingNetwork.write_network(
                shader_extension=self.extensions[0], shaders_path=os.path.dirname(file_path),
                shaders=[self.name], icon_path=temp_file)
        except Exception as exc:
            LOGGER.error('Error while exporting shader: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            if temp_file and os.path.isfile(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    LOGGER.warning('Impossible to remove temporary swatch file: {}'.format(temp_file))

        return exported_shader


class SolsticeShadersAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None):
        super(SolsticeShadersAssetFile, self).__init__(file_asset=asset)


class SolsticeShaderAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None, shader_name=None):
        self._shader_name = shader_name
        super(SolsticeShaderAssetFile, self).__init__(file_asset=asset)

    @property
    def shader_name(self):
        return self._shader_name

    def get_template_dict(self, **kwargs):
        """
        Implements get_template_dict() function
        :return: dict
        """

        template_dict = super(SolsticeShaderAssetFile, self).get_template_dict(**kwargs)
        template_dict['shader_name'] = self._shader_name

        return template_dict

    def _import_file(self, file_path, *args, **kwargs):
        LOGGER.info('Importing Asset Shader: {}'.format(file_path))
        if not os.path.isfile(file_path):
            LOGGER.warning('Shader File "{}" does not exists. Skip importing ...'.format(file_path))
            return

        if tp.Dcc.object_exists(self.name):
            LOGGER.warning('Shader "{}" already exists in current scene. Skip importing ...'.format(self.name))
            return

        shader.ShadingNetwork.load_network(shader_file_path=file_path)

    def _export_file(self, file_path, *args, **kwargs):

        exported_shader = None
        shader_swatch = kwargs.get('shader_swatch', None)

        if not shader_swatch and tp.is_maya():
            shader_swatch = maya_shader.get_shader_swatch(shader_name=self._shader_name)

        px = QPixmap(QSize(100, 100))
        shader_swatch.render(px)
        temp_file = os.path.join(os.path.dirname(file_path), 'tmp.png')
        px.save(temp_file)
        try:
            exported_shader = shader.ShadingNetwork.write_network(
                shader_extension=self.extensions[0], shaders_path=os.path.dirname(file_path),
                shaders=[self._shader_name], icon_path=temp_file)
        except Exception as exc:
            LOGGER.error('Error while exporting shader: {} | {}'.format(exc, traceback.format_exc()))
        finally:
            if temp_file and os.path.isfile(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    LOGGER.warning('Impossible to remove temporary swatch file: {}'.format(temp_file))

        return exported_shader


class SolsticeShaderMappingAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None, file_path=None):
        super(SolsticeShaderMappingAssetFile, self).__init__(file_asset=asset, file_path=file_path)

        self._data = dict()         # We do not initialize data here to avoid recursion calls

    def get_shaders_info(self, force=False, status=defines.ArtellaFileStatus.PUBLISHED):
        """
        Returns dictionary that maps the shaders contained in the file with the different geometries
        :return: dict
        """

        if not self._data or force:
            self._data = self._load_data(status=status)

        return self._data

    def get_shaders(self, status=defines.ArtellaFileStatus.PUBLISHED, force=False):
        """
        Returns a list contained in the shader file
        :return: list(str)
        """

        found_shaders = list()
        for transform_name, shape_data in self.get_shaders_info(status=status, force=force).items():
            for shape_name, shaders_list in shape_data.items():
                for shader in shaders_list:
                    if shader not in found_shaders:
                        found_shaders.append(shader)

        return found_shaders

    def get_shading_geometry_mapping(self, status=defines.ArtellaFileStatus.PUBLISHED):
        """
        Returns dictionary containing a relation with shapes and shaders to apply to
        :return:
        """

        shading_geo_mapping = dict()
        for shape_name, shape_data in self.get_shaders_info(status=status).items():
            for shading_group, shaders_list in shape_data.items():
                if shape_name not in shading_geo_mapping:
                    shading_geo_mapping[shape_name] = list()
                for shader in shaders_list:
                    if shader not in shading_geo_mapping[shape_name]:
                        shading_geo_mapping[shape_name].append(shader)

        return shading_geo_mapping

    def get_shading_group_shader_mapping(self):
        """
        Returns dictionary mapping a relation with shading groups and shaders connected to
        :return:
        """

        shading_shader_mapping = dict()
        for shape_name, shape_data in self._data.items():
            for shading_group_name, shaders_list in shape_data.items():
                if shading_group_name not in shading_shader_mapping:
                    shading_shader_mapping[shading_group_name] = list()
                for shader in shaders_list:
                    if shader not in shading_shader_mapping[shading_group_name]:
                        shading_shader_mapping[shading_group_name].append(shader)

        return shading_shader_mapping

    def _load_data(self, status=defines.ArtellaFileStatus.PUBLISHED):
        """
        Internal function that loads the data contained in the file
        :return:
        """

        file_path = self.get_file_paths(return_first=True, status=status)
        if not file_path or not os.path.isfile(file_path):
            return dict()

        with open(file_path, 'r') as f:
            return json.load(f)

    def _export_file(self, file_path, *args, **kwargs):
        if not tp.is_maya():
            LOGGER.warning('Shaders export is only supported in Maya!')
            return

        shaders_to_export = artellapipe.ShadersMgr().get_asset_shaders_to_export(
            asset=self._asset, return_only_shaders=False)

        locked_file = False
        if os.path.isfile(file_path):
            res = qtutils.show_question(
                None, 'Exporting Shaders Mapping File',
                'Shaders Mapping File "{}" already exists. Do you want to overwrite it?'.format(file_path))
            if res == QMessageBox.No:
                return

            artellapipe.FilesMgr().lock_file(file_path)
            locked_file = True

        try:
            with open(file_path, 'w') as fp:
                json.dump(shaders_to_export, fp)
        except Exception as exc:
            LOGGER.error('Error while exporting Shaders Mapping File "{}" | {}'.format(file_path, exc))
        finally:
            if locked_file:
                artellapipe.FilesMgr().unlock_file(file_path)

        if os.path.isfile(file_path):
            return file_path
