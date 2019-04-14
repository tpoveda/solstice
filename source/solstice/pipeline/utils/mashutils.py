#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities functions when working with Maya MASH nodes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.utils import namingutils as naming
from solstice.pipeline.utils import mayautils

import maya.cmds as cmds
import maya.mel as mel

if sp.dcc.get_version() <= 2017:
    import MASH.api as mapi
    import MASH.undo as undo
    import mash_repro_utils
    import mash_repro_aetemplate
    import MASHoutliner
elif sp.dcc.get_version() >= 2018:
    import MASH.api as mapi
    import MASH.undo as undo
    import mash_repro_utils
    import mash_repro_aetemplate
    import MASH.editor


def get_mash_nodes():
    return cmds.ls(type='MASH_Waiter')


def create_mash_network(name='Solstice_Scatter', type='repro'):
    name = naming.find_available_name(name=name)
    if type == 'instancer':
        mel.eval('optionVar -iv mOGT 1;')
    elif type == 'repro':
        mel.eval('optionVar -iv mOGT 2;')

    waiter_node = mel.eval('MASHnewNetwork("{0}")'.format(name))[0]
    mash_network = get_mash_network(waiter_node)
    return mash_network


def get_mash_network(node_name):
    if cmds.objExists(node_name):
        return mapi.Network(node_name)
    return None

@undo.chunk('Removing MASH Network')
def remove_mash_network(network):
    print(type(network))
    if type(network) == unicode:
        network = get_mash_network(network)
    if network:
        if cmds.objExists(network.instancer):
            cmds.delete(network.instancer)
        if cmds.objExists(network.distribute):
            cmds.delete(network.distribute)
        if cmds.objExists(network.waiter):
            cmds.delete(network.waiter)


def get_mash_outliner_tree():
    if sp.dcc.get_version() <= 2017:
        return MASHoutliner.OutlinerTreeView()
    elif sp.dcc.get_version() >= 2018:
        return MASH.editor.OutlinerTreeView()


@undo.chunk
def add_mesh_to_repro(repro_node, meshes=None):
    cmds.undoInfo(ock=True)
    if meshes == None:
        meshes = cmds.ls(sl=True)

    for obj in meshes:
        if cmds.objectType(obj) == 'mesh':
            obj = cmds.listRelatives(obj, parent=True)[0]
        if cmds.listRelatives(obj, ad=True, type='mesh'):
            mash_repro_utils.connect.mesh_group(repro_node, obj)
    cmds.undoInfo(cck=True)


def get_repro_object_widget(repro_node):
    if not repro_node:
        return

    maya_window = mayautils.get_maya_window()
    repro_widgets = maya_window.findChildren(mash_repro_aetemplate.ObjectsWidget) or []
    if len(repro_widgets) > 0:
        return repro_widgets[0]
    return None


def set_repro_object_widget_enabled(repro_node, flag):
    repro_widget = get_repro_object_widget(repro_node)
    if not repro_widget:
        return
    repro_widget.parent().parent().setEnabled(flag)
