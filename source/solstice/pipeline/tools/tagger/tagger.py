#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used to manage metadata for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from artellapipe.tools.tagger import tagger


class SolsticeTagger(tagger.ArtellaTagger, object):
    def __init__(self, project):
        super(SolsticeTagger, self).__init__(project=project)

    def _create_editors(self):
        """
        Internal function that creates the editors that should be used by tagger
        Overrides to add custom editors
        """

        from solstice.pipeline.tools.tagger.editors import nameeditor
        from solstice.pipeline.tools.tagger.editors import descriptioneditor
        from solstice.pipeline.tools.tagger.editors import typeeditor
        from solstice.pipeline.tools.tagger.editors import highproxyeditor
        from solstice.pipeline.tools.tagger.editors import shaderseditor

        name_editor = nameeditor.NameEditor(project=self._project)
        description_editor = descriptioneditor.DescriptionEditor(project=self._project)
        type_editor = typeeditor.TypeEditor(project=self._project)
        high_proxy_editor = highproxyeditor.HighProxyEditor(project=self._project)
        shader_editor = shaderseditor.ShadersEditor(project=self._project)

        self.add_editor(name_editor)
        self.add_editor(description_editor)
        self.add_editor(type_editor)
        self.add_editor(high_proxy_editor)
        self.add_editor(shader_editor)


def run():
    win = SolsticeTagger(artellapipe.solstice)
    win.show()
    return win
