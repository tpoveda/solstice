#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: sPickerScene.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Solstice characters
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import os
import json
from copy import deepcopy
import imp

import maya.cmds as cmds

import solstice_pickerButtons as btn
import solstice_pickerPart
import solstice_pickerBaseButton as baseButton

class solstice_pickerScene(QGraphicsScene, object):

    """
    Scene for the picker
    """

    __DEFAULT_SCENE_WIDTH__ = 100
    __DEFAULT_SCENE_HEIGHT__ = 200

    def __init__(self, dataPath=None, namespace='', parent=None):
        super(solstice_pickerScene, self).__init__(parent=parent)

        self._dataPath = dataPath
        self._buttons = list()
        self._dataButtons = None
        self._parts = list()
        self._namespace = namespace

        self.setDefaultSize()

        self.reloadData()

    def reloadData(self):

        """
        Reloads the data of the picker
        """

        # TODO: Check why if takes so much time to reload (when doing multiple times)

        self.clear()

        if self._dataPath is not '' and self._dataPath is not None:
            if os.path.isfile(self._dataPath):
                self.loadData(self._dataPath)

        self.update()

    def updateState(self):

        """
        Updates the state of the picker.
        Useful when the picker is not correctly syncronized with the state of the character
        This can happen when using undo/redo actions
        """

        for part in self._parts:
            if part.hasFKIK():
                if part.getFKIK(asText=True) == 'FK':
                    part.setFK()
                else:
                    part.setIK()


    def setNamespace(self, namespace):
        self._namespace = namespace

    def setSize(self, width, height):

        """
        Set the size of the scene setting the scene in the middle position
        """

        self.setSceneRect(-width/2, -height/2, width, height)

    def setDefaultSize(self):

        """
        Sets the scene with default size
        """

        return self.setSize(self.__DEFAULT_SCENE_WIDTH__, self.__DEFAULT_SCENE_HEIGHT__)

    def getBoundingRect(self):

        """
        Returns the bounding rect of the scene taking in account all the items inside of it
        """

        return self.itemsBoundingRect()

    def addButton(self, newBtn=None):

        """
        Add a new picker button to the scene
        """

        if newBtn is None:
            newBtn = btn.solstice_fkButton()

        newBtn.setScene(self)
        self.addWidget(newBtn)
        self._buttons.append(newBtn)

        partFound = None
        for part in self._parts:
            if part.name == newBtn._part and part.side == newBtn._side:
                partFound = part
        if partFound is None:
            partFound = solstice_pickerPart.solstice_pickerPart(name=newBtn._part, side=newBtn._side)
            self._parts.append(partFound)

        partFound.addButton(newBtn)

        newBtn.postCreation()

    def loadData(self, path):

        """
        Load picker scene data from a JSON file
        """

        self.pickerData = {}

        with open(path) as fp:
            data = json.load(fp)
        if data.get('fileType') != 'pickerData':
            print 'ERROR: Picker data is not valid'
            return
        offset = int(data.get('offset'))

        pickerButtons = data.get('pickerButtons')
        if pickerButtons is None:
            return

        parts = pickerButtons.get('parts')
        if parts is None:
            return
        self.pickerData['parts'] = {}
        for part, v in parts.iteritems():
            self.pickerData['parts'][part] = {}
            for buttonClass, classButtons in v.iteritems():
                self.pickerData['parts'][part][buttonClass] = []
                for newBtn in classButtons:
                    self._createButton(newBtn, part, buttonClass, offset)

        # Update control hierarchies
        for btn in self._buttons:
            if btn._parentCtrl != '':
                for newBtn in self._buttons:
                    if btn._parentCtrl == newBtn._control:
                        newBtn.addChild(btn)

        for btn in self._buttons:
            btn.updateHierarchy()

        for part in self._parts:
            if part.hasFKIK():
                if part.getFKIK(asText=True) == 'FK':
                    part.setFK()
                else:
                    part.setIK()

    def _createButton(self, btnData, part, buttonClass, offset=0):

        btnInfo = self._getButtonInfo(btnData, part, offset, buttonClass)
        newBtn = eval('btn.'+buttonClass+'.'+buttonClass+'()')
        newBtn.setInfo(btnInfo)
        self.pickerData['parts'][part][buttonClass].append(newBtn)
        self.addButton(newBtn)

        # ---------------------------------------------------------------
        if btnInfo['mirror'] != '' and btnInfo['mirror'] != None:
            newInfo = deepcopy(btnInfo)
            mirrorBtnInfo = self._getMirrorButtonInfo(newInfo, offset)
            newMirrorBtn = newBtn = eval('btn.'+mirrorBtnInfo['class']+'.'+mirrorBtnInfo['class']+'()')
            newMirrorBtn.setInfo(mirrorBtnInfo)
            self.pickerData['parts'][part][buttonClass].append(newMirrorBtn)
            self.addButton(newMirrorBtn)

    def getSideControls(self, side='M'):
        if self._parts.has_key(side):
            return self._parts[side]

    def getPartControls(self, type, side='', asButtons=False):
        controls = []
        for btn in self._buttons:
            btnInfo = btn.getInfo()
            if btnInfo and btnInfo.get('part'):
                if btnInfo['part'] == type:
                    if side != '':
                        if btnInfo['side'] == side:
                            if asButtons:
                                controls.append(btn)
                            else:
                                controls.append(btn._control)
                    else:
                        if asButtons:
                            controls.append(btn)
                        else:
                            controls.append(btn._control)
        return controls

    def getPartControlGroup(self, type, side=''):
        controls = self.getPartControls(type=type, side=side, asButtons=True)
        if controls:
            return controls[0].controlGroup

    def getPartFkIkState(self, type, side=''):
        partCtrlGrp = self.getPartControlGroup(type=type, side=side)
        if cmds.objExists(partCtrlGrp):
            if cmds.attributeQuery('FK_IK', node=partCtrlGrp, exists=True):
                return cmds.getAttr(partCtrlGrp+'.FK_IK')

    def _getButtonControl(self, side, part, type, name, fullname=''):

        if fullname != '':
            return fullname
        else:
            if type == '':
                if side != '':
                    if side != '' and name != '':
                        if part != '':
                            return '{0}_{1}_{2}_ctrl'.format(side, part, name)
                        else:
                            return '{0}_{1}_ctrl'.format(side, name)
                else:
                    if part != '' and name != '':
                        return '{0}_{1}_ctrl'.format(part, name)
            else:
                if side != '':
                    if side != '' and part != '' and type != '' and name != '':
                        return '{0}_{1}_{2}_{3}_ctrl'.format(side, part, type, name)
                else:
                    if part != '' and type != '' and name != '':
                        return '{0}_{1}_{2}_ctrl'.format(part, type, name)
        return ''

    def _getButtonInfo(self, btnData, part, offset, className):

        btnClassName = className
        btnFullname = ''
        btnXPos = offset
        btnYPos = 0
        btnText = ''
        btnRadius = 30
        btnParent = ''
        btnMirror = ''
        btnOffset = [0,0]
        btnSide = ''
        btnPart = part
        btnType = ''
        btnName = 'default'
        btnWidth = 30
        btnHeight = 15
        btnGizmo = ''
        btnColor = None
        btnGlowColor = None
        btnFKIKControl = ''
        btnCommand = ''

        if btnData.get('class'):
            btnClassName = btnData['class']
        if btnData.get('fullname'):
            btnFullname = btnData['fullname']
        if btnData.get('x'):
            btnXPos = int(btnData['x']) - offset
        if btnData.get('y'):
            btnYPos = int(btnData['y']) - offset
        if btnData.get('text'):
            btnText = btnData['text']
        if btnData.get('radius'):
            btnRadius = int(btnData['radius'])
        if btnData.get('parent'):
            btnParent = btnData['parent']
        if btnData.get('mirror'):
            btnMirror = btnData['mirror']
        if btnData.get('offset'):
            btnOffset = btnData['offset']
        if btnData.get('side'):
            btnSide = btnData['side']
        if btnData.get('type'):
            btnType = btnData['type']
        if btnData.get('name'):
            btnName = btnData['name']
        if btnData.get('width'):
            btnWidth = int(btnData['width'])
        if btnData.get('height'):
            btnHeight = int(btnData['height'])
        if btnData.get('gizmo'):
            btnGizmo = btnData['gizmo']
        if btnData.get('color'):
            btnColor = btnData['color']
        if btnData.get('glowColor'):
            btnGlowColor = btnData['glowColor']
        if btnData.get('FKIKControl'):
            btnFKIKControl = btnData['FKIKControl']
        if btnData.get('command'):
            btnCommand = btnData['command']

        btnCtrl = self._getButtonControl(btnSide, btnPart, btnType, btnName, fullname=btnFullname)

        btnInfo = {}
        btnInfo['class'] = btnClassName
        btnInfo['fullname'] = btnFullname
        btnInfo['x'] = btnXPos
        btnInfo['y'] = btnYPos
        btnInfo['text'] = btnText
        btnInfo['radius'] = btnRadius
        btnInfo['control'] = btnCtrl
        btnInfo['parent'] = btnParent
        btnInfo['mirror'] = btnMirror
        btnInfo['offset'] = btnOffset
        btnInfo['side'] = btnSide
        btnInfo['part'] = btnPart
        btnInfo['type'] = btnType
        btnInfo['name'] = btnName
        btnInfo['width'] = btnWidth
        btnInfo['height'] = btnHeight
        btnInfo['gizmo'] = btnGizmo
        btnInfo['color'] = btnColor
        btnInfo['glowColor'] = btnGlowColor
        btnInfo['FKIKControl'] = btnFKIKControl
        btnInfo['command'] = btnCommand

        return btnInfo

    def _getMirrorButtonInfo(self, btnInfo, offset=0):

        newBtnInfo = btnInfo

        if btnInfo['side'] == '' or btnInfo['side'] == None:
            return

        if btnInfo['control'] == '' or btnInfo['control'] == '':
            return

        available_sides = list()
        saved_side = btnInfo['side']
        for side in ['L', 'R']:
            for currSide in ['_{0}_'.format(side), '{0}_'.format(side), '_{0}'.format(side)]:
                available_sides.append(currSide)
            if btnInfo['side'] == side:
                if btnInfo['side'] == 'l' or btnInfo['side'] == 'L':
                    saved_side = 'R'
                elif btnInfo['side'] == 'r' or btnInfo['side'] == 'R':
                    saved_side = 'L'

        curr_side = None
        valid_side = None
        for side in available_sides:
            if side in btnInfo['control']:
                curr_side = side
                break

        if curr_side is None:
            return

        if 'l' in curr_side or 'L' in curr_side:
            valid_side = curr_side.replace('l', 'r').replace('L', 'R')
        elif 'r' in curr_side or 'R' in curr_side:
            valid_side = curr_side.replace('r', 'l').replace('R', 'L')

        if valid_side is None:
            return

        newBtnInfo['fullname'] = btnInfo['fullname'].replace(curr_side, valid_side)
        newBtnInfo['x'] = ((btnInfo['x'] + offset + 15 + (btnInfo['offset'][0])) * -1)
        newBtnInfo['y'] = newBtnInfo['y'] + btnInfo['offset'][1]
        if btnInfo['control'] != '':
            newBtnInfo['control'] = btnInfo['control'].replace(curr_side, valid_side)
            newBtnInfo['side'] = saved_side
        if btnInfo['parent'] != '':
            newBtnInfo['parent'] = btnInfo['parent'].replace(curr_side, valid_side)
        if btnInfo['FKIKControl'] != '':
            newBtnInfo['FKIKControl'] = btnInfo['FKIKControl'].replace(curr_side, valid_side)

        return newBtnInfo

