#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful utilities functions for PySide
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import re
import sys
import subprocess

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *
from Qt import QtCompat
try:
    import shiboken
    from shiboken import wrapInstance
except ImportError:
    try:
        import shiboken2 as shiboken
        from shiboken2 import wrapInstance
    except Exception:
        pass

import solstice.pipeline as sp
from solstice.pipeline.utils import pythonutils, browserutils


def ui_loader(ui_file, widget=None):
    ui = QtCompat.loadUi(ui_file)
    if widget:
        for member in dir(ui):
            if not member.startswith('__') and member is not 'staticMetaObject':
                setattr(widget, member, getattr(ui, member))

    return ui


def wrapinstance(ptr, base=None):
    if ptr is None:
        return None

    return shiboken.wrapInstance(long(ptr), base)


def dock_solstice_widget(widget_class):

    if sp.is_maya():
        import maya.cmds as cmds
        import maya.OpenMayaUI as OpenMayaUI
        from solstice.pipeline.utils import mayautils

        workspace_control = widget_class.__name__ + '_workspace_control'

        try:
            cmds.deleteUI(workspace_control)
            sys.solstice.logger.debug('Removing workspace {0}'.format(workspace_control))
        except:
            pass

        if mayautils.get_maya_api_version() >= 201700:

            main_control = cmds.workspaceControl(workspace_control, ttc=["AttributeEditor", -1], iw=425, mw=True, wp='preferred', label='{0} - {1}'.format(widget_class.title, widget_class.version))
            control_widget = OpenMayaUI.MQtUtil.findControl(workspace_control)
            control_wrap = wrapInstance(long(control_widget), QWidget)
            control_wrap.setAttribute(Qt.WA_DeleteOnClose)
            win = widget_class(name=workspace_control, parent=control_wrap, layout=control_wrap.layout())
            cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))
        else:
            pass

        return win


def ui_loader(ui_file, widget=None):
    """
    Loads GUI from .ui file
    :param ui_file: str, path to the UI file
    :param widget: parent widget
    """

    ui = QtCompat.loadUi(ui_file)
    if not widget:
        return ui
    else:
        for member in dir(ui):
            if not member.startswith('__') and member is not 'staticMetaObject':
                setattr(widget, member, getattr(ui, member))
        return ui


def create_python_qrc_file(qrc_file, py_file):

    """
    Creates a Python file from a QRC file
    :param src_file: str, QRC file name
    """

    if not os.path.isfile(qrc_file):
        return

    pyside_rcc_exe_path = 'C:\\Python27\\Lib\\site-packages\\PySide\\pyside-rcc.exe'
    # pyside_rcc_exe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'externals', 'pyside-rcc', 'pyside-rcc.exe')
    if not os.path.isfile(pyside_rcc_exe_path):
        print('RCC_EXE_PATH_DOES_NOT_EXISTS!!!!!!!!!!!!!')
    #     pyside_rcc_exe_path = filedialogs.OpenFileDialog(
    #         title='Select pyside-rcc.exe location folder ...',
    #     )
    #     pyside_rcc_exe_path.set_directory('C:\\Python27\\Lib\\site-packages\\PySide')
    #     pyside_rcc_exe_path.set_filters('EXE files (*.exe)')
    #     pyside_rcc_exe_path = pyside_rcc_exe_path.exec_()
    # if not os.path.isfile(pyside_rcc_exe_path):
        return
    # py_out = os.path.splitext(os.path.basename(src_file))[0]+'.py'
    # py_out_path = os.path.join(os.path.dirname(src_file), py_out)
    try:
        subprocess.check_output('"{0}" -o "{1}" "{2}"'.format(pyside_rcc_exe_path, py_file, qrc_file))
    except subprocess.CalledProcessError as e:
        raise RuntimeError('command {0} returned with error (code: {1}): {2}'.format(e.cmd, e.returncode, e.output))
    if not os.path.isfile(py_file):
        return
    pythonutils.replace(py_file, "from PySide import QtCore", "from Qt import QtCore")


def create_qrc_file(src_paths, dst_file):

    def tree(top='.',
             filters=None,
             output_prefix=None,
             max_level=4,
             followlinks=False,
             top_info=False,
             report=True):
        # The Element of filters should be a callable object or
        # is a byte array object of regular expression pattern.
        topdown = True
        total_directories = 0
        total_files = 0

        top_fullpath = os.path.realpath(top)
        top_par_fullpath_prefix = os.path.dirname(top_fullpath)

        if top_info:
            lines = top_fullpath
        else:
            lines = ""

        if filters is None:
            _default_filter = lambda x: not x.startswith(".")
            filters = [_default_filter]

        for root, dirs, files in os.walk(top=top_fullpath, topdown=topdown, followlinks=followlinks):
            assert root != dirs

            if max_level is not None:
                cur_dir = pythonutils.strips(root, top_fullpath)
                path_levels = pythonutils.strips(cur_dir, "/").count("/")
                if path_levels > max_level:
                    continue

            total_directories += len(dirs)
            total_files += len(files)

            for filename in files:
                for _filter in filters:
                    if callable(_filter):
                        if not _filter(filename):
                            total_files -= 1
                            continue
                    elif not re.search(_filter, filename, re.UNICODE):
                        total_files -= 1
                        continue

                    if output_prefix is None:
                        cur_file_fullpath = os.path.join(top_par_fullpath_prefix, root, filename)
                    else:
                        buf = pythonutils.strips(os.path.join(root, filename), top_fullpath)
                        if output_prefix != "''":
                            cur_file_fullpath = os.path.join(output_prefix, buf.strip('/'))
                        else:
                            cur_file_fullpath = buf

                    lines = "%s%s%s" % (lines, os.linesep, cur_file_fullpath)

        lines = lines.lstrip(os.linesep)

        if report:
            report = "%d directories, %d files" % (total_directories, total_files)
            lines = "%s%s%s" % (lines, os.linesep * 2, report)

        return lines

    def scan_files(src_path="."):
        filters = ['.(png|jpg|gif)$']
        output_prefix = './'
        report = False
        lines = tree(src_path, filters=filters, output_prefix=output_prefix, report=report)

        lines = lines.split('\n')
        if "" in lines:
            lines.remove("")

        return lines

    def create_qrc_body(src_path, root_res_path, use_alias=True):

        res_folder_files = browserutils.get_absolute_file_paths(src_path)
        lines = [os.path.relpath(f, root_res_path) for f in res_folder_files]

        if use_alias:
            buf = ['\t\t<file alias="{0}">{1}</file>\n'.format(os.path.splitext(os.path.basename(i))[0].lower().replace('-', '_'), i).replace('\\', '/') for i in lines]
        else:
            buf = ["\t\t<file>{0}</file>\n".format(i).replace('\\', '/') for i in lines]
        buf = "".join(buf)
        # buf = QRC_TPL % buf
        return buf

    # Clean existing resources files and append initial resources header text
    if dst_file:
        parent = os.path.dirname(dst_file)
        if not os.path.exists(parent):
            os.makedirs(parent)
        f = file(dst_file, "w")
        f.write('<RCC>\n')

        try:
            for res_folder in src_paths:
                res_path = os.path.dirname(res_folder)
                start_header = '\t<qresource prefix="{0}">\n'.format(os.path.basename(res_folder))
                qrc_body = create_qrc_body(res_folder, res_path)
                end_header = '\t</qresource>\n'
                res_text = start_header + qrc_body + end_header

                f = file(dst_file, 'a')
                f.write(res_text)

            # Write end header
            f = file(dst_file, "a")
            f.write('</RCC>')
            f.close()
        except RuntimeError:
            f.close()


def safe_delete_later(widget):
    """
    calls the deleteLater method on the given widget, but only
    in the necessary Qt environment
    :param widget: QWidget
    """

    from Qt import __binding__
    if __binding__ in ('PySide', 'PyQt4'):
        widget.deleteLater()


def show_question(parent, title, question):
    """
    Show a question QMessageBox with the given question text
    :param question: str
    :return:
    """

    flags = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    return QMessageBox.question(parent, title, question, flags)


def show_error(parent, title, error):
    """
    Show a error QMessageBox with the given error
    :return:
    """

    return QMessageBox.critical(parent, title, error)


def show_info(parent, title, info):
    """
    Show a info QMessageBox with the given info
    :return:
    """

    return QMessageBox.information(parent, title, info)


def clear_layout_widgets(layout):
    """
    Removes all the widgets added in the given layout
    :param layout: QLayout
    """

    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item:
            w = item.widget()
            if w:
                w.setParent(None)


def image_to_clipboard(path):
    """
    Copies the image at path to the system's global clipboard
    :param path: str
    """

    image = QImage(path)
    clipboard = QApplication.clipboard()
    clipboard.setImage(image, mode=QClipboard.Clipboard)


def get_horizontal_separator():
    v_div_w = QWidget()
    v_div_l = QVBoxLayout()
    v_div_l.setAlignment(Qt.AlignLeft)
    v_div_l.setContentsMargins(0, 0, 0, 0)
    v_div_l.setSpacing(0)
    v_div_w.setLayout(v_div_l)
    v_div = QFrame()
    v_div.setMinimumHeight(30)
    v_div.setFrameShape(QFrame.VLine)
    v_div.setFrameShadow(QFrame.Sunken)
    v_div_l.addWidget(v_div)
    return v_div_w


def dock_window(window_class, min_width=300):

    if sp.is_maya():
        import maya.cmds as cmds
        import maya.OpenMayaUI as OpenMayaUI

        try:
            cmds.deleteUI(window_class.name)
        except Exception:
            pass

        main_control = cmds.workspaceControl(window_class.name, ttc=["AttributeEditor", -1], iw=min_width, mw=True, wp='preferred', label=window_class.title)

        control_widget = OpenMayaUI.MQtUtil.findControl(window_class.name)
        control_wrap = wrapInstance(long(control_widget), QWidget)
        control_wrap.setAttribute(Qt.WA_DeleteOnClose)
        win = window_class(control_wrap)

        cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

        try:
            return win.run()
        except Exception:
            return win.show()


def center_widget_on_screen(widget):
    """
    Center a given QWidget on the active screen
    :param widget: QWidget
    """

    frame_geo = widget.frameGeometry()
    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    center_point = QApplication.desktop().screenGeometry(screen).center()
    frame_geo.moveCenter(center_point)
    widget.move(frame_geo.topLeft())


def selection_modifiers():
    """
    Returns a dictionary of the current key modifiers
    :return: dict
    """

    result = {'add': False, 'deselect': False}
    modifiers = QApplication.keyboardModifiers()
    if modifiers == Qt.ShiftModifier:
        result['deselect'] = True
    elif modifiers == Qt.ControlModifier:
        result['add'] = True

    return result


def is_modifier():
    """
    Returns True if either the alt key or control key is down
    :return: bool
    """

    return is_alt_modifier() or is_control_modifier()


def is_alt_modifier():
    """
    Returns True if the alt key is down
    :return: bool
    """

    modifiers = QApplication.keyboardModifiers()
    return modifiers == Qt.AltModifier


def is_control_modifier():
    """
    Returns True if the control key is down
    :return: bool
    """

    modifiers = QApplication.keyboardModifiers()
    return modifiers == Qt.ControlModifier


def is_shift_modifier():
    """
    Returns True if the shift key is down
    :return: bool
    """

    modifiers = QApplication.keyboardModifiers()
    return modifiers == Qt.ShiftModifier
