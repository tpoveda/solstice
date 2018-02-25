#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_initializer.py
# by Tomás Poveda
# ______________________________________________________________________
# Script that is initialized automatically when Maya launches and sets up
# solstice_tools shelf and tools
# ______________________________________________________________________
# ==================================================================="""

import os
import xml.dom.minidom as minidom
import json
import logging

from maya import cmds
from maya import mel
import maya.utils

from spigot import SpigotClient

LOGGER = logging.getLogger('solstice_tools')

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def init():
    print '-'*100
    print '*'*100
    print '='*100
    print(sLog("Initializing Solstice Tools ..."))
    print '='*100
    print(sLog("Loading Utilities Tools ..."))
    try:
        import solstice_tools.scripts.solstice_utilities
    except:
        pass
    print(sLog("Loading Animation Tools ..."))
    try:
        import solstice_tools.scripts.solstice_animation
    except:
        pass
    print(sLog("Loading Pipeline Tools ..."))
    try:
        import solstice_tools.scripts.solstice_pipeline
    except:
        pass

    print '-'*100
    print(sLog('Building Solstice Tools Shelf ...'))
    try:
        print '-'*100
        mel.eval('if(`shelfLayout -exists solstice_shelf`) deleteUI solstice_shelf;')
        print(sLog('Solstice Tools Shelf already exists! Checking for updates ...'))
    except:
        print '*'*100
        print(sLog('Builiding Solstice Tools Shelf ...'))
        
    shelfTab = mel.eval('global string $gShelfTopLevel;')
    mel.eval('global string $solstice_shelf;')
    mel.eval('$solstice_shelf = `shelfLayout -cellWidth 33 -cellHeight 33 -p $gShelfTopLevel solstice_shelf`;')

    print(sLog('Building Solstice Tools Shelf Buttons ...'))
    try:
        dirname = os.path.dirname(__file__)
        buttonsFile = os.path.join(dirname, 'shelf_buttons.xml')
        xmlMenuDoc = minidom.parse(buttonsFile)
    except Exception as e:
        print(sLog('ERROR: Impossible to build Solstice Tools Shelf because shelf_buttons.xml does not exist!'))
        print e
        return
    for shelfItem in xmlMenuDoc.getElementsByTagName('shelfItem'):
        btnIcon = shelfItem.attributes['icon'].value
        btnAnnotation = shelfItem.attributes['ann'].value
        btnCommand = shelfItem.attributes['cmds'].value
        btnLabel = shelfItem.attributes['label'].value or ''
        if btnAnnotation == 'Separator':
            mel.eval('separator -enable 1 -width 12 -height 35 -manage 1 -visible 1 -preventOverride 0 -enableBackground 0 -style "shelf" -horizontal 0 -p $solstice_shelf ;')
        else:
            cmds.shelfButton(command=btnCommand, annotation=btnAnnotation, image=btnIcon, imageOverlayLabel=btnLabel)
    mel.eval('tabLayout -edit -tabLabel $solstice_shelf Solstice $gShelfTopLevel;')

    # --------------------------------------------------------------------------------------------------------------

    print(sLog('Initializing environment variables for Solstice Tools ...'))
    try:
        cli = SpigotClient()
        appIdentifier = os.environ.get("ARTELLA_APP_IDENTIFIER", None)
        if appIdentifier is None:
            mayaVer = maya.cmds.about(version=True).split()[0]
            appIdentifier = "maya.%s" % mayaVer
        cli.listen(appIdentifier, passMsgToMainThread)

        rsp = cli.execute(command_action='do', command_name='getMetaData', payload='{}')
        metaData = json.loads(rsp)
        os.environ['ART_LOCAL_ROOT'] = metaData['local_root']
    except:
        print(sLog("It was impossible to connect with Artella! Setting default values ..."))
        try:
            cfgFile = os.path.expanduser('~maya/solstice_settings.cfg')
            print(sLog('Config file: ', cfgFile))
            with open(cfgFile, 'r') as fl:
                cfgInfo = json.loads(fl.read())
            print(sLog('Config: ', cfgInfo))
            if cfgInfo:
                envDict = cfgInfo.get('env', {})
                for k, v in envDict.iteritems():
                    print(sLog('Setting environment variable > {} as {}'.format(k, v)))
                    os.environ[k] = v
        except Exception as e:
            print str(e)

    artellaVar = os.environ.get('ART_LOCAL_ROOT')
    print(sLog('Artella environment variable is set to: {}'.format(artellaVar)))

    if artellaVar and os.path.exists(artellaVar):
        os.environ['SOLSTICE_PROJECT'] = '{}/_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'.format(artellaVar)
    else:
        print(sLog('ERROR: Impossible to set Artella environment variables! Solstice Tools wont work correctly!'))

    print '='*100
    print(sLog("Solstices Tools initialization completed!"))
    print '='*100
    print '*'*100
    print '-'*100
    print '\n'

    try:
        cmds.evalDeferred('from solstice_config import solstice_main; solstice_main.runAtMayaStart()')
    except Exception as e:
        print(sLog('ERROR: Main Solstice function failed!'))
        print str(e)
        print '\n'
    return

def passMsgToMainThread(jsonMsg):
    maya.utils.executeInMainThreadWithResult(handleMessage, jsonMsg)

def handleMessage(jsonMsg):
    try:
        msg = json.loads(jsonMsg)

        if type(msg) == dict:
            commandName = msg['CommandName']
            args = msg['CommandArgs']

            if commandName == 'open':
                mayaFile = args['path']
                opened_file = maya.cmds.file(mayaFile, open=True, force=True)
                scenefile_type = maya.cmds.file(q=True, type=True)
                if type(scenefile_type) == list:
                    scenefile_type = scenefile_type[0]
                filepath = mayaFile.replace('\\', '/')
                maya.mel.eval('$filepath = "{filepath}";'.format(filepath=filepath))
                maya.mel.eval('addRecentFile $filepath "{scenefile_type}";'.format(scenefile_type=scenefile_type))
            elif commandName == 'import':
                path = args['path']
                maya.cmds.file(path, i=True, preserveReferences=True)
            elif commandName == 'reference':
                path = args['path']
                useRename = maya.cmds.optionVar(q='referenceOptionsUseRenamePrefix')
                if useRename:
                    namespace = maya.cmds.optionVar(q='referenceOptionsRenamePrefix')
                    maya.cmds.file(path, reference=True, namespace=namespace)
                else:
                    filename = os.path.basename(path)
                    namespace, _ = os.path.splitext(filename)
                    maya.cmds.file(path, reference=True, namespace=namespace)
            else:
                LOGGER.warn("Unknown command: %s", commandName)

    except Exception, e:
        LOGGER.warn("Error: %s", e)