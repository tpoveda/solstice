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

# Defines environment variable name that can setup to define folder where configuration files are located
SOLSTICE_CONFIGURATION_ENV = 'SOLSTICE_PROJECT_CONFIGURATIONS_FOLDER'

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

# Defines the extension used for layout files
SOLSTICE_LAYOUT_EXTENSION = '.layout'

# Defines the extension used for animation files
SOLSTICE_ANIMATION_EXTENSION = '.anim'

# Defines the extension used for fx files
SOLSTICE_FX_EXTENSION = '.fx'

# Defines the extension used for lighting files
SOLSTICE_LIGHTING_EXTENSION = '.light'

# Defines tag type used to define scenes
SOLSTICE_SCENE_TAG_TYPE = 'Scene'

# Defines tag type used to define props
SOLSTICE_PROP_TAG_TYPE = 'Prop'

# Defines tag type used to define characters
SOLSTICE_CHARACTER_TAG_TYPE = 'Character'

# Defines tag type used to define background elements
SOLSTICE_BACKGROUND_ELEMENT_TAG_TYPE = 'Background Element'

# Defines tag type used to define light rigs
SOLSTICE_LIGHT_RIG_TAG_TYPE = 'Light Rig'

# Defines tag type used to define models
SOLSTICE_MODEL_TAG_TYPE = 'Model'

# Defines tag type used to define animations
SOLSTICE_ANIMATION_TAG_TYPE = 'Animation'

# Defines tag type used to define shading
SOLSTICE_SHADING_TAG_TYPE = 'Shading'

# Defines tag type used to define cloth
SOLSTICE_CLOTH_TAG_TYPE = 'Cloth'

# Defines tag type used to define grooming
SOLSTICE_GROOM_TAG_TYPE = 'Groom'

# Defines tag type used to define cameras
SOLSTICE_CAMERA_TAG_TYPE = 'Camera'

# Defines shot asset type used for layout
SOLSTICE_LAYOUT_SHOT_FILE_TYPE = 'Layout'

# Defines shot asset type used for layout
SOLSTICE_ANIMATION_SHOT_FILE_TYPE = 'Animation'

# Defines shot asset type used for layout
SOLSTICE_FX_SHOT_FILE_TYPE = 'FX'

# Defines shot asset type used for layout
SOLSTICE_LIGHTING_SHOT_FILE_TYPE = 'Lighting'

# Defines the extension used for transform shot overrides
SOLSTICE_TRANSFORM_OVERRIDE_EXTENSION = '.ovxform'
