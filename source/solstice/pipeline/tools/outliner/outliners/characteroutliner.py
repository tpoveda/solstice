class SolsticeCharactersOutliner(SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCharactersOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['character']

