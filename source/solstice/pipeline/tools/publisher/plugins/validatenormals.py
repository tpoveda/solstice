import pyblish.api

class ValidateNormals(pyblish.api.InstancePlugin):
    """
    Normals of a model may not be locked
    """

    label = 'Normals'
    order = pyblish.api.ValidatorOrder
    hosts = ['maya']
    families = ['model']

    def process(self, instance):

        import maya.cmds as cmds

        invalid = list()
        for mesh in cmds.ls(instance, type='mesh', long=True):
            faces = cmds.polyListComponentConversion(mesh, toVertexFace=True)
            locked = cmds.polyNormalPerVertex(faces, query=True, freezeNormal=True)
            invalid.append(mesh) if any(locked) else None

        assert not invalid, 'Meshes found with locked normals: {}'.format(invalid)

        self.log.info('The normals of {} are correct.'.format(instance))