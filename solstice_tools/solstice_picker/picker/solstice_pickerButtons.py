#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerButtons.py
by Tomás Poveda
Custom button used by the picker of Solstice Short Film
______________________________________________________________________
Button classes to be used in the pickers
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import solstice_pickerColors as colors
import solstice_pickerBaseButton as baseButton

import maya.cmds as cmds

class solstice_circularButton(baseButton.solstice_pickerBaseButton, object):
    def __init__(self,
                 x=0,
                 y=0,
                 text='',
                 control='',
                 parentCtrl='',
                 radius=30,
                 innerColor=colors.yellow,
                 outerColor=colors.blue,
                 glowColor=colors.red,
                 toggle=False,
                 enabled=True,
                 btnInfo=None,
                 parent=None):
        super(solstice_circularButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            innerColor=innerColor,
            outerColor=outerColor,
            glowColor=glowColor,
            toggle=toggle,
            enabled=enabled,
            btnInfo=btnInfo,
            parent=parent)

        self._radius = radius
        self.setRadius(radius)

    def radius(self):
        return self._radius

    def setRadius(self, radius):
        self._radius = radius
        self.setFixedWidth(radius)
        self.setFixedHeight(radius)

    def paintBorder(self, painter, x, y, width, height):
        #painter.drawEllipse(QRect(x + self._borderSize, y + self._borderSize, width - self._borderSize, height -self._borderSize))
        #painter.drawRoundedRect(QRect(x+1, y+1, width-1, height-1), self._radius, self._radius)
        pass

    def paintOuter(self, painter, x, y, width, height):
        pass
        #painter.drawEllipse(QRect(x + 2, y + 2, width - 3, height - 3))
        #painter.drawRoundedRect(QRect(x + 2, y + 2, width - 3, height - 3), self._radius, self._radius)

    def paintInner(self, painter, x, y, width, height):
        painter.drawEllipse(QRect(x + 3, y + 3, width - 8, height - 5))
        #painter.drawRoundedRect(QRect(x + 3, y + 3, width - 5, height - 5), self._radius - 1, self._radius - 1)

class solstice_rectangularButton(baseButton.solstice_pickerBaseButton, object):
    def __init__(self,
                 x=0,
                 y=0,
                 text='',
                 control='',
                 parentCtrl='',
                 cornerRadius=5,
                 width=30,
                 height=15,
                 innerColor=colors.yellow,
                 outerColor=colors.blue,
                 glowColor=colors.red,
                 toggle=False,
                 enabled=True,
                 btnInfo=None,
                 parent=None):
        super(solstice_rectangularButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            innerColor=innerColor,
            outerColor=outerColor,
            glowColor=glowColor,
            toggle=toggle,
            enabled=enabled,
            btnInfo=btnInfo,
            parent=parent)

        self._cornerRadius = cornerRadius
        self.setCornerRadius(cornerRadius)

        self.setFixedWidth(width)
        self.setFixedHeight(height)

    def cornerRadius(self):
        return self._cornerRadius

    def setCornerRadius(self, cornerRadius):
        self._cornerRadius = cornerRadius

    def setWidth(self, width):
        self.setFixedWidth(width)

    def setHeight(self, height):
        self.setFixedHeight(height)

    def paintBorder(self, painter, x, y, width, height):
        #painter.drawEllipse(QRect(x + self._borderSize, y + self._borderSize, width - self._borderSize, height -self._borderSize))
        #painter.drawRoundedRect(QRect(x+1, y+1, width-1, height-1), self._radius, self._radius)
        pass

    def paintOuter(self, painter, x, y, width, height):
        pass
        #painter.drawEllipse(QRect(x + 2, y + 2, width - 3, height - 3))
        #painter.drawRoundedRect(QRect(x + 2, y + 2, width - 3, height - 3), self._radius, self._radius)

    def paintInner(self, painter, x, y, width, height):
        #painter.drawEllipse(QRect(x + 3, y + 3, width - 8, height - 5))
        painter.drawRoundedRect(QRect(x + 3, y + 3, width - 5, height - 5), self._cornerRadius - 1, self._cornerRadius - 1)


class solstice_fkButton(solstice_circularButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):

        if text == '' or text == None:
            text = 'FK'

        super(solstice_fkButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            innerColor=colors.red,
            btnInfo=btnInfo,
            parent=parent)

    def setInfo(self, btnInfo):
        super(solstice_fkButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setRadius(btnInfo['radius'])

    def contextMenuEvent(self, event):
        menu = QMenu()
        selectHierarchyAction = menu.addAction('Select Hierarchy')
        resetControlAction = menu.addAction('Reset Control')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == selectHierarchyAction:
            self._selectHierarchy()
        elif action == resetControlAction:
            print 'Reset Action'

class solstice_ikButton(solstice_circularButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):

        if text == '' or text == None:
            text = 'IK'

        super(solstice_ikButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            innerColor=colors.yellow,
            btnInfo=btnInfo,
            parent=parent)

    def setInfo(self, btnInfo):
        super(solstice_ikButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setRadius(btnInfo['radius'])

class solstice_extraButton(solstice_rectangularButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
        super(solstice_extraButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            cornerRadius=cornerRadius,
            width=width,
            height=height,
            innerColor=colors.darkYellow,
            btnInfo=btnInfo,
            parent=parent
        )

    def setInfo(self, btnInfo):
        super(solstice_extraButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setCornerRadius(btnInfo['radius'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])

class solstice_moduleButton(solstice_rectangularButton, object):
    def __init__(
            self, x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
        super(solstice_moduleButton, self).__init__(
            x=x,
            y=y,
            text=text,
            cornerRadius=cornerRadius,
            width=width,
            height=height,
            innerColor=colors.black,
            btnInfo=btnInfo,
            parent=parent
        )

    def setInfo(self, btnInfo):
        super(solstice_moduleButton, self).setInfo(btnInfo)

        self.setCornerRadius(btnInfo['radius'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])

        self._part = btnInfo['part']

    def mousePressEvent(self, event):
        if self._part and self.scene():
            modifiers = cmds.getModifiers()
            shift = (modifiers & 1) > 0
            if not shift:
                cmds.select(clear=True)
            controls = self.scene().getPartControls(self._part)
            for ctrl in controls:
                try:
                    cmds.select(ctrl, add=True)
                except:
                    pass


