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
from PySide2.QtWidgets import QPushButton

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import os
import json

import solstice_pickerButtons as btn

class solstice_pickerScene(QGraphicsScene, object):

    """
    Scene for the picker
    """

    __DEFAULT_SCENE_WIDTH__ = 100
    __DEFAULT_SCENE_HEIGHT__ = 200

    def __init__(self, dataPath=None, parent=None):
        super(solstice_pickerScene, self).__init__(parent=parent)

        self._dataPath = dataPath
        self._buttons = list()
        self._dataButtons = None
        self._parts = dict()

        self.setDefaultSize()

        self.reloadData()

    def reloadData(self):
        self.clear()

        if self._dataPath is not '' and self._dataPath is not None:
            if os.path.isfile(self._dataPath):
                self.loadData(self._dataPath)


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

    def _createButton(self, btnData, offset):


        btnInfo = self._getButtonInfo(btnData, offset)

        # ---------------------------------------------------------------

        if btnInfo['mirror'] != '':
            btnInfo = self._getMirrorButtonInfo(btnInfo, offset)

        # ---------------------------------------------------------------

        newBtn = getattr(btn, btnInfo['class'])()
        newBtn.setInfo(btnInfo)
        self.addButton(newBtn)

    def getSideControls(self, side='M'):
        if self._parts.has_key(side):
            return self._parts[side]

    def getPartControls(self, type):
        controls = []
        for btn in self._buttons:
            btnInfo = btn.getInfo()
            if btnInfo.get('part'):
                if btnInfo['part'] == type:
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

        return btnInfo

    def _getMirrorButtonInfo(self, btnInfo, offset):

        btnMirrorCtrl = btnInfo['mirror']
        mirrorBtnInfo = None
        for newBtn in self._dataButtons:
            btInf = self._getButtonInfo(newBtn, offset)
            if btInf['control'] != '':
                if btInf['control'] == btnMirrorCtrl:
                    mirrorBtnInfo = btInf
                    break

        if mirrorBtnInfo is not None:
            btnInfo['class'] = mirrorBtnInfo['class']
            btnInfo['fullname'] = mirrorBtnInfo['fullname']
            btnInfo['x'] = ((mirrorBtnInfo['x'] + offset + 22 + (btnInfo['offset'])) * -1)
            btnInfo['y'] = mirrorBtnInfo['y']
            btnInfo['radius'] = mirrorBtnInfo['radius']
            btnInfo['text'] = mirrorBtnInfo['text']
            btnInfo['control'] = mirrorBtnInfo['control']
            if btnInfo['control'] != '':
                btnInfo['control'] = btnInfo['control'].replace('L_', 'R_')
                btnInfo['side'] = mirrorBtnInfo['side'].replace('L', 'R')
                btnInfo['part'] = mirrorBtnInfo['part']
                btnInfo['name'] = mirrorBtnInfo['name']
            btnInfo['parent'] = mirrorBtnInfo['parent']
            if btnInfo['parent'] != '':
                btnInfo['parent'] = btnInfo['child'].replace('L_', 'R_')
            btnInfo['width'] = mirrorBtnInfo['width']
            btnInfo['height'] = mirrorBtnInfo['height']

        return btnInfo

