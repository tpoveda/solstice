#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains different buttons used in Solstice Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys
import weakref

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.resources import resource

NORMAL, DOWN, DISABLED = 1, 2, 3
INNER, OUTER = 1, 2


class BaseButton(QPushButton, object):
    def __init__(self, *args, **kwargs):
        super(BaseButton, self).__init__(*args, **kwargs)

        palette = self.palette()
        palette.setColor(QPalette.Button, QColor(60, 60, 60, 255))
        self.setPalette(palette)


class IconButton(BaseButton, object):
    def __init__(self, icon_name='', button_text='', icon_padding=0, icon_min_size=8, icon_extension='png', icon_hover=None, parent=None):
        super(IconButton, self).__init__(parent=parent)

        self._pad = icon_padding
        self._minSize = icon_min_size
        self.setText(button_text)

        self._icon = resource.icon(name=icon_name, extension=icon_extension)

        self._icon_hover = None
        if icon_hover:
            self._icon_hover = resource.icon(name=icon_hover, extension=icon_extension)

        self.setFlat(True)
        self.setIcon(self._icon)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

    def enterEvent(self, event):
        if self._icon_hover:
            self.setIcon(self._icon_hover)

    def leaveEvent(self, event):
        self.setIcon(self._icon)


class LockButton(QPushButton, object):

    _lock_icon = resource.icon('lock')
    _unlock_icon = resource.icon('unlock')

    def __init__(self, parent=None):
        super(LockButton, self).__init__(parent=parent)
        self.setCheckable(True)
        self.unlock()
        self.toggled.connect(self.update_lock)

    def update_lock(self, isLock):
        if isLock:
            self.lock()
        else:
            self.unlock()

    def lock(self):
        self.setIcon(self._lock_icon)

    def unlock(self):
        self.setIcon(self._unlock_icon)


class CategoryButtonWidget(QWidget, object):
    def __init__(self, category_name, status, asset, check_lock_info=False, parent=None):
        super(CategoryButtonWidget, self).__init__(parent=parent)

        self._asset = weakref.ref(asset)
        self._category_name = category_name.lower()
        self._status = status.lower()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(0 ,0 , 0, 0)
        widget_layout.setSpacing(0)
        main_widget = QWidget()
        main_widget.setLayout(widget_layout)
        self._category_btn = QPushButton(category_name)
        self._category_btn.setMinimumHeight(40)
        widget_layout.addWidget(self._category_btn)
        main_layout.addWidget(main_widget)

        if status == 'working' and check_lock_info:
            button_layout = QVBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(0)
            button_frame = QFrame()
            button_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            button_frame.setLineWidth(1)
            button_frame.setLayout(button_layout)
            self._lock_btn = LockButton()
            button_layout.addWidget(self._lock_btn)
            button_frame.setParent(self)
            main_layout.addWidget(button_frame)
            self._lock_btn.toggled.connect(self.lock_file)

        self._category_btn.clicked.connect(self.open_asset_file)

        if check_lock_info:
            self.update()

    def update(self):
        if self._status == 'working':

            asset_locked_by, current_user_can_lock = self._asset().is_locked(category=self._category_name, status=self._status)

            self._lock_btn.blockSignals(True)
            if asset_locked_by is not None and asset_locked_by:
                self._lock_btn.setChecked(True)
            else:
                self._lock_btn.setChecked(False)
            self._lock_btn.blockSignals(False)

            if not current_user_can_lock:
                self._lock_btn.setEnabled(False)
                self._lock_btn.setStyleSheet('QPushButton { border: 1px solid yellow; }')
                self._lock_btn.setStatusTip('This file is locked by other Solstice team member!')
                self._lock_btn.setToolTip('This file is locked by other Solstice team member!')
            else:
                self._lock_btn.setEnabled(True)

            if not current_user_can_lock and asset_locked_by is False:
                self._lock_btn.setStyleSheet('QPushButton { border: 1px solid red; }')
                self._lock_btn.setStatusTip('This file does not exists on Artella server yet!')
                self._lock_btn.setToolTip('This file does not exists on Artella server yet!')

    def open_asset_file(self):
        if self._category_name == 'textures':
            self._asset().open_textures_folder(self._status)
        else:
            self._asset().open_asset_file(self._category_name, self._status)

    def lock_file(self, flag):
        if flag:
            self._asset().lock(category=self._category_name, status=self._status)
        else:
            self._asset() .unlock(category=self._category_name, status=self._status)


class ColorButton(QPushButton, object):

    colorChanged = Signal()

    def __init__(self, colorR=1.0, colorG=0.0, colorB=0.0, parent=None):
        super(ColorButton, self).__init__(parent=parent)
        self._color = QColor.fromRgbF(colorR, colorG, colorB)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self._update_color()

        self.clicked.connect(self.show_color_editor)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color
        self._update_color()

    def show_color_editor(self):
        if sp.is_maya():
            import maya.cmds as cmds
            cmds.colorEditor(rgbValue=(self._color.redF(), self._color.greenF(), self._color.blueF()))
            if not cmds.colorEditor(query=True, result=True):
                return
            new_color = cmds.colorEditor(query=True, rgbValue=True)
            self.color = QColor.fromRgbF(new_color[0], new_color[1], new_color[2])
            self.colorChanged.emit()
        else:
            sys.solstice.logger.warning('Color Editor is not supported in current DCC: {}'.format(sys.solstice.dcc.get_name()))
            return

    def _update_color(self):
        self.setStyleSheet('background-color:rgb({0},{1},{2});'.format(self._color.redF()*255, self._color.greenF()*255, self._color.blueF()*255))

    color = property(get_color, set_color)


class Base(object):
    _glow_pens = {}
    for index in range(1, 11):
        _glow_pens[index] = [QPen(QColor(0, 255, 0, 12   * index), 1, Qt.SolidLine),
                             QPen(QColor(0, 255, 0,  5   * index), 3, Qt.SolidLine),
                             QPen(QColor(0, 255, 0,  2   * index), 5, Qt.SolidLine),
                             QPen(QColor(0, 255, 0, 25.5 * index), 1, Qt.SolidLine)]

    _pens_text   = QPen(QColor(202, 207, 210), 1, Qt.SolidLine)
    _pens_shadow = QPen(QColor(  9,  10,  12), 1, Qt.SolidLine)
    _pens_border = QPen(QColor(  9,  10,  12), 2, Qt.SolidLine)
    _pens_clear  = QPen(QColor(  0,  0, 0, 0), 1, Qt.SolidLine)

    _pens_text_disabled   = QPen(QColor(102, 107, 110), 1, Qt.SolidLine)
    _pens_shadow_disabled = QPen(QColor(  0,   0,   0), 1, Qt.SolidLine)

    _brush_clear  = QBrush(QColor(0, 0, 0, 0))
    _brush_border = QBrush(QColor( 9, 10, 12))

    def __init__(self):
        font = QFont()
        font.setPointSize(8)
        font.setFamily("Calibri")
        self.setFont(font)

        self._hover = False
        self._glow_index = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)

    def _animateGlow(self):
        if self._hover:
            if self._glow_index >= 10:
                self._glow_index = 10
                self._anim_timer.stop()
            else:
                self._glow_index += 1

        else:
            if self._glow_index <= 0:
                self._glow_index = 0
                self._anim_timer.stop()
            else:
                self._glow_index -= 1

        sys.solstice.dcc.execute_deferred(self.update)

    #-----------------------------------------------------------------------------------------#

    def enterEvent(self, event):
        super(self.__class__, self).enterEvent(event)

        if not self.isEnabled(): return

        self._hover = True
        self._startAnim()


    def leaveEvent(self, event):
        super(self.__class__, self).leaveEvent(event)

        if not self.isEnabled(): return

        self._hover = False
        self._startAnim()


    def _startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)


class GlowButton(QPushButton, Base):
    _gradient = {NORMAL:{}, DOWN:{}, DISABLED:{}}

    inner_gradient = QLinearGradient(0, 3, 0, 24)
    inner_gradient.setColorAt(0, QColor(53, 57, 60))
    inner_gradient.setColorAt(1, QColor(33, 34, 36))
    _gradient[NORMAL][INNER] = QBrush(inner_gradient)

    outer_gradient = QLinearGradient(0, 2, 0, 25)
    outer_gradient.setColorAt(0, QColor(69, 73, 76))
    outer_gradient.setColorAt(1, QColor(17, 18, 20))
    _gradient[NORMAL][OUTER] = QBrush(outer_gradient)

    inner_gradient_down = QLinearGradient(0, 3, 0, 24)
    inner_gradient_down.setColorAt(0, QColor(20, 21, 23))
    inner_gradient_down.setColorAt(1, QColor(48, 49, 51))
    _gradient[DOWN][INNER] = QBrush(inner_gradient_down)

    outer_gradient_down = QLinearGradient(0, 2, 0, 25)
    outer_gradient_down.setColorAt(0, QColor(36, 37, 39))
    outer_gradient_down.setColorAt(1, QColor(32, 33, 35))
    _gradient[DOWN][OUTER] = QBrush(outer_gradient_down)

    inner_gradient_disabled = QLinearGradient(0, 3, 0, 24)
    inner_gradient_disabled.setColorAt(0, QColor(33, 37, 40))
    inner_gradient_disabled.setColorAt(1, QColor(13, 14, 16))
    _gradient[DISABLED][INNER] = QBrush(inner_gradient_disabled)

    outer_gradient_disabled = QLinearGradient(0, 2, 0, 25)
    outer_gradient_disabled.setColorAt(0, QColor(49, 53, 56))
    outer_gradient_disabled.setColorAt(1, QColor( 9, 10, 12))
    _gradient[DISABLED][OUTER] = QBrush(outer_gradient_disabled)

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        Base.__init__(self)
        self.setFixedHeight(27)

        self._radius = 5

        self.font_metrics = QFontMetrics(self.font())

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option  = QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1

        painter.setRenderHint(QPainter.Antialiasing)

        radius = self._radius

        gradient = self._gradient[NORMAL]
        offset = 0
        if self.isDown():
            gradient = self._gradient[DOWN]
            offset = 1
        elif not self.isEnabled():
            gradient = self._gradient[DISABLED]

        painter.setBrush(self._brush_border)
        painter.setPen(self._pens_border)
        painter.drawRoundedRect(QRect(x+1, y+1, width-1, height-1), radius, radius)

        painter.setPen(self._pens_clear)

        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(QRect(x+2, y+2, width-3, height-3), radius, radius)

        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(QRect(x+3, y+3, width-5, height-5), radius-1, radius-1)

        painter.setBrush(self._brush_clear)

        # draw text
        #
        text = self.text()
        font = self.font()

        text_width  = self.font_metrics.width(text)
        text_height = font.pointSize()

        text_path = QPainterPath()
        text_path.addText((width-text_width)/2, height-((height-text_height)/2) - 1 + offset, font, text)

        glow_index = self._glow_index
        glow_pens  = self._glow_pens

        alignment = (Qt.AlignHCenter | Qt.AlignVCenter)

        if self.isEnabled():
            painter.setPen(self._pens_shadow)
            painter.drawPath(text_path)

            painter.setPen(self._pens_text)
            painter.drawText(x, y+offset, width, height, alignment, text)

            if glow_index > 0:
                for index in range(3):
                    painter.setPen(glow_pens[glow_index][index])
                    painter.drawPath(text_path)

                painter.setPen(glow_pens[glow_index][3])
                painter.drawText(x, y+offset, width, height, alignment, text)

        else:
            painter.setPen(self._pens_shadow_disabled)
            painter.drawPath(text_path)

            painter.setPen(self._pens_text_disabled)
            painter.drawText(x, y+offset, width, height, alignment, text)


class ThinButton(GlowButton):
    def __init__(self, *args, **kwargs):
        GlowButton.__init__(self, *args, **kwargs)
        self.setFixedHeight(22)
        self._radius = 10


class CloseButton(GlowButton):
    def __init__(self, *args, **kwargs):
        GlowButton.__init__(self, *args, **kwargs)
        self._radius = 10
        self.setFixedHeight(20)
        self.setFixedWidth(20)


    def paintEvent(self, event):
        painter = QStylePainter(self)
        option  = QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1

        painter.setRenderHint(QPainter.Antialiasing)

        radius = self._radius

        gradient = self._gradient[NORMAL]
        offset = 0
        if self.isDown():
            gradient = self._gradient[DOWN]
            offset = 1
        elif not self.isEnabled():
            gradient = self._gradient[DISABLED]

        painter.setPen(self._pens_border)
        painter.drawEllipse(x+1, y+1, width-1, height-1)

        painter.setPen(self._pens_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x+2, y+2, width-3, height-2)

        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x+3, y+3, width-5, height-4)

        painter.setBrush(self._brush_clear)

        line_path = QPainterPath()
        line_path.moveTo(x+8, y+8)
        line_path.lineTo(x+12, x+12)
        line_path.moveTo(x+12,  y+8)
        line_path.lineTo( x+8, y+12)

        painter.setPen(self._pens_border)
        painter.drawPath(line_path)

        glow_index = self._glow_index
        glow_pens  = self._glow_pens

        if glow_index > 0:
            for index in range(3):
                painter.setPen(glow_pens[glow_index][index])
                painter.drawPath(line_path)

            painter.setPen(glow_pens[glow_index][3])
            painter.drawPath(line_path)
