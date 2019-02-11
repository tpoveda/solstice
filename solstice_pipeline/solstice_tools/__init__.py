import os

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_qt_utils

def get_ui_solstice_path():
    """
    Returns path where Solstice Tools UIs are located
    :return: str
    """

    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ui')


def get_tool_ui_file(tool_name):
    """
    Returns path where given tool UI is located
    :return: str
    """

    ui_file = os.path.join(get_ui_solstice_path(), tool_name+'.ui')
    if not os.path.isfile(ui_file):
        sp.logger.warning('Solstice Tool {} has not a valid UI: {}'.format(tool_name, ui_file))
        return None

    return ui_file


def load_tool_ui(tool_name):
    """
    Load and returns given tool UI
    :param tool_name: str
    :return: QWidget
    """

    ui_file = get_tool_ui_file(tool_name)
    if ui_file:
        return solstice_qt_utils.ui_loader(ui_file)

    return None
