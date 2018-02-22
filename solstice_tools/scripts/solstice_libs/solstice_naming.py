#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_naming.py
# by Tomas Poveda @ Solstice
# Library related with nomenclature stuff
# ______________________________________________________________________
# ==================================================================="""

def getName(nodeName):
    return nodeName.split('|')[1].rsplit(':',1)[-1]

def getNamespace(nodeName):
    namespace = nodeName.rpartition(':')[0]
    if namespace == ':':
        return ''
    else:
        return namespace