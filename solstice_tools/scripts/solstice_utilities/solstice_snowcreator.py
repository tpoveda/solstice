
#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_snowcreator.py
# by Javi and maintanied by Tomas Poveda
# Tool to create snow on objects easily
# ______________________________________________________________________# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om

from solstice_utils import _getMayaWindow, readJSON

class solstice_snowcreator(QMainWindow, object):
    def __init__(self):
        super(solstice_snowcreator, self).__init__(_getMayaWindow())

        winName = 'solstice_snowcreator_window'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('Solstice Tools - Snow Creator - v.1.0')
        self.customUI()
        self.show()

    def customUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignCenter)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        create_snow_btn = QPushButton('Snow it!')
        create_snow_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainLayout.addWidget(create_snow_btn)

        create_snow_btn.clicked.connect(self._create_snow)

    def _create_snow(self):
        selobj = cmds.ls(sl=True)[0]
        dup = cmds.duplicate(selobj)
        cmds.select(dup)
        obj = cmds.ls(sl=True)[0]

        bbox = cmds.xform(obj, q=True, ws=True, boundingBox=True)
        selection = om.MSelectionList()
        selection.add(obj)
        obj_mdagpath = om.MDagPath()
        selection.getDagPath(0, obj_mdagpath)
        obj_mfnMesh = om.MFnMesh(obj_mdagpath)

        faceIds = None
        triIds = None
        idsSorted = False
        space = om.MSpace.kWorld
        maxParam = 999999
        testBothDirections = False
        accelParams = None
        sortHits = True
        hitPoints = om.MFloatPointArray()
        hitRayParams = om.MFloatArray()
        hitFaces = om.MIntArray()

        selection = cmds.ls(sl=True)
        numOfFaces = cmds.polyEvaluate(selection, f=True)

        window = cmds.window(t="Adding snow ... Please wait!")
        cmds.columnLayout()
        progressControl = cmds.progressBar(maxValue=numOfFaces, width=300)
        cmds.showWindow(window)

        for i in range(numOfFaces):

            pselect = selection[0] + '.f[' + str(i) + ']'

            face = pm.MeshFace(pselect)
            pt = face.__apimfn__().center(om.MSpace.kWorld)
            centerPoint = pm.datatypes.Point(pt)

            pn = cmds.polyInfo(pselect, fn=True)[0].split("\n")[0].split()

            pnn = [float(pn[2]), float(pn[3]), float(pn[4])]

            progressInc = cmds.progressBar(progressControl, edit=True, pr=i + 1)

            rayDirection = om.MFloatVector(0, 0.25, 0)
            raySource = om.MFloatPoint(centerPoint[0], centerPoint[1] + 0.1, centerPoint[2])
            hitPoints.clear()
            if obj_mfnMesh.allIntersections(raySource,
                                            rayDirection,
                                            faceIds,
                                            triIds,
                                            idsSorted,
                                            space,
                                            maxParam,
                                            testBothDirections,
                                            accelParams,
                                            sortHits,
                                            hitPoints,
                                            hitRayParams,
                                            hitFaces,
                                            None, None, None,
                                            0.000001):
                cmds.select(pselect, add=True)
                # cmds.delete(pselect)
        cmds.selectMode(co=True)
        cmds.delete()
        cmds.selectMode(o=True)
        # cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
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

def initUI():
    solstice_snowcreator()