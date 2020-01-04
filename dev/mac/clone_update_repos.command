#!/bin/bash

# tpPyUtils
if [ ! -d ~/Documents/projects/dev/tomi/tpPyUtils ]
then
    git clone https://github.com/tpoveda/tpPyUtils.git ~/Documents/projects/dev/tomi/tpPyUtils
else
    pushd ~/Documents/projects/dev/tomi/tpPyUtils
    git pull
    popd
fi

# tpDccLib
if [ ! -d ~/Documents/projects/dev/tomi/tpDccLib ]
then
    git clone https://github.com/tpoveda/tpDccLib.git ~/Documents/projects/dev/tomi/tpDccLib
else
    pushd ~/Documents/projects/dev/tomi/tpDccLib
    git pull
    popd
fi

# tpQtLib
if [ ! -d ~/Documents/projects/dev/tomi/tpQtLib ]
then
    git clone https://github.com/tpoveda/tpQtLib.git ~/Documents/projects/dev/tomi/tpQtLib
else
    pushd ~/Documents/projects/dev/tomi/tpQtLib
    git pull
    popd
fi

# tpMayaLib
if [ ! -d ~/Documents/projects/dev/tomi/tpMayaLib ]
then
    git clone https://github.com/tpoveda/tpMayaLib.git ~/Documents/projects/dev/tomi/tpMayaLib
else
    pushd ~/Documents/projects/dev/tomi/tpMayaLib
    git pull
    popd
fi

# tpHoudiniLib
if [ ! -d ~/Documents/projects/dev/tomi/tpHoudiniLib ]
then
    git clone https://github.com/tpoveda/tpHoudiniLib.git ~/Documents/projects/dev/tomi/tpHoudiniLib
else
    pushd ~/Documents/projects/dev/tomi/tpHoudiniLib
    git pull
    popd
fi

# tpNameIt
if [ ! -d ~/Documents/projects/dev/tomi/tpNameIt ]
then
    git clone https://github.com/tpoveda/tpNameIt.git ~/Documents/projects/dev/tomi/tpNameIt
else
    pushd ~/Documents/projects/dev/tomi/tpNameIt
    git pull
    popd
fi

# ================================================================================================================================================================

# artellapipe
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe ]
then
    git clone https://github.com/ArtellaPipe/artellapipe.git ~/Documents/projects/dev/artellapipe/artellapipe
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe
    git pull
    popd
fi

# artellapipe-config
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-config ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-config.git ~/Documents/projects/dev/artellapipe/artellapipe-config
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-config
    git pull
    popd
fi

# artellapipe-libs-alembic
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-alembic ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-alembic.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-alembic
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-alembic
    git pull
    popd
fi

# artellapipe-libs-naming
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-naming ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-naming.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-naming
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-naming
    git pull
    popd
fi

# artellapipe-libs-artella
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-artella ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-artella.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-artella
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-artella
    git pull
    popd
fi

# artellapipe-libs-drive
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-drive ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-drive.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-drive
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-drive
    git pull
    popd
fi

# artellapipe-libs-pyblish
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-pyblish ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-pyblish.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-pyblish
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-pyblish
    git pull
    popd
fi

# artellapipe-libs-ffmpeg
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-libs-ffmpeg ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-libs-ffmpeg.git ~/Documents/projects/dev/artellapipe/artellapipe-libs-ffmpeg
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-libs-ffmpeg
    git pull
    popd
fi

# artellapipe-dccs-maya
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-dccs-maya ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-dccs-maya.git ~/Documents/projects/dev/artellapipe/artellapipe-dccs-maya
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-dccs-maya
    git pull
    popd
fi

# artellapipe-dccs-houdini
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-dccs-houdini ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-dccs-houdini.git ~/Documents/projects/dev/artellapipe/artellapipe-dccs-houdini
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-dccs-houdini
    git pull
    popd
fi

# artellapipe-launcher
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-launcher ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-launcher.git ~/Documents/projects/dev/artellapipe/artellapipe-launcher
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-launcher
    git pull
    popd
fi

# artellapipe-launcher-plugins-dccselector
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-dccselector ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-launcher-plugins-dccselector.git ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-dccselector
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-dccselector
    git pull
    popd
fi

# artellapipe-launcher-plugins-artellamanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-artellamanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-launcher-plugins-artellamanager.git ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-artellamanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-launcher-plugins-artellamanager
    git pull
    popd
fi

# artellapipe-tools-welcome
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-welcome ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-welcome.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-welcome
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-welcome
    git pull
    popd
fi

# artellapipe-tools-changelog
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-changelog ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-changelog.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-changelog
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-changelog
    git pull
    popd
fi

# artellapipe-tools-bugtracker
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-bugtracker ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-bugtracker.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-bugtracker
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-bugtracker
    git pull
    popd
fi

# artellapipe-tools-alembicmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-alembicmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-alembicmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-alembicmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-alembicmanager
    git pull
    popd
fi

# artellapipe-tools-artellamanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellamanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-artellamanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellamanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellamanager
    git pull
    popd
fi

# artellapipe-tools-artellauploader
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellauploader ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-artellauploader.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellauploader
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-artellauploader
    git pull
    popd
fi

# artellapipe-tools-assetslibrary
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetslibrary ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-assetslibrary.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetslibrary
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetslibrary
    git pull
    popd
fi

# artellapipe-tools-assetsmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetsmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-assetsmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetsmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetsmanager
    git pull
    popd
fi

# artellapipe-tools-shadersmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-shadersmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-shadersmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-shadersmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-shadersmanager
    git pull
    popd
fi

# artellapipe-tools-lightrigsmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-lightrigsmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-lightrigsmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-lightrigsmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-lightrigsmanager
    git pull
    popd
fi

# artellapipe-tools-namemanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-namemanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-namemanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-namemanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-namemanager
    git pull
    popd
fi

# artellapipe-tools-playblastmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-playblastmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-playblastmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-playblastmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-playblastmanager
    git pull
    popd
fi

# artellapipe-tools-outliner
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-outliner ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-outliner.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-outliner
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-outliner
    git pull
    popd
fi

# artellapipe-tools-tagger
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-tagger ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-tagger.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-tagger
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-tagger
    git pull
    popd
fi

# artellapipe-tools-toolbox
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-toolbox ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-toolbox.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-toolbox
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-toolbox
    git pull
    popd
fi

# artellapipe-tools-modelchecker
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-modelchecker ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-modelchecker.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-modelchecker
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-modelchecker
    git pull
    popd
fi

# artellapipe-tools-assetspublisher
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetspublisher ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-assetspublisher.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetspublisher
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-assetspublisher
    git pull
    popd
fi

# artellapipe-tools-dependenciesmanager
if [ ! -d ~/Documents/projects/dev/artellapipe/artellapipe-tools-dependenciesmanager ]
then
    git clone https://github.com/ArtellaPipe/artellapipe-tools-dependenciesmanager.git ~/Documents/projects/dev/artellapipe/artellapipe-tools-dependenciesmanager
else
    pushd ~/Documents/projects/dev/artellapipe/artellapipe-tools-dependenciesmanager
    git pull
    popd
fi

# ================================================================================================================================================================

# solstice
if [ ! -d ~/Documents/projects/dev/solstice/solstice ]
then
    git clone https://github.com/Solstice-Short-Film/solstice.git ~/Documents/projects/dev/solstice/solstice
else
    pushd ~/Documents/projects/dev/solstice/solstice
    git pull
    popd
fi

# solstice-config
if [ ! -d ~/Documents/projects/dev/solstice/solstice-config ]
then
    git clone https://github.com/Solstice-Short-Film/solstice-config.git ~/Documents/projects/dev/solstice/solstice-config
else
    pushd ~/Documents/projects/dev/solstice/solstice-config
    git pull
    popd
fi

# solstice-bootstrap
if [ ! -d ~/Documents/projects/dev/solstice/solstice-bootstrap ]
then
    git clone https://github.com/Solstice-Short-Film/solstice-bootstrap.git ~/Documents/projects/dev/solstice/solstice-bootstrap
else
    pushd ~/Documents/projects/dev/solstice/solstice-bootstrap
    git pull
    popd
fi

# solstice-tools-snowgenerator
if [ ! -d ~/Documents/projects/dev/solstice/solstice-tools-snowgenerator ]
then
    git clone https://github.com/Solstice-Short-Film/solstice-tools-snowgenerator.git ~/Documents/projects/dev/solstice/solstice-tools-snowgenerator
else
    pushd ~/Documents/projects/dev/solstice/solstice-tools-snowgenerator
    git pull
    popd
fi

# solstice-tools-xgenmanager
if [ ! -d ~/Documents/projects/dev/solstice/solstice-tools-xgenmanager ]
then
    git clone https://github.com/Solstice-Short-Film/solstice-tools-xgenmanager.git ~/Documents/projects/dev/solstice/solstice-tools-xgenmanager
else
    pushd ~/Documents/projects/dev/solstice/solstice-tools-xgenmanager
    git pull
    popd
fi