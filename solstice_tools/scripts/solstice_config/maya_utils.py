#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------
"""
Utility methods used by the Maya callbacks.

Copyright (c) 2012 Next Education LLC
"""
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# TODO
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------
import json
import os
import sys

import maya.cmds

# ---------------------------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------------------------

# map node type names with attribute name that contains the file path to fix
# see function below to update this from config file: `loadArtConfig`
#
fix_path_node_attrs = {
    'file' : 'ftn',
    'imagePlane' : 'imn',
    'aiImage' : 'filename',
    'aiVolume' : 'filename',
    'audio' : 'filename',
    'AlembicNode' : 'abc_File',
    'PxrBump' : 'filename',
    'PxrNormalMap' : 'filename',
    'PxrTexture' : 'filename',
}

# ---------------------------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------------------------
def logError(msg):
    print msg
def logInfo(msg):
    print msg
def logWarning(msg):
    print msg
def logDebug(msg):
    print msg

def loadArtConfig():
    """ look for an environment variable, $ART_CONF_FILE, that contains a path to a config file.
        open that config file and look for a JSON structure 
        in that JSON structure check for a key named: "fixPathNodeAttrs"
        update the existing `fix_path_node_attrs` dictionary with the contents of
        that JSON hash.  
    """
    global fix_path_node_attrs
    if 'ART_CONF_FILE' in os.environ:
        art_conf_file = os.environ['ART_CONF_FILE']
        # load fixPathNodeAttrs
        try:
            with open(art_conf_file, 'r') as art_config:
                art_config_json = art_config.read()
            art_config_data = json.loads(art_config_json)
            if 'fixPathNodeAttrs' in art_config_data:
                fix_path_node_attrs.update(art_config_data['fixPathNodeAttrs'])
                msg = "updated fixPathNodeAttrs from ART_CONF_FILE."
                logInfo(msg)
        except Exception as e:
            msg = "unable to load ART_CONF_FILE: %s" % (e)
            logError(msg)

# run this at load time
loadArtConfig()

def validateEnvironmentForCallback(callback_name):
    """
    Check that all the necessary parts are available before executing
    the guts of a Maya callback method.
    """
    if not 'ART_LOCAL_ROOT' in os.environ:
        msg = "Unable to execute Maya '%s' callback, ART_LOCAL_ROOT is not set in the environment." % callback_name
        logError(msg)
        raise Exception(msg)


def fixReferencePathsInMayaScene(isFixedPath,
                                 attemptPathFix):
    """
    Queries any referenced files and makes sure their paths conform to the
    pipeline standards.
    """
    #local_storage_top = os.environ['ART_LOCAL_ROOT'] 

    fixed_nodes = list()
    try:
        path = None
        for node in maya.cmds.ls(type='reference'):
            try:
                path = maya.cmds.referenceQuery(node, filename=True, unresolvedName=True)
            except RuntimeError, e:
                continue
            if not isFixedPath(path):
                logInfo("Attempting to fix referenced path '%s'" % path)
                isLoaded = maya.cmds.referenceQuery(node, isLoaded=True)
                fixed_path = attemptPathFix(path)
                if fixed_path is not None:
                    logInfo("    fixed: '%s'" % fixed_path)
                    # So far, actually loading the file is the only way I've
                    # found to change the reference path, but it seems like
                    # there should be an attribute to poke
                    try:
                        maya.cmds.file(fixed_path, loadReference=node)
                    except RuntimeError, e:
                        msg = "Runtime error while loading a reference in Maya."
                        logError(msg)
                        logError(unicode(e))
                    if not isLoaded:
                        try:
                            maya.cmds.file(unloadReference=node)
                        except RuntimeError, e:
                            msg = "Runtime error while unloading a reference in Maya."
                            logError(msg)
                            logError(unicode(e))
                    fixed_nodes.append(node)

    except RuntimeError, e:
        msg = "Runtime error while querying a reference in Maya."
        logError(msg)
        logError(unicode(e))

    logDebug("Exiting fixReferencePathsInMayaScene()...")
    return fixed_nodes


def fixFilePathsInMayaScene(isFixedPath,
                            attemptPathFix,
                            fixReferencedNodes=False):
    """
    Queries any file paths and makes sure their they conform to the
    pipeline standards.
    """
    fixed_nodes = list()
    try:
        # Iterate through the files in the Maya scene, checking
        # each one. If the file isn't coming from a referenced file
        # itself, fix the path.
        for node_type in fix_path_node_attrs:
        
            for node in maya.cmds.ls(type=node_type):
                try:
                    if not fixReferencedNodes and maya.cmds.referenceQuery(node, isNodeReferenced=True):
                        # Skip nodes that are from referenced files.
                        continue
                except RuntimeError, e:
                    # Certain ref nodes throw errors
                    continue
    
                attr_name = "%s.%s" % (node, fix_path_node_attrs[node_type])
                path = maya.cmds.getAttr(attr_name)
    
                if not isFixedPath(path):
                    logInfo("Attempting to fix file path '%s'" % path)
                    fixed_path = attemptPathFix(path)
                    if fixed_path is not None:
                        logInfo("    fixed: '%s'" % fixed_path)
                        maya.cmds.setAttr(attr_name, fixed_path, type='string')
                        fixed_nodes.append(node)
                    else:
                        logInfo("    failed")
                else:
                    logInfo("Skipping well-known path '%s'" % path)

    except RuntimeError, e:
        msg = "Runtime error while querying a reference in Maya."
        logError(msg)
        logError(unicode(e))

    logDebug("Exiting fixFilePathsInMayaScene()...")
    return fixed_nodes

        # TODO: Do the path replacement. I don't think test for the file's
        # existence is proper in this case. Is it? Should they exist if the
        # Maya scene was using them?

        # Check if the path starts with $ART_LOCAL_ROOT
#        if path and os.path.isfile(path):
#           if am.client.common.xpath.isSubPath(path, local_storage_top):
            


# ---------------------------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print("This is the test harness!!!")
    sys.exit(0)    
