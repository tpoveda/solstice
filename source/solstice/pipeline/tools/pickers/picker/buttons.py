#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom buttons used by the pickers
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as maya_utils

from solstice.pipeline.tools.pickers.picker import colors as colors
from solstice.pipeline.tools.pickers.picker import utils as utils
from solstice.pipeline.tools.pickers.picker import commands as commands


class ButtonShape(object):
    CIRCULAR = 'circular'
    ROUNDED_SQUARE = 'rounded_square'


class ButtonState(object):
    NORMAL = 1
    DOWN = 2
    DISABLED = 3
    SELECTED = 4
    INNER = 1, 2


class BasePickerButton(QPushButton, object):
    def __init__(self, x=0, y=0,
                 inner_color=colors.yellow, outer_color=colors.blue, glow_color=colors.red,
                 text=None,
                 radius=25,
                 control='',
                 gizmo='',
                 part='',
                 side='',
                 enabled=True,
                 parent_ctrl=None,
                 parent=None,
                 btn_info=None,
                 button_shape = ButtonShape.CIRCULAR,
                 gradient_intensity = 0.6,
                 width=15,
                 height=5):
        super(BasePickerButton, self).__init__(parent=parent)

        # Color attributes
        self._inner_color = inner_color
        self._outer_color = outer_color
        self._glow_color = glow_color
        self._gradient_intensity = gradient_intensity
        self._brush_clear = QBrush(QColor(0, 0, 0, 0))
        self._brush_border = QBrush(QColor(9, 10, 12))

        # Controls attributes
        self._namespace = None
        self._control = control
        self._parent_ctrl = parent_ctrl
        self._child_ctrls = list()
        self._hierarchy = list()

        # Control info attributes
        self._btn_info = btn_info
        self._part = part
        self._side = side

        # Button shape attributes
        self._shape = button_shape
        self._radius = radius

        # Button font attributes
        self._font = QFont()
        self._font.setPointSize(8)
        self._font.setFamily('Calibri')
        self.setFont(self._font)
        self._fontMetrics = QFontMetrics(self._font)

        # Button state attributes
        self._pressed = False
        self._enabled = enabled
        self._hover = False
        self._selected = False

        # Glow animation and color attributes
        self._glow_index = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate_glow)
        self._glow_pens = []
        self._gradient = {ButtonState.NORMAL: {}, ButtonState.DOWN: {}, ButtonState.DISABLED: {}, ButtonState.SELECTED: {}}
        self._glow_steps = 11
        self._alpha_range = [12.0, 5.0, 2.0, 25.5]
        self._alpha_type = [1, 3, 5, 1]
        self._update_colors_info()
        self._pens_border = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pens_clear = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pens_text = QPen(QColor(202, 207, 210), 1, Qt.SolidLine)
        self._pens_shadow = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pens_text_disabled = QPen(QColor(102, 107, 110), 1, Qt.SolidLine)
        self._pens_shadow_disabled = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)

        # Extras attributes
        self._text = text
        self._gizmo = gizmo
        self._scene = None
        self._context_menu = None
        self._fk_ik_control = None
        self._command = None

        if self._shape == ButtonShape.CIRCULAR:
            self.setFixedHeight(radius)
            self.setFixedWidth(radius)
        elif self._shape == ButtonShape.ROUNDED_SQUARE:
            self.setFixedHeight(height)
            self.setFixedWidth(width)
        self.move(x, y)
        self.setStyleSheet('background-color: rgba(0,0,0,0);')

    def get_width(self):
        return self.width()

    def set_width(self, width):
        self.setFixedWidth(width)

    def get_height(self):
        return self.height()

    def set_height(self, height):
        self.setFixedHeight(height)

    def get_inner_color(self):
        return self._inner_color

    def set_inner_color(self, inner_color):
        if type(inner_color) == list:
            inner_color = colors.get_color_from_list(inner_color)
        self._inner_color = inner_color
        self._update_colors_info()

    def get_outer_color(self):
        return self._outer_color

    def set_outer_color(self, outer_color):
        if type(outer_color) == list:
            outer_color = colors.get_color_from_list(outer_color)
        self._outer_color = outer_color
        self._update_colors_info()

    def get_glow_color(self):
        return self._glow_color

    def set_glow_color(self, glow_color):
        if type(glow_color) == list:
            glow_color = colors.get_color_from_list(glow_color)
        self._glow_color = glow_color
        self._update_colors_info()

    def get_gradient_intensity(self):
        return self._gradient_intensity

    def set_gradient_intensity(self, gradient_intensity):
        self._gradient_intensity = gradient_intensity
        self._update_colors_info()

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        if self._shape == ButtonShape.CIRCULAR:
            self.setFixedWidth(radius)
            self.setFixedHeight(radius)

    def get_scene(self):
        return self._scene

    def set_scene(self, scene):
        self._scene = scene

    def get_namespace(self):
        return self._namespace

    def set_namespace(self, namespace):
        """
        Set the namespace associated to this button
        :param namespace: str
        """

        self._namespace = namespace
        if self._namespace == '':
            if ':' in self._control:
                self._control = self._control.split(':')[1]
        else:
            self._control = self._namespace + ':' + self._control

    def get_control(self):
        if self.scene.namespace != '':
            return self.scene.namespace + ':' + self._control
        else:
            return self._control

    def set_control(self, ctrl):
        self._control = ctrl

    def get_control_group(self):
        if self.scene.namespace != '':
            if self._side != '':
                return self.scene.namespace + ':' + self._side.upper() + '_' + self._part + '_ctrlsGrp'
            else:
                return self.scene.namespace + ':' + self._part + '_ctrlsGrp'
        else:
            if self._side != '':
                return self._side.upper() + '_' + self._part + '_ctrlsGrp'
            else:
                return self._part + '_ctrlsGrp'

    def get_parent_ctrl(self):
        return self._parent_ctrl

    def set_parent_ctrl(self, parent_ctrl):
        self._parent_ctrl = parent_ctrl

    def get_fk_ik_control(self):
        return self._fk_ik_control

    def set_fk_ik_control(self, fk_ik_control):
        self._fk_ik_control = fk_ik_control

    def get_info(self):
        return self._btn_info

    def set_info(self, btn_info):
        self._btn_info = btn_info
        self.move(btn_info['x'], btn_info['y'])
        self._text = btn_info['text']

    def _get_part(self):
        return self._part

    def get_part(self):
        for part in self.scene.parts:
            if part.name == self._part and part.side == self._side:
                return part

        return None

    def get_gizmo(self):
        return self._gizmo

    def set_gizmo(self, gizmo):
        self._gizmo = gizmo

    def set_part(self, part):
        self._part = part

    def get_side(self):
        return self._side

    def set_side(self, side):
        self._side = side

    def get_command(self):
        return self._command

    def set_command(self, command):
        self._command = command

    width = property(get_width, set_width)
    height = property(get_height, set_height)
    inner_color = property(get_inner_color, set_inner_color)
    outer_color = property(get_outer_color, set_outer_color)
    glow_color = property(get_glow_color, set_glow_color)
    gradient_intensity = property(get_gradient_intensity, set_gradient_intensity)
    radius = property(get_radius, set_radius)
    scene = property(get_scene, set_scene)
    namespace = property(get_namespace, set_namespace)
    control = property(get_control, set_control)
    control_group = property(get_control_group)
    parent_ctrl = property(get_parent_ctrl, set_parent_ctrl)
    fk_ik_ctrl = property(get_fk_ik_control, set_fk_ik_control)
    info = property(get_info, set_info)
    part = property(_get_part, set_part)
    gizmo = property(get_gizmo, set_gizmo)
    side = property(get_side, set_side)
    command = property(get_command, set_command)

    def paint_inner(self, painter, x, y, width, height):
        """
        Draw the inner part of the button
        """

        if self._shape == ButtonShape.CIRCULAR:
            painter.drawEllipse(QRect(x + 1, y + 1, width - 1, height - 1))
        else:
            painter.drawRoundedRect(QRect(x + 2, y + 2, width - 4, height - 4), self._radius - 1, self._radius - 1)

    def paintEvent(self, *args):
        painter = QStylePainter(self)
        option = QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        # Paint button
        painter.setRenderHint(QPainter.Antialiasing)

        gradient, offset = self._get_current_gradient_offset()

        painter.setPen(self._pens_border)
        painter.setBrush(gradient[ButtonState.INNER])
        self.paint_inner(painter, x, y, width, height)

        # if self._selected:
        #     gradient = self._gradient[SELECTED]
        #     painter.setBrush(self._brush_border)
        #     painter.setPen(self._pens_border)
        #
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 1, y + 1, width - 1, height - 1))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 1, y + 1, width - 1, height - 1), self._radius, self._radius)
        #
        #     painter.setPen(self._pens_clear)
        #
        #     painter.setBrush(gradient[OUTER])
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 2, y + 2, width - 3, height - 3))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 2, y + 2, width - 3, height - 3), self._radius, self._radius)
        #
        #     painter.setBrush(gradient[INNER])
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 3, y + 3, width - 5, height - 5))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 3, y + 3, width - 5, height - 5), self._radius - 1, self._radius - 1)

        # Paint text
        if self._text != '':
            text_width = self.fontMetrics().width(self._text)
            text_height = self._font.pointSize()

            text_path = QPainterPath()
            text_path.addText((width - text_width) / 2, height - ((height - text_height) / 2) - 1 + offset, self._font, self._text)
            alignment = (Qt.AlignHCenter | Qt.AlignVCenter)

            glow_index = self._glow_index
            glow_pens = self._glow_pens

            if self.isEnabled():
                painter.setPen(self._pens_shadow)
                painter.drawPath(text_path)

                painter.setPen(self._pens_text)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

                if glow_index > 0:
                    for index in range(3):
                        painter.setPen(glow_pens[index])
                        painter.drawPath(text_path)
                    painter.setPen(self._glow_color)
                    painter.drawText(x, y + offset, width, height, alignment, self._text)
            else:
                painter.setPen(self._pens_shadowdisabled)
                painter.drawPath(text_path)
                painter.setPen(self._pens_text_disabled)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

    def enterEvent(self, event):
        super(BasePickerButton, self).enterEvent(event)

        if not self.isEnabled(): return

        self._hover = True
        self._start_glow_anim()

    def leaveEvent(self, event):
        super(BasePickerButton, self).leaveEvent(event)

        if not self.isEnabled(): return

        self._hover = False
        self._start_glow_anim()

    def mousePressEvent(self, event):
        super(BasePickerButton, self).mousePressEvent(event)

        if self.control != '' and self.control is not None:
            modifiers = cmds.getModifiers()
            shift = (modifiers & 1) > 0
            ctrl = (modifiers & 4) > 0
            if cmds.objExists(self.control):
                cmds.select(self.control, add=shift, deselect=ctrl)

                if self._gizmo != '':
                    utils.set_tool(self._gizmo)
            else:
                for side in ['L', 'R']:
                    if side + '_' in self.control:
                        self._control = self._control.replace(side + '_', '')
                        splits = self.control.split('_')
                        new_name = splits[0] + '_' + side
                        for i in xrange(len(splits)):
                            if i == 0: continue
                            new_name += '_' + splits[i]
                            if cmds.objExists(new_name):
                                self._control = new_name
                                cmds.select(self.control, add=shift, deselect=ctrl)
                                return
                print('Could not select control {0} because it does not exists in the scene'.format(self.control))

    def mouseDoubleClickEvent(self, event):
        super(BasePickerButton, self).mouseDoubleClickEvent(event)
        self._select_hierarchy()

    def post_creation(self):
        """
        This method is called after the button is added to the picker scene
        Override in custom buttons
        """

        pass

    def get_hierarchy(self):

        # NOTE: If the system fails with a maximum recursion error check that the parent
        # name is correct and not is equal as the name of the control

        hierarchy = [self.control]
        if len(self._child_ctrls) > 0:
            for child in self._child_ctrls:
                if child == self.control:
                    continue
                hierarchy.extend(child.get_hierarchy())

        return hierarchy

    def update_hierarchy(self):
        """
        Updates the hierarchy of the button
        """

        self._hierarchy = self.get_hierarchy()

    def add_child(self, btn):
        """
        Adds a child to the list of button childs
        :param btn:
        """

        self._child_ctrls.append(btn)

    def _update_colors_info(self):
        """
        Updates the color info of the button
        """

        # Update glow range colors
        for i in range(1, self._glow_steps):
            for j in range(len(self._alpha_range)):
                new_color = self._glow_color
                new_color.setAlpha(i * self._alpha_range[j])
                self._glow_pens.append(QPen(new_color, self._alpha_type[j], Qt.SolidLine))

        # Update gradient colors
        inner_gradient = QLinearGradient(0, 3, 0, 24)
        inner_gradient.setColorAt(0, self._inner_color)
        inner_gradient.setColorAt(1, self._inner_color.darker(200 * self._gradient_intensity))
        self._gradient[ButtonState.NORMAL][ButtonState.INNER] = QBrush(inner_gradient)

        inner_gradient_down = QLinearGradient(0, 3, 0, 24)
        inner_gradient_down.setColorAt(0, self._inner_color.darker(400 * self._gradient_intensity))
        inner_gradient_down.setColorAt(1, self._inner_color.darker(650 * self._gradient_intensity))
        self._gradient[ButtonState.DOWN][ButtonState.INNER] = QBrush(inner_gradient_down)

        inner_gradient_disabled = QLinearGradient(0, 3, 0, 24)
        inner_gradient_disabled.setColorAt(0, self._inner_color.darker(850 * self._gradient_intensity))
        inner_gradient_disabled.setColorAt(1, self._inner_color.darker(950 * self._gradient_intensity))
        self._gradient[ButtonState.DISABLED][ButtonState.INNER] = QBrush(inner_gradient_disabled)

        inner_gradient_selected = QLinearGradient(0, 3, 0, 24)
        inner_gradient_selected.setColorAt(0, self._inner_color.darker(300 * self._gradient_intensity))
        inner_gradient_selected.setColorAt(1, self._inner_color.darker(400 * self._gradient_intensity))
        self._gradient[ButtonState.SELECTED][ButtonState.INNER] = QBrush(inner_gradient_selected)

    def _get_current_gradient_offset(self):
        """
        Returns a correct gradient color and offset depending of the state of the button
        :return: int, int
        """

        gradient = self._gradient[ButtonState.NORMAL]
        offset = 0
        if self.isDown():
            gradient = self._gradient[ButtonState.DOWN]
            offset = 1
        elif not self.isEnabled():
            gradient = self._gradient[ButtonState.DISABLED]

        return gradient, offset

    def _animate_glow(self):
        """
        Animates the glow of the button text
        :return: float
        """

        if self._hover:
            if self._glow_index >= self._glow_steps-1:
                self._glow_index = self._glow_steps - 1
                self._anim_timer.stop()
            else:
                self._glow_index = 0
        else:
            self._glow_index = 0
            self._anim_timer.stop()
        maya_utils.executeDeferred(self.update)

    def _start_glow_anim(self):
        """
        Starts the glow animation
        """

        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)

    @utils.picker_undo
    def _select_hierarchy(self):
        """
        Select the hierarchy of the button
        """

        from solstice.pipeline.tools.pickers.picker import pickerwindow

        if len(self._hierarchy) > 0:
            for btn in self._hierarchy:
                if btn == self.control:
                    pass
                else:
                    window_picker = pickerwindow.window_picker
                    if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
                        btn = '{0}:{1}'.format(window_picker.namespace.currentText(), btn)
                    cmds.select(btn, add=True)

    @utils.picker_undo
    def _reset_control(self):
        """
        Reset the control to its default values
        """

        for axis in ['x', 'y', 'z']:
            for xform in ['t', 'r', 's']:
                try:
                    new_val = 0.0
                    if xform == 's':
                        new_val = 1.0
                    cmds.setAttr(self.control + '.' + xform + axis, new_val)
                except:
                    pass

    @utils.picker_undo
    def _mirror_control(self):
        """
        Mirror control attributes from one side to another
        """

        mirror_ctrl = utils.get_mirror_control(self.control)

        if mirror_ctrl is None:
            return
        new_x_form = {}
        for xform in ['t', 'r', 's']:
            new_x_form[xform] = {}
            for axis in ['x', 'y', 'z']:
                new_x_form[xform][axis] = cmds.getAttr(self.control + '.' + xform + axis)

        for xform, value in new_x_form.items():
            for axis, xform_value in value.items():
                try:
                    cmds.setAttr(mirror_ctrl + '.' + xform + axis, xform_value)
                except:
                    pass

    @utils.picker_undo
    def _flip_control(self):
        """
        Flip control attributes between sides
        """

        mirror_ctrl = utils.get_mirror_control(self.control)
        if mirror_ctrl is None:
            return

        orig_xform = {}
        mirror_xform = {}

        for xform in ['t', 'r', 's']:
            orig_xform[xform] = {}
            for axis in ['x', 'y', 'z']:
                orig_xform[xform][axis] = cmds.getAttr(self.control + '.' + xform + axis)
        for xform in ['t', 'r', 's']:
            mirror_xform[xform] = {}
            for axis in ['x', 'y', 'z']:
                mirror_xform[xform][axis] = cmds.getAttr(mirror_ctrl + '.' + xform + axis)

        for xform, value in orig_xform.items():
            for axis, xform_value in value.items():
                try:
                    cmds.setAttr(mirror_ctrl + '.' + xform + axis, xform_value)
                except:
                    pass
        for xform, value in mirror_xform.items():
            for axis, xform_value in value.items():
                try:
                    cmds.setAttr(self.control + '.' + xform + axis, xform_value)
                except:
                    pass

    @utils.picker_undo
    def _reset_control_attributes(self):
        """
        Reset the attributes of the control
        """

        commands.reset_attributes(self.control)


class ToggleButton(BasePickerButton, object):
    toggleOn = Signal()
    toggleOff = Signal()

    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', radius=30, btn_info=None, parent=None, on_text='ON', off_text='OFF'):
        super(ToggleButton, self).__init__(
            x=x, y=y,
            text=text,
            control=control, parent_ctrl=parent_ctrl,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=radius, inner_color=colors.blue,
            btn_info=btn_info,
            parent=parent
        )

        self._on_text = text if on_text == '' else on_text
        self._off_text = off_text

    def set_info(self, btn_info):
        super(ToggleButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def mousePressEvent(self, event):
        self._pressed = not self._pressed
        self.repaint()

        self.toggleOn.emit() if self._pressed else self.toggleOff.emit()

    def mouseDoubleClickEvent(self, event):
        event.accept()

    def paintEvent(self, event):
        super(ToggleButton, self).paintEvent(event)
        self._text = self._on_text if self._pressed is True else self._off_text

    def _get_current_gradient_offset(self):
        """
        Returns a correct gradient color and offset depending of the state of the button
        """

        gradient = self._gradient[ButtonState.NORMAL]
        offset = 0
        if self._pressed:
            gradient = self._gradient[ButtonState.DOWN]
            offset = 1
        return gradient, offset


class ToggleStateButton(BasePickerButton, object):
    onOffToggle = Signal()
    onOffUntoggle = Signal()

    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(ToggleStateButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(ToggleStateButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def post_creation(self):
        """
        Method called after the button is added into the picker scene
        """

        self.on_off_btn = ToggleButton(x=116, y=52, radius=2, text='GIMAL', on_text='ON', off_text='OFF')
        self.on_off_btn.width = 32
        self.on_off_btn.height = 20
        self.on_off_btn.inner_color = [100, 100, 100]
        self.on_off_btn.glow_color = [255, 255, 255]
        self.scene.add_button(self.on_off_btn)


class CommandButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', radius=30, btn_info=None, parent=None):
        super(CommandButton, self).__init__(
            x=x, y=y,
            text=text,
            control=control, parent_ctrl=parent_ctrl,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=radius, inner_color=colors.blue,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(CommandButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.parent_ctrl = btn_info['parent']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        self.fk_ik_ctrl = btn_info['FKIKControl']
        self.command = btn_info['command']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    @utils.picker_undo
    def execute_command(self):
        exec self.command

    def mousePressEvent(self, event):
        self.execute_command()


class ExtraButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(ExtraButton, self).__init__(
            x=x, y=y,
            width=width,
            height=height,
            text=text,
            control=control, parent_ctrl=parent_ctrl,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(ExtraButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.parent_ctrl = btn_info['parent']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def contextMenuEvent(self, event):
        menu = QMenu()
        select_hierarchy_action = menu.addAction('Select Hierarchy')
        reset_control_action = menu.addAction('Reset Control')
        mirror_control_action = menu.addAction('Mirror Control')
        flip_control_action = menu.addAction('Flip Control')
        reset_control_attributes = menu.addAction('Reset Control Attributes')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == select_hierarchy_action:
            self._select_hierarchy()
        elif action == reset_control_action:
            self._reset_control()
        elif action == mirror_control_action:
            self._mirror_control()
        elif action == flip_control_action:
            self._flip_control()
        elif action == reset_control_attributes:
            self._reset_control_attributes()


class FKButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', radius=30, btn_info=None, parent=None):

        btn_text = text
        if text == '' or text is None:
            btn_text = 'FK'

        super(FKButton, self).__init__(
            x=x, y=y,
            text=btn_text,
            control=control, parent_ctrl=parent_ctrl,
            button_shape=ButtonShape.CIRCULAR, radius=radius, inner_color=colors.blue,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(FKButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.parent_ctrl = btn_info['parent']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        self.fk_ik_ctrl = btn_info['FKIKControl']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def contextMenuEvent(self, event):
        menu = QMenu()
        select_hierarchy_action = menu.addAction('Select Hierarchy')
        reset_control_action = menu.addAction('Reset Control')
        mirror_control_action = menu.addAction('Mirror Control')
        flip_control_action = menu.addAction('Flip Control')
        reset_control_attributes = menu.addAction('Reset Control Attributes')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == select_hierarchy_action:
            self._select_hierarchy()
        elif action == reset_control_action:
            self._reset_control()
        elif action == mirror_control_action:
            self._mirror_control()
        elif action == flip_control_action:
            self._flip_control()
        elif action == reset_control_attributes:
            self._reset_control_attributes()


class IKButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', radius=30, btn_info=None, parent=None):

        btn_text = text
        if text == '' or text is None:
            btn_text = 'IK'

        super(IKButton, self).__init__(
            x=x, y=y,
            text=btn_text,
            control=control, parent_ctrl=parent_ctrl,
            button_shape=ButtonShape.CIRCULAR, radius=radius, inner_color=colors.yellow,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(IKButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.parent_ctrl = btn_info['parent']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        self.fk_ik_ctrl = btn_info['FKIKControl']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def contextMenuEvent(self, event):
        menu = QMenu()
        select_hierarchy_action = menu.addAction('Select Hierarchy')
        reset_control_action = menu.addAction('Reset Control')
        mirror_control_action = menu.addAction('Mirror Control')
        flip_control_action = menu.addAction('Flip Control')
        reset_control_attributes = menu.addAction('Reset Control Attributes')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == select_hierarchy_action:
            self._select_hierarchy()
        elif action == reset_control_action:
            self._reset_control()
        elif action == mirror_control_action:
            self._mirror_control()
        elif action == flip_control_action:
            self._flip_control()
        elif action == reset_control_attributes:
            self._reset_control_attributes()


class FKIKSwitchButton(ToggleButton, object):
    def __init__(self, x=0, y=0, text='', control='', parent_ctrl='', radius=30, btn_info=None, parent=None):
        super(FKIKSwitchButton, self).__init__(
            x=x, y=y,
            text=text,
            control=control, parent_ctrl=parent_ctrl,
            radius=radius,
            btn_info=btn_info,
            parent=parent,
            on_text='IK',
            off_text='FK'
        )

        self.toggleOn.connect(self.switch_to_ik)
        self.toggleOff.connect(self.switch_to_fk)

    def post_creation(self):
        """
        This method is called after the button is added to the picker scene
        """

        self.update_state()
        self.get_part().fkSignal.connect(self.update_state)
        self.get_part().ikSignal.connect(self.update_state)

    def get_info(self):
        """
        Override this to avoid problem with module selection (Check workaround for this)
        """

        return None

    def switch_to_fk(self):
        """
        Switch current button to FK state
        # TODO If gimbal control is selected select its fk control
        :return:
        """

        self.get_part().set_fk()
        sel = cmds.ls(sl=True)
        if len(sel) > 0:
            curr_ctrl = sel[0]
            fk_ik_ctrl = self.get_part().get_button_by_name(curr_ctrl)
            if len(fk_ik_ctrl) > 0:
                fk_ik_ctrl = fk_ik_ctrl[0].get_fk_ik_control()
                if fk_ik_ctrl and cmds.objExists(fk_ik_ctrl):
                    cmds.select(fk_ik_ctrl, r=True)
                    utils.set_tool('rotate')

    def switch_to_ik(self):
        """
        Switch current button to IK state
        # TODO If gimbal control is selected select its ik control
        :return:
        """

        self.get_part().set_ik()
        sel = cmds.ls(sl=True)
        if len(sel) > 0:
            curr_ctrl = sel[0]
            fk_ik_ctrl = self.get_part().get_button_by_name(curr_ctrl)
            if len(fk_ik_ctrl) > 0:
                fk_ik_ctrl = fk_ik_ctrl[0].get_fk_ik_control()
                if fk_ik_ctrl and cmds.objExists(fk_ik_ctrl):
                    cmds.select(fk_ik_ctrl, r=True)
                    utils.set_tool('move')

    def update_state(self):
        """
        Update current state of the toggle button
        """

        fk_ik_state = self.get_part().get_fk_ik(as_text=True)
        if fk_ik_state == 'IK':
            self._pressed = True
        else:
            self.pressed = False


class GimbalButton(ToggleStateButton, object):
    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):

        self.on_off_pos = QPoint(0, 0)

        super(GimbalButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            corner_radius=corner_radius,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(GimbalButton, self).set_info(btn_info=btn_info)
        self.on_off_pos = [btn_info['x'] + 6, btn_info['y'] + 17]

    def mousePressEvent(self, event):
        self.update_state()
        super(GimbalButton, self).mousePressEvent(event)

    def post_creation(self):
        super(GimbalButton, self).post_creation()

        self.update_state()

        # TODO: Check why this signal connect makes Maya crash
        # self.onOffBtn.toggleOn.connect(partial(self.updateGimbalVisibility, True))
        # self.onOffBtn.toggleOff.connect(partial(self.updateGimbalVisibility, False))

    def update_state(self):
        """
        Update the current state of the toggle button
        """

        self.on_off_btn.move(self.on_off_pos[0], self.on_off_pos[1])

        parts = ['', '']
        if 'arm 'in str(self.get_part().name):
            parts = ['wrist', 'arm']
        elif 'leg' in str(self.get_part().name):
            parts = ['ankle', 'foot']

        fk_ik_state = self.get_part().get_fk_ik(as_text=True)
        if fk_ik_state:
            if 'ik' in self.control:
                self.control = self.control.replace('ik_' + parts[0], 'ik_' + parts[1])
            else:
                self.control = self.control.replace('fk_' + parts[0], 'ik_' + parts[1])
        else:
            if 'ik' in self.control:
                self.control = self.control.replace('ik_' + parts[0], 'fk_' + parts[0])
            else:
                self.control = self.control.replace('ik_' + parts[1], 'fk_' + parts[0])

    def update_gimbal_visibility(self, is_enabled):

        from solstice.pipeline.tools.pickers.picker import pickerwindow

        self.update_state()
        ctrl = self.control.replace('_gimbalHelper', '')
        window_picker = pickerwindow.window_picker
        if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
            ctrl = '{0}:{1}'.format(window_picker.namespace.currentText(), ctrl)
        cmds.setAttr(ctrl + '.gimbalHelper', is_enabled)


class KeyFKIKButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(KeyFKIKButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(KeyFKIKButton, self).set_info(btn_info=btn_info)

        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def mousePressEvent(self, event):
        super(KeyFKIKButton, self).mousePressEvent(event)

        if cmds.objExists(self.control_group):
            if cmds.attributeQuery('FK_IK', node=self.control_group, exists=True):
                cmds.setKeyframe(self.control_group, attribute='FK_IK')


class ModuleButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(ModuleButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(ModuleButton, self).set_info(btn_info=btn_info)

        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def mousePressEvent(self, event):
        super(ModuleButton, self).mousePressEvent(event)

        from solstice.pipeline.tools.pickers.picker import pickerwindow

        module_ctrls = self.scene.get_part_controls(self.get_part(), self.side)
        window_picker = pickerwindow.window_picker
        module_ctrl = module_ctrls[0]
        if module_ctrl == '' or module_ctrl == '{}:'.format(window_picker.namespace.currentText()):
            module_ctrl = module_ctrls[1]
        try:
            mel.eval('vlRigIt_selectModuleControls("{}")'.format(module_ctrl))
        except Exception:
            try:
                if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
                    module_ctrl = '{0}:{1}'.format(window_picker.namespace.currentText(), module_ctrl)
                mel.eval('vlRigIt_selectModuleControls("{}")'.format(module_ctrl))
            except Exception as e:
                print('Impossible to select module')


class SelectButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(SelectButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(SelectButton, self).set_info(btn_info=btn_info)

        self.control = btn_info['control']
        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.gizmo = btn_info['gizmo']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def mousePressEvent(self, event):
        super(SelectButton, self).mousePressEvent(event)


class KeySpaceSwitchButton(BasePickerButton, object):
    def __init__(self, x=0, y=0, text='', corner_radius=5, width=30, height=15, btn_info=None, parent=None):
        super(KeySpaceSwitchButton, self).__init__(
            x=x, y=y,
            text=text,
            width=width, height=height,
            button_shape=ButtonShape.ROUNDED_SQUARE, radius=corner_radius, inner_color=colors.black,
            btn_info=btn_info,
            parent=parent
        )

    def set_info(self, btn_info):
        super(KeySpaceSwitchButton, self).set_info(btn_info=btn_info)

        self.width = btn_info['width']
        self.height = btn_info['height']
        self.radius = btn_info['radius']
        self.part = btn_info['part']
        self.side = btn_info['side']
        if btn_info['color'] is not None:
            self.inner_color = btn_info['color']
        if btn_info['glowColor'] is not None:
            self.glow_color = btn_info['glowColor']

    def mousePressEvent(self, event):
        super(KeySpaceSwitchButton, self).mousePressEvent(event)

        if cmds.objExists(self.control_group):
            if cmds.attributeQuery('FK_IK', node=self.controL_group, exists=True):
                cmds.setKeyframe(self.control_group, attribute='FK_IK')
