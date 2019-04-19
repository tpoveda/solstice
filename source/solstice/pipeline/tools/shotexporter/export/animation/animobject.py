#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class for exporter widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import abc
import json
import time
import locale
import getpass

import solstice.pipeline as sp
from solstice.pipeline.utils import namespace, namingutils, decorators

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.utils import mayautils
    show_wait_cursor = mayautils.show_wait_cursor
else:
    show_wait_cursor = decorators.empty


class AnimObject(object):
    """
    Base object to save and load animation objects (poses, animations, etc)
    """

    def __init__(self):
        self._path = None
        self._namespaces = None
        self._data = {'metadata': {}, 'objects': {}}

    @classmethod
    def from_path(cls, path):
        """
        Returns a new anim object instance for the given path
        :param path: str
        :return: AnimObject
        """

        t = cls()
        t.set_path(path)
        t.read()

        return t

    @classmethod
    def from_objects(cls, objects, **kwargs):
        """
        Returns a new anim object instance for the given objects
        :param objects: list(str)
        :return: AnimObject
        """

        t = cls(**kwargs)
        for obj in objects:
            t.add(obj)

        return t

    @staticmethod
    def read_json(path):
        """
        Reads the given JSON path
        :param path: str
        :return: dict
        """

        with open(path, 'r') as f:
            data = f.read()

        data = json.loads(data)

        return data

    def path(self):
        """
        Returns the location in disk of the anim objects
        :return: str
        """

        return self._path

    def set_path(self, path):
        """
        Sets the location in dsk for loading and saving the anim object
        :param path: str
        """

        self._path = path

    def data(self):
        """
        Returns all the data for the anim object
        :return: dict
        """

        return self._data

    def set_data(self, data):
        """
        Sets the data for the anim object
        :param data: dict
        """

        self._data = data

    def objects(self):
        """
        Returns all the object data
        :return: dict
        """

        return self.data().get('objects', {})

    def object(self, name):
        """
        Returns the data for the given object name
        :param name: str
        :return: dict
        """

        return self.objects().get(name, {})

    def create_object_data(self, name):
        """
        Creates the object data for the given object name
        :param name: str
        :return: dict
        """

        return {}

    def validate(self, **kwargs):
        """
        Validates the given keyword arguments for the current anim object
        :param kwargs: dict
        """

        namespaces = kwargs.get('namespaces')
        if namespaces is not None:
            scene_namespaces = namespace.get_all()
            for ns in namespaces:
                if ns and ns not in scene_namespaces:
                    msg = 'The namespace "{}" does not exists in current scene! Please a valid namespace.'
                    msg = msg.format(namespace)
                    raise ValueError(msg)

    def mtime(self):
        """
        Returns the modification datetime of self.path()
        :return: float
        """

        return os.path.getmtime(self.path())

    def ctime(self):
        """
        Returns the creation date time of self.path()
        :return: float
        """

        return os.path.getctime(self.path())

    def namespaces(self):
        """
        Returns the namespaces contained in the ani mobject
        :return: list(str)
        """

        if self._namespaces is None:
            group = namingutils.group_objects(self.objects())
            self._namespaces = group.keys()

        return self._namespaces

    def count(self):
        """
        Returns the number o objects in the anim object
        :return: int
        """

        return len(self.objects() or [])

    def add(self, objects):
        """
        Add the given objects to the anim object
        :param objects: str | list(str)
        """

        if isinstance(objects, (str, unicode)):
            objects = [objects]

        for name in objects:
            self.objects()[name] = self.create_object_data(name)

    def remove(self, objects):
        """
        Removes given objects from the anim object
        :param objects: str | list(str)
        """

        if isinstance(objects, (str, unicode)):
            objects = [objects]

        for obj in objects:
            del self.objects()[obj]

    def metadata(self):
        """
        Returns the current metadata for the anim object
        :return: dict
        """

        return self.data().get('metadata', {})

    def set_metadata(self, key, value):
        """
        Sets the given key and value in the metadata
        :param key: str
        :param value: int | str | float | dict
        """

        self.data()['metadata'][key] = value

    def update_metadata(self, metadata):
        """
        Updates the given key and value in the metadata
        :param metadata: dict
        """

        self.data()['metadata'].update(metadata)

    def read(self, path=''):
        """
        Returns the data from the path set on the anim object
        :param path: str
        :return: dict
        """

        path = path or self.path()
        data = self.read_json(path)

        self.set_data(data)

    @abc.abstractmethod
    def load(self, *args, **kwargs):
        pass

    @show_wait_cursor
    def save(self, path):
        """
        Saves the current metadata and object data to the given path
        :param path: str
        """

        if not sp.is_maya():
            sp.logger.warning('Anim Object saving is only supported in Maya!')
            return

        sp.logger.debug('Saving Anim Object: {}'.format(path))

        encoding = locale.getpreferredencoding()
        user = getpass.getuser()
        if user:
            user = user.decode(encoding)

        ctime = str(time.time()).split('.')[0]
        references = mayautils.get_reference_data(self.objects())

        self.set_metadata('user', user)
        self.set_metadata('ctime', ctime)
        self.set_metadata('version', '1.0.0')
        self.set_metadata('references', references)
        self.set_metadata('mayaVersion', cmds.about(v=True))
        self.set_metadata('mayaSceneFile', cmds.file(q=True, sn=True))

        metadata = {'metadata': self.metadata()}
        data = self.dump(metadata)[:-1] + ','

        objects = {'objects': self.objects()}
        data += self.dump(objects)[1:]

        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(path, 'w') as f:
            f.write(str(data))

        sp.logger.debug('Saved Anim Object: {}'.format(path))

    def dump(self, data=None):
        """
        Dumps anim object data
        :param data: str | dict
        :return: str
        """

        if data is None:
            data = self.data()

        return json.dumps(data, indent=2)
