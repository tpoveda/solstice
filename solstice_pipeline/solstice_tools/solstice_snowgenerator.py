#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_snowcreator.py
# by Javi @ Tomas
# Tool to create snow on objects easily
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtWidgets import *

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya

from solstice_gui import solstice_windows


class SnowGenerator(solstice_windows.Window, object):
    name = 'Snow Generator'
    title = 'Solstice Tools - Snow Generator'
    version = '1.0'
    docked = False

    def __init__(self, name='SnowGeneratorWindow', parent=None):
        super(SnowGenerator, self).__init__(name=name, parent=parent)

        self.setMaximumWidth(350)
        self.setMaximumHeight(150)

    def custom_ui(self):
        super(SnowGenerator, self).custom_ui()

        self.set_logo('solstice_snowgenerator_logo')

        create_snow_btn = QPushButton('Snow it!')
        create_snow_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(create_snow_btn)

        create_snow_btn.clicked.connect(self.create_snow)

    @staticmethod
    def create_snow():
        selobj = cmds.ls(sl=True)
        if len(selobj) <= 0:
            cmds.warning('Select one object to generate snow on top of it')
            return
        selobj = selobj[0]
        dup = cmds.duplicate(selobj)
        cmds.select(dup)
        obj = cmds.ls(sl=True)[0]

        bbox = cmds.xform(obj, q=True, ws=True, boundingBox=True)
        selection = OpenMaya.MSelectionList()
        selection.add(obj)
        obj_mdagpath = OpenMaya.MDagPath()
        selection.getDagPath(0, obj_mdagpath)
        obj_mfnMesh = OpenMaya.MFnMesh(obj_mdagpath)

        face_ids = None
        tri_ids = None
        ids_sorted = False
        space = OpenMaya.MSpace.kWorld
        max_param = 999999
        test_both_directions = False
        accel_params = None
        sortHits = True
        hit_points = OpenMaya.MFloatPointArray()
        hit_ray_params = OpenMaya.MFloatArray()
        hit_faces = OpenMaya.MIntArray()

        selection = cmds.ls(sl=True)
        num_of_faces = cmds.polyEvaluate(selection, f=True)

        window = cmds.window(t="Adding snow ... Please wait!")
        cmds.columnLayout()
        progress_control = cmds.progressBar(maxValue=num_of_faces, width=300)
        cmds.showWindow(window)

        for i in range(num_of_faces):

            pselect = selection[0] + '.f[' + str(i) + ']'

            face = pm.MeshFace(pselect)
            pt = face.__apimfn__().center(OpenMaya.MSpace.kWorld)
            center_point = pm.datatypes.Point(pt)

            pn = cmds.polyInfo(pselect, fn=True)[0].split("\n")[0].split()

            cmds.progressBar(progress_control, edit=True, pr=i + 1)

            ray_direction = OpenMaya.MFloatVector(0, 0.25, 0)
            ray_source = OpenMaya.MFloatPoint(center_point[0], center_point[1] + 0.1, center_point[2])
            hit_points.clear()
            if obj_mfnMesh.allIntersections(ray_source,
                                            ray_direction,
                                            face_ids,
                                            tri_ids,
                                            ids_sorted,
                                            space,
                                            max_param,
                                            test_both_directions,
                                            accel_params,
                                            sortHits,
                                            hit_points,
                                            hit_ray_params,
                                            hit_faces,
                                            None, None, None,
                                            0.000001):
                cmds.select(pselect, add=True)
        cmds.selectMode(co=True)
        cmds.delete()
        cmds.selectMode(o=True)
        cmds.deleteUI(window)
        em = cmds.emitter(type='surface', spd=0, rate=1000)
        prt = cmds.nParticle()

        cmds.connectDynamic(prt[0], em=em)
        cmds.setAttr(prt[1] + '.ignoreSolverGravity', 1)
        cmds.setAttr(prt[1] + '.ignoreSolverWind', 1)
        cmds.setAttr(prt[1] + '.maxCount', 70000)
        cmds.setAttr(prt[1] + '.radius', 1)
        cmds.setAttr(prt[1] + '.particleRenderType', 7)

        cmds.play()

        mel.eval('doParticleToPoly;')


# ============================================================================================================

# if not 'snow_window' in globals():
snow_window = None


def snow_window_closed(object=None):
    global snow_window
    if snow_window is not None:
        snow_window.cleanup()
        snow_window.parent().setParent(None)
        snow_window.parent().deleteLater()
        snow_window = None


def snow_window_destroyed(object=None):
    global snow_window
    snow_window = None


def run(restore=False):

    global snow_window
    if snow_window is None:
        snow_window = SnowGenerator()
        snow_window.destroyed.connect(snow_window_destroyed)
        snow_window.setProperty('saveWindowPref', True)

    if restore:
        parent = OpenMayaUI.MQtUtil.getCurrentParent()
        mixin_ptr = OpenMayaUI.MQtUtil.findControl(snow_window.objectName())
        OpenMayaUI.MQtUtil.addWidgetToMayaLayout(long(mixin_ptr), long(parent))
    else:
        snow_window.show(dockable=SnowGenerator.dock, save=True, closeCallback='from solstice_tools import solstice_snowgenerator\nsolstice_snowgenerator.snow_window_closed()')

    snow_window.window().raise_()
    snow_window.raise_()
    snow_window.isActiveWindow()

    return snow_window
