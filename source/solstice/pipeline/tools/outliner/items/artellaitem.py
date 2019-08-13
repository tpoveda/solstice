class OutlinerArtellaItem(outlineritems.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerArtellaItem, self).__init__(category='artella', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return artellapipe.solstice.resource.pixmap('artella', category='icons').scaled(18, 18, Qt.KeepAspectRatio)

