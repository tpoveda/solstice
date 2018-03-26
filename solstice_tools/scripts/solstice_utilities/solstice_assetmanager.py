
#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pickers.py
# by Tomas Poveda
#  Asset manager for Solstice Tool
# ==================================================================="""

#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pickers.py
# by Tomas Poveda
#  Tool that allows to instantiate geometry in different ways
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.cmds as cmds

from solstice_utils import _getMayaWindow, readJSON

class solstice_assetmanager(QMainWindow, object):
    def __init__(self):
        super(solstice_assetmanager, self).__init__(_getMayaWindow())

        winName = 'solstice_assetmanager_window'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('Solstice Tools - Asset Manager - v.1.0')
        self.customUI()
        self.show()

    def customUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignCenter)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

def initUI():
    solstice_instanciator()