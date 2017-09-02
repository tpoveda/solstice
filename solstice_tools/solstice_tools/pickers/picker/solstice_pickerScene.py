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

import solstice_pickerButtons as btn
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
        self._parts = dict()
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

    def loadData(self, path):

        """
        Load picker scene data from a JSON file
        """

        #self.addButton(getattr(btn, 'solstice_fkButton')())

        with open(path) as fp:
            data = json.load(fp)
        if data.get('fileType') == 'pickerData':
            btnOffset = int(data.get('offset'))
            self._dataButtons = data['pickerButtons']
            for btn in self._dataButtons:
                self._createButton(btn, btnOffset)

        # Update control hierarchies
        for btn in self._buttons:
            if btn._parentCtrl != '':
                for newBtn in self._buttons:
                    if btn._parentCtrl == newBtn._control:
                        newBtn.addChild(btn)
        for btn in self._buttons:
            btn.updateHierarchy()

        # print self.getPartControls('spine1')

    def _createButton(self, btnData, offset=0):

        btnInfo = self._getButtonInfo(btnData, offset)
        newBtn = eval('btn.'+btnInfo['class']+'.'+btnInfo['class']+'()')
        newBtn.setInfo(btnInfo)
        self.addButton(newBtn)

        # ---------------------------------------------------------------

        if btnInfo['mirror'] != '' and btnInfo['mirror'] != None:
            newInfo = deepcopy(btnInfo)
            mirrorBtnInfo = self._getMirrorButtonInfo(newInfo, offset)
            newMirrorBtn = newBtn = eval('btn.'+mirrorBtnInfo['class']+'.'+mirrorBtnInfo['class']+'()')
            newMirrorBtn.setInfo(mirrorBtnInfo)
            self.addButton(newMirrorBtn)

    def getSideControls(self, side='M'):
        if self._parts.has_key(side):
            return self._parts[side]

    def getPartControls(self, type, side='', asButtons=False):
        controls = []
        for btn in self._buttons:
            btnInfo = btn.getInfo()
            if btnInfo.get('part'):
                if btnInfo['part'] == type:
                    if side != '':
                        print btnInfo['side']
                        if btnInfo['side'] == side:
                            if asButtons:
                                controls.append(btn)
                            else:
                                controls.append(btn._control)
        return controls

    def _getButtonControl(self, side, part, type, name, fullname=''):

        if fullname != '':
            return fullname
        else:
            if type == '':
                if side != '':
                    if side != '' and part != '' and name != '':
                        return '{0}_{1}_{2}_ctrl'.format(side, part, name)
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

    def _getButtonInfo(self, btnData, offset):

        btnClassName = 'solstice_fkButton'
        btnFullname = ''
        btnXPos = offset
        btnYPos = 0
        btnText = ''
        btnRadius = 30
        btnParent = ''
        btnMirror = ''
        btnOffset = 0
        btnSide = ''
        btnPart = 'default'
        btnType = ''
        btnName = 'default'
        btnWidth = 30
        btnHeight = 15
        btnGizmo = ''

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
            btnOffset = int(btnData['offset'])
        if btnData.get('side'):
            btnSide = btnData['side']
        if btnData.get('part'):
            btnPart = btnData['part']
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

        return btnInfo

    def _getMirrorButtonInfo(self, btnInfo, offset=0):

        newBtnInfo = btnInfo

        if btnInfo['side'] == '' or btnInfo['side'] == None:
            return

        if btnInfo['control'] == '' or btnInfo['control'] == '':
            return

        newSide = None
        currSide = btnInfo['side']
        for side in ['l', 'r', 'L', 'R']:
            if currSide in ['_{0}_'.format(side), '{0}_'.format(side), '_{0}'.format(side), '{0}'.format(side)]:
                newSide = side
                break

        if newSide == 'l' or newSide == 'L':
            newSide = 'R'
        elif newSide == 'r' or newSide == 'R':
            newSide = 'L'

        newBtnInfo['fullname'] = btnInfo['fullname'].replace(currSide, newSide)
        newBtnInfo['x'] = ((btnInfo['x'] + offset + 15 + (btnInfo['offset'])) * -1)
        if btnInfo['control'] != '':
            newBtnInfo['control'] = btnInfo['control'].replace(currSide, newSide)
            newBtnInfo['side'] = newSide
        if btnInfo['parent'] != '':
            newBtnInfo['parent'] = btnInfo['parent'].replace(currSide, newSide)

        return newBtnInfo

