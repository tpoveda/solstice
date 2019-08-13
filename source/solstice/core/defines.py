#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains all constant definitions used by Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.core import defines


# Defines the file name of the Solstice Tagger file
SOLSTICE_TAGGER_FILE_NAME = 'tagger.json'

# Defines the asset type used for Props
SOLSTICE_PROP_ASSETS = 'Props'

# Defines the asset type used for Background Elements
SOLSTICE_BACKGROUND_ELEMENTS_ASSETS = 'Background Elements'

# Defines the asset type used for Characters
SOLSTICE_CHARACTERS_ASSETS = 'Characters'

# Defines of textures asset type for Solstice
SOLSTICE_TEXTURES_ASSET_TYPE = defines.ARTELLA_TEXTURES_ASSET_TYPE

# Defines of model asset type for Solstice
SOLSTICE_MODEL_ASSET_TYPE = defines.ARTELLA_MODEL_ASSET_TYPE

# Defines of shading asset type for Solstice
SOLSTICE_SHADING_ASSET_TYPE = defines.ARTELLA_SHADING_ASSET_TYPE

# Defines of rig asset type for Solstice
SOLSTICE_RIG_ASSET_TYPE = defines.ARTELLA_RIG_ASSET_TYPE

# Defines of groom asset type for Solstice
SOLSTICE_GROOM_ASSET_TYPE = defines.ARTELLA_GROOM_ASSET_TYPE

# Defines Alembic extension used by Solstice
SOLSTICE_ALEMBIC_EXTENSION = '.abc'

# Defines Alembic extension used by Solstice
SOLSTICE_MODEL_EXTENSION = '.ma'

# Defines Texture extensions used by Solstice
SOLSTICE_TEXTURE_EXTENSIONS = ['.tx', '.png', '.jpg', '.jpeg']

# Defines Alembic extension used by Solstice
SOLSTICE_SHADING_EXTENSION = '.ma'

# Defines Alembic extension used by Solstice
SOLSTICE_RIG_EXTENSION = '.ma'

# Defines Standin extension used by Solstice
SOLSTICE_STANDIN_EXTENSION = '.ass'
