
import threading

from gi.repository import Gtk

import wayround_org.pyabber.jid_widget
import wayround_org.utils.gtk
import wayround_org.xmpp.core
import wayround_org.xmpp.disco


ROSTER_WIDGET_MODE_LIST = [
    'grouped',
    'ungrouped',
    'all',
    'ask',
    'to',
    'from',
    'none',
    'services',
    'unknown'
    ]

ROSTER_WIDGET_MODE_LIST_TITLES = {
    'grouped': 'Grouped',
    'ungrouped': 'Ungrouped',
    'all': 'All',
    'ask': 'Asking',
    'to': 'Only To',
    'from': 'Only From',
    'none': 'Not in Roster',
    'services': 'Services',
    'unknown': 'Unknown'
    }

JID_ORDERING_MODEL = Gtk.ListStore(str, str)
JID_ORDERING_MODEL.append(['jid', 'By JID'])
JID_ORDERING_MODEL.append(['title', 'By Title'])


class RosterWidget:

    def __init__(self, controller, roster_storage, mode='all'):

        self._controller = controller
        self._roster_storage = roster_storage

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        roster_tools_box = Gtk.Box()
        roster_tools_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        roster_tools_box.set_spacing(5)

        jid_box = Gtk.FlowBox()
        self._jid_box = jid_box
        jid_box.set_orientation(Gtk.Orientation.VERTICAL)
        jid_box.set_row_spacing(2)
        jid_box.set_column_spacing(2)
#        jid_box.set_spacing(2)
        jid_box.set_margin_top(5)
        jid_box.set_margin_start(5)
        jid_box.set_margin_end(5)
        jid_box.set_margin_bottom(5)
        jid_box.set_homogeneous(False)
        jid_box.set_sort_func(self._sort, None, None)

        jid_box_frame = Gtk.Frame()
        jid_box_sw = Gtk.ScrolledWindow()
        jid_box_frame.add(jid_box_sw)
        jid_box_sw.add(jid_box)

        order_combobox = Gtk.ComboBox()
        self._order_combobox = order_combobox
        renderer_text = Gtk.CellRendererText()
        order_combobox.pack_start(renderer_text, True)
        order_combobox.add_attribute(renderer_text, "text", 1)
        order_combobox.set_model(JID_ORDERING_MODEL)
        order_combobox.set_active(0)

        groups_model = Gtk.ListStore(str, str)  # name, title
        self._groups_model = groups_model

        groups_combobox = Gtk.ComboBox()
        self._groups_combobox = groups_combobox
        renderer_text = Gtk.CellRendererText()
        groups_combobox.pack_start(renderer_text, True)
        groups_combobox.add_attribute(renderer_text, "text", 1)

        groups_combobox.set_model(groups_model)
        groups_combobox.set_active(0)
        roster_tools_box.pack_start(groups_combobox, False, False, 0)
        roster_tools_box.pack_start(order_combobox, False, False, 0)

        b.pack_start(roster_tools_box, False, False, 0)
        b.pack_start(jid_box_frame, True, True, 0)

        self._reloading_list = False
        self._main_widget = b

        self._lock = threading.Lock()
        self._add_remove_lock = threading.Lock()
        self._list = []

        self._groups_combobox.set_no_show_all(True)

        b.show_all()

        self._on_groups_combobox_changed_idle = \
            wayround_org.utils.gtk.to_idle(
                self._on_groups_combobox_changed
                )

        self._set_cb_signal()

        self.set_mode(mode)
        self.set_group('')

        self._on_order_combobox_changed_idle = \
            wayround_org.utils.gtk.to_idle(self._on_order_combobox_changed)

        order_combobox.connect(
            'changed',
            self._on_order_combobox_changed_idle
            )

        self._roster_storage_listener_idle = \
            wayround_org.utils.gtk.to_idle(self._roster_storage_listener)

        self._roster_storage.signal.connect(
            True,
            self._roster_storage_listener_idle
            )

        return

    def destroy(self):
        self._clear_list()
        self.get_widget().destroy()

        return

    def get_widget(self):
        return self._main_widget

    def set_mode(self, name):

        if not name in ROSTER_WIDGET_MODE_LIST:
            raise ValueError("Invalid Mode")

        self._lock.acquire()
        self._mode = name
        self._groups_combobox.set_visible(name == 'grouped')
        self._reload_list()
        self._lock.release()

        return

    def get_group(self):
        self._lock.acquire()
        ret = self._get_group()
        self._lock.release()
        return ret

    def _get_group(self):
        ret = None
        x = self._groups_combobox.get_active()
        if x in range(len(self._groups_model)):
            ret = self._groups_model[x][0]
        return ret

    def set_group(self, name):
        self._lock.acquire()
        self._set_group(name)
        self._reload_list()
        self._lock.release()

        return

    def _set_groups(self, lst):
        lst.sort()
        while len(self._groups_model) != 0:
            del self._groups_model[0]

        self._groups_model.append(['', ''])

        for i in lst:
            self._groups_model.append([i, i])

        return

    def _set_group(self, name):
        x = -1
        for i in range(len(self._groups_model)):
            if self._groups_model[i][0] == name:
                x = i
                break
        self._groups_combobox.set_active(x)
        return

    def _is_service(self, subject_jid_object):
        return subject_jid_object.is_domain()

    def _is_in_current_group(self, subject_jid_object, data):
        g = self._get_group()
        return (
            g == ''
            or
            self._is_in_group(subject_jid_object, g, data)
            )

    def _is_in_group(self, subject_jid_object, group_name, data):
        return (
            group_name in data[subject_jid_object.bare()]['bare']['groups']
            )

    def _is_ungrouped(self, subject_jid_object, data):
        return len(data[subject_jid_object.bare()]['bare']['groups']) == 0

    def _is_self(self, subject_jid_object):
        ret = subject_jid_object.bare() == self._controller.jid.bare()
        return ret

    def _is_normal_contact(self, subject_jid_object):
        return (
            not self._is_self(subject_jid_object)
            and
            not self._is_service(subject_jid_object)
            )

    def reload_list(self):
        self._lock.acquire()
        self._reload_list()
        self._lock.release()
        return

    def _reload_list(self):

        data = self._roster_storage.get_data()

        for i in list(data.keys()):

            subject_jid_object = wayround_org.xmpp.core.JID.new_from_str(i)

            self._add_or_remove(
                i,
                not self._is_self(subject_jid_object) and
                (
                    (self._mode == 'all')
                    or
                    (
                        self._mode == 'grouped'
                        and
                        self._is_in_current_group(subject_jid_object, data)
                        and
                        self._is_normal_contact(subject_jid_object)
                        and
                        data[i]['bare']['subscription'] == 'both'
                        )
                    or
                    (
                        self._mode == 'ungrouped'
                        and
                        self._is_ungrouped(subject_jid_object, data)
                        and
                        self._is_normal_contact(subject_jid_object)
                        and
                        data[i]['bare']['subscription'] == 'both'
                        )
                    or
                    (
                        self._mode == 'services'
                        and
                        self._is_service(subject_jid_object)
                        )
                    or
                    (
                        self._mode == 'ask'
                        and
                        data[i]['bare']['ask'] == True
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
                        self._mode == 'none'
                        and
                        data[i]['bare']['subscription'] == 'none'
                        )
                    )
                )

        self._jid_box.invalidate_sort()

#        ordering_name = \
#            JID_ORDERING_MODEL[self._order_combobox.get_active()][0]
#
#        ol = []
#        od = {}
#        for i in self._list:
#            _t = ''
#            if ordering_name == 'jid':
#                _t = i.get_jid()
#            elif ordering_name == 'title':
#                _t = i.get_title()
#
#            ol.append(_t)
#            if not _t in od:
#                od[_t] = []
#            od[_t].append(i)
#
#        ol.sort()
#        for i in ol:
#            for j in od[i]:
#                self._jid_box.reorder_child(j.get_widget(), -1)

        return

    def _sort(self, c1, c2, *args):

        w1 = self._get_widget_obj_by_gtk_widget(c1.get_child())
        w2 = self._get_widget_obj_by_gtk_widget(c2.get_child())

        ret = 0

        ordering_name = \
            JID_ORDERING_MODEL[self._order_combobox.get_active()][0]

        if w1 is not None and w2 is not None:
            v1 = None
            v2 = None

            if ordering_name == 'jid':
                v1 = w1.get_jid()
                v2 = w2.get_jid()
            elif ordering_name == 'title':
                v1 = w1.get_title()
                v2 = w2.get_title()

            if v1 == v2:
                ret = 0
            elif v1 > v2:
                ret = 1
            elif v1 < v2:
                ret = -1
            else:
                pass

        return ret

    def _get_widget_obj_by_gtk_widget(self, gtk_widget):

        ret = None
        for i in self._list:
            if i.get_widget() == gtk_widget:
                ret = i
                break
        return ret

    def _clear_list(self):

        for i in self._list[:]:
            i.destroy()
            self._list.remove(i)

        return

    def _remove_cb_signal(self):
        try:
            self._groups_combobox.disconnect_by_func(
                self._on_groups_combobox_changed_idle
                )
        except:
            pass

        return

    def _set_cb_signal(self):
        self._remove_cb_signal()
        # FIXME: re do this by making/using object attribute
        self._groups_combobox.connect(
            'changed',
            self._on_groups_combobox_changed_idle
            )

        return

    def _roster_storage_listener(
            self,
            event, roster_storage,
            bare_jid, resource, data, jid_data
            ):

        self._lock.acquire()

        if self._mode == 'grouped':

            self._remove_cb_signal()

            group = self._get_group()

            groups = self._roster_storage.get_groups()
            self._set_groups(groups)

            self._set_group(group)

            if self._groups_combobox.get_active() == -1:
                self._groups_combobox.set_active(0)

            self._set_cb_signal()

        self._reload_list()

        self._lock.release()

        return

    def _add_or_remove(self, bare_jid, add=False):
        with self._add_remove_lock:
            if add:
                self._add_jid_widget(bare_jid)
            else:
                self._remove_jid_widget(bare_jid)
        return

    def _add_jid_widget(self, bare_jid):

        if not self._is_in_roster(bare_jid):

            jw = wayround_org.pyabber.jid_widget.JIDWidget(
                controller=self._controller,
                roster_storage=self._roster_storage,
                bare_jid=bare_jid
                )
            w = jw.get_widget()

            self._list.append(jw)
            self._jid_box.add(w)

            w.set_hexpand(False)
            w.set_vexpand(False)


        return

    def _remove_jid_widget(self, bare_jid):

        for i in self._list[:]:
            if i.get_jid() == bare_jid:

                for j in self._jid_box.get_children()[:]:
                    chi = self._get_widget_obj_by_gtk_widget(j)
                    if chi != i:
                        j.destroy()

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

    def _on_groups_combobox_changed(self, widget):
        self._lock.acquire()
        self._reload_list()
        self._lock.release()

        return

    def _on_order_combobox_changed(self, widget):
        self._lock.acquire()
        self._jid_box.invalidate_sort()
        self._lock.release()

        return
