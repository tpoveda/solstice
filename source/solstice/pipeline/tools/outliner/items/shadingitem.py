class OutlinerShadingItem(outlineritems.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerShadingItem, self).__init__(category='shading', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return artellapipe.solstice.resource.pixmap('shader', category='icons').scaled(18, 18, Qt.KeepAspectRatio)

