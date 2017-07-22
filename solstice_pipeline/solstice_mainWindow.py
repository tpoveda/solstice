'''
-----------------------------------------------------------------------------------------------------
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 __   __        __  _____     __  ___
|__  |  | |    |__    |    | |    |__
 __| |__| |___  __|   |    | |__  |__

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
-----------------------------------------------------------------------------------------------------

SOLSTICE MAIN WINDOW WIDGET. 

made by Javi Gonzalez Alonso for Solstice shortfilm.
______________________________________________________________________________________________________
'''


import sys
from PySide2 import QtGui,QtCore,QtWidgets
import os


class Solstice_mainWindow(QtWidgets.QMainWindow):

    def __init__(self,*args,**kwargs):
        
        QtWidgets.QMainWindow.__init__(self)
        self.windowStyle = QtWidgets.QStyleFactory.create('Fusion')
        self.setStyle(self.windowStyle)
        self.windowSize = QtCore.QSize(kwargs['size'][0],kwargs['size'][1]) if 'size' in kwargs.keys() else QtCore.QSize(768,768)


        #-------------------------------------------
        # Path Variables ---------------------------
        #-------------------------------------------
        

        self.pathRootDir = '..//'
        self.pipeImagesPath = os.getcwd()+'//images//'
        #print os.getcwd()+'//images//'

        #-------------------------------------------
        # BG IMAGE ---------------------------------
        #-------------------------------------------
        self.bgImageLabel = QtWidgets.QLabel()
        self.bgImageLabel.setParent(self)
        
        self.setFixedSize(self.windowSize)
        self.bgImageLabel.setFixedSize(self.windowSize)
        self.bgImageLabel.setStyle(self.windowStyle)
        
        
        self.defaultImageFile = self.pipeImagesPath + 'ToolsBG2.png'
        
        self.bgImagePixmap = QtGui.QPixmap(self.defaultImageFile)
        print self.defaultImageFile
        self.scaledBgImagePixmap = self.bgImagePixmap.scaled(self.windowSize)
        self.bgImageLabel.setPixmap(self.scaledBgImagePixmap)
        self.defaultIcon = self.pipeImagesPath +'solsticeIcon.png'


        self.defaultFont = QtGui.QFont('Montserrat')
        self.defaultFont.setPixelSize(16)

        
        
        #--------------------------------------------------------------------
        # MENUS -------------------------------------------------------------
        #--------------------------------------------------------------------
        
        
        
        self.menubar = QtWidgets.QMenuBar(self)
        
        self.menubar.setFont(self.defaultFont)
        self.menubar.setGeometry(0,0,768,32)
        
        self.setWindowIcon(QtGui.QIcon(self.defaultIcon))
        self.setWindowTitle('Solstice Shot Selector')

        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.setFont(self.defaultFont)
        
        self.openAction = QtWidgets.QAction('Open', self)
        self.exitAction = QtWidgets.QAction('Exit', self)

        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.exitAction)

        
        self.editMenu = self.menubar.addMenu('&Edit')
        self.editMenu.setFont(self.defaultFont)
        


        self.preferencesMenu = self.menubar.addMenu('&Preferences')
        self.preferencesMenu.setFont(self.defaultFont)
        self.changeBgImageAction = QtWidgets.QAction('Change BG Image', self)
        self.changeBgImageAction.triggered.connect(self.setBgImage)
        self.preferencesMenu.addAction(self.changeBgImageAction)



        #---------------------------------------------------------------------        
        
    def setBgImage(self,img='None'):

        print img
        if img == 'None':
            print img

            img = QtWidgets.QFileDialog.getOpenFileName(self,"Open Image", self.pathRootDir , "Image Files (*.png)")[0]
            print img
            if not img:
                print 'image not changed.'
            else:
                self.bgImagePixmap = QtGui.QPixmap(img)
                self.scaledBgImagePixmap = self.bgImagePixmap.scaled(self.windowSize)
                self.bgImageLabel.setPixmap(self.scaledBgImagePixmap)   


        else:
            self.bgImagePixmap = QtGui.QPixmap(img)
            self.scaledBgImagePixmap = self.bgImagePixmap.scaled(self.windowSize)
            self.bgImageLabel.setPixmap(self.scaledBgImagePixmap)
        
    def setWindowSize(self,x,y):

        self.windowSize = QtCore.QSize(x,y)
        self.setFixedSize(self.windowSize)
        self.bgImageLabel.setFixedSize(self.windowSize)

    #--------------------------------------------------------
    


