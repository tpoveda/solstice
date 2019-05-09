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
import weakref

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import base, window, splitters, buttons, stack, accordion, console, messagehandler
from solstice.pipeline.utils import pipelineutils, rigutils, artellautils as artella

from solstice.pipeline.tools.sanitycheck.checks import assetchecks

if sp.is_maya():
    import maya.cmds as cmds
    from mtoa.cmds.arnoldRender import arnoldRender
    from solstice.pipeline.tools.lightrigs import lightrigs
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary

reload(pipelineutils)
reload(console)
reload(assetchecks)


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
        check_model_main_group_btn = QPushButton('Check Model Main Group')
        model_has_no_shaders_btn = QPushButton('Model Has No Shaders')
        model_proxy_hires_groups_btn = QPushButton('Setup Model Proxy/Hires Groups')
        check_tag_btn = QPushButton('Check Model Tag')
        update_tag_btn = QPushButton('Update Model Tag')
        delete_scene_shaders_btn = QPushButton('Delete Scene Shaders')
        import_shading_file_btn = QPushButton('Import Shading File')
        transfer_uvs_btn = QPushButton('Transfer UVs')
        model_check_lyt.addWidget(valid_model_path_btn, 0, 0)
        model_check_lyt.addWidget(check_model_main_group_btn, 0, 1)
        model_check_lyt.addWidget(model_has_no_shaders_btn, 1, 0)
        model_check_lyt.addWidget(model_proxy_hires_groups_btn, 1, 1)
        model_check_lyt.addWidget(check_tag_btn, 2, 0)
        model_check_lyt.addWidget(update_tag_btn, 2, 1)
        model_check_lyt.addWidget(delete_scene_shaders_btn, 3, 0)
        model_check_lyt.addWidget(import_shading_file_btn, 3, 1)
        model_check_lyt.addWidget(transfer_uvs_btn, 4, 0)

        shading_utils = QWidget()
        shading_check_lyt = QGridLayout()
        shading_utils.setLayout(shading_check_lyt)
        valid_shading_path_btn = QPushButton('Valid Shading Path')
        check_shading_main_group_btn = QPushButton('Check Shading Main Group')
        check_shading_shaders = QPushButton('Check Shaders')
        rename_shaders_btn = QPushButton('Rename Shaders')
        update_textures_paths_btn = QPushButton('Update Textures Paths')
        export_shading_file_btn = QPushButton('Export Shading JSON File')
        export_shaders_btn = QPushButton('Export Shaders')
        shading_check_lyt.addWidget(valid_shading_path_btn, 0, 0)
        shading_check_lyt.addWidget(check_shading_main_group_btn, 0, 1)
        shading_check_lyt.addWidget(check_shading_shaders, 1, 0)
        shading_check_lyt.addWidget(rename_shaders_btn, 1, 1)
        shading_check_lyt.addWidget(export_shading_file_btn, 2, 0)
        shading_check_lyt.addWidget(update_textures_paths_btn, 2, 1)
        shading_check_lyt.addWidget(export_shaders_btn, 3, 0)

        test_utils = QWidget()
        test_check_lyt = QGridLayout()
        test_utils.setLayout(test_check_lyt)

        utils_tab.addTab(textures_utils, 'Textures')
        utils_tab.addTab(model_utils, 'Model')
        utils_tab.addTab(shading_utils, 'Shading')
        utils_tab.addTab(test_utils, 'Tests')
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
        check_model_main_group_btn.clicked.connect(self._on_check_model_main_group)
        model_has_no_shaders_btn.clicked.connect(self._on_model_has_no_shaders)
        model_proxy_hires_groups_btn.clicked.connect(self._on_model_proxy_hires_groups)
        valid_shading_path_btn.clicked.connect(self._on_valid_shading_path)
        import_shading_file_btn.clicked.connect(self._on_import_shading_file)
        check_shading_main_group_btn.clicked.connect(self._on_check_shading_main_group)
        check_shading_shaders.clicked.connect(self._on_check_shaders)
        all_textures_checks_btn.clicked.connect(self._on_all_textures_checks)
        check_tag_btn.clicked.connect(self._on_check_tag)
        update_tag_btn.clicked.connect(self._on_update_tag)
        transfer_uvs_btn.clicked.connect(self._on_transfer_uvs)
        update_textures_paths_btn.clicked.connect(self._on_update_textures_path)
        export_shading_file_btn.clicked.connect(self._on_export_shading_file)
        rename_shaders_btn.clicked.connect(self._on_rename_shaders)
        export_shaders_btn.clicked.connect(self._on_export_shaders)
        delete_scene_shaders_btn.clicked.connect(self._on_delete_scene_shaders)
        ref_neutral_light_rig_btn.clicked.connect(self._on_reference_neutral_light_rig)
        sync_shaders_btn.clicked.connect(self._on_sync_shaders)
        render_low_res_btn.clicked.connect(self._on_render_low_res)
        render_mid_res_btn.clicked.connect(self._on_render_mid_res)
        render_high_res_btn.clicked.connect(self._on_render_high_res)
        render_full_hd_btn.clicked.connect(self._on_render_full_hd)
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
        sp.dcc.open_file(model_path, force=True)

    def _on_check_model_main_group(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        log.write('Opening model file in Maya ...')
        sp.dcc.open_file(model_path, force=True)
        check = assetchecks.CheckModelMainGroup(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_model_has_no_shaders(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        log.write('Opening model file in Maya ...')
        sp.dcc.open_file(model_path, force=True)
        check = assetchecks.ModelHasNoShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_model_proxy_hires_groups(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.ModelProxyHiresGroups(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_check_tag(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        log.write('Opening model file in Maya ...')
        sp.dcc.open_file(model_path, force=True)
        check = assetchecks.CheckModelTag(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_update_tag(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        model_path = asset.get_asset_file(file_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            return False
        log.write('Opening model file in Maya ...')
        sp.dcc.open_file(model_path, force=True)
        check = assetchecks.UpdateModelTag(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_transfer_uvs(self):
        sel = cmds.ls(sl=True)
        first = sel.pop(0)
        for obj in sel:
            cmds.select([first, obj])
            cmds.transferAttributes(sampleSpace=4, transferUVs=2, transferColors=2)

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
        sp.dcc.open_file(shading_path, force=True)

    def _on_check_shading_main_group(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        shading_path = asset.get_asset_file(file_type='shading', status='working')
        if shading_path is None or not os.path.isfile(shading_path):
            return False
        log.write('Opening shading file in Maya ...')
        sp.dcc.open_file(shading_path, force=True)
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
        sp.dcc.open_file(shading_path, force=True)
        check = assetchecks.CheckShadingShaders(asset=weakref.ref(asset), log=log)
        check.check()

    def _on_update_textures_path(self):
        asset = self._get_asset()
        if not asset:
            return
        log = run_console()
        check = assetchecks.UpdateTexturesPath(asset=weakref.ref(asset), log=log)
        check.check()

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
        sp.dcc.open_file(shading_path, force=True)
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
        sp.dcc.open_file(shading_path, force=True)
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
            sp.dcc.new_file(force=True)
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
        shaderlibrary.ShaderLibrary.load_scene_shaders()

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

    def _get_asset(self, asset_name=None):
        if asset_name is None:
            asset_name = self.asset_name_line.text()

        if not asset_name:
            sp.logger.warning('Type an asset name first!')
            return
        asset = sp.find_asset(asset_name)
        if not asset:
            sp.logger.error('No asset found with name: {}'.format(asset_name))
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

        self.resize(400, 550)

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
