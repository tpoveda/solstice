# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xgen.ui',
# licensing of 'xgen.ui' applies.
#
# Created: Sun Jul 21 22:40:02 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_xgen_widget(object):
    def setupUi(self, xgen_widget):
        xgen_widget.setObjectName("xgen_widget")
        xgen_widget.resize(850, 625)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(xgen_widget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(xgen_widget)
        self.groupBox.setTitle("")
        self.groupBox.setFlat(True)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grom_tabw = QtWidgets.QTabWidget(self.groupBox)
        self.grom_tabw.setObjectName("grom_tabw")
        self.exporter_tab = QtWidgets.QWidget()
        self.exporter_tab.setObjectName("exporter_tab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.exporter_tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.collection_gbx = QtWidgets.QGroupBox(self.exporter_tab)
        self.collection_gbx.setObjectName("collection_gbx")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.collection_gbx)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.collection_cbx = QtWidgets.QComboBox(self.collection_gbx)
        self.collection_cbx.setObjectName("collection_cbx")
        self.verticalLayout_5.addWidget(self.collection_cbx)
        self.verticalLayout_6.addWidget(self.collection_gbx)
        self.path_gbx = QtWidgets.QGroupBox(self.exporter_tab)
        self.path_gbx.setObjectName("path_gbx")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.path_gbx)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.path_txf = QtWidgets.QLineEdit(self.path_gbx)
        self.path_txf.setObjectName("path_txf")
        self.horizontalLayout_5.addWidget(self.path_txf)
        self.path_browse_btn = QtWidgets.QPushButton(self.path_gbx)
        self.path_browse_btn.setObjectName("path_browse_btn")
        self.horizontalLayout_5.addWidget(self.path_browse_btn)
        self.verticalLayout_6.addWidget(self.path_gbx)
        self.export_go_btn = QtWidgets.QPushButton(self.exporter_tab)
        self.export_go_btn.setObjectName("export_go_btn")
        self.verticalLayout_6.addWidget(self.export_go_btn)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem)
        self.grom_tabw.addTab(self.exporter_tab, "")
        self.importer_tab = QtWidgets.QWidget()
        self.importer_tab.setObjectName("importer_tab")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.importer_tab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groom_package_gbx = QtWidgets.QGroupBox(self.importer_tab)
        self.groom_package_gbx.setObjectName("groom_package_gbx")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groom_package_gbx)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groom_package_txf = QtWidgets.QLineEdit(self.groom_package_gbx)
        self.groom_package_txf.setObjectName("groom_package_txf")
        self.horizontalLayout_3.addWidget(self.groom_package_txf)
        self.groom_file_browser_btn = QtWidgets.QPushButton(self.groom_package_gbx)
        self.groom_file_browser_btn.setObjectName("groom_file_browser_btn")
        self.horizontalLayout_3.addWidget(self.groom_file_browser_btn)
        self.verticalLayout_7.addWidget(self.groom_package_gbx)
        self.geometry_scalpt_grp_bgx = QtWidgets.QGroupBox(self.importer_tab)
        self.geometry_scalpt_grp_bgx.setObjectName("geometry_scalpt_grp_bgx")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.geometry_scalpt_grp_bgx)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.geometry_scalpt_grp_txf = QtWidgets.QLineEdit(self.geometry_scalpt_grp_bgx)
        self.geometry_scalpt_grp_txf.setObjectName("geometry_scalpt_grp_txf")
        self.horizontalLayout_4.addWidget(self.geometry_scalpt_grp_txf)
        self.geometry_scalpt_grp_btn = QtWidgets.QPushButton(self.geometry_scalpt_grp_bgx)
        self.geometry_scalpt_grp_btn.setObjectName("geometry_scalpt_grp_btn")
        self.horizontalLayout_4.addWidget(self.geometry_scalpt_grp_btn)
        self.verticalLayout_7.addWidget(self.geometry_scalpt_grp_bgx)
        self.importer_go_btn = QtWidgets.QPushButton(self.importer_tab)
        self.importer_go_btn.setObjectName("importer_go_btn")
        self.verticalLayout_7.addWidget(self.importer_go_btn)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem1)
        self.grom_tabw.addTab(self.importer_tab, "")
        self.tools_tab = QtWidgets.QWidget()
        self.tools_tab.setObjectName("tools_tab")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tools_tab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.export_patches_btn = QtWidgets.QPushButton(self.tools_tab)
        self.export_patches_btn.setObjectName("export_patches_btn")
        self.verticalLayout_8.addWidget(self.export_patches_btn)
        self.arnold_variables_gbx = QtWidgets.QGroupBox(self.tools_tab)
        self.arnold_variables_gbx.setObjectName("arnold_variables_gbx")
        self.formLayout = QtWidgets.QFormLayout(self.arnold_variables_gbx)
        self.formLayout.setObjectName("formLayout")
        self.renderer_lbl = QtWidgets.QLabel(self.arnold_variables_gbx)
        self.renderer_lbl.setObjectName("renderer_lbl")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.renderer_lbl)
        self.renderer_cbx = QtWidgets.QComboBox(self.arnold_variables_gbx)
        self.renderer_cbx.setObjectName("renderer_cbx")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.renderer_cbx)
        self.render_mode_lbl = QtWidgets.QLabel(self.arnold_variables_gbx)
        self.render_mode_lbl.setObjectName("render_mode_lbl")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.render_mode_lbl)
        self.renderer_mode_cbx = QtWidgets.QComboBox(self.arnold_variables_gbx)
        self.renderer_mode_cbx.setObjectName("renderer_mode_cbx")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.renderer_mode_cbx)
        self.motion_blur_lbl = QtWidgets.QLabel(self.arnold_variables_gbx)
        self.motion_blur_lbl.setObjectName("motion_blur_lbl")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.motion_blur_lbl)
        self.motion_blur_cbx = QtWidgets.QComboBox(self.arnold_variables_gbx)
        self.motion_blur_cbx.setObjectName("motion_blur_cbx")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.motion_blur_cbx)
        self.verticalLayout_8.addWidget(self.arnold_variables_gbx)
        self.shader_variables_gbx = QtWidgets.QGroupBox(self.tools_tab)
        self.shader_variables_gbx.setObjectName("shader_variables_gbx")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.shader_variables_gbx)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.shader_variables_gbx)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.extra_samples_sbx = QtWidgets.QSpinBox(self.shader_variables_gbx)
        self.extra_samples_sbx.setObjectName("extra_samples_sbx")
        self.horizontalLayout_2.addWidget(self.extra_samples_sbx)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.shader_variables_gbx)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.extra_depth_sbx = QtWidgets.QSpinBox(self.shader_variables_gbx)
        self.extra_depth_sbx.setObjectName("extra_depth_sbx")
        self.horizontalLayout.addWidget(self.extra_depth_sbx)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_8.addWidget(self.shader_variables_gbx)
        self.guides_gbx = QtWidgets.QGroupBox(self.tools_tab)
        self.guides_gbx.setObjectName("guides_gbx")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.guides_gbx)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.import_guides_btn = QtWidgets.QPushButton(self.guides_gbx)
        self.import_guides_btn.setObjectName("import_guides_btn")
        self.verticalLayout_2.addWidget(self.import_guides_btn)
        self.export_guides_btn = QtWidgets.QPushButton(self.guides_gbx)
        self.export_guides_btn.setObjectName("export_guides_btn")
        self.verticalLayout_2.addWidget(self.export_guides_btn)
        self.verticalLayout_8.addWidget(self.guides_gbx)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem4)
        self.grom_tabw.addTab(self.tools_tab, "")
        self.verticalLayout.addWidget(self.grom_tabw)
        self.verticalLayout_3.addWidget(self.groupBox)

        self.retranslateUi(xgen_widget)
        self.grom_tabw.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(xgen_widget)

    def retranslateUi(self, xgen_widget):
        xgen_widget.setWindowTitle(QtWidgets.QApplication.translate("xgen_widget", "Form", None, -1))
        self.collection_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "XGen Collection", None, -1))
        self.path_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Path to save", None, -1))
        self.path_browse_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Browse", None, -1))
        self.export_go_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Go!", None, -1))
        self.grom_tabw.setTabText(self.grom_tabw.indexOf(self.exporter_tab), QtWidgets.QApplication.translate("xgen_widget", "Exporter", None, -1))
        self.groom_package_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Groom Package File", None, -1))
        self.groom_file_browser_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Browse", None, -1))
        self.geometry_scalpt_grp_bgx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Geometry Scaplt Group", None, -1))
        self.geometry_scalpt_grp_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "<--", None, -1))
        self.importer_go_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Go!", None, -1))
        self.grom_tabw.setTabText(self.grom_tabw.indexOf(self.importer_tab), QtWidgets.QApplication.translate("xgen_widget", "Importer", None, -1))
        self.export_patches_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Export Patches For Batch Render", None, -1))
        self.arnold_variables_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Arnold Variables", None, -1))
        self.renderer_lbl.setText(QtWidgets.QApplication.translate("xgen_widget", "Renderer", None, -1))
        self.render_mode_lbl.setText(QtWidgets.QApplication.translate("xgen_widget", "Render Mode", None, -1))
        self.motion_blur_lbl.setText(QtWidgets.QApplication.translate("xgen_widget", "Motion Blur", None, -1))
        self.shader_variables_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Shader Variables", None, -1))
        self.label_5.setText(QtWidgets.QApplication.translate("xgen_widget", "Extra Samples", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("xgen_widget", "Extra Depth", None, -1))
        self.guides_gbx.setTitle(QtWidgets.QApplication.translate("xgen_widget", "Guides", None, -1))
        self.import_guides_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Import Guides", None, -1))
        self.export_guides_btn.setText(QtWidgets.QApplication.translate("xgen_widget", "Export Guides", None, -1))
        self.grom_tabw.setTabText(self.grom_tabw.indexOf(self.tools_tab), QtWidgets.QApplication.translate("xgen_widget", "Tools", None, -1))

