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

import os
import sys
import json
import weakref
import urllib2
import tempfile

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import base, window, splitters, buttons, stack, accordion, console, messagehandler
from solstice.pipeline.utils import browserutils, pipelineutils, rigutils, artellautils as artella, slackutils as slack

from solstice.pipeline.tools.sanitycheck.checks import assetchecks
from solstice.pipeline.tools.tagger import tagger

if sp.is_maya():
    import maya.cmds as cmds
    from mtoa.cmds.arnoldRender import arnoldRender
    from solstice.pipeline.tools.lightrigs import lightrigs
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary
    from solstice.pipeline.utils import mayautils
    reload(shaderlibrary)

reload(pipelineutils)
reload(console)
reload(assetchecks)
reload(slack)
reload(mayautils)

console_win = None


class AutoCompleterLine(QLineEdit, object):
    def __init__(self, parent=None):
        super(AutoCompleterLine, self).__init__(parent=parent)

    def focusInEvent(self, event):
        super(AutoCompleterLine, self).focusInEvent(event)
        self.completer().complete()


class BaseTDToolBoxWidget(base.BaseWidget, object):

    emitInfo = Signal(str)
    emitWarning = Signal(str)
    emitError = Signal(str, object)

    def __init__(self, title, parent=None):
        super(BaseTDToolBoxWidget, self).__init__(parent=parent)

        self._title = title

    @property
    def title(self):
        return self._title


class PipelineToolbox(BaseTDToolBoxWidget, object):
    def __init__(self, parent=None):
        super(PipelineToolbox, self).__init__('Pipeline', parent)

    def custom_ui(self):
        super(PipelineToolbox, self).custom_ui()

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.props_pipeline = PropsPipelineWidget()
        self.tabs.addTab(self.props_pipeline, 'Props | Background Elements')


class PropsPipelineWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(PropsPipelineWidget, self).__init__(parent=parent)

    def custom_ui(self):
        super(PropsPipelineWidget, self).custom_ui()

        all_assets = sp.find_all_assets(assets_path=sp.get_solstice_assets_path())
        asset_name_completer = QCompleter([asset.name for asset in all_assets], self)
        asset_lbl = QLabel('Asset Name: ')
        self.asset_name_line = AutoCompleterLine()
        self.asset_name_line.setCompleter(asset_name_completer)
        if sp.is_maya():
            import maya.cmds as cmds
            objs = cmds.ls(type='transform')
            if objs:
                for obj in objs:
                    for asset in all_assets:
                        if asset.name == obj:
                            self.asset_name_line.setText(obj)
                            break

        name_layout = QHBoxLayout()
        self.main_layout.addLayout(name_layout)
        name_layout.addWidget(asset_lbl)
        name_layout.addWidget(self.asset_name_line)
        self.main_layout.addLayout(splitters.SplitterLayout())

        self.accordion = accordion.AccordionWidget(parent=self)
        self.accordion.rollout_style = accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.accordion)

        # Checkers
        check_widget = QWidget()
        check_layout = QHBoxLayout()
        check_widget.setLayout(check_layout)
        utils_tab = QTabWidget()
        check_layout.addWidget(utils_tab)

        textures_utils = QWidget()
        textures_check_lyt = QGridLayout()
        textures_utils.setLayout(textures_check_lyt)
        valid_textures_path_btn = QPushButton('Valid Textures Path')
        textures_folder_empty_btn = QPushButton('Textures Folder Empty?')
        textures_file_size_btn = QPushButton('Valid Textures File Size?')
        all_textures_checks_btn = QPushButton('All Checks')
        textures_check_lyt.addWidget(valid_textures_path_btn, 0, 0)
        textures_check_lyt.addWidget(textures_folder_empty_btn, 0, 1)
        textures_check_lyt.addWidget(textures_file_size_btn, 1, 0)
        textures_check_lyt.addLayout(splitters.SplitterLayout(), 2, 0, 1, 2)
        textures_check_lyt.addWidget(all_textures_checks_btn, 3, 0, 1, 2)

        model_utils = QWidget()
        model_check_lyt = QGridLayout()
        model_utils.setLayout(model_check_lyt)
        valid_model_path_btn = QPushButton('Valid Model Path')
        valid_proxy_path_btn = QPushButton('Valid Proxy Path')
        check_model_main_group_btn = QPushButton('Check Model Main Group')
        check_proxy_main_group_btn = QPushButton('Check Proxy Model Main Group')
        model_has_no_shaders_btn = QPushButton('Model Has No Shaders')
        proxy_has_no_shaders_btn = QPushButton('Proxy Has No Shaders')
        delete_scene_shaders_btn = QPushButton('Delete Scene Shaders')
        import_shading_file_btn = QPushButton('Import Shading File')
        transfer_uvs_btn = QPushButton('Transfer UVs')
        remove_type_tag_data_attrs_btn = QPushButton('Remove Type and Tag Data Attributes')
        clean_render_layer_nodes_btn = QPushButton('Clean Render Layer Nodes')
        clean_file_nodes = QPushButton('Clean File Nodes')
        clean_model_file_btn = QPushButton('Clean Model File')
        clean_proxy_file_btn = QPushButton('Clean Proxy File')
        model_check_lyt.addWidget(valid_model_path_btn, 0, 0)
        model_check_lyt.addWidget(valid_proxy_path_btn, 0, 1)
        model_check_lyt.addWidget(check_model_main_group_btn, 1, 0)
        model_check_lyt.addWidget(check_proxy_main_group_btn, 1, 1)
        model_check_lyt.addWidget(model_has_no_shaders_btn, 2, 0)
        model_check_lyt.addWidget(proxy_has_no_shaders_btn, 2, 1)
        model_check_lyt.addWidget(delete_scene_shaders_btn, 3, 0)
        model_check_lyt.addWidget(import_shading_file_btn, 3, 1)
        model_check_lyt.addWidget(transfer_uvs_btn, 4, 0)
        model_check_lyt.addWidget(remove_type_tag_data_attrs_btn, 4, 1)
        model_check_lyt.addWidget(clean_render_layer_nodes_btn, 5, 0)
        model_check_lyt.addWidget(clean_file_nodes, 5, 1)
        model_check_lyt.addWidget(clean_model_file_btn, 6, 0)
        model_check_lyt.addWidget(clean_proxy_file_btn, 6, 1)

        rig_utils = QWidget()
        rig_utils_lyt = QGridLayout()
        rig_utils.setLayout(rig_utils_lyt)
        valid_rig_path_btn = QPushButton('Valid Rig Path')
        valid_builder_path_btn = QPushButton('Valid Builder Path')
        build_rig_btn = QPushButton('Build Rig')
        lock_rig_btn = QPushButton('Lock Rig File')
        save_rig_btn = QPushButton('Save Rig')
        new_rig_version_btn = QPushButton('New Rig Version')
        model_proxy_hires_groups_btn = QPushButton('Setup Model Proxy/Hires Groups')
        create_tag_btn = QPushButton('Create Tag')
        check_tag_btn = QPushButton('Check Tag')
        update_tag_btn = QPushButton('Update Tag')
        open_skin_weights_saver_btn = QPushButton('Open bSkinSaver')
        export_skin_weights_btn = QPushButton('Export Skin Weights')
        import_skin_weight_btn = QPushButton('Import Skin Weights')
        rig_utils_lyt.addWidget(valid_rig_path_btn, 0, 0)
        rig_utils_lyt.addWidget(valid_builder_path_btn, 0, 1)
        rig_utils_lyt.addWidget(lock_rig_btn, 1, 0)
        rig_utils_lyt.addWidget(save_rig_btn, 1, 1)
        rig_utils_lyt.addWidget(new_rig_version_btn, 2, 0)
        rig_utils_lyt.addWidget(model_proxy_hires_groups_btn, 2, 1)
        rig_utils_lyt.addWidget(create_tag_btn, 3, 0)
        rig_utils_lyt.addWidget(check_tag_btn, 3, 1)
        rig_utils_lyt.addWidget(update_tag_btn, 4, 0)
        rig_utils_lyt.addWidget(open_skin_weights_saver_btn, 4, 1)
        rig_utils_lyt.addWidget(export_skin_weights_btn, 5, 0)
        rig_utils_lyt.addWidget(import_skin_weight_btn, 5, 1)
        rig_utils_lyt.addWidget(build_rig_btn, 6, 0, 1, 2)

        shading_utils = QWidget()
        shading_check_lyt = QGridLayout()
        shading_utils.setLayout(shading_check_lyt)
        valid_shading_path_btn = QPushButton('Valid Shading Path')
        check_shading_main_group_btn = QPushButton('Check Shading Main Group')
        check_shading_shaders = QPushButton('Check Shaders')
        rename_shaders_btn = QPushButton('Rename Shaders')
        print_texture_files = QPushButton('Print Texture Files')
        update_textures_paths_btn = QPushButton('Update Textures Paths')
        clean_textures_paths_btn = QPushButton('Clean Textures Paths')
        export_shading_file_btn = QPushButton('Export Shading JSON File')
        export_shaders_btn = QPushButton('Export Shaders')
        clean_render_layer_nodes2_btn = QPushButton('Clean Render Layer Nodes')
        shading_check_lyt.addWidget(valid_shading_path_btn, 0, 0)
        shading_check_lyt.addWidget(check_shading_main_group_btn, 0, 1)
        shading_check_lyt.addWidget(check_shading_shaders, 1, 0)
        shading_check_lyt.addWidget(rename_shaders_btn, 1, 1)
        shading_check_lyt.addWidget(print_texture_files, 2, 0)
        shading_check_lyt.addWidget(export_shading_file_btn, 2, 1)
        shading_check_lyt.addWidget(update_textures_paths_btn, 3, 0)
        shading_check_lyt.addWidget(clean_textures_paths_btn, 3, 1)
        shading_check_lyt.addWidget(export_shaders_btn, 4, 0)
        shading_check_lyt.addWidget(clean_render_layer_nodes2_btn, 4, 1)

        test_utils = QWidget()
        test_check_lyt = QGridLayout()
        test_utils.setLayout(test_check_lyt)

        slack_utils = QWidget()
        slack_utils_lyt = QGridLayout()
        slack_utils.setLayout(slack_utils_lyt)

        artella_utils = QWidget()
        artella_utils_lyt = QGridLayout()
        artella_utils.setLayout(artella_utils_lyt)
        sync_asset_btn = QPushButton('Sync Asset')
        lock_file_btn = QPushButton('Lock Current File')
        new_version_btn = QPushButton('New File Version')
        artella_utils_lyt.addWidget(sync_asset_btn, 0, 0)
        artella_utils_lyt.addWidget(lock_file_btn, 0, 1)
        artella_utils_lyt.addWidget(new_version_btn, 1, 0)

        utils_tab.addTab(textures_utils, 'Textures')
        utils_tab.addTab(model_utils, 'Model')
        utils_tab.addTab(rig_utils, 'Rig')
        utils_tab.addTab(shading_utils, 'Shading')
        utils_tab.addTab(test_utils, 'Tests')
        utils_tab.addTab(slack_utils, 'Slack')
        utils_tab.addTab(artella_utils, 'Artella')
        ref_neutral_light_rig_btn = QPushButton('Reference Neutral Light Rig')
        sync_shaders_btn = QPushButton('Sync Shaders')
        render_low_res_btn = QPushButton('Render Low Res')
        render_mid_res_btn = QPushButton('Render Mid Res')
        render_high_res_btn = QPushButton('Render High Res')
        render_full_hd_btn = QPushButton('Render Full HD')
        test_check_lyt.addWidget(ref_neutral_light_rig_btn, 0, 0)
        test_check_lyt.addWidget(sync_shaders_btn, 0, 1)
        test_check_lyt.addWidget(render_low_res_btn, 1, 0)
        test_check_lyt.addWidget(render_mid_res_btn, 1, 1)
        test_check_lyt.addWidget(render_high_res_btn, 2, 0)
        test_check_lyt.addWidget(render_full_hd_btn, 2, 1)

        asset_published_btn = QPushButton('Asset Published')
        grab_viewport_image_btn = QPushButton('Grab Viewport Image')
        slack_utils_lyt.addWidget(asset_published_btn, 0, 0)
        slack_utils_lyt.addWidget(grab_viewport_image_btn, 0, 1)

        self.accordion.add_item('Utils', check_widget)

        # Export Alembic/Standin File
        export_tab = QTabWidget()
        self.accordion.add_item('Generate Alembic', export_tab)

        export_abc_widget = QWidget()
        export_abc_layout = QHBoxLayout()
        export_abc_widget.setLayout(export_abc_layout)
        gen_abc_btn = QPushButton('Generate')
        export_abc_layout.addWidget(gen_abc_btn)

        export_standin_widget = QWidget()
        export_standin_layout = QHBoxLayout()
        export_standin_widget.setLayout(export_standin_layout)
        self.prepare_standin_btn = QPushButton('Setup')
        self.prepare_standin_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sep_lbl = QLabel()
        path = "<span style='color:#E2AC2C'> &#9656; </span>"
        path = "<big>%s</big>" % path
        sep_lbl.setText(path)
        self.gen_standin_btn = QPushButton('Generate')
        self.gen_standin_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.gen_standin_btn.setEnabled(False)
        export_standin_layout.addWidget(self.prepare_standin_btn)
        export_standin_layout.addWidget(sep_lbl)
        export_standin_layout.addWidget(self.gen_standin_btn)

        test_asset_files_widget = QWidget()
        test_asset_files_layout = QHBoxLayout()
        test_asset_files_widget.setLayout(test_asset_files_layout)
        self.test_asset_files_btn = QPushButton('Setup')
        test_asset_files_layout.addWidget(self.test_asset_files_btn)

        export_tab.addTab(export_abc_widget, 'Alembic')
        export_tab.addTab(export_standin_widget, 'Standin')
        export_tab.addTab(test_asset_files_widget, 'Test')

        valid_textures_path_btn.clicked.connect(self._on_valid_textures_path)
        textures_folder_empty_btn.clicked.connect(self._on_textures_folder_empty)
        textures_file_size_btn.clicked.connect(self._on_textures_file_size)
        valid_model_path_btn.clicked.connect(self._on_valid_model_path)
        valid_proxy_path_btn.clicked.connect(self._on_valid_proxy_path)
        check_model_main_group_btn.clicked.connect(self._on_check_model_main_group)
        check_proxy_main_group_btn.clicked.connect(self._on_check_proxy_main_group)
        model_has_no_shaders_btn.clicked.connect(self._on_model_has_no_shaders)
        proxy_has_no_shaders_btn.clicked.connect(self._on_proxy_has_no_shaders)
        clean_render_layer_nodes_btn.clicked.connect(self._on_clean_render_layer_nodes)
        valid_shading_path_btn.clicked.connect(self._on_valid_shading_path)
        import_shading_file_btn.clicked.connect(self._on_import_shading_file)
        check_shading_main_group_btn.clicked.connect(self._on_check_shading_main_group)
        check_shading_shaders.clicked.connect(self._on_check_shaders)
        all_textures_checks_btn.clicked.connect(self._on_all_textures_checks)
        transfer_uvs_btn.clicked.connect(self._on_transfer_uvs)
        remove_type_tag_data_attrs_btn.clicked.connect(self._on_remove_type_tag_data_attrs)
        clean_file_nodes.clicked.connect(self._on_clean_file_nodes)
        clean_model_file_btn.clicked.connect(self._on_clean_model_file)
        clean_proxy_file_btn.clicked.connect(self._on_clean_proxy_file)
        valid_rig_path_btn.clicked.connect(self._on_valid_rig_path)
        valid_builder_path_btn.clicked.connect(self._on_valid_builder_path)
        build_rig_btn.clicked.connect(self._on_build_rig)
        lock_rig_btn.clicked.connect(self._on_lock_rig)
        save_rig_btn.clicked.connect(self._on_save_rig)
        new_rig_version_btn.clicked.connect(self._on_new_rig_version)
        model_proxy_hires_groups_btn.clicked.connect(self._on_model_proxy_hires_groups)
        create_tag_btn.clicked.connect(self._on_create_tag)
        check_tag_btn.clicked.connect(self._on_check_tag)
        update_tag_btn.clicked.connect(self._on_update_tag)
        open_skin_weights_saver_btn.clicked.connect(self._on_open_skinweights_saver)
        export_skin_weights_btn.clicked.connect(self._on_export_skin_weights)
        import_skin_weight_btn.clicked.connect(self._on_import_skin_weights)
        print_texture_files.clicked.connect(self._on_print_texture_files)
        update_textures_paths_btn.clicked.connect(self._on_update_textures_path)
        clean_textures_paths_btn.clicked.connect(self._on_clean_textures_path)
        export_shading_file_btn.clicked.connect(self._on_export_shading_file)
        rename_shaders_btn.clicked.connect(self._on_rename_shaders)
        export_shaders_btn.clicked.connect(self._on_export_shaders)
        clean_render_layer_nodes2_btn.clicked.connect(self._on_clean_render_layer_nodes)
        delete_scene_shaders_btn.clicked.connect(self._on_delete_scene_shaders)
        ref_neutral_light_rig_btn.clicked.connect(self._on_reference_neutral_light_rig)
        sync_shaders_btn.clicked.connect(self._on_sync_shaders)
        render_low_res_btn.clicked.connect(self._on_render_low_res)
        render_mid_res_btn.clicked.connect(self._on_render_mid_res)
        render_high_res_btn.clicked.connect(self._on_render_high_res)
        render_full_hd_btn.clicked.connect(self._on_render_full_hd)
        sync_asset_btn.clicked.connect(self._on_sync_asset)
        lock_file_btn.clicked.connect(self._on_lock_file)
        new_version_btn.clicked.connect(self._on_new_file_version)
        asset_published_btn.clicked.connect(self._on_asset_published)
        grab_viewport_image_btn.clicked.connect(self._on_grab_viewport_image)
        gen_abc_btn.clicked.connect(lambda: pipelineutils.generate_alembic_file(self.asset_name_line.text()))
        self.prepare_standin_btn.clicked.connect(self._on_prepare_standin)
        self.gen_standin_btn.clicked.connect(self._on_generate_standin)
        self.test_asset_files_btn.clicked.connect(lambda: pipelineutils.test_asset_pipeline_files(self.asset_name_line.text()))

    def _on_valid_textures_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidTexturesPath(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_textures_folder_empty(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.TexturesFolderIsEmpty(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_textures_file_size(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.TextureFileSize(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_valid_model_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidModelPath(asset=weakref.ref(asset), log=log)
        check.check()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        log.write('Opening model file in Maya ...')
        sys.solstice.dcc.open_file(model_path, force=True)

    def _on_valid_proxy_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidProxyPath(asset=weakref.ref(asset), log=log)
        check.check()
        proxy_path = asset.get_asset_file(file_type='proxy', status='working')
        if proxy_path is None or not os.path.isfile(proxy_path):
            return False
        log.write('Opening proxy model file in Maya ...')
        sys.solstice.dcc.open_file(proxy_path, force=True)

    def _on_check_model_main_group(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        if sys.solstice.dcc.scene_path() != model_path:
            log.write('Opening model file in Maya ...')
            sys.solstice.dcc.open_file(model_path, force=True)
        check = assetchecks.CheckModelMainGroup(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_check_proxy_main_group(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        proxy_path = asset.get_asset_file(file_type='proxy', status='working')
        if proxy_path is None or not os.path.isfile(proxy_path):
            return False
        if sys.solstice.dcc.scene_path() != proxy_path:
            log.write('Opening proxy file in Maya ...')
            sys.solstice.dcc.open_file(proxy_path, force=True)
        check = assetchecks.CheckModelProxyMainGroup(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_model_has_no_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        if sys.solstice.dcc.scene_path() != model_path:
            log.write('Opening model file in Maya ...')
            sys.solstice.dcc.open_file(model_path, force=True)
        check = assetchecks.ModelHasNoShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_proxy_has_no_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        proxy_path = asset.get_asset_file(file_type='proxy', status='working')
        if proxy_path is None or not os.path.isfile(proxy_path):
            return False
        if sys.solstice.dcc.scene_path() != proxy_path:
            log.write('Opening proxy file in Maya ...')
            sys.solstice.dcc.open_file(proxy_path, force=True)
        check = assetchecks.ProxyHasNoShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_clean_render_layer_nodes(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        render_layer_found = False
        for render_layer in sys.solstice.dcc.list_nodes(node_type='renderLayer'):
            if render_layer != 'defaultRenderLayer':
                log.write('Removing render layer: {} ...'.format(render_layer))
                sys.solstice.dcc.delete_object(render_layer)
                render_layer_found = True

        if render_layer_found:
            log.write_ok('All render layers removed!')
        else:
            log.write('Current scene has no render layer nodes!')

    def _on_model_proxy_hires_groups(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.RigProxyHiresGroups(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_create_tag(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()

        valid_obj = None
        if sys.solstice.dcc.object_exists(asset.name):
            objs = sys.solstice.dcc.list_nodes(node_name=asset.name)
            for obj in objs:
                parent = sys.solstice.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                sys.solstice.logger.error('Main group is not valid. Please change it manually to {}'.format(asset.name))
                return False

        # Check if main group has a valid tag node connected
        valid_tag_data = False
        main_group_connections = sys.solstice.dcc.list_source_destination_connections(valid_obj)
        for connection in main_group_connections:
            attrs = sys.solstice.dcc.list_user_attributes(connection)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        if not valid_tag_data:
            sys.solstice.logger.warning('Main group has not a valid tag data node connected to it. Creating it ...')
            try:
                sys.solstice.dcc.select_object(valid_obj)
                tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(asset.category)
                sys.solstice.dcc.clear_selection()
                valid_tag_data = False
                main_group_connections = sys.solstice.dcc.list_source_destination_connections(valid_obj)
                for connection in main_group_connections:
                    attrs = sys.solstice.dcc.list_user_attributes(connection)
                    if attrs and type(attrs) == list:
                        for attr in attrs:
                            if attr == 'tag_type':
                                valid_tag_data = True
                if not valid_tag_data:
                    sys.solstice.logger.error('Impossible to create tag data node. Please contact TD team to fix this ...')
                    return False
            except Exception as e:
                sys.solstice.logger.error('Impossible to create tag data node. Please contact TD team to fix this ...')
                sys.solstice.logger.error(str(e))
                return False

        tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not sys.solstice.dcc.object_exists(tag_data_node):
            sys.solstice.logger.error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        # Connect proxy group to tag data node
        valid_connection = tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if not valid_connection:
            sys.solstice.logger.warning(
                'Error while connecting Proxy Group to tag data node!  Check Maya editor for more info about the error!')

        # Connect hires group to tag data node
        valid_connection = tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if not valid_connection:
            sys.solstice.logger.warning(
                'Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            return False

        # Getting shaders info data
        shaders_file = shaderlibrary.ShaderLibrary.get_asset_shader_file_path(asset=asset)
        if not os.path.exists(shaders_file):
            sys.solstice.logger.warning(
                'Shaders JSON file for asset {0} does not exists: {1}'.format(asset.name, shaders_file))

        with open(shaders_file) as f:
            shader_data = json.load(f)
        if shader_data is None:
            sys.solstice.logger.warning(
                'Shaders JSON file for asset {0} is not valid: {1}'.format(asset.name, shaders_file))

        hires_grp = None
        hires_grp_name = '{}_hires_grp'.format(asset.name)
        children = sys.solstice.dcc.list_relatives(node=valid_obj, all_hierarchy=True, full_path=True, relative_type='transform')
        if children:
            for child in children:
                child_name = child.split('|')[-1]
                if child_name == hires_grp_name:
                    hires_children = sys.solstice.dcc.list_relatives(node=child_name, all_hierarchy=True,
                                                           relative_type='transform')
                    if len(hires_children) > 0:
                        if hires_grp is None:
                            hires_grp = child
                        else:
                            sys.solstice.logger.error('Multiple Hires groups in the file. Please check it!')
                            return False
        if not hires_grp:
            sys.solstice.logger.error('No hires group found ...')
            return False
        hires_meshes = sys.solstice.dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True,
                                             relative_type='transform')

        # Checking if shader data is valid
        check_meshes = dict()
        for shading_mesh, shading_group in shader_data.items():
            shading_name = shading_mesh.split('|')[-1]
            check_meshes[shading_mesh] = False
            for model_mesh in hires_meshes:
                mesh_name = model_mesh.split('|')[-1]
                if shading_name == mesh_name:
                    check_meshes[shading_mesh] = True

        valid_meshes = True
        for mesh_name, mesh_check in check_meshes.items():
            if mesh_check is False:
                sys.solstice.logger.error('Mesh {} not found in both model and shading file ...'.format(mesh_name))
                valid_meshes = False
        if not valid_meshes:
            sys.solstice.logger.error('Some shading meshes and model hires meshes are missed. Please contact TD!')
            return False

        # Create if necessary shaders attribute in model tag data node
        if not tag_data_node or not sys.solstice.dcc.object_exists(tag_data_node):
            sys.solstice.logger.error('Tag data does not exists in the current scene!'.format(tag_data_node))
            return False

        attr_exists = sys.solstice.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
        if attr_exists:
            sys.solstice.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')
        else:
            sys.solstice.dcc.add_string_attribute(node=tag_data_node, attribute_name='shaders')
            attr_exists = sys.solstice.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
            if not attr_exists:
                sys.solstice.logger.error('No Shaders attribute found on model tag data node: {}'.format(tag_data_node))
                return False

        sys.solstice.dcc.unlock_attribute(node=tag_data_node, attribute_name='shaders')
        sys.solstice.dcc.set_string_attribute_value(node=tag_data_node, attribute_name='shaders', attribute_value=shader_data)
        sys.solstice.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')

        return True


    def _on_check_tag(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        if rig_path is None or not os.path.isfile(rig_path):
            return False
        log.write('Opening rig file in Maya ...')
        sys.solstice.dcc.open_file(rig_path, force=True)
        check = assetchecks.CheckRigTag(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_update_tag(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        if rig_path is None or not os.path.isfile(rig_path):
            return False
        log.write('Opening rig file in Maya ...')
        sys.solstice.dcc.open_file(rig_path, force=True)
        check = assetchecks.UpdateTag(asset=weakref.ref(asset), file_type='rig', log=log)
        check.check()

    def _on_open_skinweights_saver(self):
        from solstice.pipeline.externals import bSkinSaver
        bSkinSaver.showUI()

    def _on_export_skin_weights(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()

        print('Exporting Skin weights ...')

    def _on_import_skin_weights(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()

        print('Importing Skin weights ...')

    def _on_print_texture_files(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        invalid_textures = list()
        solstice_var = os.path.normpath(os.environ['SOLSTICE_PROJECT'])
        all_file_nodes = cmds.ls(et="file")
        for eachFile in all_file_nodes:
            current_file = cmds.getAttr("%s.fileTextureName" % eachFile)
            computed_file = browserutils.clean_path(current_file.replace('$SOLSTICE_PROJECT', solstice_var))
            file_exists = os.path.isfile(computed_file)
            if not file_exists or '__working__' in computed_file:
                invalid_textures.append((current_file, eachFile))
            for print_fn in [print, log.write]:
                print_fn('{} <=====> {} <=====> {}'.format(current_file, eachFile, file_exists))
        if invalid_textures:
            for print_fn in [print, log.write_error]:
                print_fn('>>> INVALID TEXTURES FOUND <<<')

            for txt_data in invalid_textures:
                for print_fn in [print, log.write]:
                    print_fn('{} <=====> {}'.format(txt_data[0], txt_data[1]))
        else:
            for print_fn in [print, log.write_ok]:
                print_fn('>>> ALL TEXTURE FILES ARE VALID!!! <<<')
        for print_fn in [print, log.write]:
            print_fn('\n\n')

    def _on_valid_rig_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidRigPath(asset=weakref.ref(asset), log=log)
        check.check()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        if rig_path is None or not os.path.isfile(rig_path):
            return False
        log.write('Opening rig file in Maya ...')
        sys.solstice.dcc.open_file(rig_path, force=True)

    def _on_valid_builder_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidBuilderPath(asset=weakref.ref(asset), log=log)
        check.check()
        builder_path = asset.get_asset_file(file_type='builder', status='working')
        if builder_path is None or not os.path.isfile(builder_path):
            return False
        log.write('Opening builder file in Maya ...')
        sys.solstice.dcc.open_file(builder_path, force=True)

    def _on_build_rig(self):
        asset = self._get_asset()
        if not asset:
            return
        asset.build_rig()

    def _on_lock_rig(self):
        asset = self._get_asset()
        if not asset:
            return

        log = run_console()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        if os.path.isfile(rig_path):
            log.write('Locking Rig File: {}'.format(rig_path))
            artella.lock_file(rig_path, force=True)

    def _on_save_rig(self):
        asset = self._get_asset()
        if not asset:
            return

        log = run_console()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        log.write('Saving Rig File: {}'.format(rig_path))
        if os.path.isfile(rig_path):
            artella.lock_file(rig_path, force=True)

        try:
            sys.solstice.dcc.save_current_scene(file_path=rig_path)
            mayautils.clean_student_line(rig_path)
            log.write_ok('Rig File saved successfully!')
        finally:
            if os.path.isfile(rig_path):
                artella.unlock_file(rig_path)

    def _on_new_rig_version(self):
        asset = self._get_asset()
        if not asset:
            return

        log = run_console()
        rig_path = asset.get_asset_file(file_type='rig', status='working')
        if not rig_path or not os.path.isfile(rig_path):
            log.write_error('No Rig Path found: {}!'.format(rig_path))
            return

        new_version = messagehandler.MessageHandler().show_confirm_dialog(
            'Do you want to create new version of rig file in Artella?')
        if new_version:
            log.write('Creating new rig version in Artella: {}'.format(asset.name))
            artella.upload_new_asset_version(rig_path, comment='New Rig {} version'.format(asset.name),
                                             skip_saving=True)
            log.write_ok('New version for rig submitted into Artella server')

    def _on_transfer_uvs(self):
        sel = cmds.ls(sl=True)
        first = sel.pop(0)
        for obj in sel:
            cmds.select([first, obj])
            cmds.transferAttributes(sampleSpace=4, transferUVs=2, transferColors=2)

    def _on_remove_type_tag_data_attrs(self, group_type='model'):
        asset = self._get_asset()
        if not asset:
            return

        cmds.setAttr('{}_{}.tag_data'.format(asset.name, group_type.upper()), lock=False)
        cmds.deleteAttr('{}_{}.type'.format(asset.name, group_type.upper()))
        cmds.deleteAttr('{}_{}.tag_data'.format(asset.name, group_type.upper()))

    def _on_clean_file_nodes(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        file_found = False
        for render_layer in sys.solstice.dcc.list_nodes(node_type='file'):
            log.write('Removing file node: {} ...'.format(render_layer))
            sys.solstice.dcc.delete_object(render_layer)
            file_found = True

        if file_found:
            log.write_ok('All file nodes removed!')
        else:
            log.write('Current scene has no file nodes!')

    def _on_clean_model_file(self):
        asset = self._get_asset()
        if not asset:
            return

        tag_data = asset.get_tag_data_node()
        if tag_data:
            proxy_grp = cmds.listConnections('{}.hires'.format(tag_data.get_node()))
            if not proxy_grp:
                return
            proxy_grp = proxy_grp[0]
            unparent_children = [child for child in sys.solstice.dcc.list_children(proxy_grp, all_hierarchy=False, children_type='transform', full_path=False) if 'Constraint' not in child]
            for child in unparent_children:
                sys.solstice.dcc.set_parent(child, None)
            children = [child for child in sys.solstice.dcc.list_children(asset.name, all_hierarchy=False, children_type='transform', full_path=False)]
            for child in children:
                sys.solstice.dcc.delete_object(child)
            for obj in unparent_children:
                sys.solstice.dcc.set_parent(obj, asset.name)
            sys.solstice.dcc.rename_node(asset.name, '{}_MODEL'.format(asset.name))
            sys.solstice.dcc.clear_selection()

            self._on_remove_type_tag_data_attrs('model')

    def _on_clean_proxy_file(self):
        asset = self._get_asset()
        if not asset:
            return

        tag_data = asset.get_tag_data_node()
        if tag_data:
            proxy_grp = cmds.listConnections('{}.proxy'.format(tag_data.get_node()))
            if not proxy_grp:
                return
            proxy_grp = proxy_grp[0]
            unparent_children = [child for child in sys.solstice.dcc.list_children(proxy_grp, all_hierarchy=False, children_type='transform', full_path=False) if 'Constraint' not in child]
            for child in unparent_children:
                sys.solstice.dcc.set_parent(child, None)
            children = [child for child in sys.solstice.dcc.list_children(asset.name, all_hierarchy=False, children_type='transform', full_path=False)]
            for child in children:
                sys.solstice.dcc.delete_object(child)
            for obj in unparent_children:
                sys.solstice.dcc.set_parent(obj, asset.name)
            sys.solstice.dcc.rename_node(asset.name, '{}_PROXY'.format(asset.name))
            sys.solstice.dcc.clear_selection()

            self._on_remove_type_tag_data_attrs('proxy')

    def _on_import_shading_file(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Importing shading file {} ...'.format(shading_path))
        artella.import_file_in_maya(shading_path)

    def _on_valid_shading_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ValidShadingPath(asset=weakref.ref(asset), log=log)
        check.check()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sys.solstice.dcc.open_file(shading_path, force=True)

    def _on_check_shading_main_group(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sys.solstice.dcc.open_file(shading_path, force=True)
        check = assetchecks.CheckShadingMainGroup(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_check_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sys.solstice.dcc.open_file(shading_path, force=True)
        check = assetchecks.CheckShadingShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_update_textures_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.UpdateTexturesPath(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_clean_textures_path(self):
        all_file_nodes = cmds.ls(et="file")
        for each_file in all_file_nodes:
            current_file = os.path.normpath(cmds.getAttr("%s.fileTextureName" % each_file))
            cmds.setAttr('{}.fileTextureName'.format(each_file), current_file.replace('\\', '/'), type='string')

    def _on_export_shading_file(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        do_continue = messagehandler.MessageHandler().show_confirm_dialog(
            'Do you want to submit a new version of the Shading file to Artella?')
        if do_continue:
            publish = True
        else:
            publish = False
        check = assetchecks.ExportShaderJSON(asset=weakref.ref(asset), log=log, publish=publish)
        check.check()

    def _on_rename_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sys.solstice.dcc.open_file(shading_path, force=True)
        check = assetchecks.RenameShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_export_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sys.solstice.dcc.open_file(shading_path, force=True)
        do_continue = messagehandler.MessageHandler().show_confirm_dialog(
            'Do you want to submit export shader files to Artella?')
        if do_continue:
            publish = True
        else:
            publish = False
        check = assetchecks.ExportShaders(asset=weakref.ref(asset), log=log, publish=publish)
        check.check()

    def _on_delete_scene_shaders(self):
        if not sp.is_maya():
            return

        mats = cmds.ls(mat=True)
        for m in mats:
            if m not in ['lambert1', 'particleCloud1']:
                cmds.delete(m)
        shading_groups = cmds.ls(type='shadingEngine')
        for sg in shading_groups:
            if sg not in ['initialShadingGroup', 'initialParticleSE']:
                cmds.delete(sg)

        shapes = cmds.ls(type=['mesh', 'nurbsSurface'])
        for shp in shapes:
            cmds.sets(shp, edit=True, forceElement='initialShadingGroup')

    def _on_prepare_standin(self):
        valid_prepare = pipelineutils.setup_standin_export(self.asset_name_line.text())
        self.gen_standin_btn.setEnabled(bool(valid_prepare))
        self.prepare_standin_btn.setEnabled(not bool(valid_prepare))

    def _on_generate_standin(self):
        valid_export = pipelineutils.generate_standin_file(self.asset_name_line.text())
        if not valid_export:
            sys.solstice.dcc.new_file(force=True)
        self.gen_standin_btn.setEnabled(False)
        self.prepare_standin_btn.setEnabled(True)

    def _on_all_textures_checks(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        log.clear()
        self._on_valid_textures_path()
        self._on_textures_folder_empty()
        self._on_textures_file_size()

    def _on_all_model_checks(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        log.clear()
        self._on_valid_model_path()
        self._on_check_model_main_group()
        self._on_model_has_no_shaders()
        self._on_model_proxy_hires_groups()

    def _on_all_shading_checks(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        log.clear()
        self._on_valid_shading_path()
        self._on_check_shading_main_group()
        self._on_check_shaders()

    def _on_reference_neutral_light_rig(self):
        if not sp.is_maya():
            return
        lightrigs.LightRigManager.reference_light_rig('Neutral Contrast', do_save=False)

    def _on_sync_shaders(self):
        if not sp.is_maya():
            return
        shaderlibrary.ShaderLibrary.load_all_scene_shaders()

    def _on_render_low_res(self):
        if not sp.is_maya():
            return
        cmds.RenderViewWindow()
        arnoldRender(480, 270, True, True, 'persp', '-layer defaultRenderLayer')

    def _on_render_mid_res(self):
        if not sp.is_maya():
            return
        cmds.RenderViewWindow()
        arnoldRender(960, 540, True, True, 'persp', '-layer defaultRenderLayer')

    def _on_render_high_res(self):
        if not sp.is_maya():
            return
        cmds.RenderViewWindow()
        arnoldRender(1280, 720, True, True, 'persp', '-layer defaultRenderLayer')

    def _on_render_full_hd(self):
        if not sp.is_maya():
            return
        cmds.RenderViewWindow()
        arnoldRender(1920, 1080, True, True, 'persp', '-layer defaultRenderLayer')

    def _on_asset_published(self):
        asset = self._get_asset()
        if not asset:
            return

        slack.asset_published(asset.name)

    def _on_grab_viewport_image(self):
        view_image = mayautils.grab_viewport_image()
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                view_image.writeToFile(path, 'png')
                slack.new_viewport_image(os.path.normpath(path), os.path.basename(sys.solstice.dcc.scene_path()), channel_name='pipeline')
        finally:
            os.remove(path)


    def _on_sync_asset(self):
        asset = self._get_asset()
        if not asset:
            return

        asset.sync()

    def _on_lock_file(self):
        current_file = sys.solstice.dcc.scene_path()
        if os.path.isfile(current_file):
            artella.lock_file(current_file, force=True)

    def _on_new_file_version(self):
        current_file = sys.solstice.dcc.scene_path()
        if not os.path.isfile(current_file):
            return

        log = run_console()

        new_version = messagehandler.MessageHandler().show_confirm_dialog(
            'Do you want to create new version of file {} in Artella?'.format(current_file))
        if new_version:
            result = cmds.promptDialog(
                title='Comment',
                message='Enter Comment:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
            if result != 'OK':
                return

            comment = cmds.promptDialog(query=True, text=True)
            if not comment:
                return

        rel_path = os.path.relpath(current_file, sp.get_solstice_project_path())
        url_path = os.path.join(sp.get_artella_project_url(), os.path.dirname(rel_path)).replace('\\', '/')
        ret = urllib2.urlopen(url_path)
        if ret.code != 200:
            log.write_error('Artella URL {} does not exists! Impossible to submit new version of the file!'.format(url_path))
            return

        artella.upload_new_asset_version(current_file, comment=comment, skip_saving=True)
        slack.new_version(current_file, url_path, comment=comment)

        log.write_ok('New version for file {} submitted into Artella server'.format(os.path.basename(current_file)))

    def _get_asset(self, asset_name=None):
        if asset_name is None:
            asset_name = self.asset_name_line.text()

        if not asset_name:
            sys.solstice.logger.warning('Type an asset name first!')
            return
        asset = sp.find_asset(asset_name)
        if not asset:
            sys.solstice.logger.error('No asset found with name: {}'.format(asset_name))
            return

        return asset


class RiggingToolbox(BaseTDToolBoxWidget, object):
    def __init__(self, parent=None):
        super(RiggingToolbox, self).__init__('Rigging', parent)

    def custom_ui(self):
        super(RiggingToolbox, self).custom_ui()
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.props_rig = PropsRiggingWidget()
        self.tabs.addTab(self.props_rig, 'Props | Background Elements')


class PropsRiggingWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(PropsRiggingWidget, self).__init__(parent=parent)

    def custom_ui(self):
        super(PropsRiggingWidget, self).custom_ui()

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


class TDToolBoxMenu(QFrame, object):
    def __init__(self, parent=None):
        super(TDToolBoxMenu, self).__init__(parent=parent)

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


class TDToolBoxWidget(QFrame, object):
    def __init__(self, parent=None):
        super(TDToolBoxWidget, self).__init__(parent=parent)

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
        self.toolbox_menu = TDToolBoxMenu(parent=self)
        self.main_layout.addWidget(self.toolbox_menu)

        self.generic = PipelineToolbox(parent=self)
        self.props = RiggingToolbox(parent=self)
        for w in [self.generic, self.props]:
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


class SolsticeTDConsole(window.Window, object):

    name = 'Solstice_TDToolboxConsole'
    title = 'Solstice Tools - TD ToolBox Console'
    version = '1.0'

    def __init__(self):
        super(SolsticeTDConsole, self).__init__()

        self.windowClosed.connect(self._on_close_console)

    def custom_ui(self):
        super(SolsticeTDConsole, self).custom_ui()

        self.resize(600, 550)

        self.log = console.SolsticeConsole()
        self.log.write_ok('>>> TD TOOLBOX LOG <<<\n')
        self.log.write_ok('\n')
        self.main_layout.addWidget(self.log)

    def _on_close_console(self):
        global console_win
        console_win = None


class SolsticeTDToolbox(window.Window, object):

    name = 'Solstice_TDToolbox'
    title = 'Solstice Tools - TD ToolBox'
    version = '1.1'

    def __init__(self):
        super(SolsticeTDToolbox, self).__init__()

        self.windowClosed.connect(self._on_close_console)

    def custom_ui(self):
        super(SolsticeTDToolbox, self).custom_ui()

        self.resize(480, 700)

        self.toolbow_widget = TDToolBoxWidget(parent=self)
        self.main_layout.addWidget(self.toolbow_widget)

    def _on_close_console(self):
        global console_win
        if console_win:
            console_win.close()


def run_console():
    global console_win
    if not console_win:
        console_win = SolsticeTDConsole()
    console_win.show()

    return console_win.log


def run():
    win = SolsticeTDToolbox().show()

    return win
