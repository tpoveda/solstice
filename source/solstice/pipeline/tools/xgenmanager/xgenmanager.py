#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to import/export XGen data
"""

from __future__ import print_function, division, absolute_import

from solstice.pipeline.tools.shaderlibrary import shaderlibrary

__author__ = "Enrique Velasco"
__license__ = "MIT"
__maintainer__ = "Enrique Velasco"
__email__ = "enriquevelmai@hotmail.com"

import sys
from functools import partial

import maya.cmds as mc
import pymel.core as pm

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt import QtWidgets, QtCore, QtGui
from solstice.pipeline import tools
from solstice.pipeline.gui import window, animations

import xgenm as xg
import xgenm.XgExternalAPI as xge
import xgenm.xgGlobal as xgg


########################################################################################################################
# class definition
########################################################################################################################
class ControlXgenUi(window.Window):
    # global class variables
    name = 'xgenmanager'  # Do not change or UI load'll fail and Maya'll crash painfully
    title = 'Solstice Tools - XGen Manager'
    version = '1.0'
    docked = False

    ####################################################################################################################
    # class constructor
    ####################################################################################################################
    def __init__(self, **kwargs):

        self.shaders_dict = dict()
        self.scalps_list = list()
        self.collection_name = None

        super(ControlXgenUi, self).__init__(**kwargs)

    ####################################################################################################################
    # ui definitions
    ####################################################################################################################
    def custom_ui(self):
        super(ControlXgenUi, self).custom_ui()

        self.set_logo('solstice_xgen_manager')

        self.resize(500, 400)
        self.ui = tools.load_tool_ui(self.name)
        self.main_layout.addWidget(self.ui)
        self._populate_data()
        self._connect_componets_to_actions()

    def _populate_data(self):
        self.ui.collection_cbx.addItems(self._get_all_collections())
        self.ui.renderer_cbx.addItems(["None", "Arnold Renderer"])
        self.ui.renderer_cbx.setCurrentIndex(1)
        self.ui.renderer_mode_cbx.addItems(["Live", "Batch Render"])
        self.ui.renderer_mode_cbx.setCurrentIndex(1)
        self.ui.motion_blur_cbx.addItems(["Use Global Settings", "On", "Off"])
        self.ui.extra_depth_sbx.setValue(16)
        self.ui.extra_samples_sbx.setValue(0)

        characters_to_set = sp.os.listdir(sp.os.path.join(sp.get_solstice_assets_path(), "Characters"))
        characters_to_set.insert(0, "")
        self.ui.export_character_cbx.addItems(characters_to_set)
        self.ui.import_character_cbx.addItems(characters_to_set)

    def _connect_componets_to_actions(self):
        self.ui.export_go_btn.clicked.connect(self._do_export)
        self.ui.importer_go_btn.clicked.connect(self._do_import)
        self.ui.path_browse_btn.clicked.connect(self._save_file)
        self.ui.groom_file_browser_btn.clicked.connect(self._open_file)
        self.ui.geometry_scalpt_grp_btn.clicked.connect(
            partial(self._load_selection_to_line, self.ui.geometry_scalpt_grp_txf))
        self.ui.export_character_cbx.currentIndexChanged.connect(self._set_path)

    ####################################################################################################################
    # UI functions set
    ####################################################################################################################
    def _set_path(self):
        """
        Sets path to the text widget
        """
        asset_name = self.ui.export_character_cbx.currentText()
        if asset_name:
            save_path = sp.os.path.join(sp.get_solstice_assets_path(), "Characters", asset_name, "__working__",
                                        "groom", "groom_package.groom")
            self.ui.path_txf.setText(save_path)
            return
        self.ui.path_txf.setText("")

    def _load_selection_to_line(self, qt_object):
        """
        Load selection into the given texfiled
        :param qt_object: QTexField object where to set the selected items
        """
        # set the string to load
        selection = mc.ls(sl=True)
        text_to_add = '"{}"'.format(selection[0])
        if len(selection) > 1:
            for obj in selection[1:]:
                text_to_add += ';"{}"'.format(obj)

        # set text to the object
        qt_object.setText(text_to_add)

    def _get_all_collections(self):
        """
        Get all collections in the maya scene
        :return: list, with the collection names
        """
        collections_list = list()
        for item in xg.palettes():
            collections_list.append(item)
        return collections_list

    def _open_file(self):
        """
        Open file dialog, and sets the path to the QTexField
        """
        file_path, _ext = QtWidgets.QFileDialog.getOpenFileName(self, dir=sp.os.environ['home'],
                                                                filter='Folder(.groom)')
        self.ui.groom_package_txf.setText(str(file_path))

    def _save_file(self):
        """
        Save file dialog, and sets the path to the QTexField
        :return:
        """
        file_path, _ext = QtWidgets.QFileDialog.getSaveFileName(self, dir=sp.os.environ['home'],
                                                                filter='Folder(.groom)')
        self.ui.path_txf.setText(str(file_path))

    ####################################################################################################################
    # class core functions
    ####################################################################################################################
    def _do_export(self):
        """
        Executes the export of the choose collection
        """

        # Get data from ui
        self.collection_name = self.ui.collection_cbx.currentText()
        self.shaders_dict = self._get_shaders()
        self.scalps_list = self._get_scalps()
        ptx_folder = self._get_root_folder()
        export_path = self.ui.path_txf.text()
        self.character = self.ui.export_character_cbx.currentText()
        comment = self.ui.comment_pte.toPlainText()

        # analise if there is an export folder
        if not export_path:
            if not self.character:
                raise ValueError("export path must be specified")

        ################################################################################################################
        # Export objects into a .groom folder
        ################################################################################################################
        # generate export path
        if export_path:
            self.export_path_folder = export_path
            if not '.groom' in export_path:
                self.export_path_folder = export_path + '.groom'
        else:
            self.export_path_folder = sp.os.path.join(sp.get_solstice_assets_path(), "Characters", self.character,
                                                      "__working__", "groom", "groom_package.groom")

        # if the folder already exists delete it, and create a new one
        self.delete_artella_folder(self.export_path_folder)
        sp.os.makedirs(self.export_path_folder)

        # get the ptx path
        if '${PROJECT}' in ptx_folder:
            project_path = str(mc.workspace(fullName=True, q=True))
            ptx_folder = sp.os.path.join(project_path, ptx_folder.replace('${PROJECT}', ''))
        sys.solstice.logger.debug("XGEN || All data parsed")
        self.ui.progress_lbl.setText("Exporting Files (PTX)")
        # copy the ptx files
        sp.shutil.copytree(ptx_folder, sp.os.path.join(self.export_path_folder, self.collection_name))
        sys.solstice.logger.debug("XGEN || PTEX files exported")

        # export xgen file
        xg.exportPalette(palette=str(self.collection_name),
                         fileName=str("{}/{}.xgen".format(self.export_path_folder, self.collection_name)))
        self.ui.progress_lbl.setText("Exporting Files (.XGEN)")
        sys.solstice.logger.debug("XGEN || Collection file exported")

        # export sculpts
        mc.select(self.scalps_list, replace=True)
        mc.file(rename=sp.os.path.join(self.export_path_folder, 'sculpts.ma'))
        mc.file(es=True, type='mayaAscii')
        mc.select(cl=True)
        self.ui.progress_lbl.setText("Exporting Sculpts (.MA)")
        sys.solstice.logger.debug("XGEN || Sculpts Exported")

        # export material
        exporter = shaderlibrary.ShaderExporter(shaders=self.shaders_dict.values(), parent=self)
        exporter.export_shaders(publish=comment)

        self.ui.progress_lbl.setText("Exporting Material (.sshader)")
        sys.solstice.logger.debug("XGEN || Material Exported")

        # export mapping
        with open(sp.os.path.join(self.export_path_folder, 'shader.json'), 'w') as fp:
            sp.json.dump(self.shaders_dict, fp)
        self.ui.progress_lbl.setText("Exporting Mapping (.JSON)")
        sys.solstice.logger.debug("XGEN || Mapping Exported")

        # add file to artella
        if comment:
            self._add_file_to_artella(file_path_global=self.export_path_folder, comment=comment)
            sys.solstice.logger.debug("XGEN || Files added to artella")
        else:
            sys.solstice.logger.warning("XGEN || Files are not been loaded to Artella. Do it manually")

    def _do_import(self):
        """
        Imports the grom into the scene        
        """
        import_folder = self.ui.groom_package_txf.text()

        if not import_folder:
            raise ValueError("Import path must be specified")

        # build scene
        mc.loadPlugin('xgenToolkit.mll')

        import_path_folder = import_folder.replace('.zip', '')
        _, groom_asset = sp.os.path.split(import_path_folder)
        xgen_file = [f for f in sp.os.listdir(import_path_folder) if f.endswith('.xgen')][-1]
        map_folder = [sp.os.path.join(import_path_folder, d) for d in sp.os.listdir(import_path_folder) if
                      sp.os.path.isdir(sp.os.path.join(import_path_folder, d))][0]

        # import maya scenes
        mc.file(sp.os.path.join(import_folder, 'scalps.ma'), i=True, type="mayaAscii", ignoreVersion=True,
                mergeNamespacesOnClash=False, gl=True, namespace=groom_asset, options="v=0", groupReference=False)
        mc.file(sp.os.path.join(import_folder, 'shader.ma'), i=True, type="mayaAscii", ignoreVersion=True,
                mergeNamespacesOnClash=False, gl=True, namespace=groom_asset, options="v=0", groupReference=False)
        # import xgen
        try:
            xg.importPalette(fileName=str(xgen_file), deltas=[])
        except:
            mc.warning('Not found maps folder')
        # set path to xgen
        xg.setAttr('xgDataPath', str(map_folder), xg.palettes()[0])

        # Get the description editor first.
        # Changes in the groom itself, guides, and so on
        de = xgg.DescriptionEditor
        #
        #
        #
        #
        # Do a full UI refresh
        de.refresh("Full")

    def _get_root_folder(self):
        """
        Gets the xgen root folder
        :return: String with the xgen folder path
        """
        return xg.getAttr('xgDataPath', str(self.collection_name))

    def delete_artella_folder(self, p):
        self.ui.progress_bar.setValue(0)
        self.ui.progress_lbl.setText("Locking Files")
        i = 0
        for root, dirs, files in sp.os.walk(p):
            for file in files:
                i += 1
        if i == 0:
            return
        j = 0
        self.ui.progress_bar.setMinimum(0)
        self.ui.progress_bar.setMaximum(i - 1)
        for root, dirs, files in sp.os.walk(p):
            for file in files:
                sp.lock_file(file_path=sp.os.path.join(root, file))
                self.ui.progress_bar.setValue((j / float(i)) * 100)
                sys.solstice.logger.debug("XGEN || {} file locked".format(file))
                j += 1
        sp.shutil.rmtree(p, onerror=sp.on_rm_error)
        sys.solstice.logger.debug("XGEN || {} path deleted".format(p))

    def _add_file_to_artella(self, file_path_global, comment):
        """
        Method that adds all the files of a given path to the artella system
        :param file_path_global: String with the base path to ad
        :param comment: String with the comment to add
        """
        self.ui.progress_bar.setValue(0)
        self.ui.progress_lbl.setText("Uploading Files")
        i = 0
        for root, dirs, files in sp.os.walk(file_path_global):
            for file in files:
                i += 1
        j = 0
        self.ui.progress_bar.setMinimum(0)
        self.ui.progress_bar.setMaximum(i - 1)
        for root, dirs, files in sp.os.walk(file_path_global):
            for file in files:
                sp.upload_working_version(sp.os.path.join(root, file), comment=comment, force=True)
                self.ui.progress_bar.setValue((j / float(i)) * 100)
                sys.solstice.logger.debug("XGEN || {} file added".format(file))
                j += 1

    def _get_shaders(self):
        """
        Gets a dictionary with the used materials for each description
        :return: Dictionary with the shader --> description mapping
        """
        material_dict = dict()
        for description in xg.descriptions(str(self.collection_name)):
            pm.select(description)
            pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
            for shd in pm.selected(materials=True):
                if [c for c in shd.classification() if 'shader/surface' in c]:
                    material_dict[description] = shd.name()
        return material_dict

    def _get_scalps(self):
        """
        Gets a list with the used scalps in the descriptions
        :return: List with the scalps names
        """
        scalps = list()
        for description in xg.descriptions(str(self.collection_name)):
            scalpt = xg.boundGeometry(str(self.collection_name), str(description))[0]
            if scalpt not in scalps:
                scalps.append(scalpt)

        return scalps


def run():
    """
    Runs the Xgen manager GUI
    :return: QWindow object
    """
    myWin = ControlXgenUi()
    myWin.show()

    return myWin
