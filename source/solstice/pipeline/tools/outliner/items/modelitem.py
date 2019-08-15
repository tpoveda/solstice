class OutlinerModelItem(outlineritems.OutlinerFileItem, object):

    proxyHiresToggled = Signal(QObject, int)

    def __init__(self, parent=None):
        super(OutlinerModelItem, self).__init__(category='model', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return artellapipe.solstice.resource.pixmap('cube', category='icons').scaled(18, 18, Qt.KeepAspectRatio)

    def custom_ui(self):
        super(OutlinerModelItem, self).custom_ui()

        self.model_buttons = widget_buttons.ModelDisplayButtons()
        self.item_layout.addWidget(self.model_buttons, 0, 3, 1, 1)

    # def setup_signals(self):
    #     self.model_buttons.proxy_hires_cbx.currentIndexChanged.connect(partial(self.proxyHiresToggled.emit, self))
