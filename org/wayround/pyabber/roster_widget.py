
import threading

from gi.repository import Gtk

import org.wayround.pyabber.jid_widget
import org.wayround.xmpp.core


ROSTER_WIDGET_MODE_LIST = [
    'all', 'grouped', 'ungrouped', 'transports', 'services',
    'ask', 'to', 'from', 'none', 'not_in_roster_soft', 'not_in_roster_hard'
    ]


class RosterWidget:

    def __init__(self, controller, roster_storage, mode='all'):

        self._controller = controller
        self._roster_storage = roster_storage

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        roster_tools_box = Gtk.Box()
        roster_tools_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        jid_box = Gtk.Box()
        self._jid_box = jid_box
        jid_box.set_orientation(Gtk.Orientation.VERTICAL)
        jid_box.set_spacing(5)
        jid_box.set_margin_top(5)
        jid_box.set_margin_left(5)
        jid_box.set_margin_right(5)
        jid_box.set_margin_bottom(5)

        jid_box_frame = Gtk.Frame()
        jid_box_sw = Gtk.ScrolledWindow()
        jid_box_frame.add(jid_box_sw)
        jid_box_sw.add(jid_box)

        groups_model = Gtk.ListStore(str, str)  # name, title

        groups_combobox = Gtk.ComboBox()
        self._groups_combobox = groups_combobox
        renderer_text = Gtk.CellRendererText()
        groups_combobox.pack_start(renderer_text, True)
        groups_combobox.add_attribute(renderer_text, "text", 1)

        groups_combobox.set_model(groups_model)
        roster_tools_box.pack_start(groups_combobox, False, False, 0)

        b.pack_start(roster_tools_box, False, False, 0)
        b.pack_start(jid_box_frame, True, True, 0)

        self._reloading_list = False
        self._main_widget = b

        self._lock = threading.Lock()
        self._list = []

        self._groups_combobox.set_no_show_all(True)

        b.show_all()

        self.set_mode(mode)

        self._roster_storage.connect_signal(
            True,
            self._roster_storage_listener
            )

        return

    def destroy(self):
        self._clear_list()
        self.get_widget().destroy()

    def get_widget(self):
        return self._main_widget

    def set_mode(self, name):

        if not name in ROSTER_WIDGET_MODE_LIST:
            raise ValueError("Invalid Mode")

        self._mode = name
        self._groups_combobox.set_visible(name == 'grouped')
        self._reload_list()

    def _reload_list(self):

        self._lock.acquire()

        data = self._roster_storage.get_data()

        own_jid = self._controller.jid.bare()

        for i in list(data.keys()):

            j = org.wayround.xmpp.core.JID.new_from_str(i)

            self._add_or_remove(
                i,
                i != own_jid
                and
                (
                 self._mode == 'all'
                 and
                 not j.is_domain()
                 )
                 or
                (
                 self._mode == 'grouped'
                 and
                 not j.is_domain()
                 )
                or
                (
                 self._mode == 'services'
                 and
                 j.is_domain()
                 )
                or
                (
                 self._mode == 'to'
                 and
                 data[i]['bare']['subscription'] == 'to'
                 )
                or
                (
                 self._mode == 'from'
                 and
                 data[i]['bare']['subscription'] == 'from'
                 )
                or
                (
                 self._mode == 'not_in_roster_soft'
                 and
                 data[i]['bare']['subscription'] == 'none'
                 )
                or
                (
                 self._mode == 'not_in_roster_hard'
                 and
                 data[i]['bare']['not_in_roster'] == True
                 )
                )

        self._lock.release()

        return

    def _clear_list(self):

        for i in self._list[:]:
            i.destroy()
            self._list.remove(i)

    def _roster_storage_listener(
        self,
        event, roster_storage,
        bare_jid, data, jid_data
        ):

        self._reload_list()

    def _add_or_remove(self, bare_jid, add=False):
        if add:
            self._add_jid_widget(bare_jid)
        else:
            self._remove_jid_widget(bare_jid)

    def _add_jid_widget(self, bare_jid):

        if not self._is_in_roster(bare_jid):

            jw = org.wayround.pyabber.jid_widget.JIDWidget(
                controller=self._controller,
                roster_storage=self._roster_storage,
                bare_jid=bare_jid
                )
            self._list.append(jw)
            self._jid_box.pack_start(jw.get_widget(), False, False, 0)

    def _remove_jid_widget(self, bare_jid):
        for i in self._list[:]:
            if i.get_jid() == bare_jid:
                i.destroy()
                self._list.remove(i)

        return

    def _is_in_roster(self, bare_jid):
        found = False
        for j in self._list:
            if j.get_jid() == bare_jid:
                found = True
                break
        return found
