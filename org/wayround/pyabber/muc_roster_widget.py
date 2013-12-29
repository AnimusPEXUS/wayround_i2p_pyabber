
from gi.repository import Gtk


class MUCRosterWidget:

    def __init__(self, room_jid_obj, controller, muc_roster_storage):

        self._room_jid_obj = room_jid_obj
        self._controller = controller
        self._muc_roster_storage = muc_roster_storage

        self._dict = {}

        muc_roster_storage.connect_event(
            True,
            self._on_muc_roster_storage_event
            )

        return

    def _on_muc_roster_storage_event(self, event):
        return
