#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful utilities  and classes related with Slack
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys

import solstice.pipeline as sp

from slackclient import SlackClient


def get_solstice_slack_api():
    """
    Returns API code for Solstice Slack App
    :return: str
    """

    return os.environ.get('SOLSTICE_SLACK_API', None)


def asset_published(asset_name):
    """
    Sends a message to general group notifying that a new asset has been published
    :param asset_name: str, name of the published asset
    :return:
    """

    asset = sp.find_asset(asset_name)
    if not asset:
        sys.solstice.logger.warning('No asset found with name: {}'.format(asset_name))
        return

    slack_token = get_solstice_slack_api()
    if not slack_token:
        sys.solstice.logger.warning('Solstice Slack App is not available because you are not a developer. Please contact TD!')
        return

    msg = 'Solstice Publisher: {} has been published!'.format(asset.name)
    asset_url = asset.get_asset_artella_url()
    asset_render = asset.get_artella_render_image()
    if not asset_render:
        sys.solstice.logger.warning('Impossible to send message because render image is not available!')
        return

    sc = SlackClient(slack_token)

    sc.api_call(
        "chat.postMessage",
        channel="#general",
        text=msg
    )

    sc.api_call(
        "chat.postMessage",
        channel="#general",
        text=asset_url
    )

    with open(asset_render) as f:
        sc.api_call(
            'files.upload',
            channels='#general',
            file=f,
            title=asset.name
        )


def new_version(file_name, url, comment, channel_name='general'):
    """
    Creates a new version of the current file with given info
    :param url: str
    :param comment: str
    :param channel_name: str
    """

    slack_token = get_solstice_slack_api()
    if not slack_token:
        sys.solstice.logger.warning('Solstice Slack App is not available because you are not a developer. Please contact TD!')
        return

    msg = 'New version of file {} has been uploaded into Artella server!'.format(os.path.relpath(file_name, sp.get_solstice_project_path()))
    comment_msg = 'Comment: {}'.format(comment) if comment else None

    sc = SlackClient(slack_token)

    sc.api_call(
        "chat.postMessage",
        channel="#{}".format(channel_name),
        text=msg
    )

    sc.api_call(
        "chat.postMessage",
        channel="#{}".format(channel_name),
        text=comment_msg
    )

    sc.api_call(
        "chat.postMessage",
        channel="#{}".format(channel_name),
        text=url
    )


def new_viewport_image(image_path, file_name, channel_name='general'):
    """
    Grabs viewport image and submits to given channel
    :param image_path: str
    :param file_name: str
    :param channel_name: str
    :return:
    """

    slack_token = get_solstice_slack_api()
    if not slack_token:
        sys.solstice.logger.warning('Solstice Slack App is not available because you are not a developer. Please contact TD!')
        return

    sc = SlackClient(slack_token)

    with open(image_path) as f:
        print(f)
        sc.api_call(
            'files.upload',
            channels=["#{}".format(channel_name)],
            file=f,
            title=os.path.basename(file_name)
        )
