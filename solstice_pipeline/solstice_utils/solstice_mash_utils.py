#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_mash_utils.py
# by Tomas Poveda
# Utilities functions when working with MASH nodes
# ______________________________________________________________________
# ==================================================================="""


import maya.cmds as cmds
import MASH.api as mapi
import MASHoutliner


from solstice_utils import solstice_naming_utils as naming
reload(naming)


def get_mash_nodes():
    return cmds.ls(type='MASH_Waiter')


def create_mash_network(name='Solstice_Scatter'):
    name = naming.find_available_name(name=name)
    mash_network = mapi.Network()
    mash_network.createNetwork(name=name)
    return mash_network


def get_mash_network(node_name):
    if cmds.objExists(node_name):
        return mapi.Network(node_name)
    return None


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
    return MASHoutliner.OutlinerTreeView()