

class PreferencesWidget:

    def __init__(self, controller):

        self._editable = False

        return

    def set_preferences(self, obj, editable):
        if isinstance(editable, bool):
            self.set_editable(editable)
        return

    def set_editable(self, value):
        self._editable = value == True
        return

    def get_editable(self):
        return self._editable
