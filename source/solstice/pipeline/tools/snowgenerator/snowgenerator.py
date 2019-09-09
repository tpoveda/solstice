#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to manage Light Rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

import tpDccLib as tp

import artellapipe
from artellapipe.gui import window

if tp.is_maya():
    import tpMayaLib as maya


class ArtellaLightRigManager(window.ArtellaWindow, object):

    VERSION = '0.0.1'
    LOGO_NAME = 'snowgenerator_logo'

    def __init__(self, project):
        super(ArtellaLightRigManager, self).__init__(
            project=project,
            name='SnowGeneratorWindow',
            title='Snow Generator',
            size=(100, 150)
        )

    def ui(self):
        super(ArtellaLightRigManager, self).ui()

        create_snow_btn = QPushButton('Snow it!')
        create_snow_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(create_snow_btn)

        create_snow_btn.clicked.connect(self.create_snow)

    @staticmethod
    def create_snow():

        import pymel as pm

        selobj = maya.cmds.ls(sl=True)
        if len(selobj) <= 0:
            maya.cmds.warning('Select one object to generate snow on top of it')
            return
        selobj = selobj[0]
        dup = maya.cmds.duplicate(selobj)
        maya.cmds.select(dup)
        obj = maya.cmds.ls(sl=True)[0]

        bbox = maya.cmds.xform(obj, q=True, ws=True, boundingBox=True)
        selection = maya.OpenMaya.MSelectionList()
        selection.add(obj)
        obj_mdagpath = maya.OpenMaya.MDagPath()
        selection.getDagPath(0, obj_mdagpath)
        obj_mfnMesh = maya.OpenMaya.MFnMesh(obj_mdagpath)

        face_ids = None
        tri_ids = None
        ids_sorted = False
        space = maya.OpenMaya.MSpace.kWorld
        max_param = 999999
        test_both_directions = False
        accel_params = None
        sortHits = True
        hit_points = maya.OpenMaya.MFloatPointArray()
        hit_ray_params = maya.OpenMaya.MFloatArray()
        hit_faces = maya.OpenMaya.MIntArray()

        selection = maya.cmds.ls(sl=True)
        num_of_faces = maya.cmds.polyEvaluate(selection, f=True)

        window = maya.cmds.window(t="Adding snow ... Please wait!")
        maya.cmds.columnLayout()
        progress_control = maya.cmds.progressBar(maxValue=num_of_faces, width=300)
        maya.cmds.showWindow(window)

        for i in range(num_of_faces):

            pselect = selection[0] + '.f[' + str(i) + ']'

            face = pm.MeshFace(pselect)
            pt = face.__apimfn__().center(maya.OpenMaya.MSpace.kWorld)
            center_point = pm.datatypes.Point(pt)

            pn = maya.cmds.polyInfo(pselect, fn=True)[0].split("\n")[0].split()

            maya.cmds.progressBar(progress_control, edit=True, pr=i + 1)

            ray_direction = maya.OpenMaya.MFloatVector(0, 0.25, 0)
            ray_source = maya.OpenMaya.MFloatPoint(center_point[0], center_point[1] + 0.1, center_point[2])
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
                maya.cmds.select(pselect, add=True)
        maya.cmds.selectMode(co=True)
        maya.cmds.delete()
        maya.cmds.selectMode(o=True)
        maya.cmds.deleteUI(window)
        em = maya.cmds.emitter(type='surface', spd=0, rate=1000)
        prt = maya.cmds.nParticle()

        maya.cmds.connectDynamic(prt[0], em=em)
        maya.cmds.setAttr(prt[1] + '.ignoreSolverGravity', 1)
        maya.cmds.setAttr(prt[1] + '.ignoreSolverWind', 1)
        maya.cmds.setAttr(prt[1] + '.maxCount', 70000)
        maya.cmds.setAttr(prt[1] + '.radius', 1)
        maya.cmds.setAttr(prt[1] + '.particleRenderType', 7)

        maya.cmds.play()

        maya.mel.eval('doParticleToPoly;')


def run():
    win = ArtellaLightRigManager(project=artellapipe.solstice)
    win.show()

    return win
