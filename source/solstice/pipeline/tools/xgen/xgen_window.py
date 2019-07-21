import zipfile
from functools import partial

# import os
# # for path in sp.os.sys.path:
# #     if 'solstice' in path:
# #         sp.os.sys.path.remove(path)
# os.sys.path.insert(0, "C:\\Users\\enriq\\dev\\solstice\\source")

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as mc
import pymel.core as pm

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt import QtWidgets, QtCore, QtGui
from solstice.pipeline import tools
from solstice.pipeline.gui import dialog, animations

import xgenm as xg
import xgenm.XgExternalAPI as xge
import xgenm.xgGlobal as xgg


class ControlXgenUi(dialog.Dialog):
    name = 'xgen_window'  # Do not change or UI load'll fail and Maya'll crash painfully
    title = 'Solstice Tools - XGen Handle'
    version = '1.0'
    docked = False

    def __init__(self, **kwargs):
        super(ControlXgenUi, self).__init__(**kwargs)
        # class variables
        self.shaders_dict = dict()
        self.scalpts_list = list()
        self.collection_name = None

    def custom_ui(self):
        super(ControlXgenUi, self).custom_ui()

        self.resize(500, 400)
        self.ui = tools.load_tool_ui(self.name)
        self.main_layout.addWidget(self.ui)
        self.populate_data()
        self.connect_componets_to_actions()

        self.show()

    def populate_data(self):
        self.ui.collection_cbx.addItems(self.get_all_collections())
        self.ui.renderer_cbx.addItems(["None", "Arnold Renderer"])
        self.ui.renderer_cbx.setCurrentIndex(1)
        self.ui.renderer_mode_cbx.addItems(["Live", "Batch Render"])
        self.ui.renderer_mode_cbx.setCurrentIndex(1)
        self.ui.motion_blur_cbx.addItems(["Use Global Settings", "On", "Off"])
        self.ui.extra_depth_sbx.setValue(16)
        self.ui.extra_samples_sbx.setValue(0)

    def connect_componets_to_actions(self):
        self.ui.export_go_btn.clicked.connect(self.do_export)
        self.ui.importer_go_btn.clicked.connect(self.do_import)
        self.ui.path_browse_btn.clicked.connect(self.save_file)
        self.ui.groom_file_browser_btn.clicked.connect(self.open_file)
        self.ui.geometry_scalpt_grp_btn.clicked.connect(partial(self.load_selection_to_line,
                                                                self.ui.geometry_scalpt_grp_txf))

    def get_all_collections(self):
        collections_list = list()
        for item in xg.palettes():
            collections_list.append(item)
        return collections_list

    def do_export(self):

        # Get Data
        self.collection_name = self.ui.collection_cbx.currentText()
        self.shaders_dict = self.get_shaders()
        self.scalpts_list = self.get_scalpts()
        ptx_folder = self.get_root_folder()
        export_path = self.ui.path_txf.text()

        if not export_path:
            raise ValueError("export path must be specified")

        # Export objects into file and compress it
        # copy maps
        export_path_folder = export_path.replace('.zip', '')
        sp.os.makedirs(export_path_folder)
        if '${PROJECT}' in ptx_folder:
            project_path = str(mc.workspace(fullName=True, q=True))
            ptx_folder = sp.os.path.join(project_path, ptx_folder.replace('${PROJECT}', ''))
        sp.shutil.copytree(ptx_folder, sp.os.path.join(export_path_folder, self.collection_name))

        # export xgen
        xg.exportPalette(palette=str(self.collection_name),
                         fileName=str("{}/{}.xgen".format(export_path_folder, self.collection_name)))

        # export sculpts
        mc.select(self.scalpts_list, replace=True)
        mc.file(rename=sp.os.path.join(export_path_folder, 'sculpts.ma'))
        mc.file(es=True, type='mayaAscii')
        mc.select(cl=True)

        # export material
        mc.select(self.shaders_dict.values(), replace=True)
        mc.file(rename=sp.os.path.join(export_path_folder, 'shader.ma'))
        mc.file(es=True, type='mayaAscii')
        mc.select(cl=True)

        # export mapping
        with open(sp.os.path.join(export_path_folder, 'shader.json'), 'w') as fp:
            sp.json.dump(self.shaders_dict, fp)

        # close
        sp.shutil.make_archive(export_path_folder, 'zip', export_path_folder)

        # clean up
        sp.shutil.rmtree(export_path_folder, ignore_errors=True)

    def do_import(self):
        import_folder = self.ui.groom_package_txf.text()

        if not import_folder:
            raise ValueError("Import path must be specified")

        # build scene
        mc.loadPlugin('xgenToolkit.mll')
        # opening the zip file in READ mode
        with zipfile.ZipFile(import_folder, 'r') as zip:
            # printing all the contents of the zip file
            zip.printdir()

            # extracting all the files
            print('Extracting all the files now...')
            zip.extractall()
            print('Done!')

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

    def get_root_folder(self):
        return xg.getAttr('xgDataPath', str(self.collection_name))

    def load_selection_to_line(self, qt_object):
        # set the string to load
        selection = mc.ls(sl=True)
        text_to_add = '"{}"'.format(selection[0])
        if len(selection) > 1:
            for obj in selection[1:]:
                text_to_add += ';"{}"'.format(obj)

        # set text to the object
        qt_object.setText(text_to_add)

    def open_file(self):
        file_path, _ext = QtWidgets.QFileDialog.getOpenFileName(self, dir=sp.os.environ['home'], filter='Zip File(*.zip)')
        self.ui.groom_package_txf.setText(str(file_path))

    def save_file(self):
        file_path, _ext = QtWidgets.QFileDialog.getSaveFileName(self, dir=sp.os.environ['home'], filter='Zip File(*.zip)')
        self.ui.path_txf.setText(str(file_path))

    def add_file_to_artella(self):
        pass

    def get_shaders(self):
        material_dict = dict()
        for description in xg.descriptions(str(self.collection_name)):
            pm.select(description)
            pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
            for shd in pm.selected(materials=True):
                if [c for c in shd.classification() if 'shader/surface' in c]:
                    material_dict[description] = shd.name()
        return material_dict

    def get_scalpts(self):
        scalpts = list()
        for description in xg.descriptions(str(self.collection_name)):
            scalpt = xg.boundGeometry(str(self.collection_name), str(description))[0]
            if scalpt not in scalpts:
                scalpts.append(scalpt)

        return scalpts


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


myWin = ControlXgenUi(parent=maya_main_window())
myWin.custom_ui()
myWin.show()
