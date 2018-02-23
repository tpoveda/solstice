import os

import maya.cmds as cmds

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def withinArtellaScene():
    cur_scene = cmds.file(q=True, sn=True) or 'untitled'
    print(sLog('Current scene name : {}'.format(cur_scene)))
    if 'artella' not in cur_scene.lower():
        return False
    return True

def runAtMayaStart(updateProject=False):
    if updateProject:
        updateSolsticeProject()
    if not withinArtellaScene():
        pass
    print(sLog('Checking for Solstice Tools updates ...'))
    try:
        import solstice_updater as s_updater
        s_updater.updateTools()
    except Exception as e:
        print str(e)

# --------------------------------------------------------------------------------------

def updateSolsticeProject():
    try:
        print(sLog('Setting Solstice Project ...'))
        solsticeProjectFolder = os.environ.get('SOLSTICE_PROJECT', 'folder-not-defined')
        if solsticeProjectFolder and os.path.exists(solsticeProjectFolder):
            cmds.workspace(solsticeProjectFolder, openWorkspace=True)
            print(sLog('Solstice Project setup succesfully! => {}'.format(solsticeProjectFolder)))
        else:
            print(sLog('Unable to set Solstice project! Folder {} does not exists!'.format(solsticeProjectFolder)))
    except Exception as e:
        print str(e)