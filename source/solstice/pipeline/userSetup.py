#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization for Solstice Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

print('='*100)
print('| Solstice Pipeline | > Loading Solstice Tools')

try:
    import solstice as sp
    from maya import cmds
    cmds.evalDeferred('sp.init()')
    print('| Solstice Pipeline | Solstice Tools loaded successfully!')
    print('='*100)
except Exception as e:
    try:
        import solstice as sp
        sp.init()
        print('| Solstice Pipeline | Solstice Tools loaded successfully!')
        print('='*100)
    except Exception as e:
        print('ERROR: Impossible to load Solstice Tools, contact TD!')
        print(str(e))
