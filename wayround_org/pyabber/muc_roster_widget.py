
import threading

from gi.repository import Gtk

import wayround_org.pyabber.jid_widget
import wayround_org.utils.gtk


class MUCRosterWidget:

    def __init__(self, room_jid_obj, controller, muc_roster_storage):

        self._room_jid_obj = room_jid_obj
        self._controller = controller
        self._muc_roster_storage = muc_roster_storage

        self._lock = threading.RLock()
        self._reordering_lock = threading.Lock()

        self._list = []

        self._sw = Gtk.ScrolledWindow()

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        self._b = b
        self._sw.add(b)

        self.sync_with_storage()

        self._on_muc_roster_storage_event_idle = \
            wayround_org.utils.gtk.to_idle(
                self._on_muc_roster_storage_event
                )

        muc_roster_storage.signal.connect(
            'set',
            self._on_muc_roster_storage_event_idle
            )

        return

    def get_widget(self):
        return self._sw

    def destroy(self):
        self._muc_roster_storage.signal.disconnect(
            self._on_muc_roster_storage_event_idle
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
            t = wayround_org.pyabber.jid_widget.MUCRosterJIDWidget(
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

            scroll_value = self._get_scroll_value()

            items = self._muc_roster_storage.get_items()

            i_n = self._get_nicks_in_items(items)
            l_n = self._get_nicks_in_list()

            for i in l_n:
                if not i in i_n:
                    self._remove_item(i)

            for i in i_n:
                if not i in l_n:
                    self._add_item(i)

            self._set_scroll_value(scroll_value)

        return

    def sort_jid_widgets(self):

        with self._reordering_lock:

            scroll_value = self._get_scroll_value()

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

                    affillers.sort(key=lambda x: str(x.get_nick()).lower())
                    final_sorting_list += affillers

            for i in final_sorting_list:
                for j in self._list:
                    if j.get_nick() == i.get_nick():
                        self._b.reorder_child(j.get_widget(), -1)

            self._set_scroll_value(scroll_value)

        return

    def _widget_changed(self):
        self.sort_jid_widgets()

    def _get_scroll_value(self):
        ret = None
        sb = self._sw.get_vscrollbar()
        if sb:
            adj = sb.get_adjustment()
            if adj:
                ret = adj.get_value()
        return ret

    def _set_scroll_value(self, value):
        if value != None:
            sb = self._sw.get_vscrollbar()
            if sb:
                adj = sb.get_adjustment()
                if adj:
                    adj.set_value(value)
        return
