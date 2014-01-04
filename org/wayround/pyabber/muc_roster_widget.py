
from gi.repository import Gtk

import org.wayround.pyabber.jid_widget


class MUCRosterWidget:

    def __init__(self, room_jid_obj, controller, muc_roster_storage):

        self._room_jid_obj = room_jid_obj
        self._controller = controller
        self._muc_roster_storage = muc_roster_storage

        self._list = []

        muc_roster_storage.connect_signal(
            True,
            self._on_muc_roster_storage_event
            )

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        self._b = b

        return

    def get_widget(self):
        return self._b

    def destroy(self):
        self._remove_all_items()
        self.get_widget().destroy()

    def _is_in(self, name):
        return self._get_item(name)

    def _get_item(self, name):
        ret = None
        for i in self._list:
            if i.get_nick() == name:
                ret = i
                break
        return ret

    def _add_item(self, name):
        if not self._is_in(name):
            t = org.wayround.pyabber.jid_widget.MUCRosterJIDWidget(
                self._room_jid_obj.bare(),
                name,
                self._controller,
                self._muc_roster_storage
                )
            self._list.append(t)
            self._b.pack_start(t.get_widget(), False, False, 0)

    def _remove_item(self, name):
        item = self._get_item(name)
        if item != None:
            item.destroy()
            self._list.remove(item)

    def _remove_all_items(self):
        for i in self._list[:]:
            i.destroy()
            self._list.remove(i)

    def _on_muc_roster_storage_event(self, event, storage, nick, item):
        self.sync_with_storage()

    def _get_nicks_in_list(self):

        ret = []

        for i in self._list:
            ret.append(i.get_nick())

        return list(set(ret))

    def _get_nicks_in_items(self, items):

        ret = []

        for i in items:
            ret.append(i.get_nick())

        return list(set(ret))

    def sync_with_storage(self):

        items = self._muc_roster_storage.get_items()

        i_n = self._get_nicks_in_items(items)
        l_n = self._get_nicks_in_list()

        for i in l_n:
            if not i in i_n:
                self._remove_item(i)

        for i in i_n:
            if not i in l_n:
                self._add_item(i)

        return
