'''
-----------------------------------------------------------------------------------------------------
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 __   __        __  _____     __  ___
|__  |  | |    |__    |    | |    |__
 __| |__| |___  __|   |    | |__  |__

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
-----------------------------------------------------------------------------------------------------

SOLSTICE LIST WIDGET. 

made by Javi Gonzalez Alonso for Solstice shortfilm.
______________________________________________________________________________________________________
'''


import sys
from PySide2 import QtGui,QtCore,QtWidgets
import os
import json
from functools import partial


class Solstice_listWidget(QtWidgets.QListWidget):

        def __init__(self,*args,**kwargs):
            QtWidgets.QListWidget.__init__(self)

            #------------------------------------
            # Kwargs defaults -------------------
            #------------------------------------

            # Name of the Widget --

            self.name = kwargs['name'] if 'name' in kwargs.keys() else ''

            # Position --
            self.posX = kwargs['pos'][0] if 'pos' in kwargs.keys() else 5
            self.posY = kwargs['pos'][1] if 'pos' in kwargs.keys() else 5
            
            # Size --
            
            self.w = kwargs['size'][0] if 'size' in kwargs.keys() else 64
            self.h = kwargs['size'][1] if 'size' in kwargs.keys() else 64
            self.size = [self.w,self.h]
            
            # Items--
            self.items = kwargs['items'] if 'items' in kwargs.keys() else []

            # Func --
            
            # Icon per Item, sets an icon per each item in the list based on this True or False statement.
            # It'll pick an image for the icon already set by default unless the flag iconPerItemPath is 
            # is used in wich case it'll use it to find the desired image.--

            self.iconPerItem = kwargs['iconPerItem'] if 'iconPerItem' in kwargs.keys() else False
            self.iconPerItemPath = kwargs['iconPerItemPath'] if 'iconPerItemPath' in kwargs.keys() else '../images/solsticeIcon.png'
            self.iconSize = kwargs['iconSize'] if 'iconSize' in kwargs.keys() else 32
            # Parent --
            self.parent = kwargs['parent'] if 'parent' in kwargs.keys() else 'None'
            
            # Font --
            
            self.defaultFont = QtGui.QFont(kwargs['font'] if 'font' in kwargs.keys() else 'Montserrat')
            self.defaultFont.setBold(True)          
            
            #-----------------------------------------------------------------------------------------

            

            # Other Vars --
            
            self.listWidgetStyle = "QListWidget{background-color:rgba(25,25,25,180);border-style: solid;border-color:grey;border-width: 2.5px;border-radius: 10px;}QListWidget::item{color:white;}"
            self.listTitleStyle = "QLabel{background-color:rgba(125,125,125,255);border-style: solid;border-color:grey;border-width: 2.5px;border-radius: 10px; qproperty-alignment: AlignCenter;}"

            titleOfTheListWidget = QtWidgets.QLabel(self.name)
            titleOfTheListWidget.setFont(self.defaultFont)
            titleOfTheListWidget.setGeometry(self.posX,self.posY-32,self.w,32)
            titleOfTheListWidget.setParent(self.parent)
            

            titleOfTheListWidget.setStyleSheet(self.listTitleStyle)


            # Init methods ---------------------------------------------------------------------------

            
            self.defaultFont.setPixelSize(16)

            self.defaultItemColor = QtGui.QColor(125,125,125,180)
            self.defaultItemColor.setRgba(180)

            if self.parent != 'None':
                self.setParent(self.parent)

            self.setFont(self.defaultFont)
            self.setGeometry(self.posX,self.posY,self.w,self.h)
   
            self.setStyleSheet(self.listWidgetStyle)

            self.clear()
            self.addItems(self.items)
            if self.iconPerItem: 
                for item in self.items:
                    imgeded = QtGui.QPixmap(self.iconPerItemPath)
                    imged = imgeded.scaled(self.iconSize,self.iconSize)
                    icon = QtGui.QIcon(imged)
                    itmSize = QtCore.QSize(self.iconSize,self.iconSize)
                    self.setIconSize(itmSize)
                    itm = [self.item(x) for x in range(self.count()) if self.item(x).text() == item][0]
                    itm.setIcon(icon)
                    itm.setSizeHint(itmSize)
                    itm.setTextAlignment(QtCore.Qt.AlignCenter)
                    

            #---------------------------------------------------------------------

# Function Definitions -----------------------------------------------------------
        
        def setItemToDefaultColor(self,item):

            for x in range(self.count()):
    
                if self.item(x).text() == item:
                    self.item(x).setBackground(self.defaultItemColor)

        def setSelectedItemIcon(self,item,iconPath,iconSize=[32,32]):
            
            imgeded = QtGui.QPixmap(iconPath)
            imged = imgeded.scaled(iconSize[0],iconSize[1])
            icon = QtGui.QIcon(imged)
            itmSize = QtCore.QSize(iconSize[0],iconSize[1])
            self.setIconSize(itmSize)
            itm = [self.item(x) for x in range(self.count()) if self.item(x).text() == item][0]
            itm.setIcon(icon)
            itm.setSizeHint(itmSize)
            itm.setTextAlignment(QtCore.Qt.AlignCenter)
        

        def setItemColor(self,item,color):
            
            r = color[0]
            g = color[1]
            b = color[2]
            
            newItemColor = QtGui.QColor(r,g,b)
            for x in range(self.count()):
    
                if self.item(x).text() == item:
                    self.item(x).setBackground(newItemColor)
                

        def addItemsWithIcon(self,*args,**kwargs):
            
            perItem = kwargs['iconPerItem'] if 'iconPerItem' in kwargs.keys() else False
            iconPath = kwargs['iconPath'] if 'iconPath' in kwargs.keys() else '..//images//solsticeIcon.png'
            
            items = kwargs['items'] if 'items' in kwargs.keys() else []
            
            self.addItems(items)

            for item in items:
                if perItem:
                    if 'iconPath' not in kwargs.keys():
                        imgeded = QtGui.QPixmap( iconPath)
                    else:    
                        imgeded = QtGui.QPixmap( iconPath + item + '//' + item +'.png' )

                else:
                    imgeded = QtGui.QPixmap(iconPath)

                imged = imgeded.scaled(self.iconSize,self.iconSize)
                icon = QtGui.QIcon(imged)
                itmSize = QtCore.QSize(self.iconSize,self.iconSize)
                self.setIconSize(itmSize)
                itm = [self.item(x) for x in range(self.count()) if self.item(x).text() == item][0]
                itm.setIcon(icon)
                itm.setSizeHint(itmSize)
                itm.setTextAlignment(QtCore.Qt.AlignCenter)



        
#----------------------------------------------------------------------------------
