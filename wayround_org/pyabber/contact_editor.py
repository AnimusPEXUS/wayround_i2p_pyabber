
from gi.repository import Gtk

import wayround_org.xmpp.core

import wayround_org.pyabber.roster_window


class ContactEditor:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

#        self._roster_window = roster_window

        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)

        jid_frame = Gtk.Frame()
        jid_frame.set_label("Jabber ID (JID)")

        jid_entry = Gtk.Entry()
        jid_entry.set_margin_top(5)
        jid_entry.set_margin_bottom(5)
        jid_entry.set_margin_start(5)
        jid_entry.set_margin_end(5)

        jid_frame.add(jid_entry)

        nick_box = Gtk.Box()
        nick_box.set_margin_top(5)
        nick_box.set_margin_bottom(5)
        nick_box.set_margin_start(5)
        nick_box.set_margin_end(5)

        nick_frame = Gtk.Frame()

        nick_box.set_orientation(Gtk.Orientation.VERTICAL)
        nick_box.set_margin_top(5)
        nick_box.set_margin_bottom(5)
        nick_box.set_margin_start(5)
        nick_box.set_margin_end(5)

        nick_edit = Gtk.Entry()

        nick_box.pack_start(nick_edit, False, False, 0)
        nick_box.pack_start(
            Gtk.Label("(leave empty to automatically use vCard or JID)"),
            False,
            False,
            0
            )

        nick_frame.add(nick_box)

        groups_frame = Gtk.Frame()

        groups_box = Gtk.Box()
        groups_box.set_margin_top(5)
        groups_box.set_margin_bottom(5)
        groups_box.set_margin_start(5)
        groups_box.set_margin_end(5)
        groups_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        available_g_box = Gtk.Box()
        available_g_box.set_orientation(Gtk.Orientation.VERTICAL)

        gr_entry_box = Gtk.Box()
        gr_entry_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        new_group_entry = Gtk.Entry()

        gr_entry_box.pack_start(
            Gtk.Label("Group"), False, False, 0
            )
        gr_entry_box.pack_start(
            new_group_entry, True, True, 0
            )
        gr_entry_box.set_spacing(5)

        f1 = Gtk.Frame()
        sw1 = Gtk.ScrolledWindow()
        f1.add(sw1)
        available_groups_treeview = Gtk.TreeView()
        sw1.add(available_groups_treeview)
        c1 = Gtk.TreeViewColumn()
        cr1 = Gtk.CellRendererText()
        c1.pack_start(cr1, False)
        c1.add_attribute(cr1, 'text', 0)
        available_groups_treeview.append_column(c1)
        available_groups_treeview.set_headers_visible(False)

        available_groups_treeview.get_selection().set_mode(
            Gtk.SelectionMode.MULTIPLE
            )

        available_g_box.pack_start(
            Gtk.Label("Available Groups"), False, False, 0
            )

        available_g_box.pack_start(gr_entry_box, False, False, 0)
        available_g_box.pack_start(f1, True, True, 0)
        available_g_box.set_spacing(5)

        action_g_box = Gtk.ButtonBox()
        action_g_box.set_orientation(Gtk.Orientation.VERTICAL)
        action_g_box.set_layout(Gtk.ButtonBoxStyle.CENTER)

        add_button = Gtk.Button("Add ->")
        remove_button = Gtk.Button("<- Remove")

        add_button.connect('clicked', self._on_add_clicked)
        remove_button.connect('clicked', self._on_rm_clicked)

        action_g_box.pack_start(add_button, False, False, 0)
        action_g_box.pack_start(remove_button, False, False, 0)

        current_g_box = Gtk.Box()
        current_g_box.set_orientation(Gtk.Orientation.VERTICAL)

        f2 = Gtk.Frame()
        sw2 = Gtk.ScrolledWindow()
        f2.add(sw2)
        current_groups_treeview = Gtk.TreeView()
        sw2.add(current_groups_treeview)
        c2 = Gtk.TreeViewColumn()
        cr2 = Gtk.CellRendererText()
        c2.pack_start(cr2, False)
        c2.add_attribute(cr2, 'text', 0)
        current_groups_treeview.append_column(c2)
        current_groups_treeview.set_headers_visible(False)

        current_groups_treeview.get_selection().set_mode(
            Gtk.SelectionMode.MULTIPLE
            )

        current_g_box.pack_start(Gtk.Label("Current Groups"), False, False, 0)
        current_g_box.pack_start(f2, True, True, 0)
        current_g_box.set_spacing(5)

        groups_box.pack_start(available_g_box, True, True, 0)
        groups_box.pack_start(action_g_box, False, False, 0)
        groups_box.pack_start(current_g_box, True, True, 0)

        sg = Gtk.SizeGroup()
        sg.set_mode(Gtk.SizeGroupMode.HORIZONTAL)
        sg.add_widget(available_g_box)
        sg.add_widget(current_g_box)

        groups_box.set_spacing(5)

        groups_frame.add(groups_box)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        save_button = Gtk.Button("Save")
        save_button.connect('clicked', self._on_save_clicked)

        bb.pack_start(save_button, False, False, 0)

        b.pack_start(jid_frame, False, False, 0)
        b.pack_start(nick_frame, False, False, 0)
        b.pack_start(groups_frame, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._available_groups_treeview = available_groups_treeview
        self._current_groups_treeview = current_groups_treeview
        self._groups_frame = groups_frame
        self._jid_entry = jid_entry
        self._jid_frame = jid_frame
        self._new_group_entry = new_group_entry
        self._nick_edit = nick_edit
        self._nick_frame = nick_frame
        self._window = window

        return

    def run(self, jid=None, mode='new'):
        if not mode in ['new', 'edit']:
            raise Exception("DNA Error")

        if mode == 'new':
            self._window.set_title("Edit Properties for New Roster Contact")
        else:
            self._window.set_title("Edit Properties for `{}'".format(jid))

        self._jid_frame.set_sensitive(mode == 'new')

        if mode == 'edit':
            self._jid_entry.set_text(jid)

        if mode == 'new':
            self._nick_frame.set_label("Nickname")
        else:
            self._nick_frame.set_label("Nickname for {}".format(jid))

        if mode == 'new':
            self._groups_frame.set_label("Groups")
        else:
            self._groups_frame.set_label("Groups for {}".format(jid))

        available_lst = Gtk.ListStore(str)
        current_lst = Gtk.ListStore(str)

        groups = self._controller.roster_storage.get_groups()
        groups.sort()

        for i in groups:
            available_lst.append([i])

        roster_data = self._controller.roster_storage.get_data()
        current_list = []

        if mode == 'edit' and jid in roster_data:
            current_list = list(roster_data[jid]['bare']['groups'])

        for i in current_list:
            current_lst.append([i])

        self._available_groups_treeview.set_model(available_lst)
        self._current_groups_treeview.set_model(current_lst)

        self.show()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()

    def _on_destroy(self, window):
        self.destroy()

    def _already_in(self, model, value):

        ret = False

        f = model.get_iter_first()

        while f != None:

            if model[f][0] == value:
                ret = True
                break

            f = model.iter_next(f)

        return ret

    def _on_add_clicked(self, button):

        ne = self._new_group_entry.get_text()

        sele = self._available_groups_treeview.get_selection()

        am, rows = sele.get_selected_rows()

        cm = self._current_groups_treeview.get_model()

        if ne != '':
            if not self._already_in(cm, ne):
                cm.append([ne])
            self._new_group_entry.set_text('')
        else:

            for i in rows:
                ne = am[am.get_iter(i)][0]
                if not self._already_in(cm, ne):
                    cm.append([ne])

        self._current_groups_treeview.set_model(cm)

        return

    def _on_rm_clicked(self, button):

        sele = self._current_groups_treeview.get_selection()

        am, rows = sele.get_selected_rows()

        rows2 = []

        for i in rows:
            rows2.append(Gtk.TreeRowReference.new(am, i))

        for i in rows2:

            am.remove(am.get_iter(i.get_path()))

        for i in rows2:
            if i.valid():
                i.free()

        self._current_groups_treeview.set_model(am)

        return

    def _on_save_clicked(self, button):

        lst = []

        mod = self._current_groups_treeview.get_model()

        it = mod.get_iter_first()

        while it:
            lst.append(mod[it][0])
            it = mod.iter_next(it)

        name = self._nick_edit.get_text()

        if name == '':
            name = None

        jid = wayround_org.xmpp.core.JID.new_from_str(
            self._jid_entry.get_text()
            )

        self._controller.roster_client.set(
            jid.bare(),
            groups=lst,
            name=name
            )

        self._window.destroy()

        return
