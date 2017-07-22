'''
-----------------------------------------------------------------------------------------------------
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 __   __        __  _____     __  ___
|__  |  | |    |__    |    | |    |__
 __| |__| |___  __|   |    | |__  |__

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
-----------------------------------------------------------------------------------------------------

SOLSTICE PUSH BUTTON WIDGET. 

made by Javi Gonzalez Alonso for Solstice shortfilm.
______________________________________________________________________________________________________
'''


import sys
from PySide2 import QtGui,QtCore,QtWidgets
import os

from functools import partial

class Solstice_pushButton(QtWidgets.QPushButton):

        def __init__(self,*args,**kwargs):
            QtWidgets.QPushButton.__init__(self)

            #------------------------------------
            # Kwargs defaults -------------------
            #------------------------------------

            # Position --
            self.posX = kwargs['pos'][0] if 'pos' in kwargs.keys() else 5
            self.posY = kwargs['pos'][1] if 'pos' in kwargs.keys() else 5
            
            # Size --
            self.w = kwargs['size'][0] if 'size' in kwargs.keys() else 64
            self.h = kwargs['size'][1] if 'size' in kwargs.keys() else 64

            # Text --
            self.text = kwargs['text'] if 'text' in kwargs.keys() else 'default'
            
            # Func --
            self.func = kwargs['func'] if 'func' in kwargs.keys() else None
            
            # Icon --
            self.icon = kwargs['icon'] if 'icon' in kwargs.keys() else None

            # Parent --
            self.parent = kwargs['parent'] if 'parent' in kwargs.keys() else None
            
            # Font --
            self.defaultFont = QtGui.QFont(kwargs['font'] if 'font' in kwargs.keys() else 'Montserrat')
            self.defaultFont.setBold(True)          
            
            # transparentStyle --
            
            self.transparentStyle = kwargs['transparentStyle'] if 'transparentStyle' in kwargs.keys() and isinstance(kwargs['transparentStyle'],bool) else False
                
            #-----------------------------------------------------------------------------------------

            # Other Vars --
            self.buttonStyle_transparent = "QPushButton{opacity: 50;background-color:rgba(125,125,125,180);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;} QPushButton:hover{background-color:rgba(120,105,125,180);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;} QPushButton:pressed{background-color:rgba(150,135,155,180);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;}   "            
            self.buttonStyle = "QPushButton{opacity: 50;background-color:rgba(125,125,125,255);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;} QPushButton:hover{background-color:rgba(120,105,125,255);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;} QPushButton:pressed{background-color:rgba(150,135,155,255);border-style: solid;border-color: grey;border-width: 2.5px;border-radius: 10px;}   "            
            # Init methods ---------------------------------------------------------------------------

            self.setText(self.text)
            self.defaultFont.setPixelSize(16)

            if self.parent != None:
                self.setParent(self.parent)

            if self.icon != None:
                self.buttonIcon = QtGui.QIcon(self.icon)
                self.buttonIconSize = QtCore.QSize(self.w,self.h)
                self.setIcon(self.buttonIcon)
                self.setIconSize(self.buttonIconSize)

            self.setFont(self.defaultFont)
            self.setGeometry(self.posX,self.posY,self.w,self.h)
            if self.transparentStyle == True:

                self.setStyleSheet(self.buttonStyle_transparent)
            else:
                self.setStyleSheet(self.buttonStyle)

            if self.func != None:
                self.clicked.connect(partial(self.func,self))

            #---------------------------------------------------------------------

# Function Definitions -----------------------------------------------------------

        def setButtonSize(self,w,h):
            
            self.w = w
            self.h = h

            self.setGeometry(self.posX,self.posY,self.w,self.h)

        def setButtonPos(self,posX,posY):
            
            self.posX = posX
            self.posY = posY
            
            self.setGeometry(self.posX,self.posY,self.w,self.h)

        def setButtonIcon(self,icon):
            self.icon = icon
            self.buttonIcon = QtGui.QIcon(self.icon)
            self.buttonIconSize = QtCore.QSize(self.w,self.h)
            self.setIcon(self.buttonIcon)
            self.setIconSize(self.buttonIconSize)            

#----------------------------------------------------------------------------------
