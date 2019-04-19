#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for animation files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.tools.shotexporter.core import exporter as base_exporter
from solstice.pipeline.tools.shotexporter.export.animation import exportlist, propertieswidget

reload(exportlist)

class AnimationExporter(base_exporter.BaseExporter, object):
    def __init__(self, parent=None):
        super(AnimationExporter, self).__init__(parent=parent)

    def get_exporter_list_widget(self):
        """
        Overrides base BaseExporter get_exporter_list_widget() function
        Returns exporter list widget used by the exporter
        :return: exporter.LayoutExportList
        """

        return exportlist.AnimationExportList()

    def get_exporter_properties_widget(self):
        """
        Overrides base BaseExporter get_exporter_properties_widget() function
        Returns exporter properties widget used by the exporter
        :return: exporter.LayoutPropertiesWidget
        """

        return propertieswidget.AnimationPropertiesWidget()

    def get_export_button_text(self):
        """
        Overrides base BaseExporter get_export_button_text() function
        Returns exporter button text
        :return: str
        """

        return 'SAVE ANIMATION'

    # def setup_signals(self):
    #     self.exporter_list.updateProperties.connect(self._on_update_properties)
    #     self.exporter_list.refresh.connect(self._on_clear_properties)
    #     self.save_btn.clicked.connect(self._on_save)
    #
    # def init_ui(self):
    #     self.exporter_list.init_ui()
    #
    # def refresh(self):
    #     self.exporter_list.refresh_exporter()
    #
    # def _on_update_properties(self, asset_widget):
    #     if asset_widget and sp.dcc.object_exists(asset_widget.asset.name):
    #         self.anims_list.update_attributes(asset_widget)
    #     else:
    #         sp.logger.warning('Impossible to update properties because object {} does not exists!'.format(asset_widget.asset))
    #         self.anims_list.clear_properties()
    #
    # def _on_clear_properties(self):
    #     self.anims_list.clear_properties()

    # def _on_save(self):
    #     if not sp.is_maya():
    #         sp.logger.warning('Shot Export only works for Maya!')
    #         return
    #
    #     import maya.cmds as cmds
    #
    #     anim_file = sp.dcc.save_file_dialog(title='Animation File', start_directory=sp.get_solstice_project_path(), pattern='Animation Files (*.anim)')
    #     print(anim_file)
    #     if not anim_file:
    #         return
    #
    #     anim_info = dict()
    #     anim_info['data_version'] = sp.DataVersions.ANIM
    #     anim_info['exporter_version'] = shotexporter.ShotExporter.version
    #     anim_info['anims'] = dict()
    #     for w in self.exporter_list.all_widgets():
    #         abc_files = w.asset.get_alembic_files()
    #         if not abc_files:
    #             sp.logger.warning('Skipping {} because Alembic File does not exists!'.format(w.asset.name))
    #             continue
    #         abc_file = sp.dcc.get_attribute_value(node=w.abc_node, attribute_name='abc_File')
    #         if not os.path.isfile(abc_file):
    #             sp.logger.warning('Skipping {} because Alembic File {} does not exists!'.format(w.asset.name))
    #             continue
    #         abc_file = os.path.relpath(abc_file, sp.get_solstice_project_path())
    #         if not abc_file:
    #             sp.logger.warning('Skipping {} because Alembic File {} is not located in Soltice Project path!'.format(w.asset.name))
    #             continue
    #         anim_name = w.asset.name
    #         anim_uuid = cmds.ls(anim_name, uuid=True)[0]
    #         anim_info['anims'][anim_uuid] = dict()
    #         anim_info['anims'][anim_uuid]['name'] = anim_name
    #         anim_info['anims'][anim_uuid]['path'] = abc_file
    #         anim_info['anims'][anim_uuid]['attrs'] = dict()
    #         anim_info['anims'][anim_uuid]['abc_attrs'] = dict()
    #         anim_info['anims'][anim_uuid]['overrides'] = dict()
    #         for attr, flag in w.attrs.items():
    #             if not flag and attr not in defines.MUST_ATTRS:
    #                 continue
    #             attr_value = sp.dcc.get_attribute_value(node=anim_name, attribute_name=attr)
    #             anim_info['anims'][anim_uuid]['attrs'][attr] = attr_value
    #         for attr, flag in w.abc_attrs.items():
    #             if not flag and attr not in defines.ABC_ATTRS:
    #                 continue
    #             attr_value = sp.dcc.get_attribute_value(node=w.abc_node, attribute_name=attr)
    #             anim_info['anims'][anim_uuid]['abc_attrs'][attr] = attr_value
    #
    #     try:
    #         with open(anim_file, 'w') as f:
    #             json.dump(anim_info, f)
    #     except Exception as e:
    #         sp.logger.error(str(e))
