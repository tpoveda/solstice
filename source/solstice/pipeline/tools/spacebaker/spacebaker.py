#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to bake animation between space changes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import traceback
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import maya.cmds as cmds

import solstice.pipeline as sp
from solstice.pipeline.gui import window, splitters, buttons
from solstice.pipeline.utils import mayautils as utils, animutils as anim_utils


SPACE_CONSTRAINTS = {
    'parent': 'Parent Constraint',
    'point': 'Point Constraint',
    'orient': 'Orient Constraint'
}

CONSTRAINTS_LIST = {
    'point': cmds.pointConstraint,
    'orient': cmds.orientConstraint,
    'parent': cmds.parentConstraint
}

RADIAL_POSITIONS = ['N', 'NE', 'NW', 'E', 'W']

SPACE_SWITCH_MENU_NAME = 'SS_spaceSwitchMenu'
SPACE_DRIVER_ATTR = 'SS_spaceDriver'


class SpaceAnimBaker(window.Window, object):
    name = 'SpaceAnimBaker'
    title = 'Solstice Tools - Spacer Baker'
    version = '1.0'

    def __init__(self):
        self._target = None
        self._space_widgets = list()

        super(SpaceAnimBaker, self).__init__()

    def custom_ui(self):
        super(SpaceAnimBaker, self).custom_ui()

        self.set_logo('solstice_space_switcher_logo')

        self.resize(425, 800)
        self.setFixedWidth(425)

        space_setup_options = QGridLayout()
        space_setup_options.setContentsMargins(2, 2, 2, 2)
        space_setup_options.setSpacing(2)
        self.main_layout.addLayout(space_setup_options)
        target_control_lbl = QLabel('Target Control: ')
        self.target_control_line = QLineEdit()
        self.target_control_line.setReadOnly(True)
        self.target_control_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        target_control_btn = buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.target_control_delete_btn = buttons.IconButton(icon_name='delete', icon_hover='delete_hover')
        self.target_control_delete_btn.setFixedSize(QSize(15, 15))
        self.target_control_delete_btn.setParent(self.target_control_line)
        self.target_control_delete_btn.move(268, 2)
        self.target_control_delete_btn.setVisible(False)
        parent_space_group_lbl = QLabel('Parent Group: ')
        self.parent_space_group_line = QLineEdit()
        self.parent_space_group_line.setReadOnly(True)
        self.parent_space_group_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parent_space_group_btn = buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.parent_space_group_delete_btn = buttons.IconButton(icon_name='delete', icon_hover='delete_hover')
        self.parent_space_group_delete_btn.setFixedSize(QSize(15, 15))
        self.parent_space_group_delete_btn.setParent(self.parent_space_group_line)
        self.parent_space_group_delete_btn.move(268, 2)
        self.parent_space_group_delete_btn.setVisible(False)
        space_attr_lbl = QLabel('Space Attribute: ')
        self.space_attr_line = QLineEdit()
        self.space_attr_line.setText('space')
        space_constraint_lbl = QLabel('Space Constraint: ')
        button_group = QButtonGroup(self)
        self.parent_cns_btn = buttons.BaseButton('Parent')
        self.point_cns_btn = buttons.BaseButton('Point')
        self.orient_cns_btn = buttons.BaseButton('Orient')
        self.parent_cns_btn.setCheckable(True)
        self.parent_cns_btn.setChecked(True)
        self.point_cns_btn.setCheckable(True)
        self.orient_cns_btn.setCheckable(True)
        button_group.addButton(self.parent_cns_btn)
        button_group.addButton(self.point_cns_btn)
        button_group.addButton(self.orient_cns_btn)
        cns_layout = QHBoxLayout()
        cns_layout.addWidget(self.parent_cns_btn)
        cns_layout.addWidget(self.point_cns_btn)
        cns_layout.addWidget(self.orient_cns_btn)
        driving_cns_lbl = QLabel('Driving Constraint: ')
        self.driving_line = QLineEdit()
        self.driving_line.setReadOnly(True)
        self.driving_select_btn = buttons.IconButton(icon_name='cursor', icon_hover='cursor_hover')

        space_setup_options.addWidget(target_control_lbl, 0, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.target_control_line, 0, 1, 1, 1)
        space_setup_options.addWidget(target_control_btn, 0, 2, 1, 1)
        space_setup_options.addWidget(parent_space_group_lbl, 1, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.parent_space_group_line, 1, 1, 1, 1)
        space_setup_options.addWidget(self.parent_space_group_btn, 1, 2, 1, 1)
        space_setup_options.addWidget(space_attr_lbl, 2, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.space_attr_line, 2, 1, 1, 1)
        space_setup_options.addWidget(space_constraint_lbl, 3, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addLayout(cns_layout, 3, 1, 1, 1)
        space_setup_options.addLayout(splitters.SplitterLayout(), 4, 0, 1, 4)
        space_setup_options.addWidget(driving_cns_lbl, 5, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.driving_line, 5, 1, 1, 1)
        space_setup_options.addWidget(self.driving_select_btn, 5, 2, 1, 1)

        scroll_area = QScrollArea()
        scroll_area.setObjectName('spaceScroll')
        scroll_area.setWidgetResizable(True)
        scroll_area.setFocusPolicy(Qt.NoFocus)
        scroll_area.setStyleSheet('#spaceScroll {background: transparent}')

        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(scroll_area)

        main_spaces_widget = QWidget()
        main_spaces_widget.setObjectName('spaceWidget')
        main_spaces_widget.setStyleSheet('#spaceWidget {background: transparent}')
        scroll_area.setWidget(main_spaces_widget)
        main_spaces_layout = QVBoxLayout()
        main_spaces_layout.setContentsMargins(0, 0, 0, 0)
        main_spaces_layout.setSpacing(0)
        main_spaces_widget.setLayout(main_spaces_layout)
        main_spaces_layout.addWidget(splitters.Splitter('SPACES LIST'))

        buttons_layout = QHBoxLayout()
        main_spaces_layout.addLayout(buttons_layout)
        self.create_space_btn = buttons.IconButton(icon_name='plus', icon_hover='plus_hover')
        self.refresh_spaces_btn = buttons.IconButton(icon_name='refresh', icon_hover='refresh_hover')
        self.bake_all_spaces_btn = buttons.IconButton(icon_name='stamp', icon_hover='stamp_hover')
        self.delete_all_spaces_btn = buttons.IconButton(icon_name='delete', icon_hover='delete_hover')

        self.create_space_btn.setEnabled(False)
        self.refresh_spaces_btn.setEnabled(False)
        buttons_layout.addWidget(self.create_space_btn)
        buttons_layout.addWidget(self.refresh_spaces_btn)
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        buttons_layout.addWidget(self.bake_all_spaces_btn)
        buttons_layout.addWidget(self.delete_all_spaces_btn)

        self.spaces_widget = DropFrame()
        self.spaces_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.spaces_widget.setFrameShape(QFrame.StyledPanel)
        self.spaces_widget.setFrameShadow(QFrame.Raised)
        main_spaces_layout.addWidget(self.spaces_widget)

        target_control_btn.clicked.connect(self._on_set_target_control)
        self.parent_space_group_btn.clicked.connect(self._on_set_parent_group)
        self.target_control_delete_btn.clicked.connect(self._on_reset_control)
        self.parent_space_group_delete_btn.clicked.connect(partial(self._on_clear_line, self.parent_space_group_line))
        self.create_space_btn.clicked.connect(self._on_create_space_switch)
        self.delete_all_spaces_btn.clicked.connect(self._on_clear_spaces)

        self._update_ui()

    @property
    def switch_control(self):
        return str(self.target_control_line.text())

    @property
    def parent_group(self):
        return str(self.parent_space_group_line.text())

    @property
    def switch_attribute(self):
        return str(self.space_attr_line.text())

    @property
    def spaces_widgets(self):
        return self._space_widgets

    @property
    def constraint_type(self):
        if self.point_cns_btn.isChecked():
            return 'point'
        elif self.orient_cns_btn.isChecked():
            return 'orient'
        elif self.parent_cns_btn.isChecked():
            return 'parent'

        return None

    def add_space(self, from_selection=False):

        if not self.switch_control or not cmds.objExists(self.switch_control):
            return
        if from_selection:
            sel = cmds.ls(sl=True)
            if sel:
                for drv in sel:
                    self._create_space(self.switch_control, drv)
                return

        self._create_space(self.switch_control, None)

    @utils.maya_undo
    def _create_space(self, switch_control, driver_node):
        new_space = SpaceWidget(switch_control, driver_node)
        self.spaces_widget.drop_layout.addWidget(new_space)
        self._space_widgets.append(new_space)
        new_space.closeSpace.connect(self.remove_space)
        new_space.setFixedHeight(0)
        new_space._animate_expand(True)

        if not self._space_widgets:
            sp.logger.warning('No spaces created yet! Please add a space first!')
            return

        if not self.parent_group or not cmds.objExists(self.parent_group):
            if cmds.referenceQuery(self.switch_control, isNodeReferenced=True):
                self.parent_space_group_line.setStyleSheet('border: 2px solid red;')
                QMessageBox.warning(
                    self,
                    'Error',
                    'When working with reference files you must manually set the Parent Group, that needs '
                    'to have the same pivot as the target control'
                )
                return

            self._create_parent_group()

        if not self.parent_group:
            sp.logger.warning('Parent Group not selected!')
            return
        if not self.switch_control:
            sp.logger.warning('Switch Control not selected!')
            return
        if not self.switch_attribute:
            sp.logger.warning('Switch Attribute Name not specified!')
            return

        if self.parent_group == self.switch_control:
            sp.logger.warning('Parent Group and Switch Control cannot be the same object!')
            return

        for required in [self.parent_group, self.switch_control]:
            if not cmds.objExists(required):
                sp.logger.warning('{} does not exists in the scene!'.format(required))
                return

        spaces_group_name = 'SS_spaces_grp'
        if not cmds.objExists(spaces_group_name):
            spaces_group = cmds.group(n=spaces_group_name, w=True, empty=True)
        else:
            spaces_group = spaces_group_name

        if not utils.attribute_exists(spaces_group, 'SS_spacesGroup'):
            cmds.addAttr(spaces_group, longName='SS_spacesGroup', at='message')
        if not utils.attribute_exists(self.switch_control, 'SS_spacesGroup'):
            cmds.addAttr(self.switch_control, longName='SS_spacesGroup', at='message')

        try:
            cmds.connectAttr('{}.SS_spacesGroup'.format(spaces_group), '{}.SS_spacesGroup'.format(self.switch_control), force=True)
        except Exception as e:
            pass

        driver_node = self.get_space_driver_node(new_space)
        if not driver_node:
            return

        if self.check_space_exists(driver_node):
            sp.logger.warning('Already found space driver node: {}'.format(driver_node))
            return

        display_name = self.get_space_name(new_space)
        if not cmds.objExists(driver_node):
            sp.logger.warning('{} space driver node does not exist in the scene!'.format(driver_node))
            return
        if not display_name:
            display_name = utils.get_short_name(driver_node)

        spaces = [{driver_node: display_name}]

        try:
            self._space_switch(self.parent_group, self.switch_control, self.constraint_type, spaces, spaces_group, self.switch_attribute)
        except Exception as e:
            QMessageBox.warning(self, 'Error', traceback.format_exc())
            return



        # for space_widget in self.spaces_widgets:
        #     driver_node = self.get_space_driver_node(space_widget)
        #     if not driver_node:
        #         continue
        #     if self.check_space_exists(driver_node):
        #         sp.logger.warning('Already found space driver node: {}'.format(driver_node))
        #         continue
        #     display_name = self.get_space_name(space_widget)
        #     if not cmds.objExists(driver_node):
        #         sp.logger.warning('{} space driver node does not exist in the scene!'.format(driver_node))
        #         return
        #     if not display_name:
        #         display_name = utils.get_short_name(driver_node)
        #
        #     spaces_dict = {driver_node: display_name}
        #     spaces.append(spaces_dict)
        #
        # if not spaces:
        #     return
        #
        # try:
        #     self._space_switch(self.parent_group, self.switch_control, self.constraint_type, spaces, spaces_group, self.switch_attribute)
        # except Exception as e:
        #     QMessageBox.warning(self, 'Error', traceback.format_exc())
        #     return

        sp.logger.debug('Space Switch Setup sucessfully created!')

        return new_space

    def _remove_space_ui(self, space_widget):
        space_widget.deleteSpace.connect(self._on_delete_space_switch)
        self._space_widgets.remove(space_widget)
        space_widget._animate_expand(False)

    def remove_space(self, space_widget):
        self._remove_space_ui(space_widget)
        driver_node = space_widget.driver_node
        if not driver_node or not cmds.objExists(driver_node):
            return

        stored_name = None
        if utils.attribute_exists(driver_node, 'SS_driverName'):
            stored_name = cmds.getAttr('{}.SS_driverName'.format(driver_node))

        if utils.attribute_exists(driver_node, 'SS_driverName'):
            cmds.deleteAttr('{}.SS_driverName'.format(driver_node))
        if utils.attribute_exists(driver_node, 'SS_driverNode'):
            cmds.deleteAttr('{}.SS_driverNode'.format(driver_node))
        if utils.attribute_exists(driver_node, 'SS_driverGroup'):
            space_grp = cmds.listConnections('{}.SS_driverGroup'.format(driver_node))
            if space_grp:
                if space_grp[0] and cmds.objExists(space_grp[0]):
                    cmds.delete(space_grp[0])
            cmds.deleteAttr('{}.SS_driverGroup'.format(driver_node))

        if not utils.attribute_exists(space_widget.switch_control, SPACE_DRIVER_ATTR):
            return
        space_cnt = cmds.listConnections(space_widget.switch_control + '.{}'.format(SPACE_DRIVER_ATTR), p=True)
        if not space_cnt:
            return
        enum_names = cmds.addAttr(space_cnt[0], query=True, enumName=True)
        enum_list = enum_names.split(':')
        driver_node_short = utils.get_short_name(driver_node)
        new_enum = False
        if driver_node_short in enum_list:
            enum_list.remove(driver_node_short)
            new_enum = True
        if stored_name and stored_name in enum_list:
            enum_list.remove(stored_name)
            new_enum = True
        if new_enum:
            space_cnt = cmds.listConnections(space_widget.switch_control + '.{}'.format(SPACE_DRIVER_ATTR))[0]
            if enum_list:
                enum_list = ':'.join(enum_list)
                cmds.addAttr('{}.space'.format(space_cnt), edit=True, enumName=enum_list)
            else:
                cmds.deleteAttr('{}.space'.format(space_cnt))

    @utils.maya_undo
    def _clear_spaces(self):
        if not self.switch_control or not cmds.objExists(self.switch_control):
            for w in reversed(self._space_widgets):
                self.remove_space(w)
            self._space_widgets = list()
            self._update_ui()
            return
        try:
            switcher_node_dag = utils.get_mdag_path(self.switch_control)

            cns_groups = self.get_constraint_groups(switcher_node_dag.fullPathName())
            if not cns_groups:
                return

            for grp in cns_groups:
                driver_cond = cmds.listConnections(grp+'.SS_condNode')
                driver_offset_grp = cmds.listConnections(grp+'.SS_offsetGrp')
                cmds.delete(driver_cond, driver_offset_grp)

            space_cond = cmds.listConnections(self.switch_control+'.{}'.format(SPACE_DRIVER_ATTR), p=True)[0]
            cmds.deleteAttr(space_cond)

            if utils.attribute_exists(self.switch_control, 'SS_drivenNode'):
                driven_node = cmds.listConnections(self.switch_control+'.SS_drivenNode')[0]
                if utils.attribute_exists(driven_node, 'SS_autoSpace'):
                    driven_node_parent = cmds.listRelatives(driven_node, parent=True, fullPath=True)[0]
                    driven_node_child = cmds.listRelatives(driven_node, children=True, fullPath=True)[0]
                    cmds.parent(driven_node_child, driven_node_parent)
                    cmds.delete(driven_node)
                cmds.deleteAttr(self.switch_control+'.SS_drivenNode')

            for w in reversed(self._space_widgets):
                self.remove_space(w)
            self._space_widgets = list()

            self._update_ui()
        except Exception as e:
            sp.logger.error(traceback.format_exc())
            return

        sp.logger.debug('Space Switch Setup deleted successfully!')

    def _update_ui(self):
        if self.target_control_line.text():
            self.create_space_btn.setEnabled(True)
            self.refresh_spaces_btn.setEnabled(True)
            self.bake_all_spaces_btn.setEnabled(True)
            self.delete_all_spaces_btn.setEnabled(True)
            self.target_control_delete_btn.setVisible(True)
            self.parent_space_group_delete_btn.setVisible(True)
            self.create_space_btn.setEnabled(True)
            self.space_attr_line.setEnabled(True)
            self.parent_cns_btn.setEnabled(True)
            self.point_cns_btn.setEnabled(True)
            self.orient_cns_btn.setEnabled(True)
            self.spaces_widget.setEnabled(True)
        else:
            # self._clear_spaces()
            self.create_space_btn.setEnabled(False)
            self.refresh_spaces_btn.setEnabled(False)
            self.bake_all_spaces_btn.setEnabled(False)
            self.delete_all_spaces_btn.setEnabled(False)
            self.target_control_delete_btn.setVisible(False)
            self.parent_space_group_delete_btn.setVisible(False)
            self.create_space_btn.setEnabled(False)
            self.space_attr_line.setEnabled(False)
            self.parent_cns_btn.setEnabled(False)
            self.point_cns_btn.setEnabled(False)
            self.orient_cns_btn.setEnabled(False)
            self.spaces_widget.setEnabled(False)

        if not self._space_widgets:
            self.bake_all_spaces_btn.setEnabled(False)
            self.delete_all_spaces_btn.setEnabled(False)
        else:
            self.bake_all_spaces_btn.setEnabled(True)
            self.delete_all_spaces_btn.setEnabled(True)

        if self.switch_control:
            self.parent_space_group_line.setEnabled(True)
            self.parent_space_group_btn.setEnabled(True)
        else:
            self.parent_space_group_line.setEnabled(False)
            self.parent_space_group_btn.setEnabled(False)

        if self.parent_space_group_line.text():
            self.parent_space_group_delete_btn.setVisible(True)
        else:
            self.parent_space_group_delete_btn.setVisible(False)

    def _on_create_space_switch(self):
        sel = cmds.ls(sl=True)
        if self.switch_control in sel:
            sel.remove(self.switch_control)
        if len(sel) == 0:
            sp.logger.warning('Select Driver control first!')
            return
        if sel:
            self.add_space(from_selection=True)
        else:
            self.add_space(from_selection=False)
        self._update_ui()

    def _on_clear_spaces(self):
        if not self._space_widgets:
            return

        msg_box = QMessageBox(self)
        msg_box.setText('This action may be undoable!')
        msg_box.setInformativeText('Are you sure you want to delete all space setups?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        ret = msg_box.exec_()
        if ret == QMessageBox.Yes:
            self._clear_spaces()
        elif ret == QMessageBox.No:
            return False

    def _on_delete_space_switch(self, space_widget):
        self.spaces_widget.drop_layout.removeWidget(space_widget)
        space_widget._animation = None
        space_widget.deleteLater()

    def _on_clear_line(self, line_widget):
        line_widget.setText('')
        self._update_ui()

    def _on_reset_control(self):
        self._on_clear_line(self.target_control_line)
        self.parent_space_group_line.setText('')
        for w in reversed(self._space_widgets):
            self._remove_space_ui(w)
        self._update_ui()

    def _get_selected(self, line_widget):
        sel = cmds.ls(sl=True, l=True)
        if not sel:
            sp.logger.warning('Please select a object first!')
            return
        if len(sel) > 1:
            sp.logger.warning('You have selected more than one object. First item in the selection will be used ...')
        sel = sel[0]
        if sel.startswith('|'):
            sel = sel[1:]

        uuid = cmds.ls(sel, uuid=True)
        self._target = uuid
        short = cmds.ls(sel)[0]

        line_widget.clear()
        line_widget.setText(short)

        self._update_ui()

        return sel

    def _create_parent_group(self):
        if not self.switch_control:
            return

        driven_node = None
        if utils.attribute_exists(self.switch_control, 'SS_drivenNode'):
            driven_node = cmds.listConnections(self.switch_control+'.SS_drivenNode')
        cns = None
        if driven_node:
            cns = cmds.listConnections(driven_node[0]+'.SS_spaceConstraint')

        offset_grp = '{}_space_grp'.format(utils.get_short_name(self.switch_control))

        if cns:
            if offset_grp and cmds.objExists(offset_grp):
                self.parent_space_group_line.setText(offset_grp)

        if not cmds.objExists(offset_grp):
            offset_grp = cmds.group(n=offset_grp, world=True, empty=True)
            cmds.addAttr(offset_grp, longName='SS_autoSpace', at='bool')
        else:
            all_space_grps = cmds.ls(offset_grp)
            if len(all_space_grps) > 1:
                for grp in all_space_grps:
                    parent = cmds.listRelatives(grp, p=True)
                    if not parent:
                        cmds.delete(grp)

        switch_control_parent = cmds.listRelatives(self.switch_control, parent=True)
        if switch_control_parent:
            if switch_control_parent[0] == offset_grp:
                self.parent_space_group_line.setText(offset_grp)
                return

        cmds.delete(cmds.pointConstraint(self.switch_control, offset_grp)[0])
        driven_node_rot = cmds.xform(self.switch_control, query=True, rotation=True, worldSpace=True)
        driven_node_scale = cmds.xform(self.switch_control, query=True, scale=True, worldSpace=True)
        cmds.xform(offset_grp, rotation=driven_node_rot, worldSpace=True)
        cmds.xform(offset_grp, scale=driven_node_scale, worldSpace=True)
        switch_control = utils.get_mdag_path(self.switch_control)
        control_parent = cmds.listRelatives(self.switch_control, parent=True)
        if control_parent:
            cmds.parent(offset_grp, control_parent[0])
        switch_ctrl_parent = cmds.listRelatives(self.switch_control, parent=True)
        if switch_ctrl_parent:
            if switch_ctrl_parent[0] != offset_grp:
                cmds.parent(self.switch_control, offset_grp)
        else:
            cmds.parent(self.switch_control, offset_grp)
        # cmds.select(switch_control.fullPathName())
        self.parent_space_group_line.setText(offset_grp)

        return offset_grp

    def _load_space_driver_node(self, line_widget):
        node = self._get_selected(line_widget)
        if not node:
            return
        if not utils.attribute_exists(node, '{}'.format(SPACE_DRIVER_ATTR)):
            sp.logger.debug('No space switch found on this node: {}'.format(node))
            QMessageBox.warning(self, 'Value Error', 'No space switch found on this node: {}'.format(node))
            line_widget.clear()
            return

        return node

    def _get_display_name(self, grp, switcher):
        if not utils.attribute_exists(grp, 'SS_switchNo'):
            sp.logger.debug('No Switch found, skipping the {} driver'.foramt(grp))
            return
        switch_no = cmds.getAttr('{}.SS_switchNo'.format(grp))
        space_cnt = cmds.listConnections(switcher+'.{}'.format(SPACE_DRIVER_ATTR), p=True)
        enum_names = cmds.addAttr(space_cnt[0], query=True, enumName=True)
        enum_list = enum_names.split(':')

        return enum_list[switch_no]

    def _update_spaces(self):
        switcher_node = self.target_control_line.text()
        if not switcher_node or not cmds.objExists(switcher_node):
            return
        if not utils.attribute_exists(switcher_node, '{}'.format(SPACE_DRIVER_ATTR)) or not utils.attribute_exists(switcher_node, 'SS_drivenNode'):
            return

        driven_node = cmds.listConnections(switcher_node+'.SS_drivenNode')
        if not driven_node:
            return
        cns = cmds.listConnections(driven_node[0] + '.SS_spaceConstraint')
        if not cns:
            return

        # self._clear_spaces()

        groups_list = self.get_constraint_groups(switcher_node)
        for i, grp in enumerate(groups_list):
            driver = self.get_driver_from_group(grp)
            if not driver:
                continue
            new_space = self._create_space(switcher_node, driver)
            # new_space.target_control_line.setText(driver)
            # try:
            #     namespace, name = driver.rsplit(":", 1)
            # except Exception:
            #     namespace, name = None, driver
            # new_space.title_line.setText(name)

        # switcher_node_path = utils.get_mdag_path(switcher_node)
        #
        # space_cn = cmds.listConnections(switcher_node+'.SS_spaceDriver', p=True)
        # enum_names = cmds.addAttr(space_cn[0], query=True, enumName=True)
        # enum_list = enum_names.split(':')

    def _on_set_target_control(self):
        self._get_selected(self.target_control_line)
        self._update_spaces()

    def _on_set_parent_group(self):
        self._get_selected(self.parent_space_group_line)
        if self.switch_control == self.parent_group:
            sp.logger.warning('Parent Group and Switch Control cannot be the same object!')
            self.parent_space_group_line.setText('')
        self.parent_space_group_line.setStyleSheet('')
        self._update_ui()

    def get_space_driver_node(self, space_widget):
        return space_widget.driver_node

    def get_space_name(self, space_widget):
        return space_widget.name

    def get_constraint_groups(self, switcher_node):
        if not utils.attribute_exists(switcher_node, 'SS_drivenNode'):
            return
        driven_node = cmds.listConnections(switcher_node+'.SS_drivenNode')
        if not driven_node:
            return
        space_cns = cmds.listConnections(driven_node[0] + '.SS_spaceConstraint')
        if not space_cns:
            return

        space_cns = space_cns[0]
        cns = CONSTRAINTS_LIST[cmds.nodeType(space_cns).replace('Constraint', '')]
        cns_target_list = cns(space_cns, targetList=True, query=True)

        return cns_target_list

    def get_drivers(self, switcher_node):
        constraint_target_list = self.get_constraint_groups(switcher_node)
        if not constraint_target_list:
            return
        driver_nodes = list()
        for target in constraint_target_list:
            driver_node = self.get_driver_from_group(target)
            if driver_node:
                driver_nodes.append(driver_node)

        return driver_nodes

    def check_space_exists(self, driver):
        drivers_list = self.get_drivers(self.switch_control)
        if not drivers_list:
            return
        if driver in drivers_list:
            sp.logger.debug('{} is already a driving space for {}'.format(driver, self.parent_group))
            return driver

    def get_driver_from_group(self, grp):
        if not utils.attribute_exists(grp, 'SS_driverNode'):
            return
        driver_node = cmds.listConnections(grp+'.SS_driverNode')
        if driver_node:
            return driver_node[0]

    def _space_switch(self, driven_node, controller, constraint_type, driver_spaces, spaces_grp, attr_name='spaces'):
        cns = CONSTRAINTS_LIST[constraint_type]

        for space_dict in driver_spaces:
            for key, value in space_dict.items():
                driver_grp = ''
                if utils.attribute_exists(key, 'SS_driverGroup'):
                    driver_grp = cmds.listConnections(key+'.SP_driverGroup')
                    if driver_grp:
                        driver_grp = utils.get_mdag_path(driver_grp[0])
                if not cmds.objExists(key+'_space_grp'):
                    driver_grp = utils.get_mdag_path(cmds.group(empty=True, name=utils.get_short_name(key) + '_space_grp'))
                else:
                    driver_grp = utils.get_mdag_path(key+'_space_grp')
                utils.add_message_attribute(key, driver_grp.fullPathName(), 'SS_driverGroup')
                try:
                    cmds.pointConstraint(key, driver_grp.fullPathName(), mo=False)
                    cmds.orientConstraint(key, driver_grp.fullPathName(), mo=False)
                except RuntimeError as e:
                    sp.logger.error(traceback.format_exc())
                try:
                    cmds.parent(driver_grp.fullPathName(), spaces_grp)
                except Exception as e:
                    sp.logger.error(traceback.format_exc())

                if not utils.attribute_exists(controller, attr_name):
                    cmds.addAttr(controller, longName=attr_name, keyable=True, attributeType='enum', enumName=value)

                enum_name = cmds.addAttr('{}.{}'.format(controller, attr_name), query=True, enumName=True)
                enum_list = enum_name.split(':')
                for enum in enum_list:
                    if enum == value:
                        enum_list.remove(value)
                new_enum = ':'.join(enum_list)

                cmds.addAttr('{}.{}'.format(controller, attr_name), edit=True, enumName='{}:{}'.format(new_enum, value))
                constraint_grp = '{}_{}_space_grp'.format(utils.get_short_name(driven_node), utils.get_short_name(key))
                constraint_grp_offset = '{}_offset_grp'.format(constraint_grp)
                if not cmds.objExists(constraint_grp):
                    constraint_grp = cmds.group(empty=True, name=constraint_grp)
                    constraint_grp_offset = cmds.group(constraint_grp, name='{}_offset_grp'.format(constraint_grp))
                utils.add_message_attribute(key, constraint_grp, 'SS_driverNode')
                utils.add_message_attribute(constraint_grp, constraint_grp_offset, 'SS_offsetGrp')
                cmds.delete(cmds.pointConstraint(driven_node, constraint_grp_offset)[0])
                driven_node_scale = cmds.xform(driven_node, query=True, scale=True, worldSpace=True)
                driven_node_rot = cmds.xform(driven_node, query=True, rotation=True, worldSpace=True)
                cmds.setAttr(constraint_grp_offset+'.scale', driven_node_scale[0], driven_node_scale[1], driven_node_scale[2], type='double3')
                cmds.xform(constraint_grp_offset, rotation=driven_node_rot, worldSpace=True)
                cmds.delete(cmds.orientConstraint(driven_node, constraint_grp)[0])
                try:
                    cmds.parent(constraint_grp_offset, driver_grp.fullPathName())
                except RuntimeError as e:
                    sp.logger.error(traceback.format_exc())

                cns_node = cns(constraint_grp, driven_node, mo=True)[0]
                cns_target_list = cns(cns_node, targetList=True, query=True)
                cns_weights_list = cns(cns_node, weightAliasList=True, query=True)
                cns_driver_idx = cns_target_list.index(constraint_grp)
                utils.add_message_attribute(driven_node, cns_node, 'SS_spaceConstraint')
                cond = '{}_{}_space_cond'.format(utils.get_short_name(driven_node), key)
                if not utils.attribute_exists(constraint_grp, 'PP_switchNo'):
                    cmds.addAttr(constraint_grp, longName='SS_switchNo', at='long')
                cmds.setAttr('{}.SS_switchNo'.format(constraint_grp), cns_driver_idx)
                if not cmds.objExists(cond):
                    cond = cmds.shadingNode('condition', name=cond, asUtility=True)
                try:
                    cmds.connectAttr('{}.SS_switchNo'.format(constraint_grp), cond+'.secondTerm')
                except RuntimeError as e:
                    sp.logger.error(traceback.format_exc())

                cmds.setAttr(cond+'.operation', 0)
                cmds.setAttr(cond+'.colorIfTrueR', 1)
                cmds.setAttr(cond+'.colorIfFalseR', 0)
                try:
                    cmds.connectAttr(cond+'.outColorR', '{}.{}'.format(cns_node, cns_weights_list[cns_driver_idx]), force=True)
                except Exception as e:
                    sp.logger.error(traceback.format_exc())

                try:
                    cmds.connectAttr('{}.{}'.format(controller, attr_name), cond+'.firstTerm', force=True)
                except Exception as e:
                    sp.logger.error(traceback.format_exc())

                utils.add_message_attribute(controller, driven_node, 'SS_drivenNode')
                utils.add_message_attribute(constraint_grp, cond, 'SS_condNode')

        if not utils.attribute_exists(controller, SPACE_DRIVER_ATTR):
            cmds.addAttr(controller, longName=SPACE_DRIVER_ATTR, at='long', dv=0)
        try:
            cmds.connectAttr('{}.{}'.format(controller, attr_name), '{}.{}'.format(controller, SPACE_DRIVER_ATTR), force=True)
        except Exception as e:
            sp.logger.error(traceback.format_exc())


class DropFrame(QFrame):
    dropped = Signal(QWidget, int)

    def __init__(self, parent = None):
        super(DropFrame, self).__init__(parent)
        self.setAcceptDrops(True)
        self.drop_layout = QVBoxLayout()
        self.drop_layout.setContentsMargins(0, 0, 0, 0)
        self.drop_layout.setSpacing(0)
        self.drop_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.drop_layout)
        self.setObjectName('spacesWidget')

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dropFrame'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-dropFrame'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
            source_space = event.source()
            source_space.move_space_frame()
            for i in range(source_space.move_offset()):
                self.move_in_layout(source_space, source_space.move_direction())

            source_space.move_update()
            self.update()
            source_space.saveGeometry()
        else:
            event.ignore()

    def move_in_layout(self, widget, direction):
        index = self.drop_layout.indexOf(widget)
        if direction == 'UP' and index == 0:
            return 0
        if direction == 'DOWN' and index == self.drop_layout.count() - 1:
            return 0
        if direction == 'UP':
            new_index = index - 1
        else:
            new_index = index + 1
        self.drop_layout.removeWidget(widget)
        self.drop_layout.insertWidget(new_index, widget)
        self.dropped.emit(widget, new_index)
        return True


class SpaceWidget(QFrame, object):
    closeSpace = Signal(object)
    deleteSpace = Signal(object)

    def __init__(self, switch_control, driver_node, parent=None):
        super(SpaceWidget, self).__init__(parent)

        self._switch_control = switch_control
        self._animation = None
        self._slider_down = False
        self._items = dict()
        self._drag_start_position = None
        self._old_x = self._old_y = 0
        self._mouse_click_x = self._mouse_click_y = 0

        self.setObjectName('spaceWidget')
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFixedWidth(417)
        self.setFixedHeight(90)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        main_widget = QWidget()
        main_widget.setLayout(QVBoxLayout())
        main_widget.layout().setContentsMargins(0, 0, 0, 0)
        main_widget.layout().setSpacing(0)
        main_widget.setFixedHeight(80)
        main_widget.setFixedWidth(407)

        scene = QGraphicsScene()
        view = QGraphicsView()
        view.setScene(scene)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setFocusPolicy(Qt.NoFocus)
        view.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        view.setStyleSheet('QGraphicsView {border-style: none;}')
        self.main_layout.addWidget(view)
        self.main_widget_proxy = scene.addWidget(main_widget)
        main_widget.setParent(view)

        space_layout = QHBoxLayout()
        main_widget.layout().addLayout(space_layout)

        close_layout = QVBoxLayout()
        self.close_btn = buttons.CloseButton('X')
        self.bake_btn = buttons.IconButton(icon_name='stamp', icon_hover='stamp_hover')
        self.bake_btn.setCheckable(True)
        close_layout.addWidget(self.close_btn)
        close_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Expanding))
        close_layout.addWidget(self.bake_btn)

        self.bake_widget = QWidget()
        self.bake_widget.setVisible(False)
        bake_layout = QVBoxLayout()
        bake_layout.setContentsMargins(0, 0, 0, 0)
        bake_layout.setSpacing(0)
        self.bake_widget.setLayout(bake_layout)

        bake_options_layout = QHBoxLayout()
        bake_options_layout.setContentsMargins(0, 0, 0, 0)
        bake_options_layout.setSpacing(0)
        bake_layout.addLayout(bake_options_layout)
        frame_options_layout = QVBoxLayout()
        frame_options_layout.setContentsMargins(0, 0, 0, 0)
        frame_options_layout.setSpacing(0)
        bake_options_layout.addLayout(frame_options_layout)
        self.timeline_radio = QRadioButton('Timeline Range')
        self.frame_range_radio = QRadioButton('Playback Range')
        self.custom_range_radio = QRadioButton('Custom Range')
        frame_options_layout.addWidget(self.timeline_radio)
        frame_options_layout.addWidget(self.frame_range_radio)
        frame_options_layout.addWidget(self.custom_range_radio)

        frames_layout = QVBoxLayout()
        frames_layout.setContentsMargins(0, 0, 0, 0)
        frames_layout.setSpacing(0)
        bake_options_layout.addLayout(frames_layout)
        start_layout = QHBoxLayout()
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.setSpacing(0)
        end_layout = QHBoxLayout()
        end_layout.setContentsMargins(0, 0, 0, 0)
        end_layout.setSpacing(0)
        start_frame_lbl = QLabel('Start Frame')
        end_frame_lbl = QLabel('End Frame')
        self.start_spin = QSpinBox()
        self.end_spin = QSpinBox()
        start_layout.addWidget(start_frame_lbl)
        start_layout.addWidget(self.start_spin)
        end_layout.addWidget(end_frame_lbl)
        end_layout.addWidget(self.end_spin)
        frames_layout.addLayout(start_layout)
        frames_layout.addLayout(end_layout)

        self.do_bake_btn = buttons.BaseButton('B A K E')
        bake_layout.addLayout(splitters.SplitterLayout())
        bake_layout.addWidget(self.do_bake_btn)

        title_layout = QGridLayout()
        title_lbl = QLabel('Space Name: ')
        self.title_line = QLineEdit()
        self.title_line.setPlaceholderText('Input name of the space')
        first_update = True
        if driver_node and cmds.objExists(driver_node):
            if utils.attribute_exists(driver_node, 'SS_driverName'):
                first_update = False
                self.title_line.setText(cmds.getAttr('{}.SS_driverName'.format(driver_node)))
            else:
                try:
                    namespace, name = driver_node.rsplit(":", 1)
                except Exception:
                    namespace, name = None, self._switch_control
                self.title_line.setText(name)

        target_control_lbl = QLabel('Target Control: ')
        self.target_control_line = QLineEdit()
        self.target_control_line.setPlaceholderText('Input name of the control')
        self.target_control_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if driver_node and cmds.objExists(driver_node):
            self.target_control_line.setText(driver_node)
        if first_update:
            self._on_update_driver_name(driver_node)

        target_control_btn = buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.target_control_select_btn = buttons.IconButton(icon_name='cursor', icon_hover='cursor_hover')
        title_layout.addWidget(title_lbl, 0, 0, 1, 1, Qt.AlignRight)
        title_layout.addWidget(self.title_line, 0, 1, 1, 1)
        title_layout.addWidget(target_control_lbl, 1, 0, 1, 1, Qt.AlignRight)
        title_layout.addWidget(self.target_control_line, 1, 1, 1, 1)
        title_layout.addWidget(target_control_btn, 1, 2, 1, 1)
        title_layout.addWidget(self.target_control_select_btn, 1, 3, 1, 1)

        space_layout.addLayout(title_layout)
        space_layout.addLayout(close_layout)
        self.space_separator = splitters.get_horizontal_separator_widget()
        self.space_separator.setVisible(False)
        space_layout.addWidget(self.space_separator)
        space_layout.addWidget(self.bake_widget)

        self.title_line.textChanged.connect(self._on_update_driver_name)
        target_control_btn.clicked.connect(partial(self._get_selected, self.target_control_line))
        self.bake_btn.toggled.connect(self._on_open_bake)
        self.close_btn.clicked.connect(self.close_widget)
        self.do_bake_btn.clicked.connect(self._on_do_bake)

    @property
    def name(self):
        return str(self.title_line.text())

    @property
    def driver_node(self):
        return str(self.target_control_line.text())

    @property
    def switch_control(self):
        return self._switch_control

    def mousePressEvent(self, event):
        self._drag_start_position = event.pos()
        self._old_x = self.geometry().x()
        self._old_y = self.geometry().y()
        mouse_pos = self.mapFromGlobal(QCursor.pos())
        self._mouse_click_x = mouse_pos.x()
        self._mouse_click_y = mouse_pos.y()

    def mouseMoveEvent(self, event):
        mime_data = QMimeData()
        item_data = QByteArray()
        mime_data.setData('application/x-dropFrame', item_data)
        pixmap = QPixmap.grabWidget(self)
        painter = QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(self._drag_start_position)
        drag.exec_(Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        self.move_update()

    def move_update(self):
        self.update()
        parent_widget = self.parentWidget().layout()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        parent_widget.update()
        self.saveGeometry()

    def move_space_frame(self):
        mouse_position = self.mapFromGlobal(QCursor.pos())
        mouse_pos_y = mouse_position.y()
        y_value = mouse_pos_y - self._mouse_click_y + self._old_y
        bottom_border = self.parentWidget().geometry().height() - self.geometry().height()
        if y_value < 0:
            y_value = 0
        elif y_value > bottom_border:
            y_value = bottom_border
        self.move(self._old_x, y_value)

    def move_direction(self):
        y_pos = self.geometry().y()
        self.direction = ''
        if self._old_y > y_pos:
            self.direction = 'UP'
        elif self._old_y < y_pos:
            self.direction = 'DOWN'

        return self.direction

    def move_offset(self):
        y_pos = self.geometry().y()
        offset = 0
        if self._old_y > y_pos:
            offset = self._old_y - y_pos
        elif self._old_y < y_pos:
            offset = y_pos - self._old_y
        count = offset / self.height()

        return count

    def close_widget(self):
        self.closeSpace.emit(self)

    def delete_widget(self):
        self.deleteSpace.emit(self)

    def _animate_expand(self, value):
        opacity_anim = QPropertyAnimation(self.main_widget_proxy, "opacity")
        opacity_anim.setStartValue(not (value));
        opacity_anim.setEndValue(value)
        opacity_anim.setDuration(200)
        opacity_anim_curve = QEasingCurve()
        if value is True:
            opacity_anim_curve.setType(QEasingCurve.InQuad)
        else:
            opacity_anim_curve.setType(QEasingCurve.OutQuad)
        opacity_anim.setEasingCurve(opacity_anim_curve)

        size_anim = QPropertyAnimation(self, "geometry")

        geometry = self.geometry()
        width = geometry.width()
        x, y, _, _ = geometry.getCoords()

        size_start = QRect(x, y, width, int(not (value)) * 90)
        size_end = QRect(x, y, width, value * 90)

        size_anim.setStartValue(size_start)
        size_anim.setEndValue(size_end)
        size_anim.setDuration(300)

        size_anim_curve = QEasingCurve()
        if value:
            size_anim_curve.setType(QEasingCurve.InQuad)
        else:
            size_anim_curve.setType(QEasingCurve.OutQuad)
        size_anim.setEasingCurve(size_anim_curve)

        self._animation = QSequentialAnimationGroup()
        if value:
            self.main_widget_proxy.setOpacity(0)
            self._animation.addAnimation(size_anim)
            self._animation.addAnimation(opacity_anim)
        else:
            self.main_widget_proxy.setOpacity(1)
            self._animation.addAnimation(opacity_anim)
            self._animation.addAnimation(size_anim)

        size_anim.valueChanged.connect(self._force_resize)
        self._animation.finished.connect(self._animation.clear)

        if not value:
            self._animation.finished.connect(self.delete_widget)

        self._animation.start(QAbstractAnimation.DeleteWhenStopped)

    def _force_resize(self, new_height):
        self.setFixedHeight(new_height.height())

    def _get_selected(self, line_widget):
        sel = cmds.ls(sl=True, l=True)
        if not sel:
            sp.logger.warning('Please select a object first!')
            return
        if len(sel) > 1:
            sp.logger.warning('You have selected more than one object. First item in the selection will be used ...')
        sel = sel[0]
        if sel.startswith('|'):
            sel = sel[1:]

        uuid = cmds.ls(sel, uuid=True)
        self._target = uuid
        short = cmds.ls(sel)[0]

        line_widget.clear()
        line_widget.setText(short)

        return sel

    def _on_update_driver_name(self, new_name):
        if not self.driver_node or not cmds.objExists(self.driver_node):
            return

        if not utils.attribute_exists(self.driver_node, 'SS_driverName'):
            cmds.addAttr(self.driver_node, ln='SS_driverName', dt='string')
        cmds.setAttr('{}.SS_driverName'.format(self.driver_node), new_name, type='string')

        switch_control = self.switch_control
        if not switch_control or not cmds.objExists(switch_control):
            return
        switch_node = utils.get_mdag_path(switch_control).fullPathName()

        if not utils.attribute_exists(switch_node, 'SS_spaceDriver'):
            return
        space_cnt = cmds.listConnections(switch_node+'.SS_spaceDriver', p=True)
        if not space_cnt:
            return
        space_cnt = space_cnt[0]

        space_index = self.parentWidget()
        if not space_index:
            return
        space_index = space_index.drop_layout.indexOf(self)
        enum_name = cmds.addAttr(space_cnt, query=True, enumName=True)
        enum_list = enum_name.split(':')
        enum_list[space_index] = self.name
        new_enum = ':'.join(enum_list)
        space_cnt = cmds.listConnections(switch_node+'.SS_spaceDriver', p=True)[0]
        cmds.addAttr(space_cnt, edit=True, enumName=new_enum)

    def _on_open_bake(self, toggle):
        self.bake_widget.setVisible(toggle)
        self.close_btn.repaint()

    @utils.maya_undo
    def _on_do_bake(self):
        switcher_node = self._switch_control
        if not switcher_node or not cmds.objExists(switcher_node):
            return
        if self.start_spin.value() == self.end_spin.value():
            sp.logger.warning('The start and end frame have the same values! Skipping space baking ...')
            return
        if not self.start_spin.isEnabled():
            return
        frame_range = [self.start_spin.value(), self.end_spin.value()]
        target_space = utils.get_short_name(self.driver_node)

        space_cnt = cmds.listConnections(switcher_node + '.{}'.format(SPACE_DRIVER_ATTR), p=True)
        if not space_cnt:
            return
        enum_names = cmds.addAttr(space_cnt[0], query=True, enumName=True)
        enum_list = enum_names.split(':')
        if target_space not in enum_list:
            sp.logger.warning('Space {} is not stored. Stoping space baking process ...'.format(target_space))
            return
        index = enum_list.index(target_space)

        space_cnt = cmds.listConnections(switcher_node+'.{}'.format(SPACE_DRIVER_ATTR), p=True)[0].split('.')[-1]
        anim_utils.bake_space_switch(node=switcher_node, attr_name=space_cnt, attr_value=index, frame_range=frame_range)
        sp.logger.debug('Space successfully baked!')


def check_space_switch_node(full_object_name):
    if not cmds.attributeQuery(SPACE_DRIVER_ATTR, node=full_object_name, exists=True):
        return
    space_attr = cmds.listConnections('{}.{}'.format(full_object_name, SPACE_DRIVER_ATTR), p=True)
    if not space_attr:
        return
    return space_attr[0]


def override_dag_menu_proc():
    cmds.dagObjectHit(menu=SPACE_SWITCH_MENU_NAME)
    pop_children = cmds.popupMenu(SPACE_SWITCH_MENU_NAME, query=True, itemArray=True)
    command = cmds.menuItem(pop_children[0], query=True, command=True)
    if not command:
        return
    full_name = command.split(' ')[-1]
    cmds.popupMenu(SPACE_SWITCH_MENU_NAME, edit=True, deleteAllItems=True)

    return full_name


def launch_space_switch_marking_menu():

    def _build_marking_menu(*args):
        if cmds.popupMenu(SPACE_SWITCH_MENU_NAME, exists=True):
            cmds.popupMenu(SPACE_SWITCH_MENU_NAME, edit=True, deleteAllItems=True)
        cmds.setParent(SPACE_SWITCH_MENU_NAME, menu=True)
        if cmds.dagObjectHit():
            full_object_name = eval('override_dag_menu_proc()')
            if not full_object_name:
                return
        else:
            full_object_name = cmds.ls(sl=True)
            if full_object_name:
                full_object_name = full_object_name[0]
            else:
                return

        object_space = check_space_switch_node(full_object_name)
        if not object_space:
            return

        space_attr = object_space.split('.')[-1]
        current_space = cmds.getAttr(object_space, asString=True)
        bake_space_menu = cmds.menuItem(l='Bake Space', parent=SPACE_SWITCH_MENU_NAME, sm=True, to=True)
        start_frame, end_frame = anim_utils.get_playback_range()
        all_spaces = cmds.attributeQuery(space_attr, node=full_object_name, le=1)[0]
        if not all_spaces:
            return
        all_spaces = all_spaces.split(':')
        menu_item = ''
        radial_index = 0
        for i, space in enumerate(all_spaces):
            spaces_cmd = 'from solstice_pipeline.solstice_utils import solstice_anim_utils as anim_utils; anim_utils.space_switch_match("{}", "{}", {})'.format(full_object_name, space_attr, str(i))
            bake_cmd = ''
            if space != current_space:
                if radial_index >= 5:
                    menu_item = cmds.menuItem(l=space, c=spaces_cmd, parent=SPACE_SWITCH_MENU_NAME, insertAfter=menu_item)
                else:
                    cmds.menuItem(l=space, c=spaces_cmd, rp=RADIAL_POSITIONS[radial_index], parent=SPACE_SWITCH_MENU_NAME)
                    radial_index += 1
            cmds.menuItem(l=space, c=bake_cmd, parent=bake_space_menu)

    sp.logger.debug('Initializing Space Switch marking menu ...')
    if cmds.popupMenu(SPACE_SWITCH_MENU_NAME, exists=True):
        cmds.deleteUI(SPACE_SWITCH_MENU_NAME)
    try:
        cmds.popupMenu(SPACE_SWITCH_MENU_NAME, mm=1, b=2, ctl=1, p='viewPanes', pmc=_build_marking_menu)
    except TypeError as e:
        sp.logger.error(traceback.format_exc())


def run():
    launch_space_switch_marking_menu()
    win = SpaceAnimBaker().show()
    return win
