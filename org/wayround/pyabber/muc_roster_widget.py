
import threading

from gi.repository import Gtk

import org.wayround.pyabber.jid_widget


class MUCRosterWidget:

    def __init__(self, room_jid_obj, controller, muc_roster_storage):

        self._room_jid_obj = room_jid_obj
        self._controller = controller
        self._muc_roster_storage = muc_roster_storage

        self._lock = threading.RLock()
        self._reordering_lock = threading.Lock()

        self._list = []

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        self._b = b

        self.sync_with_storage()

        muc_roster_storage.signal.connect(
            'set',
            self._on_muc_roster_storage_event
            )

        return

    def get_widget(self):
        return self._b

    def destroy(self):
        self._muc_roster_storage.signal.disconnect(
            self._on_muc_roster_storage_event
            )
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
        with self._lock:
            self.sync_with_storage()
            self.sort_jid_widgets()
        return

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

        with self._lock:
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

    def sort_jid_widgets(self):

        with self._reordering_lock:

            initial_sorting_list = []
            for i in self._list:
                t = i.get_nick()
                if t:
                    t = self._muc_roster_storage.get_item(t)
                    if t:
                        initial_sorting_list.append(t)

            final_sorting_list = []
            for i in ['moderator', 'none', 'participant', 'visitor', None]:
                rollers = []
                for j in initial_sorting_list:
                    if j.get_role() == i:
                        rollers.append(j)

                for j in ['owner', 'admin', 'member', 'outcast', 'none', None]:
                    affillers = []

                    for k in rollers:
                        if k.get_affiliation() == j:
                            affillers.append(k)

                    affillers.sort(key=lambda x: x.get_nick())
                    final_sorting_list += affillers

            for i in final_sorting_list:
                for j in self._list:
                    if j.get_nick() == i.get_nick():
                        self._b.reorder_child(j.get_widget(), -1)

        return

    def _widget_changed(self):
        self.sort_jid_widgets()
