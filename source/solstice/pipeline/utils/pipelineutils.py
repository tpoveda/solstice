#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utility functions related with pipeline
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import traceback

import solstice.pipeline as sp

from solstice.pipeline.tools.alembicmanager import alembicmanager
from solstice.pipeline.tools.lightrigs import lightrigs

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary
    from solstice.pipeline.tools.standinmanager import standinmanager


def generate_alembic_file(asset_name, start_frame=1, end_frame=1):
    """
    Exports Alembic file from the given asset name and in proper location
    :param asset_name: str
    :param start_frame: int
    :param end_frame: int
    """

    if not asset_name:
        sys.solstice.logger.warning('Type an asset name first!')
        return

    asset = sp.find_asset(asset_name)
    if not asset:
        sys.solstice.logger.error('No asset found with name: {}'.format(asset_name))
        return

    asset.export_alembic_file(start_frame=start_frame, end_frame=end_frame)


def setup_standin_export(asset_name, export_path=None):
    """
    Setup the standin export
    :param asset_name: str
    :param export_path: str
    """

    if not asset_name:
        sys.solstice.logger.warning('Type an asset name first!')
        return

    asset = sp.find_asset(asset_name)
    if not asset:
        sys.solstice.logger.error('No asset found with name: {}'.format(asset_name))
        return

    sys.solstice.dcc.new_file()

    if not export_path:
        export_path = os.path.dirname(asset.get_asset_file(file_type='model', status='working'))
    if not os.path.isdir(export_path):
        sys.solstice.logger.error('Export Path {} does not exists! Aborting operation ...'.format(export_path))
        return

    alembic_name = asset.name + '.abc'
    abc_path = os.path.join(export_path, alembic_name)
    if not os.path.isfile(abc_path):
        sys.solstice.logger.error('Alembic File for asset {} not found: {}. Aborting operation ...'.format(asset_name, abc_path))
        return

    alembicmanager.AlembicImporter.reference_alembic(abc_path)
    sys.solstice.dcc.refresh_viewport()
    shaderlibrary.ShaderLibrary.load_all_scene_shaders()
    sys.solstice.dcc.refresh_viewport()

    return True


def generate_standin_file(asset_name, export_path=None, start_frame=1, end_frame=1):
    """
    Exports Standin file from the given asset name and in proper location
    NOTE: To work properly with our pipeline you need to call first setup_standin_export function
    :param asset_name: str
    :param export_path: str
    :param start_frame: int
    :param end_frame: int
    """

    if not asset_name:
        sys.solstice.logger.warning('Type an asset name first!')
        return

    try:
        asset = sp.find_asset(asset_name)
        if not asset:
            sys.solstice.logger.error('No asset found with name: {}'.format(asset_name))
            return

        if not export_path:
            export_path = os.path.dirname(asset.get_asset_file(file_type='model', status='working'))
        if not os.path.isdir(export_path):
            sys.solstice.logger.error('Export Path {} does not exists! Aborting operation ...'.format(export_path))
            return

        sys.solstice.dcc.select_object(asset.name)
        sys.solstice.dcc.refresh_viewport()
        standinmanager.StandinExporter().export_standin(
            export_path=export_path,
            standin_name=asset.name,
            start_frame=start_frame,
            end_frame=end_frame
        )
    except Exception:
        sys.solstice.logger.error(traceback.format_exc())
        return False

    return True


def test_asset_pipeline_files(asset_name, export_path=None, axis_to_move='x'):
    """
    Tries to import all files related with an asset (rig, alembic and pipeline)
    :param asset_name: str
    :param export_path: str
    :param axis_to_move: str
    """

    if not sp.is_maya():
        sys.solstice.logger.warning('Test Asset functionality is only available in Maya!')
        return

    if not asset_name:
        sys.solstice.logger.warning('Type an asset name first!')
        return
    asset = sp.find_asset(asset_name)
    if not asset:
        sys.solstice.logger.error('No asset found with name: {}'.format(asset_name))
        return

    sys.solstice.dcc.new_file()
    if not export_path:
        export_path = os.path.dirname(asset.get_asset_file(file_type='model', status='working'))
    if not os.path.isdir(export_path):
        sys.solstice.logger.error('Export Path {} does not exists! Aborting operation ...'.format(export_path))
        return

    asset.import_asset_file('rig', status='working')
    sys.solstice.dcc.refresh_viewport()

    abc_name = asset.name + '.abc'
    abc_path = os.path.join(export_path, abc_name)
    if os.path.isfile(abc_path):
        alembicmanager.AlembicImporter.reference_alembic(abc_path)

    standin_name = asset.name + '.ass'
    standin_path = os.path.join(export_path, standin_name)
    if os.path.isfile(standin_path):
        standinmanager.StandinImporter.import_standin(standin_path)

    sys.solstice.dcc.set_integer_attribute_value(node=asset.name, attribute_name='type', attribute_value=1)

    hires_name = '|' + asset.name + '1'
    standin_obj = '|' + asset.name + '3'

    bbox = cmds.exactWorldBoundingBox(hires_name)
    margin = 15

    if axis_to_move == 'x' or axis_to_move == 'X':
        bbox_width = abs(bbox[0] - bbox[3])
        total_move = bbox_width + margin
        cmds.move(total_move, 0, 0, hires_name)
        cmds.move(total_move * 2, 0, 0, standin_obj)
    elif axis_to_move == 'y' or axis_to_move == 'Y':
        bbox_height = abs(bbox[1] - bbox[4])
        total_move = bbox_height + margin
        cmds.move(0, total_move, 0, hires_name)
        cmds.move(0, total_move * 2, 0, standin_obj)
    else:
        bbox_depth = abs(bbox[2] - bbox[5])
        total_move = bbox_depth + margin
        cmds.move(0, 0, total_move, hires_name)
        cmds.move(0, 0, total_move * 2, standin_obj)

    cmds.viewFit(an=True)

    sys.solstice.dcc.refresh_viewport()

    shaderlibrary.ShaderLibrary.load_all_scene_shaders()

    lightrigs.LightRigManager.reference_light_rig('Neutral Contrast', do_save=False)


