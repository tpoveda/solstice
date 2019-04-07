#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Picker View Class
# ==================================================================="""

import os
import imp
import json
from copy import deepcopy

from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import maya.cmds as cmds

from solstice_pipeline.solstice_pickers.picker import picker_buttons, picker_part


class PickerScene(QGraphicsScene, object):
    """
    Picker scene
    """

    __DEFAULT_SCENE_WIDTH__ = 100
    __DEFAULT_SCENE_HEIGHT__ = 200

    def __init__(self, data_path=None, namespace='', parent=None):
        super(PickerScene, self).__init__(parent=parent)

        self._data_path = data_path
        self._buttons = list()
        self._data_buttons = None
        self._parts = list()
        self._namespace = namespace

        self.set_default_size()
        self.reload_data()

    def get_namespace(self):
        return self._namespace

    def set_namespace(self, namespace):
        self._namespace = namespace

    def get_parts(self):
        return self._parts

    namespace = property(get_namespace, set_namespace)
    parts = property(get_parts)

    def get_bounding_rect(self):
        """
        Returns the bounding rect of the scene taking in account all the items inside of it
        :return: QRect
        """

        return self.itemsBoundingRect()

    def set_size(self, width, height):
        """
        Set the size of the scene
        :param width: int, width of the scene
        :param height: int, height of the scene
        """

        self.setSceneRect(-width*0.5, -height*0.5, width, height)

    def set_default_size(self):
        """
        Sets the scene with default size
        """

        self.set_size(self.__DEFAULT_SCENE_WIDTH__, self.__DEFAULT_SCENE_HEIGHT__)

    def load_data(self, path):
        """
        Load Picker scene data from a JSON file
        :param path: str, path where JSON data is stored
        """

        self.picker_data = dict()

        if not os.path.isfile(path):
            return

        with open(path) as fp:
            data = json.load(fp)
        if data.get('fileType') != 'pickerData':
            print('ERROR: Picker data is not valid!')
            return
        offset = int(data.get('offset'))
        picker_buttons = data.get('pickerButtons')
        if picker_buttons is None:
            return
        parts = picker_buttons.get('parts')
        if parts is None:
            return

        self.picker_data['parts'] = dict()
        for part, v in parts.items():
            self.picker_data['parts'][part] = dict()
            for button_class, class_buttons in v.items():
                self.picker_data['parts'][part][button_class] = list()
                for new_btn in class_buttons:
                    self._create_button(new_btn, part, button_class, offset)

        # Update control hierarchies
        for btn in self._buttons:
            if btn.parent_ctrl != '':
                for new_btn in self._buttons:
                    if btn.parent_ctrl == new_btn.control:
                        new_btn.add_child(btn)
        for btn in self._buttons:
            btn.update_hierarchy()

        # Moved to update_pickers() function in picker_window because at this point namespace is not updated
        # for part in self.parts:
        #     if part.has_fk_ik():
        #         if part.get_fk_ik(as_text=True) == 'FK':
        #             part.set_fk()
        #         else:
        #             part.set_ik()

    def reload_data(self):
        """
        Reloads the data of the picker
        """

        self.clear()

        if self._data_path is not '' and self._data_path is not None:
            if os.path.isfile(self._data_path):
                self.load_data(self._data_path)
            else:
                print('Impossible to load data from: {}'.format(self._data_path))

        self.update()

    def update_state(self):
        """
        Updates the state of the picker
        Useful when the picker is not correctly sync with the state of the character
        This can happen when using undo/redo actions
        :return:
        """

        # TODO: Use Maya callbacks to call this method each time a undo/redo action is done

        for part in self._parts:
            if part.has_fk_ik():
                if part.get_fk_ik(as_text=True) == 'FK':
                    part.set_fk()
                else:
                    part.set_ik()

    def add_button(self, new_button=None):
        """
        Adds a new picker button to the scene
        :param new_button: SolsticeButton
        """

        if new_button is None:
            new_button = picker_buttons.FKButton()
        new_button.scene = self
        self.addWidget(new_button)
        self._buttons.append(new_button)

        part_found = None
        for part in self._parts:
            if part.name == new_button.part and part.side == new_button.side:
                part_found = part

        if part_found is None:
            part_found = picker_part.PickerPart(name=new_button.part, side=new_button.side)
            self._parts.append(part_found)

        part_found.add_button(new_button)
        new_button.post_creation()

    def get_side_controls(self, side='M'):
        if self.parts.has_key(side):
            return self.parts[side]

    def get_part_controls(self, control_type, side='', as_buttons=False):
        controls = list()
        for btn in self._buttons:
            btn_info = btn.get_info()
            if btn_info and btn_info.get('part'):
                if btn_info['part'] == control_type.name:
                    if side != '':
                        if btn_info['side'] == side:
                            if as_buttons:
                                controls.append(btn)
                            else:
                                controls.append(btn.control)
                    else:
                        if as_buttons:
                            controls.append(btn)
                        else:
                            controls.append(btn.control)

        return controls

    def get_part_controls_group(self, control_type, side=''):
        controls = self.get_part_controls(control_type=control_type, side=side, as_buttons=True)
        if controls:
            return controls[0].control_group

        return None

    def get_part_fk_ik_state(self, control_type, side=''):
        part_ctrl_group = self.get_part_controls_group(control_Type=control_type, side=side)
        if cmds.objExists(part_ctrl_group):
            if cmds.attributeQuery('FK_IK', node=part_ctrl_group, exist=True):
                return cmds.getAttr(part_ctrl_group + '.FK_IK')

    def _create_button(self, btn_data, part, button_class, offset=0):
        btn_info = self._get_button_info(btn_data, part, offset, button_class)
        new_btn = eval('picker_buttons.' + button_class + '()')
        new_btn.set_info(btn_info)
        self.picker_data['parts'][part][button_class].append(new_btn)
        self.add_button(new_btn)

        if btn_info['mirror'] != '' and btn_info['mirror'] is not None:
            new_info = deepcopy(btn_info)
            mirror_btn_info = self._get_mirror_button_info(new_info, offset)
            new_mirror_btn = eval('picker_buttons.' + mirror_btn_info['class']+'()')
            new_mirror_btn.set_info(mirror_btn_info)
            self.picker_data['parts'][part][button_class].append(new_mirror_btn)
            self.add_button(new_mirror_btn)

    def _get_button_control(self, side, part, control_type, name, fullname=''):
        if fullname != '':
            return fullname
        else:
            if control_type == '':
                if side != '':
                    if side != '' and name != '':
                        if part != '':
                            return '{0}_{1}_{2}_ctrl'.format(side, part, name)
                        else:
                            return '{0}_{1}_ctrl'.format(side, name)
                else:
                    if part != '' and name != '':
                        return '{0}_{1}_ctrl'.format(part, name)
            else:
                if side != '':
                    if side != '' and part != '' and control_type != '' and name != '':
                        return '{0}_{1}_{2}_{3}_ctrl'.format(side, part, control_type, name)
                else:
                    if part != '' and control_type != '' and name != '':
                        return '{0}_{1}_{2}_ctrl'.format(part, control_type, name)
        return ''

    def _get_button_info(self, btn_data, part, offset, class_name):

        btn_class_name = class_name
        btn_fullname = ''
        btn_x_pos = offset
        btn_y_pos = 0
        btn_text = ''
        btn_radius = 30
        btn_parent = ''
        btn_mirror = ''
        btn_offset = [0, 0]
        btn_side = ''
        btn_part = part
        btn_type = ''
        btn_name = 'default'
        btn_width = 30
        btn_height = 15
        btn_gizmo = ''
        btn_color = None
        btn_glow_color = None
        btn_fk_ik_control = ''
        btn_command = ''

        if btn_data.get('class'):
            btn_class_name = btn_data['class']
        if btn_data.get('fullname'):
            btn_fullname = btn_data['fullname']
        if btn_data.get('x'):
            btn_x_pos = int(btn_data['x']) - offset
        if btn_data.get('y'):
            btn_y_pos = int(btn_data['y']) - offset
        if btn_data.get('text'):
            btn_text = btn_data['text']
        if btn_data.get('radius'):
            btn_radius = int(btn_data['radius'])
        if btn_data.get('parent'):
            btn_parent = btn_data['parent']
        if btn_data.get('mirror'):
            btn_mirror = btn_data['mirror']
        if btn_data.get('offset'):
            btn_offset = btn_data['offset']
        if btn_data.get('side'):
            btn_side = btn_data['side']
        if btn_data.get('type'):
            btn_type = btn_data['type']
        if btn_data.get('name'):
            btn_name = btn_data['name']
        if btn_data.get('width'):
            btn_width = int(btn_data['width'])
        if btn_data.get('height'):
            btn_height = int(btn_data['height'])
        if btn_data.get('gizmo'):
            btn_gizmo = btn_data['gizmo']
        if btn_data.get('color'):
            btn_color = btn_data['color']
        if btn_data.get('glowColor'):
            btn_glow_color = btn_data['glowColor']
        if btn_data.get('FKIKControl'):
            btn_fk_ik_control = btn_data['FKIKControl']
        if btn_data.get('command'):
            btn_command = btn_data['command']

        btn_ctrl = self._get_button_control(btn_side, btn_part, btn_type, btn_name, fullname=btn_fullname)

        btn_info = dict()
        btn_info['class'] = btn_class_name
        btn_info['fullname'] = btn_fullname
        btn_info['x'] = btn_x_pos
        btn_info['y'] = btn_y_pos
        btn_info['text'] = btn_text
        btn_info['radius'] = btn_radius
        btn_info['control'] = btn_ctrl
        btn_info['parent'] = btn_parent
        btn_info['mirror'] = btn_mirror
        btn_info['offset'] = btn_offset
        btn_info['side'] = btn_side
        btn_info['part'] = btn_part
        btn_info['type'] = btn_type
        btn_info['name'] = btn_name
        btn_info['width'] = btn_width
        btn_info['height'] = btn_height
        btn_info['gizmo'] = btn_gizmo
        btn_info['color'] = btn_color
        btn_info['glowColor'] = btn_glow_color
        btn_info['FKIKControl'] = btn_fk_ik_control
        btn_info['command'] = btn_command

        return btn_info

    def _get_mirror_button_info(self, btn_info, offset=0):

        new_btn_info = btn_info
        if btn_info['side'] == '' or btn_info['side'] is None:
            return
        if btn_info['control'] == '' or btn_info['control'] == '':
            return

        available_sides = list()
        saved_side = btn_info['side']
        for side in ['L', 'R']:
            for curr_side in ['_{0}_'.format(side), '{0}_'.format(side), '_{0}'.format(side)]:
                available_sides.append(curr_side)
            if btn_info['side'] == side:
                if btn_info['side'] == 'l' or btn_info['side'] == 'L':
                    saved_side = 'R'
                elif btn_info['side'] == 'r' or btn_info['side'] == 'R':
                    saved_side = 'L'

        curr_side = None
        valid_side = None
        for side in available_sides:
            if side in btn_info['control']:
                curr_side = side
                break

        if curr_side is None:
            return

        if 'l' in curr_side or 'L' in curr_side:
            valid_side = curr_side.replace('l', 'r').replace('L', 'R')
        elif 'r' in curr_side or 'R' in curr_side:
            valid_side = curr_side.replace('r', 'l').replace('R', 'L')

        if valid_side is None:
            return

        new_btn_info['fullname'] = btn_info['fullname'].replace(curr_side, valid_side)
        new_btn_info['x'] = ((btn_info['x'] + offset + 15 + (btn_info['offset'][0])) * -1)
        new_btn_info['y'] = new_btn_info['y'] + btn_info['offset'][1]
        if btn_info['control'] != '':
            new_btn_info['control'] = btn_info['control'].replace(curr_side, valid_side)
            new_btn_info['side'] = saved_side
        if btn_info['parent'] != '':
            new_btn_info['parent'] = btn_info['parent'].replace(curr_side, valid_side)
        if btn_info['FKIKControl'] != '':
            new_btn_info['FKIKControl'] = btn_info['FKIKControl'].replace(curr_side, valid_side)

        return new_btn_info
