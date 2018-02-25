# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_winterPicker.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Winter Character
______________________________________________________________________
==================================================================="""

# Import PySide modules
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance


# Import standard Python modules
import os

# Import custom modules
from pickers.picker import solstice_pickerWindow as window
from pickers.picker import solstice_pickerUtils as utils
import solstice_winterBodyPicker as bodyPicker
import solstice_winterFacialPicker as facialPicker

# --------------------------------------------------------------------------------------------
imagesPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
dataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
# --------------------------------------------------------------------------------------------

class Solstice_WinterPicker(window.Solstice_PickerWindow, object):

    def __init__(self, pickerName, pickerTitle, charName, parent=None, fullWindow=False):

        self._fullWindow = fullWindow
        self._bodyPickerData = os.path.join(dataPath, 'winterBodyPickerData.json')
        self._facialPickerData = os.path.join(dataPath, 'winterFacialPickerData.json')

        super(Solstice_WinterPicker, self).__init__(pickerName=pickerName, pickerTitle=pickerTitle, charName=charName, parent=parent)

    def initSetup(self):

        super(Solstice_WinterPicker, self).initSetup()

        return True

    def bodyPickerData(self):
        return self._bodyPickerData

    def facialPickerData(self):
        return self._facialPickerData

    def toolUI(self):

        # Init and check tool
        if self.initSetup() == True:

            # Init default UI for all pickers
            super(Solstice_WinterPicker, self).toolUI()

            self.setCharacterImage(os.path.join(imagesPath, 'winter_icon.png'))
            self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            self.load_pickers(fullwindow=self._fullWindow)
            self.updatePickers()

    def load_pickers(self, fullwindow=False):

        super(Solstice_WinterPicker, self).load_pickers(fullwindow=fullwindow)

        try:
            if self.bp:
                self.bp.setParent(None)
                self.bp.deleteLater()
            if self.fp:
                self.fp.setParent(None)
                self.fp.deleteLater()
            if self.pickers_layout:
                self.pickers_layout.setParent(None)
                self.pickers_layout.deleteLater()
        except:
            pass

        self.pickers_layout = QHBoxLayout()
        self.pickers_layout.setContentsMargins(5, 5, 5, 5)
        self.pickers_layout.setSpacing(2)
        self.mainLayout.addLayout(self.pickers_layout)

        self.bp = bodyPicker.solstice_winterBodyPicker(dataPath=self.bodyPickerData(), imagePath=os.path.join(imagesPath, 'pickerWinter_body.svg'))
        self.fp = facialPicker.solstice_winterFacialPicker(dataPath=self.facialPickerData(), imagePath=os.path.join(imagesPath, 'pickerWinter_facial.svg'))

        if fullwindow:
            for picker in [self.bp, self.fp]:
                self.pickers_layout.addWidget(picker)
        else:
            self.charTab = QTabWidget()
            self.pickers_layout.addWidget(self.charTab)
            self.charTab.addTab(self.bp, 'Body')
            self.charTab.addTab(self.fp, 'Facial')
            # self.charTab.setCurrentIndex(1)

    def updatePickers(self):
        for picker in [self.bp, self.fp]:
            picker.setNamespace(self.namespace.currentText())

    def setFullWindow(self, fullWindow):
        self._fullWindow = fullWindow

    def reloadData(self):
        self.bp.reloadData()


def initPicker(fullWindow=True):
    utils.dock_window(pickerName='winterPicker', pickerTitle='Solstice - Winter Picker', charName='Winter', dialog_class=Solstice_WinterPicker)
