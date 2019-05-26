#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utilities functions to work with Alembics
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import traceback

import solstice.pipeline as sp


def export(alembicFile,
           eulerFilter=False,
           noNormals=False,
           preRoll=False,
           renderableOnly=False,
           selection=False,
           uvWrite=False,
           writeColorSets=False,
           writeFaceSets=False,
           wholeFrameGeo=False,
           worldSpace=False,
           writeVisibility=False,
           writeUVSets=False,
           writeCreases=False,
           dataFormat="Ogawa",
           step=1.0,
           melPerFrameCallback="",
           melPostJobCallback="",
           pythonPerFrameCallback="",
           pythonPostJobCallback="",
           userAttr=[],
           userAttrPrefix=["ABC_"],
           attr=[],
           attrPrefix=[],
           root=[],
           frameRelativeSample=[],
           frameRange=[],
           stripNamespaces=-1,
           dontSkipUnwrittenFrames=False,
           verbose=False,
           preRollStartFrame=0
           ):
    """
    Export Alembic.
    Args:
        alembicFile (str): File location to write the Alembic data.
        eulerFilter (bool, optional): Apply Euler filter while sampling
            rotations. Defaults to False.
        noNormals (bool, optional): Present normal data for Alembic poly meshes
            will not be written. Defaults to False.
        preRoll (bool, optional): This frame range will not be sampled.
            Defaults to False.
        renderableOnly (bool, optional): Non-renderable hierarchy
            (invisible, or templated) will not be written out. Defaults to
            False.
        selection (bool, optional): Write out all all selected nodes from the
            active selection list that are descendents of the roots specified
            with -root. Defaults to False.
        uvWrite (bool, optional): Uv data for PolyMesh and SubD shapes will be
            written to the Alembic file.  Only the current uv map is used.
            Defaults to False.
        writeColorSets (bool, optional): Write all color sets on MFnMeshes as
            color 3 or color 4 indexed geometry parameters with face varying
            scope. Defaults to False.
        writeFaceSets (bool, optional): Write all Face sets on MFnMeshes.
            Defaults to False.
        wholeFrameGeo (bool, optional): Data for geometry will only be written
            out on whole frames. Defaults to False.
        worldSpace (bool, optional): Any root nodes will be stored in world
            space. Defaults to False.
        writeVisibility (bool, optional): Visibility state will be stored in
            the Alembic file.  Otherwise everything written out is treated as
            visible. Defaults to False.
        writeUVSets (bool, optional): Write all uv sets on MFnMeshes as vector
            2 indexed geometry parameters with face varying scope. Defaults to
            False.
        writeCreases (bool, optional): If the mesh has crease edges or crease
            vertices, the mesh (OPolyMesh) would now be written out as an OSubD
            and crease info will be stored in the Alembic file. Otherwise,
            creases info won't be preserved in Alembic file unless a custom
            Boolean attribute SubDivisionMesh has been added to mesh node and
            its value is true. Defaults to False.
        dataFormat (str, optional): The data format to use to write the file.
            Can be either "HDF" or "Ogawa". Defaults to "Ogawa".
        step (float, optional): The time interval (expressed in frames) at
            which the frame range is sampled. Additional samples around each
            frame can be specified with -frs. Defaults to 1.0.
        melPerFrameCallback (str, optional): When each frame
            (and the static frame) is evaluated the string specified is
            evaluated as a Mel command. See below for special processing rules.
            Defaults to "".
        melPostJobCallback (str, optional): When the translation has finished
            the string specified is evaluated as a Mel command. See below for
            special processing rules. Defaults to "".
        pythonPerFrameCallback (str, optional): When each frame
            (and the static frame) is evaluated the string specified is
            evaluated as a python command. See below for special processing
            rules. Defaults to "".
        pythonPostJobCallback (str, optional): When the translation has
            finished the string specified is evaluated as a python command. See
            below for special processing rules. Defaults to "".
        userAttrPrefix (list of str, optional): Prefix filter for determining
            which user attributes to write out. Defaults to [].
        userAttr (list of str, optional): Specific user attributes to write
            out. Defaults to [].
        attr (list of str, optional): A specific geometric attribute to write
            out. Defaults to [].
        attrPrefix (list of str, optional): Prefix filter for determining which
            geometric attributes to write out. Defaults to ["ABC_"].
        root (list of str, optional): Maya dag path which will be parented to
            the root of the Alembic file. Defaults to [], which means the
            entire scene will be written out.
        frameRelativeSample (list of float, optional): Frame relative sample
            that will be written out along the frame range. Defaults to [].
        frameRange (list of list of two floats, optional): The frame range to
            write. Each list of two floats defines a new frame range. step or
            frameRelativeSample will affect the current frame range only.
        stripNamespaces (int, optional): Namespaces will be stripped off of
            the node before being written to Alembic. The int specifies how
            many namespaces will be stripped off of the node name. Be careful
            that the new stripped name does not collide with other sibling node
            names.
            Examples:
            taco:foo:bar would be written as just bar with stripNamespaces=0
            taco:foo:bar would be written as foo:bar with stripNamespaces=1
            Defaults to -1, which means namespaces will be preserved.
        dontSkipUnwrittenFrames (bool, optional): When evaluating multiple
            translate jobs, this decides whether to evaluate frames between
            jobs when there is a gap in their frame ranges. Defaults to False.
        verbose (bool, optional): Prints the current frame that is being
            evaluated. Defaults to False.
        preRollStartFrame (float, optional): The frame to start scene
            evaluation at.  This is used to set the starting frame for time
            dependent translations and can be used to evaluate run-up that
            isn't actually translated. Defaults to 0.
    Special callback information:
    On the callbacks, special tokens are replaced with other data, these tokens
    and what they are replaced with are as follows:
    #FRAME# replaced with the frame number being evaluated.
    #FRAME# is ignored in the post callbacks.
    #BOUNDS# replaced with a string holding bounding box values in minX minY
    minZ maxX maxY maxZ space seperated order.
    #BOUNDSARRAY# replaced with the bounding box values as above, but in
    array form.
    In Mel: {minX, minY, minZ, maxX, maxY, maxZ}
    In Python: [minX, minY, minZ, maxX, maxY, maxZ]
    """

    if not sp.is_maya():
        sys.solstice.logger.warning('DCC {} does not support Alembic Export functionality yet!'.format(sys.solstice.dcc.get_name()))
        return

    import maya.cmds as cmds

    # Generate job add_argument
    jobArg = ""

    # Boolean flags
    booleans = {
        "eulerFilter": eulerFilter,
        "noNormals": noNormals,
        "preRoll": preRoll,
        "renderableOnly": renderableOnly,
        "selection": selection,
        "uvWrite": uvWrite,
        "writeColorSets": writeColorSets,
        "writeFaceSets": writeFaceSets,
        "wholeFrameGeo": wholeFrameGeo,
        "worldSpace": worldSpace,
        "writeVisibility": writeVisibility,
        "writeUVSets": writeUVSets,
        "writeCreases": writeCreases
    }
    for key, value in booleans.iteritems():
        if value:
            jobArg += " -{0}".format(key)

    # Single argument flags
    single_arguments = {
        "dataFormat": dataFormat,
        "step": step,
        "melPerFrameCallback": melPerFrameCallback,
        "melPostJobCallback": melPostJobCallback,
        "pythonPerFrameCallback": pythonPerFrameCallback,
        "pythonPostJobCallback": pythonPostJobCallback
    }
    for key, value in single_arguments.iteritems():
        if value:
            jobArg += " -{0} \"{1}\"".format(key, value)

    # Multiple arguments flags
    multiple_arguments = {
        "attr": attr,
        "attrPrefix": attrPrefix,
        "root": root,
        "userAttrPrefix": userAttrPrefix,
        "userAttr": userAttr,
        "frameRelativeSample": frameRelativeSample
    }
    for key, value in multiple_arguments.iteritems():
        for item in value:
            jobArg += " -{0} \"{1}\"".format(key, item)

    # frame range flag
    for start, end in frameRange:
        jobArg += " -frameRange {0} {1}".format(start, end)

    # strip namespaces flag
    if stripNamespaces == 0:
        jobArg += " -stripNamespaces"
    if stripNamespaces > 0:
        jobArg += " -stripNamespaces {0}".format(stripNamespaces)

    # file flag
    # Alembic exporter does not like back slashes
    jobArg += " -file {0}".format(alembicFile.replace("\\", "/"))

    # Execute export
    sys.solstice.dcc.load_plugin('AbcExport.mll', quiet=True)

    export_args = {
        "dontSkipUnwrittenFrames": dontSkipUnwrittenFrames,
        "verbose": verbose,
        "preRollStartFrame": preRollStartFrame,
        "jobArg": jobArg
    }

    print("Exporting with: {0}".format(export_args))

    sys.solstice.logger.debug('\n> Exporting model Alembic with jog arguments:\n "{}"'.format(export_args))
    abc_folder = os.path.dirname(alembicFile)
    if not os.path.exists(abc_folder):
        os.makedirs(abc_folder)

    try:
        cmds.AbcExport(**export_args)
    except Exception as e:
        raise Exception(e)

    sys.solstice.logger.debug('Abc export completed!')
    return os.path.exists(alembicFile)

def import_alembic(alembic_file, mode='import', nodes=None, parent=None):
    if not os.path.exists(alembic_file):
        sys.solstice.dcc.confirm_dialog(
            title='Error',
            message='Alembic File does not exists:\n{}'.format(alembic_file)
        )
        return None

    sys.solstice.logger.debug('Import Alembic File ({}) with job arguments:\n{}\n\n{}'.format(mode, alembic_file, nodes))

    try:
        if sp.is_maya():
            import maya.cmds as cmds
            if nodes:
                res = cmds.AbcImport(alembic_file, ct=' '.join(nodes))
            elif parent:
                res = cmds.AbcImport(alembic_file, mode=mode, rpr=parent)
            else:
                res = cmds.AbcImport(alembic_file, mode=mode)
            return res
        elif sp.is_houdini():
            if not parent:
                sys.solstice.logger.warning('Impossible to import Alembic File because not Alembic parent given!')
                return
            parent.parm('fileName').set(alembic_file)
            parent.parm('buildHierarchy').pressButton()

    except Exception as e:
        sys.solstice.logger.error(traceback.format_exc())
        raise Exception(e)

    sys.solstice.logger.debug('Alembic File {} imported successfully!'.format(os.path.basename(alembic_file)))


def reference_alembic(alembic_file, namespace=None):

    if not sp.is_maya():
        sys.solstice.logger.warning('DCC {} does not support Alembic Reference functionality yet!'.format(sys.solstice.dcc.get_name()))
        return

    import maya.cmds as cmds

    if not os.path.exists(alembic_file):
        sys.solstice.dcc.confirm_dialog(
            title='Error',
            message='Alembic File does not exists:\n{}'.format(alembic_file)
        )
        return None

    try:
        if namespace:
            cmds.file(alembic_file, type='Alembic', reference=True, namespace=namespace)
        else:
            cmds.file(alembic_file, type='Alembic', reference=True)
    except Exception as e:
        sys.solstice.logger.error(traceback.format_exc())
        raise Exception(e)

    sys.solstice.logger.debug('Alembic File {} referenced successfully!'.format(os.path.basename(alembic_file)))

    return True
