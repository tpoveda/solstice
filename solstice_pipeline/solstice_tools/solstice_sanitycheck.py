#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sanitycheck.py
# by Irakli KUblashvili
# Solstice Pipeline tool to smooth the workflow between Maya and Artella
# ______________________________________________________________________
# ==================================================================="""


from pymel.core import *
import maya.mel as mel
import sys
from pymel.mayautils import *
import os
from functools import partial


class sanityCheck(object):

    # V2.0

    def __init__(self, uiSwipe=0):
        if uiSwipe == 0:
            layoutDialog(ui=self.sanitiCheckUI, title='Sanity Check(beta v0.6)')
        else:
            self.sanitiCheckUI(win=1)

    def sanitiCheckUI(self, win=0):

        self.namespacesDeleted = []

        self.allCheckBox = []

        closeBtnLabel = ''
        rig = False
        shd = False
        geo = False
        bsh = False
        value = 0
        width = 744
        height = 348
        scene_Name = cmds.file(sceneName=True, query=True)
        name = scene_Name.rpartition('/')[2]

        if 'RIG' in name:
            rig = True
        if 'SHD' in name:
            shd = True
        if 'GEO' in name:
            geo = True
        if 'BLSH' in name:
            bsh = True

        checkBoxNames = ['Hidden Shapes', 'Generic', 'References', 'Dynamics', 'Delete History', 'Freeze', 'Cleanup',
                         'Empty Groups',
                         'Unused Nodes', 'Namespaces', 'Cameras', 'Materials', 'Render Layers', 'Display Layers',
                         'Driven Keys',
                         'Fur Description', 'Vertex Freeze', 'Lights', 'Anim Curves', 'Image planes', 'Proc Textures',
                         'Arnold Nodes', 'Non Manifold', 'File Textures', 'Object sets', 'Controller Keys(AS Only)', 'Unknown']

        checkBoxNames.sort()

        rigCheckBoxOff = {'Hidden Shapes': 0, 'Delete History': 0, 'Freeze': 0, 'Cleanup': 0,
                          'Driven Keys': 0, 'References': 0,
                          'Empty Groups': 0,  'Anim Curves': 0, 'Object sets': 0, 'Vertex Freeze': 0, 'Non Manifold':0}

        shadingCheckboxOff = {'Render Layers': 0, 'Hidden Shapes': 0, 'Cleanup': 0, 'Check Simetry': 0,
                              'Materials': 0, 'Lights': 0, 'Textures': 0, 'Arnold Nodes': 0, 'Non Manifold': 0}

        geometryCheckboxOff = {'Vertex Freeze': 0}

        blendShapesCheckBoxOff = {'Vertex Freeze': 0, 'Non Manifold': 0,'Freeze': 0 }

        if win == 1:
            closeBtnLabel = 'Close'
            irx_sanityWindow = 'irx_sanityCheck_window'
            if window(irx_sanityWindow, q=1, ex=1):
                cmds.deleteUI(irx_sanityWindow)
            schw = window(irx_sanityWindow, title='Sanity Check(beta v0.6)', sizeable=False, width=width, height=height)
            schw.show()
            uiElem = self.schLayouts(width, height, rig, shd, geo, bsh, checkBoxNames, rigCheckBoxOff, shadingCheckboxOff,
                                     geometryCheckboxOff, blendShapesCheckBoxOff, value,closeBtnLabel , closButtonEnable=True, optionMenuEnable=True)
            with uiElem[0]:
                with uiElem[1]:
                    with uiElem[2]:
                        uiCheckboxes = self.loopForCheckBoxes(rig, shd, geo,bsh, value, checkBoxNames, rigCheckBoxOff,
                                                              shadingCheckboxOff, geometryCheckboxOff, blendShapesCheckBoxOff,)
                        uiCheckboxes[0]
                        self.allCheckBox = uiCheckboxes[1]

                    with uiElem[3]:
                        uiElem[8]
                        uiElem[11]
                        uiElem[12]
                        uiElem[13]
                        uiElem[4]
                        uiElem[5]
                        uiElem[14]
                        uiElem[15]
                        uiElem[6]
                        uiElem[7]


        else:
            closeBtnLabel = 'Close(Disabled On Publish Mode)'
            self.schLayouts(width, height, rig, shd, geo,bsh, checkBoxNames, rigCheckBoxOff, shadingCheckboxOff,
                            geometryCheckboxOff,blendShapesCheckBoxOff, value, closeBtnLabel, saverTrigger=1)

    def schLayouts(self, width, height, rig, shd, geo, bsh, checkBoxNames, rigCheckBoxOff, shadingCheckboxOff,
                   geometryCheckboxOff,blendShapesCheckBoxOff, value, closeBtnLabel, closButtonEnable=False, saverTrigger=0, optionMenuEnable=False):

        self.allCheckBox = []
        self.geoCheckBoxes = geometryCheckboxOff
        self.rigCheckBoxes = rigCheckBoxOff
        self.blendShapesCheckBoxes = blendShapesCheckBoxOff
        buttonWidth = 360
        buttonHeight = 30
        closeBtnLabel = closeBtnLabel
        vl = verticalLayout(width=width, height=height)
        fl = frameLayout(labelVisible=False, borderVisible=True, width=width-17, height=height-3, marginWidth=6)
        gl = gridLayout(numberOfColumns=5, cellWidthHeight=(145, 40))
        rl = rowColumnLayout(nc=2, columnAttach=([1, 'both', 1], [2, 'both', 3]), parent=fl,
                             rowOffset=([1, 'both', 1], [2, 'both', 1]), width=width-17)
        emptyText = text(label='')
        self.optionMenuBtn = optionMenu(label='Presets :', enable=optionMenuEnable, changeCommand = partial(self.checkUnCheck, 1,1))
        # Menu items don't need to return
        geometryItem = menuItem(label='Geometry' )
        rigItem  = menuItem(label='Rig' )
        blendShapeItem = menuItem(label='BlendShape' )

        leftSeparator = separator(height=5)
        rigthSeparator = separator(height=5)
        btnChAll = button(label='Check All', width=buttonWidth, height=buttonHeight,
                          command=Callback(self.checkUnCheck, True))
        btnUChAll = button(label='Uncheck All', width=buttonWidth, height=buttonHeight,
                           command=Callback(self.checkUnCheck, False))
        leftBtnSeparator = separator()
        rigthBtnSeparator = separator()
        bntRun = button(label='Run', width=buttonWidth, height=buttonHeight, command=self.checkSanity)
        btnClose = button(label=closeBtnLabel, width=buttonWidth, height=buttonHeight,
                          command=("cmds.deleteUI('irx_sanityCheck_window', window=True)"), enable=closButtonEnable)


        if saverTrigger == 1:
            with vl:
                with fl:
                    with gl:
                        uiCheckboxes = self.loopForCheckBoxes(rig, shd, geo,bsh, value, checkBoxNames, rigCheckBoxOff,
                                                              shadingCheckboxOff, geometryCheckboxOff, blendShapeItem)
                        uiCheckboxes[0]

                        self.allCheckBox = uiCheckboxes[1]

                    with rl:
                        btnChAll
                        btnUChAll
                        bntRun
                        btnClose

        return [vl, fl, gl, rl, btnChAll, btnUChAll, bntRun, btnClose, self.optionMenuBtn ,geometryItem, rigItem, emptyText, leftSeparator, rigthSeparator,
            leftBtnSeparator, rigthBtnSeparator ]

    def loopForCheckBoxes(self, rig=False, shd=False, geo=False, bsh=False, value=0, checkBoxNames=[], rigCheckBoxOff={}, shadingCheckboxOff={},
                          geometryCheckboxOff={}, blendShapesCheckBoxOff={}):

        allCheckBoxes = []
        value = value
        checkBx = []
        for c in checkBoxNames:
            if rig:
                try:
                    value = rigCheckBoxOff[c]
                except:
                    value = 1
            elif shd:
                try:
                    value = shadingCheckboxOff[c]
                except:
                    value = 1
            elif geo:
                try:
                    value = geometryCheckboxOff[c]
                except:
                    value = 1
            elif bsh:
                try:
                    value = blendShapesCheckBoxOff[c]
                except:
                    value = 1

            checkBx = checkBox(c, label=c, value=value)

            allCheckBoxes.append(c)
        return [checkBx, allCheckBoxes]

    def checkUnCheck(self, value=0,optMenu=0, *args ):

        value = value
        mItem = optionMenu(self.optionMenuBtn, query=True, value=True)

        for c in self.allCheckBox:

            ### Get real name of checkboxes
            if c == 'Controller Keys(AS Only)':
                c = 'Controller_Keys_AS_Only_'
            c = c.replace(' ', '_')
            ##################################
            checkBox(c, edit=True, value=value)
            # optionMenu
            if optMenu == 1:
                if mItem == 'Geometry':
                    for key, val in self.geoCheckBoxes.iteritems():
                        key=key.replace(' ', '_')
                        checkBox(key, edit=True, value=val)
                if mItem == 'Rig':
                    for key, val in self.rigCheckBoxes.iteritems():
                        key = key.replace(' ', '_')
                        checkBox(key, edit=True, value=val)
                if mItem == 'BlendShape':
                    for key, val in self.blendShapesCheckBoxes.iteritems():
                        key = key.replace(' ', '_')
                        checkBox(key, edit=True, value=val)


    def delteHist(self, hystoryCheckBox):

        hystoryObjects = []
        historyCleanedVar = []
        if hystoryCheckBox:

            hystoryObjects = ls(type=['mesh', 'nurbsSurface'])

            if hystoryObjects:
                for h in hystoryObjects:
                    if objExists(h) == True:

                        try:
                            a = listHistory(h.getParent(), pruneDagObjects=True, interestLevel=True)
                        except MayaNodeError:
                            print 'Node does not exists!'

                        if not nodeType(a) == 'shadingEngine':
                            try:
                                if len(listHistory((PyNode(h).getParent()), pruneDagObjects=True, interestLevel=True)) > 0:
                                    historyCleanedVar.append(PyNode(h).getParent())
                                    delete(PyNode(h).getParent(), ch=True)


                            except MayaNodeError:
                                print 'The node does not exists'
        return historyCleanedVar

    def nmSpaceInfo(self, nInfo):




        for n in nInfo:
            if not n == 'UI' and not n == 'shared':
                self.namespacesDeleted.append(n)

                if n in (namespaceInfo(lon=True)):
                    namespace(mergeNamespaceWithRoot=True, rm=n)

                nsps = namespaceInfo(lon=True)
                if len(nsps) > 2:
                    self.nmSpaceInfo(nsps)

        return self.namespacesDeleted

    def checkSanity(self, *args):

        layoutDialog(dismiss='Continue')

        mel.eval('source "cleanUpScene.mel";')
        os.environ["MAYA_TESTING_CLEANUP"] = "1"

        hShapesCheckBox = checkBox('Hidden_Shapes', query=True, value=True)
        genericCheckBox = checkBox('Generic', query=True, value=True)
        referncesCheckBox = checkBox('References', query=True, value=True)
        dynamicsCheckBox = checkBox('Dynamics', query=True, value=True)
        arnoldNodesCheckBox = checkBox('Arnold_Nodes', query=True, value=True)
        hystoryCheckBox = checkBox('Delete_History', query=True, value=True)
        freezeCheckBox = checkBox('Freeze', query=True, value=True)
        noneManCheckbox = checkBox('Non_Manifold', query=True, value=True)
        unusedCheckBox = checkBox('Unused_Nodes', query=True, value=True)
        namespaceCheckBox = checkBox('Namespaces', query=True, value=True)
        camerasCheckbox = checkBox('Cameras', query=True, value=True)
        materialsCheckBox = checkBox('Materials', query=True, value=True)
        renderlayersCheckBox = checkBox('Render_Layers', query=True, value=True)
        displaylayersCheckBox = checkBox('Display_Layers', query=True, value=True)
        furCheckBox = checkBox('Fur_Description', query=True, value=True)
        vertexFreezeCheckBox = checkBox('Vertex_Freeze', query=True, value=True)
        emptyTransCheckBox = checkBox('Empty_Groups', query=True, value=True)
        lightsCheckBox = checkBox('Lights', query=True, value=True)
        animCurvesCheckBox = checkBox('Anim_Curves', query=True, value=True)
        drivenKeysCheckBox = checkBox('Driven_Keys', query=True, value=True)
        imageplanesCheckBox = checkBox('Image_planes', query=True, value=True)
        procTextCheckBox = checkBox('Proc_Textures', query=True, value=True)
        filetextureCheckBox = checkBox('File_Textures', query=True, value=True)
        objectsetCheckBox = checkBox('Object_sets', query=True, value=True)
        cAnimCurvesCheckBox = checkBox('Controller_Keys_AS_Only_', query=True, value=True)
        uknownCheckBox = checkBox('Unknown', query=True, value=True)


        historyCleanedVar = []
        # hidden shapes ##
        hidenShapesLog = []
        if hShapesCheckBox:

            #[delete(x, ch=True) for x in ls(transforms=True, dagObjects=True)]


            histShapes =  self.delteHist(True)
            historyCleanedVar.extend(histShapes)

            models = [s for s in ls(type='mesh')]

            for m in models:

                if (m.intermediateObject.get()) == True:
                    if objExists(m):

                        hidenShapesLog.append(m.getParent().name())
                        delete(m)

            # if hidenShapesLog:

            #     histShapes =  self.delteHist(True)
            #     historyCleanedVar.extend(histShapes)


        # Controls Anim Curves( ADVANCED SKELETON)
        controlsAnimCurvesVar = []

        if cAnimCurvesCheckBox:

            facialConotrls = []
            bodyControls = []

            nurbsSurfaces = ls(type='nurbsSurface')
            nubrsCurves = ls(type='nurbsCurve')
            if nubrsCurves:
                for c in nubrsCurves:
                    if 'FK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'R':
                        bodyControls.append(c.getParent())

                    if 'FK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'L':
                        bodyControls.append(c.getParent())

                    if 'FK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if 'IK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'R':
                        bodyControls.append(c.getParent())

                    if 'IK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'L':
                        bodyControls.append(c.getParent())

                    if 'IK' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if 'RootX' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if 'Fingers' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'L':
                        bodyControls.append(c.getParent())

                    if 'Fingers' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if 'HipSwinger' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if 'AimEye' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        bodyControls.append(c.getParent())

                    if c.getParent() == 'Main':
                        bodyControls.append(c.getParent())

                    if 'FC' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'R' or \
                                    str(c.getParent()).rpartition('_')[2] == 'RM' or str(c.getParent()).rpartition('_')[
                        2] == 'RL' or str(c.getParent()).rpartition('_')[2] == 'RR':
                        facialConotrls.append(c.getParent())

                    if 'FC' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'L' or \
                                    str(c.getParent()).rpartition('_')[2] == 'LM' or str(c.getParent()).rpartition('_')[
                        2] == 'LR' or str(c.getParent()).rpartition('_')[2] == 'LL':
                        facialConotrls.append(c.getParent())

                    if 'FC' in str(c.getParent()) and str(c.getParent()).rpartition('_')[2] == 'M':
                        facialConotrls.append(c.getParent())

            if nurbsSurfaces:
                for n in nurbsSurfaces:
                    if 'FC' in str(n.getParent()) and str(n.getParent()).rpartition('_')[2] == 'L' or \
                                    str(n.getParent()).rpartition('_')[2] == 'R' or 'eyelid' in str(n.getParent()) or 'Eyelid' in str(n.getParent()):
                        facialConotrls.append(n.getParent())

            # Facial


            for ac in facialConotrls:

                fcAnimCurves = listConnections(str(ac), c=True,
                                               type=['animCurveTL', 'animCurveTA', 'animCurveTU'],
                                               plugs=False)
                if fcAnimCurves:
                    for i in range(0, len(fcAnimCurves)):
                        controlsAnimCurvesVar.append(fcAnimCurves[i][1].name())
                        delete(fcAnimCurves[i][1])
            # Body

            for bc in bodyControls:
                bcAnimCurves = listConnections(str(bc), c=True,
                                               type=['animCurveTL', 'animCurveTA', 'animCurveTU'],
                                               plugs=False)
                if bcAnimCurves:
                    for i in range(0, len(bcAnimCurves)):
                        controlsAnimCurvesVar.append(bcAnimCurves[i][1].name())
                        delete(bcAnimCurves[i][1])

        # Anim Curves ##
        animCurves = []
        animCurvesVar = []
        if animCurvesCheckBox:

            animCurves = ls(type=['animCurveTL', 'animCurveTA', 'animCurveTU'])
            animCurvesVar = [a.name() for a in animCurves]
            if animCurves:
                for g in animCurves:
                    if (PyNode(g).nodeType()) == 'animCurveTL' or (PyNode(g).nodeType()) == 'animCurveTA' or (
                    PyNode(g).nodeType()) == 'animCurveTU':
                        delete(g)

        # Set Driven Keys ##
        drivenKeys = []
        drivenKeysVar = []
        if drivenKeysCheckBox:

            drivenKeys = ls(type='animCurveUU')
            drivenKeysVar = [d.name() for d in drivenKeys]
            if drivenKeys:
                for d in drivenKeys:
                    if (PyNode(d).nodeType()) == 'animCurveUU':
                        if objExists(d):
                            delete(d)

        # imagePlanes ##
        imagePlanes = []
        imagePlanesVar = []
        if imageplanesCheckBox:
            imagePlanes = ls(type=['imagePlane'])
            imagePlanesVar = [i.name() for i in imagePlanes]

            delete(imagePlanes)

        # procedural textures ##

        deletedProctexturesVar = []

        if procTextCheckBox:
            procTextures = ls(textures=True)

            for t in procTextures:

                if not nodeType(t) == 'file':
                    attrs = listAttr(t)
                    if not 'doNotTouchMe' in attrs:
                        if 'texture3d' in nodeType(t, inherited=True):
                            connections3D = listConnections(t + '.placementMatrix', plugs=False)
                            deletedProctexturesVar.append(t.name())
                            delete(connections3D)
                        if 'texture2d' in nodeType(t, inherited=True):
                            connections2D = listConnections(t + '.uvCoord', plugs=False)
                            deletedProctexturesVar.append(t.name())
                            delete(connections2D)

                        if nodeType(t) == 'fluidTexture3D':
                            deletedProctexturesVar.append(t.name())
                            delete(t.getParent())

                        else:
                            deletedProctexturesVar.append(t.name())
                            delete(t)



                            # translates = ls(transforms=True)
                            # if translates:
                            #     for t in translates:
                            #         if not t.getChildren():
                            #             delete(t)

        # File textures ##
        fileTextures = []
        fileTexturesVar = []
        if filetextureCheckBox:
            fileTextures = ls(type='file')
            fileTexturesVar = [f.name() for f in fileTextures]
            for t in fileTextures:
                if 'texture2d' in nodeType(t, inherited=True):
                    connections2D = listConnections(t + '.uvCoord', plugs=False)
                    delete(connections2D)

                delete(t)
            # translates = ls(transforms=True)
            # if translates:
            #     for t in translates:
            #         if not t.getChildren():
            #             delete(t)
            mel.eval('scOpt_performOneCleanup( { "transformOption" } );')

        # genric
        # paint effects
        paintFxNoes = []
        paintFxNoesVar = []
        toonLine = []
        toonLineVar = []
        generic = []
        genericVar = []
        if genericCheckBox:

            paintFxNoes = ls(type=['stroke', 'brush'])
            paintFxNoesVar = [p.name() for p in paintFxNoes]
            try:
                paintFx = []
                for g in paintFxNoes:

                    if PyNode(g).nodeType() == 'stroke':
                        select(g)
                        pfx = listConnections(c=True, plugs=True)
                        for n, p in enumerate(pfx):
                            objectShapes = p[n].rpartition('.')[0]

                            paintFx.append(PyNode(objectShapes).getParent())

                delete(paintFx)
            except:
                pass
            # Toon Lines

            toonLine = ls(type=['stroke', 'brush', 'pfxToon'])
            toonLineVar = [t.name() for t in toonLine]

            for g in toonLine:
                if PyNode(g).nodeType() == 'pfxToon':
                    delete(PyNode(g).getParent())

            # the rest of generics
            generic = ls(
                type=['unknown', 'substance', 'substanceOutput', 'quatSub'])
            genericVar = [g.name() for g in generic]

            try:
                delete(generic)
            except:
                pass

        # Lights
        lightsVar = []
        if lightsCheckBox:

            lights = ls(lights=True)

            lightsVar = [l.getParent().name() for l in lights]  # convert to string list for log

            for g in lights:
                delete(g.getParent())

        # references
        # List refernces
        refs = []
        if referncesCheckBox:
            refs = [x for x in ls(references=True)]
            for r in refs:
                if not r.rpartition(':')[0]:
                    sys.stdout.write(('Reference node to remove : {}\n').format(r))
            # remove Refences
            for r in refs:
                if not r.rpartition(':')[0]:
                    mel.eval(('file -removeReference -referenceNode {};').format(r))

        # dynamics
        pCLoudNodes = []
        sampleInfoNode = []
        sampleInfoNodeVar = []
        particleCloudNode = []
        dynamics = []
        dynamicsVar = []
        pCLoudNodesVar = []
        hairSystem = []
        hairSystemVar = []
        if dynamicsCheckBox:

            # Saplerinfo ocean shader
            sampleInfoNode = ls(type=['particleSamplerInfo', 'oceanShader'])
            sampleInfoNodeVar = [s.name() for s in sampleInfoNode]
            if sampleInfoNode:
                delete(sampleInfoNode)

            # particle cloud

            particleCloudNode = ls(type='particleCloud')
            pCLoudNodesVar = [p.name() for p in particleCloudNode if not p == 'particleCloud1']
            if particleCloudNode:
                # [delete(x) for x in particleCloudNode if not x == 'particleCloud1']
                for x in particleCloudNode:
                    if not x == 'particleCloud1':
                        delete(x)

            # Generic dinamics
            dynamics = ls(type=['pointEmitter', 'particle', 'instancer', 'nCloth', 'nRigid',
                                'pfxHair', 'dynamicConstraint', 'rigidBody', 'fluidShape',
                                'fluidEmitter', 'heightField', 'fluidTexture3D',
                                'choice', 'nComponent', 'nucleus'], dag=True)

            dynamicsVar = [d.name() for d in dynamics]
            if dynamics:
                parentTransforms = []
                restOfTheDynNodes = []

                for d in dynamics:

                    if not d.nodeType() == 'nComponent':

                        parentTransforms.append(d.listRelatives(p=True))
                        if not (d.listRelatives(p=True)):
                            restOfTheDynNodes.append(d)

                delete(filter(None, parentTransforms))
                delete(filter(None, restOfTheDynNodes))

            # hair system
            hairSystem = ls(type='hairSystem')
            hairSystemVar = [h.name() for h in hairSystem]
            if hairSystem:
                hairConnections = listConnections(hairSystem, plugs=False, s=True)

                folliclesTramsform = []
                curves = []
                nucleusNode = []
                for h in hairConnections:

                    if PyNode(h).nodeType() == 'transform':
                        curves.append(listConnections(h.getShape().outCurve))
                        folliclesTramsform.append(h)
                    if PyNode(h).nodeType() == 'nucleus':
                        nucleusNode.append(h)

                delete(listRelatives(curves[0], parent=True))
                delete(listRelatives(folliclesTramsform[0], parent=True))
                delete(nucleusNode)
                delete(listRelatives(hairSystem[0], parent=True))

                mel.eval('scOpt_performOneCleanup( { "transformOption" } );')

        # arnold nodes ##
        arnoldNodes = []
        arnoldNodesVar = []
        if arnoldNodesCheckBox:
            isArnoldpluginLoaded = pluginInfo('mtoa', name=True, query=True, loaded=True)
            if isArnoldpluginLoaded == True:
                arnoldNodes = ls(type=['aiSkyDomeLight', 'aiAreaLight', 'aiGobo', 'aiLightBlocker',
                                       'aiLightDecay', 'aiBarndoor', 'aiPhotometricLight',
                                       'aiNoise', 'aiImage', 'aiPhysicalSky', 'aiSky'  ])
                arnoldNodesVar = [a.name() for a in arnoldNodes]
                if arnoldNodes:
                    for a in arnoldNodes:
                        if PyNode(a).getParent():
                            delete(PyNode(a).getParent())
                        else:
                            delete(a)

            arnoldRenderNodes = ls(type=['aiOptions', 'aiAOVFilter', 'aiAOVDriver'])
            if not arnoldRenderNodes == []:
                arnoldNodesVar = [a.name() for a in arnoldNodes]
                for  ar in arnoldRenderNodes:
                    delete(ar)

        # delete History ##

        if hystoryCheckBox:
            hist = self.delteHist(hystoryCheckBox)
            historyCleanedVar.extend(hist)


        # Freeze ##
        getModels = []
        freezedObjVar = []
        if freezeCheckBox:
            freezeObjects = ls(shapes=True)
            if freezeObjects:
                getModelsShapes = [x for x in freezeObjects if not x.nodeType() == 'camera']
                getModels = [x.getParent() for x in getModelsShapes]
                for g in getModels:
                    tr = 0
                    rot = 0
                    sc = 0
                    t = PyNode(g).translate.get()
                    r = PyNode(g).rotate.get()
                    s = PyNode(g).scale.get()
                    if not (t[0], t[1], t[2]) == (0.0, 0.0, 0.0):
                        tr = 1

                    if not (r[0], r[1], r[2]) == (0.0, 0.0, 0.0):
                        rot = 1

                    if not (s[0], s[1], s[2]) == (1.0, 1.0, 1.0):
                        sc = 1

                    makeIdentity(getModels, apply=1, t=tr, r=rot, s=sc)
                    if not tr == 0 or not rot == 0 or not sc == 0:
                        freezedObjVar.append(g)

        # None Manifold
        getModelsMan = []
        if noneManCheckbox:
            objects = ls(shapes=True)
            if objects:
                getModelsShapes = [x for x in objects if not x.nodeType() == 'camera']
                getModelsMan = [x.getParent() for x in getModelsShapes]
                select(getModelsMan)
                for m in getModelsMan:
                    errorList = mel.eval(
                        'polyCleanupArgList 3 { "1","2","1","0","1","1","1","1","1","1e-005","1","1e-005","0","1e-005","0","2","1" };')

                    if errorList:
                        sys.stdout.write(m + ' object have this errors: ' + errorList[0])

        # transforms without shapes ##
        emptyTranslatesDel = []
        emptyTranslatesDelVar = []
        if emptyTransCheckBox:
            emptyTranslates = ls(transforms=True)
            if emptyTranslates:
                for t in emptyTranslates:
                    if nodeType(t) == 'transform':
                        if not t.getChildren():
                            connections = listConnections(t, c=True)
                            if connections == []:
                                emptyTranslatesDel.append(t)

                emptyTranslatesDelVar = [e.name() for e in emptyTranslatesDel]
                delete(emptyTranslatesDel)

        # namespaces ##

        namespacesDeletedInfo = []

        if namespaceCheckBox:

            nInfo = namespaceInfo(lon=True)

            namespacesDeletedInfo = self.nmSpaceInfo(nInfo)

        # Old Code
        # namespacesDeleted = []
        # if namespaceCheckBox:
        #     nInfo = namespaceInfo(lon=True)
        #     for n in nInfo:
        #         if not n == 'UI' and not n == 'shared':
        #             namespace(mergeNamespaceWithParent=True, rm=n)
        #             namespacesDeleted.append(n)

        # cameras ##

        userCameras = []

        if camerasCheckbox:
            cameras = listCameras()
            for c in cameras:
                if not c == 'persp' and not c == 'top' and not c == 'front' and not c == 'side':
                    userCameras.append(c)

            delete(userCameras)
            sterioCamTransforms = ls(type='stereoRigTransform')
            if not sterioCamTransforms == []:
                delete(sterioCamTransforms)
        # Materials

        materialsToDelete = []
        deletedMaterialsVar = []
        if materialsCheckBox:

            shadingEngines = ls(materials=True, type='lambert')

            for s in shadingEngines:
                if not s == 'particleCloud1' and not s == 'initialParticleSE' and not s == 'initialShadingGroup' and not s == 'lambert1':
                    attrs = listAttr(s)
                    if not 'doNotTouchMe' in attrs:
                        materialsToDelete.append(s)

            deletedMaterialsVar = [d.name() for d in materialsToDelete]
            delete(materialsToDelete)

            allGeometry = ls(type=['mesh', 'nurbsSurface'])



            for a in allGeometry:
                allAttrs = listAttr(a)
                if not 'doNotToutchMe' in allAttrs: # objects have these attributes
                    if not 'generic_ctrlShape' in str(a) and not 'eyelid' in str(a) and not 'Eyelid' in str(a) : # TT names
                        intMObj = getAttr(a + '.intermediateObject')
                        if not intMObj:
                            try:
                                connectAttr(a + '.instObjGroups[0]', 'initialShadingGroup.dagSetMembers', nextAvailable=True)
                            except:
                                print a + ' already connected to initialShadingGroup'

        # render layers
        rLayers = []
        rLayersVar = []
        if renderlayersCheckBox:
            rLayersVar = [r.name() for r in ls(type='renderLayer')]
            [rLayers.append(x) for x in ls(type='renderLayer') if not x == 'defaultRenderLayer']
            [delete(x) for x in ls(type='renderLayer') if not x == 'defaultRenderLayer']

        # display layers
        dLayers = []
        dLayersVar = []
        if displaylayersCheckBox:
            dLayersVar = [d.name() for d in ls(type='displayLayer')]
            [dLayers.append(x) for x in ls(type='displayLayer') if not x == 'defaultLayer']
            [delete(x) for x in ls(type='displayLayer') if not x == 'defaultLayer']

        # Freeze for verteces
        if vertexFreezeCheckBox:
            modelObjects = [x.getParent() for x in ls(type='mesh')]

            for m in modelObjects:
                select(m)
                polySoftEdge()
                delete(constructionHistory=True)
                select(d=True)

        # fur description
        furDesVar = []
        if furCheckBox:
            furType = ls(type=['FurFeedback', 'FurDescription'])
            furDesVar = [f.name() for f in furType]

            if furType:
                for f in furType:
                    try:
                        parent = f.getAllParents()[-1]

                    except:
                        sys.stdout.write(('Node "{}" has no transform node').format(f))
                    if parent:

                        delete(parent)
                    else:

                        delete(f)


                        # Unused nodes
        if unusedCheckBox:
            mel.eval('scOpt_performOneCleanup( { "shaderOption" } );')


        # Sets


        objectSetsVar = []

        if objectsetCheckBox:
            objectSets = []
            allSets = ls(type='objectSet')

            for a in allSets:
                if not a == 'defaultLightSet' and not a == 'defaultObjectSet' and not a == 'initialParticleSE' and not a == 'initialShadingGroup' and not a == 'TurtleDefaultBakeLayer':
                    objectSets.append(a)


            objectSetsVar = [o.name() for o in objectSets]
            if objectSets:
                delete(objectSets)

        unknowVar = []
        if uknownCheckBox:

            unknown = ls(type='unknown')
            unknowVar = [x.name() for x in unknown]

            if not unknown == []:
                for u in unknown:
                    if objExists(u):
                        lockNode(u, lock=False)
                        delete(u)

        # Log UI
        width = 506
        height = 300
        tab1 = '<<'
        tab2 = '>>'
        sep = '  '
        tHeight = 1
        backgroundColor = [0.2, 0.2, 0.2]
        backgroundColor2 = [0.2 ,0.2, 0.2]
        font = 'boldLabelFont'
        irx_sanityLogWindow = 'irx_sanityCheck_Log_window'
        if window(irx_sanityLogWindow, q=1, ex=1):
            deleteUI(irx_sanityLogWindow)
        schlw = window(irx_sanityLogWindow, title='Sanity Check Log', sizeable=False, width=width, height=height)
        schlw.show()

        with schlw:
            with verticalLayout(width=width, height=height):
                with frameLayout(labelVisible=False, borderVisible=True, width=width, height=height):
                    scrollLayout()
                    frameLayout(labelVisible=False, borderVisible=True, width = width - 20)
                    text(label='Hiden Shapes Deleted On These Objects:\n', font = font)
                    for h in hidenShapesLog:
                        if not h == []:
                            text(label=str(h), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Animation curves Deleted :\n', font = font)
                    for a in animCurvesVar:
                        if not a == []:
                            text(label=str(tab1 + a + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Controllers Anim Curves deleted :\n', font = font)
                    for c in controlsAnimCurvesVar:
                        if not c == []:
                            text(label=str(tab1 + c +tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Objects Have Lost DG Nodes :\n', font = font)
                    for h in list(set(historyCleanedVar)):
                        if h:
                            text(label=str(tab1 + h + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Driven Keys Deleted :\n', font = font)
                    for d in drivenKeysVar:
                        if not d == []:
                            text(label=str(tab1 + d + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Image Planes Deleted :\n', font = font)
                    for i in imagePlanesVar:
                        if not i == []:
                            text(label=str(tab1 + i + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Procedural Textures Deleted :\n', font = font)
                    for d in list(set(deletedProctexturesVar)):
                        if not d == []:
                            text(label=str(tab1 + d + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='File Textures Deleted :\n', font = font)
                    for f in fileTexturesVar:
                        if not f == []:
                            text(label=str(tab1 + f +tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Paint FX Strokes Deleted :\n', font = font)
                    for p in paintFxNoesVar:
                        if not p == []:
                            text(label=str(tab1 + p + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Toon Lines Deleted :\n', font = font)
                    for t in toonLineVar:
                        if not t == []:
                            text(label=str(tab1 + t + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Other Generic Nodes Deleted :\n', font = font)
                    for g in genericVar:
                        if not g == []:
                            text(label=str(tab1 + g + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='lights Deleted :\n', font = font)
                    for l in lightsVar:

                        if not l == []:
                            text(label=str(tab1 + l + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Reference Nodes Deleted :\n', font = font)
                    for r in refs:
                        if r:
                            text(label=str(tab1 + r + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Dinamic Nodes Deleted :\n', font = font)
                    for x in [sampleInfoNodeVar, pCLoudNodesVar, dynamicsVar, hairSystemVar]:
                        if x:
                            text(label=str(tab1) + str(x)+tab2, wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Arnold Nodes Deleted :\n', font = font)
                    for a in arnoldNodesVar:
                        if not a == []:
                            text(label=str(tab1 + a + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Objects Transforms Freezed :\n', font = font)
                    for f in freezedObjVar:
                        if g:
                            text(label=str(tab1 + f +tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Empty Translates Deleted :\n', font = font)
                    for e in emptyTranslatesDelVar:
                        if not e == []:
                            text(label=str(tab1 + e +tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Namespaces Merged :\n', font = font)
                    for n in list(set(namespacesDeletedInfo)):
                        if n:
                            text(label=str(tab1 + n +tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Materials and Shading Groups deleted :\n', font = font)
                    for d in deletedMaterialsVar:
                        if not d == []:
                            text(label=str(tab1 + d + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='cameras deleted :\n', font = font)
                    for c in userCameras:
                        if not c == []:
                            text(label=str(tab1 + c + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Render Layers deleted :\n', font = font)
                    for r in rLayersVar:
                        if not r == [] and not r == 'defaultRenderLayer' and not 'defaultRenderLayer' in r:
                            text(label=str(tab1 + r + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Display Layers deleted :\n', font = font)
                    for d in dLayersVar:
                        if not d == [] and not d == 'defaultLayer' and not d == 'jointLayer' and not 'defaultLayer' in d:
                            text(label=str(tab1 + d + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Fur Nodes deleted :\n', font = font)
                    for f in furDesVar:
                        if not f == []:
                            text(label=str(tab1 + f + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Sets deleted :\n', font = font)
                    for o in objectSetsVar:
                        if not o == []:
                            text(label=str(tab1 + o + tab2), wordWrap=False, backgroundColor=backgroundColor)
                    text(label=sep, backgroundColor = backgroundColor2, height = tHeight)
                    text(label='Unknown Nodes deleted :\n', font = font)
                    for u in unknowVar:
                        if not u == []:
                            text(label=str(tab1 + u + tab2), wordWrap=False, backgroundColor=backgroundColor)


#sanityCheck(1)
