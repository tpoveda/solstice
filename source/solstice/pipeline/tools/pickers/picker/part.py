#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class for picker parts
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *

import maya.cmds as cmds
import maya.mel as mel

from solstice.pipeline.tools.pickers.picker import buttons


class PickerPart(QObject, object):
    fkSignal = Signal()
    ikSignal = Signal()

    def __init__(self, name, side):
        super(PickerPart, self).__init__()

        self._name = name
        self._side = side
        self._buttons = list()

    def get_name(self):
        return self._name

    def get_side(self):
        return self._side

    name = property(get_name)
    side = property(get_side)

    def get_controls(self, as_buttons=True):
        """
        Returns list with all controls in the part
        :param as_buttons: bool, whter the controls should be return as PickerButtons or a string (name)
        :return:
        """
        if as_buttons:
            return self._buttons

        return [btn._control for btn in self._buttons]

    def get_control_group(self):
        """
        Returns the control group of the part
        """

        return self.get_controls()[0].control_group

    def get_ik_buttons(self):
        """
        Returns all IK buttons in the part controls
        :return: list<IKButton>
        """

        return [btn for btn in self._buttons if isinstance(btn, buttons.IKButton)]

    def get_fk_buttons(self):
        """
        Returns all FK buttons in the part controls
        :return: list<FKButton>
        """

        return [btn for btn in self._buttons if isinstance(btn, buttons.FKButton)]

    def add_button(self, new_btn):
        """
        Adds a new button to the list of part buttons
        :param new_btn:
        """

        self._buttons.append(new_btn)

    def get_button_by_name(self, btn_name):
        """
        Returns part button by its name
        :param btn_name: str, name of the part button to get
        :return:
        """

        return [btn for btn in self._buttons if btn._control == btn_name]

    def has_fk_ik(self):
        """
        Returns whether or not the given part has fk ik functionality
        :return: bool
        """

        ctrl_grp = self.get_control_group()
        if cmds.objExists(ctrl_grp):
            return cmds.attributeQuery('FK_IK', node=ctrl_grp, exists=True)

        return False

    def get_fk_ik(self, as_text=False):
        if not self.has_fk_ik():
            return None

        fk_ik_value = cmds.getAttr(self.get_controls()[0].control_group + '.FK_IK')
        if as_text:
            if fk_ik_value == 0:
                return 'FK'
            else:
                return 'IK'
        else:
            return fk_ik_value

    def set_fk(self):
        if self.has_fk_ik():
            mel.eval('vlRigIt_snap_ikFk("{}","{}")'.format(self.get_control_group(), 0))
            [btn.setVisible(False) for btn in self.get_ik_buttons()]
            [btn.setVisible(True) for btn in self.get_fk_buttons()]
            self.fkSignal.emit()

    def set_ik(self):
        if self.has_fk_ik():
            mel.eval('vlRigIt_snap_ikFk("{}","{}")'.format(self.get_control_group(), 1))
            [btn.setVisible(False) for btn in self.get_fk_buttons()]
            [btn.setVisible(True) for btn in self.get_ik_buttons()]
            self.ikSignal.emit()
