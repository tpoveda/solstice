#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pickerButtons.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Button classes to be used in the pickers
# ______________________________________________________________________
# ==================================================================="""
#
# try:
#     from PySide2.QtGui import *
#     from PySide2.QtCore import *
#     from PySide2.QtWidgets import *
# except:
#     from PySide.QtGui import *
#     from PySide.QtCore import *
#
# import solstice_pickerUtils as utils
# import solstice_pickerColors as colors
# import solstice_pickerBaseButton as baseButton
#
# import maya.cmds as cmds
#
# class solstice_fkButton(solstice_circularButton, object):
#     def __init__(
#             self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):
#
#         btnText = text
#         if text == '' or text == None:
#             btnText = 'FK'
#
#         super(solstice_fkButton, self).__init__(
#             x=x,
#             y=y,
#             text=btnText,
#             control=control,
#             parentCtrl=parentCtrl,
#             radius=radius,
#             innerColor=colors.blue,
#             btnInfo=btnInfo,
#             parent=parent)
#
#     def setInfo(self, btnInfo):
#         super(solstice_fkButton, self).setInfo(btnInfo)
#
#         self.setControl(btnInfo['control'])
#         self.setParentControl(btnInfo['parent'])
#         self.setRadius(btnInfo['radius'])
#         self.setGizmo(btnInfo['gizmo'])
#
#     def contextMenuEvent(self, event):
#         menu = QMenu()
#         selectHierarchyAction = menu.addAction('Select Hierarchy')
#         resetControlAction = menu.addAction('Reset Control')
#         mirrorControlAction = menu.addAction('Mirror Control')
#         flipControlAction = menu.addAction('Flip Control')
#         action = menu.exec_(self.mapToGlobal(event.pos()))
#         if action == selectHierarchyAction:
#             self._selectHierarchy()
#         elif action == resetControlAction:
#             self._resetControl()
#         elif action == mirrorControlAction:
#             self._mirrorControl()
#         elif action == flipControlAction:
#             self._flipControl()
#
# class solstice_ikButton(solstice_circularButton, object):
#     def __init__(
#             self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):
#
#         btnText = text
#         if text == '' or text == None:
#             btnText = 'IK'
#
#         super(solstice_ikButton, self).__init__(
#             x=x,
#             y=y,
#             text=btnText,
#             control=control,
#             parentCtrl=parentCtrl,
#             radius=radius,
#             innerColor=colors.yellow,
#             btnInfo=btnInfo,
#             parent=parent)
#
#     def setInfo(self, btnInfo):
#         super(solstice_ikButton, self).setInfo(btnInfo)
#
#         self.setControl(btnInfo['control'])
#         self.setParentControl(btnInfo['parent'])
#         self.setRadius(btnInfo['radius'])
#         self.setGizmo(btnInfo['gizmo'])
#
#     def contextMenuEvent(self, event):
#         menu = QMenu()
#         selectHierarchyAction = menu.addAction('Select Hierarchy')
#         resetControlAction = menu.addAction('Reset Control')
#         mirrorControlAction = menu.addAction('Mirror Control')
#         flipControlAction = menu.addAction('Flip Control')
#         action = menu.exec_(self.mapToGlobal(event.pos()))
#         if action == selectHierarchyAction:
#             self._selectHierarchy()
#         elif action == resetControlAction:
#             self._resetControl()
#         elif action == mirrorControlAction:
#             self._mirrorControl()
#         elif action == flipControlAction:
#             self._flipControl()
#
# class solstice_extraButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='', control='', parentCtrl='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_extraButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             control=control,
#             parentCtrl=parentCtrl,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.darkYellow,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_extraButton, self).setInfo(btnInfo)
#
#         self.setControl(btnInfo['control'])
#         self.setParentControl(btnInfo['parent'])
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self.setGizmo(btnInfo['gizmo'])
#         self._side = btnInfo['side']
#
# class solstice_pinButton(solstice_circularButton, object):
#     def __init__(
#             self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):
#
#         super(solstice_pinButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             control=control,
#             parentCtrl=parentCtrl,
#             radius=radius,
#             innerColor=colors.blue,
#             btnInfo=btnInfo,
#             parent=parent)
#
#     def setInfo(self, btnInfo):
#         super(solstice_pinButton, self).setInfo(btnInfo)
#
#         self.setControl(btnInfo['control'])
#         self.setParentControl(btnInfo['parent'])
#         self.setRadius(btnInfo['radius'])
#         self.setGizmo(btnInfo['gizmo'])
#
# class solstice_moduleButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_moduleButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.black,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_moduleButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         if self._part and self.scene():
#             modifiers = cmds.getModifiers()
#             shift = (modifiers & 1) > 0
#             if not shift:
#                 cmds.select(clear=True)
#             controls = self.scene().getPartControls(self._part, self._side)
#             for ctrl in controls:
#                 try:
#                     cmds.select(ctrl, add=True)
#                 except:
#                     pass
#
#     def contextMenuEvent(self, event):
#         menu = QMenu()
#         resetModuleAction = menu.addAction('Reset module')
#         mirrorModuleAction = menu.addAction('Mirror module')
#         flipModuleAction = menu.addAction('Flip module')
#         action = menu.exec_(self.mapToGlobal(event.pos()))
#         controls = self.scene().getPartControls(self._part, self._side, asButtons=True)
#         @utils.pickerUndo
#         def resetControls():
#             for control in controls:
#                 control._resetControl()
#         @utils.pickerUndo
#         def mirrorControls():
#             for control in controls:
#                 control._mirrorControl()
#         @utils.pickerUndo
#         def flipControls():
#             for control in controls:
#                 control._flipControl()
#         if action == resetModuleAction:
#             resetControls()
#         elif action == mirrorModuleAction:
#             mirrorControls()
#         elif action == flipModuleAction:
#             flipControls()
#
# class solstice_mirrorButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='MIRROR', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_mirrorButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.black,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_mirrorButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         @utils.pickerUndo
#         def mirrorControls():
#             if self._part and self.scene():
#                 controls = self.scene().getPartControls(self._part, self._side, asButtons=True)
#                 for control in controls:
#                     control._mirrorControl()
#         mirrorControls()
#
# class solstice_flipButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='MIRROR', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_flipButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.black,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_flipButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         print 'FLIPPING ARM'
#
# class solstice_ikSwitchButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='IK', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_ikSwitchButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.yellow,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_ikSwitchButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         print 'FLIPPING ARM'
#
# class solstice_fkSwitchButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='IK', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_fkSwitchButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.red,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_fkSwitchButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         print 'FLIPPING ARM'
#
# class solstice_keyPartButton(solstice_rectangularButton, object):
#     def __init__(
#             self, x=0, y=0, text='IK', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
#         super(solstice_keyPartButton, self).__init__(
#             x=x,
#             y=y,
#             text=text,
#             cornerRadius=cornerRadius,
#             width=width,
#             height=height,
#             innerColor=colors.green,
#             btnInfo=btnInfo,
#             parent=parent
#         )
#
#     def setInfo(self, btnInfo):
#         super(solstice_keyPartButton, self).setInfo(btnInfo)
#
#         self.setCornerRadius(btnInfo['radius'])
#         self.setWidth(btnInfo['width'])
#         self.setHeight(btnInfo['height'])
#         self._part = btnInfo['part']
#         self._side = btnInfo['side']
#
#     def mousePressEvent(self, event):
#         pass