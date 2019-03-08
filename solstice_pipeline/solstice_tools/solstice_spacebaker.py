#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_spacebaker.py
# by Tomas Poveda
# Tool to bake animation between space changes
# ______________________________________________________________________
# ==================================================================="""

from functools import partial

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters, solstice_buttons
from solstice_pipeline.solstice_utils import solstice_maya_utils as utils

reload(utils)

SPACE_CONSTRAINTS = {
    'parent': 'Parent Constraint',
    'point': 'Point Constraint',
    'orient': 'Orient Constraint'
}


class SpaceAnimBaker(solstice_windows.Window, object):
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
        target_control_btn = solstice_buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.target_control_delete_btn = solstice_buttons.IconButton(icon_name='delete', icon_hover='delete_hover')
        self.target_control_delete_btn.setFixedSize(QSize(15, 15))
        self.target_control_delete_btn.setParent(self.target_control_line)
        self.target_control_delete_btn.move(245, 2)
        self.target_control_delete_btn.setVisible(False)
        parent_space_group_lbl = QLabel('Parent Group: ')
        self.parent_space_group_line = QLineEdit()
        self.parent_space_group_line.setReadOnly(True)
        self.parent_space_group_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parent_space_group_btn = solstice_buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.parent_space_group_delete_btn = solstice_buttons.IconButton(icon_name='delete', icon_hover='delete_hover')
        self.parent_space_group_delete_btn.setFixedSize(QSize(15, 15))
        self.parent_space_group_delete_btn.setParent(self.parent_space_group_line)
        self.parent_space_group_delete_btn.move(245, 2)
        self.parent_space_group_delete_btn.setVisible(False)
        space_attr_lbl = QLabel('Space Attribute: ')
        self.space_attr_line = QLineEdit()
        self.space_attr_line.setText('space')
        space_constraint_lbl = QLabel('Space Constraint: ')
        button_group = QButtonGroup(self)
        self.parent_cns_btn = solstice_buttons.BaseButton('Parent')
        self.point_cns_btn = solstice_buttons.BaseButton('Point')
        self.orient_cns_btn = solstice_buttons.BaseButton('Orient')
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
        driven_node_lbl = QLabel('Driven Node: ')
        self.driven_line = QLineEdit()
        self.driven_line.setReadOnly(True)
        self.driven_select_btn = solstice_buttons.IconButton(icon_name='cursor', icon_hover='cursor_hover')
        driving_cns_lbl = QLabel('Driving Constraint: ')
        self.driving_line = QLineEdit()
        self.driving_line.setReadOnly(True)
        self.driving_select_btn = solstice_buttons.IconButton(icon_name='cursor', icon_hover='cursor_hover')

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
        space_setup_options.addLayout(solstice_splitters.SplitterLayout(), 4, 0, 1, 4)
        space_setup_options.addWidget(driven_node_lbl, 5, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.driven_line, 5, 1, 1, 1)
        space_setup_options.addWidget(self.driven_select_btn, 5, 2, 1, 1)
        space_setup_options.addWidget(driving_cns_lbl, 6, 0, 1, 1, Qt.AlignRight)
        space_setup_options.addWidget(self.driving_line, 6, 1, 1, 1)
        space_setup_options.addWidget(self.driving_select_btn, 6, 2, 1, 1)

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
        main_spaces_layout.addWidget(solstice_splitters.Splitter('SPACES LIST'))

        buttons_layout = QHBoxLayout()
        main_spaces_layout.addLayout(buttons_layout)
        self.create_space_btn = solstice_buttons.IconButton(icon_name='plus', icon_hover='plus_hover')
        self.refresh_spaces_btn = solstice_buttons.IconButton(icon_name='refresh', icon_hover='refresh_hover')
        self.bake_all_spaces_btn = solstice_buttons.IconButton(icon_name='stamp', icon_hover='stamp_hover')
        self.delete_all_spaces_btn = solstice_buttons.IconButton(icon_name='delete', icon_hover='delete_hover')

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

        self.spaces_layout = QVBoxLayout()
        self.spaces_layout.setAlignment(Qt.AlignTop)
        self.spaces_widget.drop_layout.addLayout(self.spaces_layout)
        main_spaces_layout.addWidget(self.spaces_widget)

        target_control_btn.clicked.connect(partial(self._get_selected, self.target_control_line))
        self.parent_space_group_btn.clicked.connect(self._on_set_parent_group)
        self.target_control_delete_btn.clicked.connect(self._on_reset_control)
        self.parent_space_group_delete_btn.clicked.connect(partial(self._on_clear_line, self.parent_space_group_line))
        self.create_space_btn.clicked.connect(self._on_create_space_switch)
        self.delete_all_spaces_btn.clicked.connect(self._on_clear_spaces)
        self.refresh_spaces_btn.clicked.connect(self._on_create_spaces)

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

    def add_space(self, from_selection=False):
        if from_selection:
            sel = cmds.ls(sl=True)
            if sel:
                for drv in sel:
                    new_space = self._create_space()
                    new_space.target_control_line.setText(drv)

                    try:
                        namespace, name = drv.rsplit(":", 1)
                    except Exception:
                        namespace, name = None, drv
                    new_space.title_line.setText(name)
                return

        self._create_space()

    def _create_space(self):
        new_space = SpaceWidget()
        self.spaces_layout.addWidget(new_space)
        self._space_widgets.append(new_space)
        new_space.closeSpace.connect(self.remove_space)
        new_space.setFixedHeight(0)
        new_space._animate_expand(True)

        return new_space

    def remove_space(self, space_widget):
        space_widget.deleteSpace.connect(self._on_delete_space_switch)
        self._space_widgets.remove(space_widget)
        space_widget._animate_expand(False)

    def clear_spaces(self):
        for w in reversed(self._space_widgets):
            self.remove_space(w)

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
            self.clear_spaces()
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
        if sel:
            self.add_space(from_selection=True)
        else:
            self.add_space(from_selection=False)
        self._update_ui()

    def _on_clear_spaces(self):
        self.clear_spaces()
        self._update_ui()

    def _on_delete_space_switch(self, space_widget):
        self.spaces_layout.removeWidget(space_widget)
        space_widget._animation = None
        space_widget.deleteLater()

    def _on_clear_line(self, line_widget):
        line_widget.setText('')
        self._update_ui()

    def _on_reset_control(self):
        self._on_clear_line(self.target_control_line)
        self.parent_space_group_line.setText('')
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
        if utils.attribute_exists(self.switch_control, 'SP_drivenNode'):
            driven_node = cmds.listConnections(self.switch_control+'.SP_drivenNode')
        cns = None
        if driven_node:
            cns = cmds.listConnections(driven_node[0]+'.SP_spaceConstraint')
        if cns:
            QMessageBox.warning(self, 'Warning', '{} already ahs a space group: {}'.format(utils.get_short_name(self.switch_control), driven_node[0]))
            return

        offset_grp = cmds.group(n='{}_space_grp'.format(utils.get_short_name(self.switch_control)), world=True, empty=True)
        cmds.delete(cmds.pointConstraint(self.switch_control, offset_grp)[0])
        driven_node_rot = cmds.xform(self.switch_control, query=True, rotation=True, worldSpace=True)
        driven_node_scale = cmds.xform(self.switch_control, query=True, scale=True, worldSpace=True)
        cmds.xform(offset_grp, rotation=driven_node_rot, worldSpace=True)
        cmds.xform(offset_grp, scale=driven_node_scale, worldSpace=True)
        switch_control = utils.get_mdag_path(self.switch_control)
        control_parent = cmds.listRelatives(self.switch_control, parent=True)
        if control_parent:
            cmds.parent(offset_grp, control_parent[0])
        cmds.parent(self.switch_control, offset_grp)
        cmds.select(switch_control.fullPathName())
        self.driven_line.setText(offset_grp)

        return offset_grp

    def _on_set_parent_group(self):
        self._get_selected(self.parent_space_group_line)
        if self.switch_control == self.parent_group:
            sp.logger.warning('Parent Group and Switch Control cannot be the same object!')
            self.parent_space_group_line.setText('')
        self.parent_space_group_line.setStyleSheet('')
        self._update_ui()

    @utils.maya_undo
    def _on_create_spaces(self):
        if not self._space_widgets:
            return

        if self.parent_group == self.switch_control:
            sp.logger.warning('Parent Group and Switch Control cannot be the same object!')
            return

        if self.parent_group and cmds.objExists(self.parent_group):
            print('Creating space setup ...')
        else:
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

    def __init__(self, parent=None):
        super(SpaceWidget, self).__init__(parent)


        self._animation = None
        self._slider_down = False
        self._items = dict()
        self._drag_start_position = None
        self._old_x = self._old_y = 0
        self._mouse_click_x = self._mouse_click_y = 0
        
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
        self.close_btn = solstice_buttons.CloseButton('X')
        self.bake_btn = solstice_buttons.IconButton(icon_name='stamp', icon_hover='stamp_hover')
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

        self.do_bake_btn = solstice_buttons.BaseButton('B A K E')
        bake_layout.addLayout(solstice_splitters.SplitterLayout())
        bake_layout.addWidget(self.do_bake_btn)

        title_layout = QGridLayout()
        title_lbl = QLabel('Space Name: ')
        self.title_line = QLineEdit()
        self.title_line.setPlaceholderText('Input name of the space')
        target_control_lbl = QLabel('Target Control: ')
        self.target_control_line = QLineEdit()
        self.target_control_line.setPlaceholderText('Input name of the control')
        self.target_control_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        target_control_btn = solstice_buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        self.target_control_select_btn = solstice_buttons.IconButton(icon_name='cursor', icon_hover='cursor_hover')
        title_layout.addWidget(title_lbl, 0, 0, 1, 1, Qt.AlignRight)
        title_layout.addWidget(self.title_line, 0, 1, 1, 1)
        title_layout.addWidget(target_control_lbl, 1, 0, 1, 1, Qt.AlignRight)
        title_layout.addWidget(self.target_control_line, 1, 1, 1, 1)
        title_layout.addWidget(target_control_btn, 1, 2, 1, 1)
        title_layout.addWidget(self.target_control_select_btn, 1, 3, 1, 1)

        space_layout.addLayout(title_layout)
        space_layout.addLayout(close_layout)
        self.space_separator = solstice_splitters.get_horizontal_separator_widget()
        self.space_separator.setVisible(False)
        space_layout.addWidget(self.space_separator)
        space_layout.addWidget(self.bake_widget)

        target_control_btn.clicked.connect(partial(self._get_selected, self.target_control_line))
        self.bake_btn.toggled.connect(self._on_open_bake)
        self.close_btn.clicked.connect(self.close_widget)

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

    def _on_open_bake(self, toggle):
        self.bake_widget.setVisible(toggle)
        self.close_btn.repaint()


def run():
    win = SpaceAnimBaker().show()
    return win
