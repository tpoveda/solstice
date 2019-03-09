#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Maya
# ______________________________________________________________________
# ==================================================================="""

import os
import glob
import stat
import shutil
import functools
import contextlib
from collections import OrderedDict

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
try:
    import shiboken2 as shiboken
    from shiboken2 import wrapInstance
except ImportError:
    import shiboken as shiboken
    from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya

import solstice_pipeline as sp
from solstice_utils import solstice_python_utils as python

_DPI_SCALE = 1.0 if not hasattr(cmds, "mayaDpiSetting") else cmds.mayaDpiSetting(query=True, realScaleValue=True)


class MessageType(object):
    OK = 0
    WARNING = 1
    ERROR = 2


class MCallbackIdWrapper(object):
    """
    Wrapper class to handle cleaning up of MCallbackIds from registered MMessages
    """

    def __init__(self, callback_id):
        super(MCallbackIdWrapper, self).__init__()
        self.callback_id = callback_id
        sp.logger.debug('Adding Callback: %s' % self.callback_id)

    def __del__(self):
        try:
            OpenMaya.MDGMessage.removeCallback(self.callback_id)
        except Exception:
            pass
        try:
            OpenMaya.MMessage.removeCallback(self.callback_id)
        except Exception:
            pass
        sp.logger.debug('Removing Callback: %s' % self.callback_id)

    def __repr__(self):
        return 'MCallbackIdWrapper(%r)' % self.callback_id


def maya_undo(fn):
    """
    Undo function decorator for Maya function calls
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            return fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)

    return lambda *args, **kwargs: utils.executeDeferred(wrapper, *args, **kwargs)


@contextlib.contextmanager
def maya_no_undo():
    """
    Disable undo functionality during the context
    """

    try:
        cmds.undoInfo(stateWithoutFlush=False)
        yield
    finally:
        cmds.undoInfo(stateWithoutFlush=True)


def get_maya_api_version():
    """
    Returns Maya API version
    :return: int
    """

    return int(cmds.about(api=True))


def get_maya_window():
    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QWidget)

    return None


def get_maya_commands():
    """
    Returns a list with all commands available in Maya
    :return: list<str>
    """

    def search_menu(menu):
        filter_list = [
            'Attributes',
             'Hotbox',
             "What's New",
             'Help',
             'Tutorials',
             'Maya Scripting Reference',
             'Recent Commands',
             'Recent Projects',
             'Recent Files',
             'Saved Layouts',
             'Maya Communities',
             'Maya Services and Support',
             'Maya Resources and Tools',
             'Speak Back',
             'Try Other Autodesk Products'
        ]

        for item in menu.children():
            try:
                parent = item.parentWidget()
                value = True
                for content in filter_list:
                    if content in parent.title():
                        value = False
            except Exception:
                pass

            if value:
                if type(item) == QMenu:
                    parent = item.parentWidget()
                    if type(parent) == QMenuBar:
                        parent = 'TOPMENU'
                    else:
                        parent = parent.title()
                    item.aboutToShow.emit()
                    search_menu(item)
                elif type(item) == QWidgetAction:
                    name = item.text()
                    if name and not item.isSeparator() and not item.menu():
                        try:
                            parent = item.parentWidget()
                            item_name = item.text()
                            if any([x in item_name for x in ('Option Box', 'Options', 'DialogItem', 'Dialog', 'ItemDialog', 'Item')]):
                                commands_list[-1]['altCommand'] = item
                            else:
                                item_info = item.toolTip()
                                category = parent.title()
                                menu_item = OpenMayaUI.MQtUtil.fullName(long(shiboken.getCppPointer(item)[0]))
                                item_cmd = item
                                item_icon_path = ':' + cmds.menuItem(menu_item, query=True, i=True).split('.')[0]
                                tags = category.lower() + ',MAYA'
                                if item_icon_path == ':':
                                    item_icon_path = 'mayaDefault@2x'
                                exists = False
                                for cmd in commands_list:
                                    if cmd['name'] == item_name:
                                        if cmd['info'] == item_info:
                                            exists = True

                                if not exists:
                                    if item_cmd != 'None':
                                        cmd = {'name': item_name,
                                               'command': item_cmd,
                                               'tags': tags,
                                               'icon': item_icon_path,
                                               'category': 'Maya/' + category}
                                        commands_list.append(cmd)
                        except Exception:
                            pass

            return commands_list

    commands_list = list()
    maya_window = get_maya_window()
    main_menu_bar = None
    for obj in maya_window.children():
        if type(obj) == QMenuBar:
            main_menu_bar = obj

    if main_menu_bar is not None:
        commands_list = search_menu(main_menu_bar)
        return commands_list
    else:
        return


def get_main_shelf():
    """
    Returns the Maya main shelf
    """

    return mel.eval('$tempVar = $gShelfTopLevel')


def get_main_window():
    """
    Returns Maya main window through MEL
    """

    return mel.eval("$tempVar = $gMainWindow")


def viewport_message(text, header='SOLSTICE', mode=MessageType.OK):
    """
    Shows a message in the Maya viewport
    :param text: str, text to show in Maya viewport
    """

    fade_time = len(text) * 110
    if fade_time > 10000:
        fade_time = 10000
    elif fade_time < 2000:
        fade_time = 4000

    if mode == MessageType.OK:
        cmds.inViewMessage(amg=u'<span style="color:#21C4F5;">{}:</span> {}'.format(header, text), pos='topRight', fade=True, fadeStayTime=fade_time)
    elif mode == MessageType.WARNING:
        cmds.inViewMessage(amg=u'<span style="color:#FFB600;">{}:</span> {}'.format(header, text), pos='topRight', fade=True, fadeStayTime=fade_time)
    elif mode == MessageType.ERROR:
        cmds.inViewMessage(amg=u'<span style="color:#21C4F5;">{}:</span> {}'.format(header, text), pos='topRight', fade=True, fadeStayTime=fade_time)
    else:
        cmds.inViewMessage(amg=u'<h1>{}:</h1> {}'.format(header, text), pos='topRight', fade=True, fadeStayTime=fade_time)


def force_stack_trace_on():
    """
    Forces enabling Maya Stack Trace
    """

    try:
        mel.eval('stackTrace -state on')
        cmds.optionVar(intValue=('stackTraceIsOn', True))
        what_is = mel.eval('whatIs "$gLastFocusedCommandReporter"')
        if what_is != 'Unknown':
            last_focused_command_reporter = mel.eval('$tmp = $gLastFocusedCommandReporter')
            if last_focused_command_reporter and last_focused_command_reporter != '':
                mel.eval('synchronizeScriptEditorOption 1 $stackTraceMenuItemSuffix')
    except RuntimeError:
        pass


def pass_message_to_main_thread(message_handler, *args):
    """
    Executes teh message_handler with the given list of arguments in Maya's main thread
    during the next idle event
    :param message_handler: variant, str || function, string containing Python code or callable function
    """

    utils.executeInMainThreadWithResult(message_handler, *args)


def get_upstream_nodes(node):
    """
    Return a list with all upstream nodes of the given Maya node
    :param node: str, name of the node
    :return: lsitzstr>
    """

    upstream_nodes = list()
    upstream_nodes.append(node)
    incoming_nodes = cmds.listConnections(node, source=True, destination=False)
    if incoming_nodes:
        for n in incoming_nodes:
            upstream_nodes.extend(get_upstream_nodes(n))
        return upstream_nodes
    else:
        return upstream_nodes


def delete_all_incoming_nodes(node):
    """
    Delete all incoming nodes from the given Maya node
    :param node: str
    :param attrs: list<str>
    """

    upstream_nodes = list()
    upstream_nodes_clean = list()
    connections = cmds.listConnections(node, source=True, destination=False)
    if connections:
        for node in connections:
            upstream_nodes.extend(get_upstream_nodes(node))

        for node in upstream_nodes:
            if node not in upstream_nodes_clean:
                upstream_nodes_clean.append(node)

        for node in upstream_nodes_clean:
            cmds.delete(node)


def remove_callback(callback_id):
    try:
        OpenMaya.MEventMessage.removeCallback(callback_id)
        return
    except Exception:
        pass
    try:
        OpenMaya.MDGMessage.removeCallback(callback_id)
        return
    except Exception:
        pass


def dpi_scale(value):
    return _DPI_SCALE * value


def shelf_exists(shelf_name):
    """
    Returns True if the given shelf name already exists or False otherwise
    :param shelf_name: str, shelf name
    :return: bool
    """

    return cmds.shelfLayout(shelf_name, exists=True)


def delete_shelf(shelf_name):
    """
    Deletes given shelf by name, if exists
    :param shelf_name: str, shelf name
    """

    if shelf_exists(shelf_name=shelf_name):
        cmds.deleteUI(shelf_name)


def create_shelf(name, parent_layout='ShelfLayout'):
    """
    Creates a new shelf parented on the given layout
    :param name: str, name of the shelf to create
    :param parent_layout: name of the parent shelf layout
    :return: str
    """

    return cmds.shelfLayout(name, parent=parent_layout)


def get_top_maya_shelf():
    return mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")


def get_all_shelves():
    return cmds.tabLayout(get_top_maya_shelf(), query=True, ca=True)


def get_current_shelf():
    return cmds.tabLayout(get_top_maya_shelf(), query=True, st=True)


def main_menu():
    """
    Returns Maya main menu
    """

    return mel.eval('$tmp=$gMainWindow')


def get_menus():
    """
    Return a list with all Maya menus
    :return: list<str>
    """

    return cmds.lsUI(menus=True)


def remove_menu(menu_name):
    """
    Removes, if exists, a menu of Max
    :param menu_name: str, menu name
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            cmds.deleteUI(m, menu=True)


def check_menu_exists(menu_name):
    """
    Returns True if a menu with the given name already exists
    :param menu_name: str, menu name
    :return: bol
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            return True

    return False


def find_menu(menu_name):
    """
    Returns Menu instance by the given name
    :param menu_name: str, menu of the name to search for
    :return: nativeMenu
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            return m

    return None


def get_plugin_shapes():
    """
    Return all available plugin shapes
    :return: dict, plugin shapes by their menu label and script name
    """

    filters = cmds.pluginDisplayFilter(query=True, listFilters=True)
    labels = [cmds.pluginDisplayFilter(f, query=True, label=True) for f in filters]
    return OrderedDict(zip(labels, filters))


def get_current_scene_name():
    """
    Returns the name of the current scene opened in Maya
    :return: str
    """

    scene_path = cmds.file(query=True, sceneName=True)
    if scene_path:
        return os.path.splitext(os.path.basename(scene_path))[0]

    return None


def get_current_camera():
    """
    Returns the currently active camera
    :return: str, name of the active camera transform
    """

    panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=panel) == 'modelPanel':
        cam = cmds.modelEditor(panel, query=True, camera=True)
        if cam:
            if cmds.nodeType(cam) == 'transform':
                return cam
            elif cmds.objectType(cam, isAType='shape'):
                parent = cmds.listRelatives(cam, parent=True, fullPath=True)
                if parent:
                    return parent[0]

    cam_shapes = cmds.ls(sl=True, type='camera')
    if cam_shapes:
        return cmds.listRelatives(cam_shapes, parent=True, fullPath=True)[0]

    transforms = cmds.ls(sl=True, type='transform')
    if transforms:
        cam_shapes = cmds.listRelatives(transforms, shapes=True, type='camera')
        if cam_shapes:
            return cmds.listRelatives(cam_shapes, parent=True, fullPath=True)[0]


def get_active_editor():
    """
    Returns the active editor panel of Maya
    """

    cmds.currentTime(cmds.currentTime(query=True))
    panel = cmds.playblast(activeEditor=True)
    return panel.split('|')[-1]


def get_current_frame():
    """
    Return current Maya frame set in time slier
    :return: int
    """

    return cmds.currentTime(query=True)


def get_time_slider_range(highlighted=True, within_highlighted=True, highlighted_only=False):
    """
    Return the time range from Maya time slider
    :param highlighted: bool, If True it will return a selected frame range (if there is any selection of more than one frame) else
    it will return min and max playblack time
    :param within_highlighted: bool, Maya returns the highlighted range end as a plus one value by default. If True, this is fixed by
    removing one from the last frame number
    :param highlighted_only: bool, If True, it wil return only highlighted frame range
    :return: list<float, float>, [start_frame, end_frame]
    """

    if highlighted is True:
        playback_slider = mel.eval("global string $gPlayBackSlider; " "$gPlayBackSlider = $gPlayBackSlider;")
        if cmds.timeControl(playback_slider, query=True, rangeVisible=True):
            highlighted_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            if within_highlighted:
                highlighted_range[-1] -= 1
            return highlighted_range

    if not highlighted_only:
        return [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)]


def get_current_render_layer():
    """
    Returns the current Maya render layer
    :return: str
    """

    return cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)


def get_playblast_formats():
    """
    Returns all formats available for Maya playblast
    :return: list<str>
    """

    cmds.currentTime(cmds.currentTime(query=True))
    return cmds.playblast(query=True, format=True)


def get_playblast_compressions(format='avi'):
    """
    Returns playblast compression for the given format
    :param format: str, format to check compressions for
    :return: list<str>
    """

    cmds.currentTime(cmds.currentTime(query=True))
    return mel.eval('playblast -format "{0}" -query -compression'.format(format))


def fix_playblast_output_path(file_path):
    """
    Workaround a bug in maya.cmds.playblast to return a correct playblast
    When the `viewer` argument is set to False and maya.cmds.playblast does not
    automatically open the playblasted file the returned filepath does not have
    the file's extension added correctly.
    To workaround this we just glob.glob() for any file extensions and assume
    the latest modified file is the correct file and return it.
    :param file_path: str
    :return: str
    """

    if file_path is None:
        sp.logger.warning('Playblast did not result in output path. Maybe it was interrupted!')
        return

    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        parts = filename.split('.')
        if len(parts) == 3:
            query = os.path.join(directory, '{}.*.{}'.format(parts[0], parts[-1]))
            files = glob.glob(query)
        else:
            files = glob.glob('{}.*'.format(file_path))

        if not files:
            raise RuntimeError('Could not find playblast from "{}"'.format(file_path))

        file_path = max(files, key=os.path.getmtime)

    return file_path


def get_is_standalone():
    return not hasattr(cmds, 'about') or cmds.about(batch=True)


def get_active_panel():
    """
    Returns the current active modelPanel
    :return: str, name of the model panel or raises an error if no active modelPanel iis found
    """

    panel = cmds.getPanel(withFocus=True)
    if not panel or 'modelPanel' not in panel:
        raise RuntimeError('No active model panel found!')

    return panel


def get_available_screen_size():
    """
    Returns available screen size without space occupied by task bar
    """

    if get_is_standalone():
        return [0, 0]

    rect = QDesktopWidget().screenGeometry(-1)
    return [rect.width(), rect.height()]


def file_has_student_line(filename):
    """
    Returns True if the given Maya file has a student license on it
    :param filename: str
    :return: bool
    """

    if not os.path.exists(filename):
        sp.logger.error('File "{}" does not exists!'.format(filename))
        return False

    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if 'createNode' in line:
            return False
        if 'fileInfo' in line and 'student' in line:
            return True

    return False


def clean_student_line(filename=None):
    """
    Clean the student line from the given Maya file name
    :param filename: str
    """

    changed = False

    if filename is None:
        filename = cmds.file(q=True, sn=True)

    if not os.path.exists(filename):
        sp.logger.error('File "{}" does not exists!'.format(filename))
        return False

    if not file_has_student_line(filename=filename):
        sp.logger.info('File is already cleaned: no student line found!')
        return False

    with open(filename, 'r') as f:
        lines = f.readlines()
    step = len(lines)/4

    no_student_filename = filename.replace('.ma', '.no_student.ma')
    with open(no_student_filename, 'w') as f:
        step_count = 0
        for line in lines:
            step_count += 1
            if 'fileInfo' in line:
                if 'student' in line:
                    changed = True
                    continue
            f.write(line)
            if step_count > step:
                sp.logger.debug('Updating File: {}% ...'.format(100/(len(lines)/step_count)))
                step += step

    if changed:
        os.chmod(filename, stat.S_IWUSR | stat.S_IREAD)
        shutil.copy2(no_student_filename, filename)
        os.remove(no_student_filename)
        sp.logger.info('Student file cleaned successfully!')

    return changed


@contextlib.contextmanager
def create_independent_panel(width, height, off_screen=False):
    """
    Creates a Maya panel window without decorations
    :param width: int, width of panel
    :param height: int, height of panel
    :param off_screen: bool
    with create_independent_panel(800, 600):
        cmds.capture()
    """

    screen_width, screen_height = get_available_screen_size()
    top_left = [int((screen_height-height)*0.5), int((screen_width-width)*0.5)]
    window = cmds.window(width=width, height=height, topLeftCorner=top_left, menuBarVisible=False, titleBar=False, visible=not off_screen)
    cmds.paneLayout()
    panel = cmds.modelPanel(menuBarVisible=False, label='CapturePanel')
    # Hide icons under panel menus
    bar_layout = cmds.modelPanel(panel, query=True, barLayout=True)
    cmds.frameLayout(bar_layout, edit=True, collapse=True)
    if not off_screen:
        cmds.showWindow(window)

    # Set the modelEditor of the modelPanel as the active view, so it takes the playback focus
    editor = cmds.modelPanel(panel, query=True, modelEditor=True)
    cmds.modelEditor(editor, edit=True, activeView=True)
    cmds.refresh(force=True)

    try:
        yield panel
    finally:
        cmds.deleteUI(panel, panel=True)
        cmds.deleteUI(window)


@contextlib.contextmanager
def disable_inview_messages():
    """
    Disable in-view help messages during the context
    """

    original = cmds.optionVar(query='inViewMessageEnable')
    cmds.optionVar(iv=('inViewMessageEnable', 0))
    try:
        yield
    finally:
        cmds.optionVar(iv=('inViewMessageEnable', original))


@contextlib.contextmanager
def maintain_camera_on_panel(panel, camera):
    """
    Tries to maintain given camera on given panel during the context
    :param panel: str, name of the panel to focus camera on
    :param camera: str, name of the camera we want to focus
    """

    state = dict()
    if not get_is_standalone():
        cmds.lookThru(panel, camera)
    else:
        state = dict((camera, cmds.getAttr(camera + '.rnd')) for camera in cmds.ls(type='camera'))
        cmds.setAttr(camera + '.rnd', True)
    try:
        yield
    finally:
        for camera, renderable in state.items():
            cmds.setAttr(camera + '.rnd', renderable)


@contextlib.contextmanager
def reset_time():
    """
    The time is reset once the context is finished
    """

    current_time = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(current_time)


@contextlib.contextmanager
def isolated_nodes(nodes, panel):
    """
    Context manager used for isolating given nodes in  given panel
    """

    if nodes is not None:
        cmds.isolateSelect(panel, state=True)
        for obj in nodes:
            cmds.isolateSelect(panel, addDagObject=obj)
    yield


def delete_nodes_of_type(node_type):
    """
    Delete all nodes of the given type
    :param node_type: varaiant, list<str> || str, name of node type (eg: hyperView, etc) or list of names
    """

    node_type = python.force_list(node_type)
    deleted_nodes = list()

    for node_type_name in node_type:
        nodes_to_delete = cmds.ls(type=node_type_name)
        for n in nodes_to_delete:
            if n == 'hyperGraphLayout':
                continue
            if not cmds.objExists(n):
                continue

            cmds.lockNode(n, lock=False)
            cmds.delete(n)
            deleted_nodes.append(n)

    return deleted_nodes


def delete_unknown_nodes():
    """
    Find all unknown nodes and delete them
    """

    unknown = cmds.ls(type='unknown')
    deleted = list()
    for n in unknown:
        if cmds.objExists(n):
            cmds.lockNode(n, lock=False)
            cmds.delete(n)
            deleted.append(n)

    print('Deleted uknowns: {}'.format(deleted))


def delete_turtle_nodes():
    """
    Find all turtle nodes in a scene and delete them
    """

    plugin_list = cmds.pluginInfo(query=True, pluginsInUse=True)
    turtle_nodes = list()
    if plugin_list:
        for plugin in plugin_list:
            if plugin[0] == 'Turtle':
                turtle_types = ['ilrBakeLayer',
                                'ilrBakeLayerManager',
                                'ilrOptionsNode',
                                'ilrUIOptionsNode']
                turtle_nodes = delete_nodes_of_type(turtle_types)
                break

    try:
        cmds.lockNode('TurtleDefaultBakeLayer', lock=False)
        cmds.delete('TurtleDefaultBakeLayer')
        turtle_nodes.append('TurtleDefaultBakeLayer')
    except Exception:
        pass

    print('Removed Turtle nodes: {}'.format(turtle_nodes))


def delete_unused_plugins():
    """
    Removes all nodes in the scene that belongs to unused plugins (plugins that are not loaded)
    """

    # This functionality is not available in old Maya versions
    list_cmds = dir(cmds)
    if not 'unknownPlugin' in list_cmds:
        return

    unknown_nodes = cmds.ls(type='unknown')
    if unknown_nodes:
        return

    unused = list()
    unknown_plugins = cmds.unknownPlugin(query=True, list=True)
    if unknown_plugins:
        for p in unknown_plugins:
            try:
                cmds.unknownPlugin(p, remove=True)
            except Exception:
                continue
            unused.append(p)

    print('Removed unused plugins: {}'.format(unused))


def clean_scene():
    """
    Function that cleans current open scene
    - Clean Unknown nodes
    - Clean Turtle nodes
    - Clean Unused Plugins nodes
    """

    delete_unknown_nodes()
    delete_turtle_nodes()
    delete_unused_plugins()


def get_project_rule(rule):
    """
    Get the full path of the rule of the project
    :param rule: str
    :return: str
    """

    workspace = cmds.workspace(query=True, rootDirectory=True)
    workspace_folder = cmds.workspace(fileRuleEntry=rule)
    if not workspace_folder:
        sp.logger.warning('File Rule Entry "{}" has no value, please check if the rule name is typed correctly!'.format(rule))

    return os.path.join(workspace, workspace_folder)


def get_short_name(node):
    """
    Returns short name of a Maya node
    :param node: str, maya node
    :return: str
    """

    return node.split(':')[-1].split('|')[-1]


def attribute_exists(node, attr):
    """
    Returns whether give attribute exists in given node
    :param node: str, maya node
    :param attr: str, attribute name to check
    :return: bool
    """

    return cmds.attributeQuery(attr, node=node, exists=True)


def get_mdag_path(node):
    """
    Returns MDag path object of the given node
    :param node: str, Maya node name
    :return: OpenMaya.MDagPath
    """

    new_node = node
    if node.startswith('|'):
        new_node = node[1:]
    sel = cmds.ls(new_node)[0]
    dag_path = OpenMaya.MDagPath()
    sel_list = OpenMaya.MSelectionList()
    sel_list.add(sel)
    sel_list.getDagPath(0, dag_path)

    return dag_path


def add_message_attribute(node_a, node_b, attr_name, force=True):
    """
    Connects node_a and node_b using a message attribute with the given name
    :param node_a: str, name of a Maya node
    :param node_b: str, name of a Maya node
    :param attr_name: str, name of the message attribute
    :param force: bool, Whether to force the connection or not
    """

    if not attribute_exists(node_a, attr_name):
        cmds.addAttr(node_a, longName=attr_name, attributeType='message')
    if not attribute_exists(node_b, attr_name):
        cmds.addAttr(node_b, longName=attr_name, attributeType='message')
    try:
        cmds.connectAttr('{}.{}'.format(node_a, attr_name), '{}.{}'.format(node_b, attr_name), f=force)
    except StandardError as e:
        sp.logger.debug(e)


def get_locked_attributes(node, mode='rotate'):
    """
    Returns a list of the locked attributes of the given node
    :param node: str, name of Maya node
    :param mode: str, type of locked attributes we want to check
    :return: list<str>
    """

    locked_attrs = list()
    if mode == 'rotate':
        attrs = ['rotateX', 'rotateY', 'rotateZ']
    if mode == 'translate':
        attrs = ['translateX', 'translateY', 'translateZ']
    for attr in attrs:
        if not cmds.getAttr('%s.%s' % (node, attr), settable=True):
            locked_attrs.append(attr.replace(mode, '').lower())

    return locked_attrs
