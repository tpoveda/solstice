class OutlinerGroomItem(outlineritems.OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerGroomItem, self).__init__(category='groom', parent=parent)