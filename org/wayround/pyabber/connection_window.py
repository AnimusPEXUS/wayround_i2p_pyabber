
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Pango

import org.wayround.utils.gtk

import org.wayround.pyabber.main
import org.wayround.pyabber.ccc


class ConnectionMgrWindow:

    def __init__(self, main, profile):

        if not isinstance(main, org.wayround.pyabber.main.Main):
            raise ValueError("`main' must be org.wayround.pyabber.main.Main")

        if not isinstance(
            profile, org.wayround.pyabber.main.ProfileSession
            ):
            raise ValueError(
        "`profile' must be org.wayround.pyabber.main.ProfileSession"
                )

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_spacing(5)

        b.set_orientation(Gtk.Orientation.VERTICAL)

        conn_table = Gtk.TreeView()

        # FIXME: column additions looks too scary!

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        _c.set_title('Pst Nm')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 1)
        _c.set_title('Usr Nm')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 2)
        _c.set_title('Server')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 3)
        _c.set_title('Res Md')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 4)
        _c.set_title('Resours')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 5)
        _c.set_title('Mnl H/P?')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 6)
        _c.set_title('Host')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 7)
        _c.set_title('Port')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 8)
        _c.set_title('A SF?')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 9)
        _c.set_title('S.TLS')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 10)
        _c.set_title('Necess')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 11)
        _c.set_title('Verify')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 12)
        _c.set_title('Reg')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 13)
        _c.set_title('Log')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 14)
        _c.set_title('Bind')
        conn_table.append_column(_c)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 15)
        _c.set_title('Sess')
        conn_table.append_column(_c)

        conn_table_f = Gtk.Frame()
        sw = Gtk.ScrolledWindow()
        sw.add(conn_table)
        conn_table_f.add(sw)
        conn_table_f.set_label("Available Presets")

        conn_table.set_margin_left(5)
        conn_table.set_margin_right(5)
        conn_table.set_margin_top(5)
        conn_table.set_margin_bottom(5)

        bb01 = Gtk.ButtonBox()
        bb01.set_orientation(Gtk.Orientation.HORIZONTAL)
        bb01.set_margin_left(5)
        bb01.set_margin_right(5)
        bb01.set_margin_top(5)
        bb01.set_margin_bottom(5)
        bb01.set_spacing(5)

        bb01_ff = Gtk.Frame()
        bb01_ff.add(bb01)
        bb01_ff.set_label("Actions")

        but6 = Gtk.Button('Refresh')
        but1 = Gtk.Button('Open')
        but3 = Gtk.Button('New...')
        but4 = Gtk.Button('Edit...')
        but5 = Gtk.Button('Delete')

        bb01.pack_start(but6, False, True, 0)
        bb01.pack_start(but1, False, True, 0)
        bb01.pack_start(but3, False, True, 0)
        bb01.pack_start(but4, False, True, 0)
        bb01.pack_start(but5, False, True, 0)

        but1.connect('clicked', self._on_connect_clicked)
        but3.connect('clicked', self._on_new_clicked)
        but6.connect('clicked', self._on_refresh_clicked)
        but4.connect('clicked', self._on_edit_clicked)
        but5.connect('clicked', self._on_delete_clicked)

        b.pack_start(bb01_ff, False, True, 0)
        b.pack_start(conn_table_f, True, True, 0)

        self._conn_table = conn_table

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        window.add(b)

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._main = main
        self._profile = profile
        self._window = window

        return

    def run(self):
        self.show()
        self._iterated_loop.wait()
        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._iterated_loop.stop()
        self._window.destroy()

    def _on_destroy(self, window):
        self._window.hide()
        self._iterated_loop.stop()

    def _on_new_clicked(self, button):

        w = org.wayround.pyabber.connection_window.ConnectionPresetWindow(
            self.window_elements.window, typ='new'
            )
        r = w.run()
        w.destroy()

        result_code = r['button']

        del r['button']

        if result_code == 'ok':
            new_preset = {}
            new_preset.update(r)

            for i in range(
                len(self._profile.data['connection_presets']) - 1, -1, -1
                ):

                if (self._profile.data['connection_presets'][i]['name']
                    == new_preset['name']):
                    del self._profile._data['connection_presets'][i]

            self._profile.data['connection_presets'].append(new_preset)
            self._reload_list()
            self._profile.save()

    def _get_selection_name(self):

        items = self._conn_table.get_selection().get_selected_rows()[1]

        i_len = len(items)

        name = None

        if i_len == 0:
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Preset not selected"
                )
            d.run()
            d.destroy()

        else:

            name = self._conn_table.get_model()[items[0][0]][0]

        return name

    def _on_edit_clicked(self, button):

        name = self._get_selection_name()

        # FIXME: insanity here

        if name:

            w = org.wayround.pyabber.connection_window.ConnectionPresetWindow(
                self.window_elements.window,
                typ='edit',
                preset_name=name,
                preset_data=data
                )

            r = w.run()
            w.destroy()

            result_code = r['button']

            del r['button']

            if result_code == 'ok':
                new_preset = {}
                new_preset.update(r)

                for i in range(
                    len(self._profile.data['connection_presets']) - 1,
                    - 1,
                    - 1
                    ):

                    if (
                self._profile.data['connection_presets'][i]['name']
                == new_preset['name']
                        ):
                        del self._profile.data['connection_presets'][i]

                    elif (
                self._profile.data['connection_presets'][i]['name']
                == name
                        ):
                        del self._profile.data['connection_presets'][i]

                self._profile.data['connection_presets'].append(
                    new_preset
                    )

                self._profile.save()

        self._reload_list()

    def _on_delete_clicked(self, button):

        name = self._get_selection_name()

        if name:

            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "Do You really wish to delete profile `{}'".format(name)
                )
            r = d.run()
            d.destroy()

            if r == Gtk.ResponseType.YES:

                for i in range(
                    len(self._profile.data['connection_presets']) - 1,
                    - 1,
                    - 1
                    ):

                    if (
                self._profile.data['connection_presets'][i]['name']
                == name
                        ):
                        del self._profile.data['connection_presets'][i]

                self._main.profile.save()

        self._reload_list()

    def _on_connect_clicked(self, button):
        name = self._get_selection_name()

        already_exists = False
        for i in self._profile.connection_controllers:
            if i.preset_name == name:
                already_exists = True

        if not already_exists:
            org.wayround.pyabber.ccc.ClientConnectionController(
                self._main, self._profile, name
                )

    def _on_disconnect_clicked(self):
        self.disconnect()

    def _reload_list(self):

        storage = Gtk.ListStore(
            str,  # 0. name
            str,  # 1. username
            str,  # 2. server
            str,  # 3. resource mode
            str,  # 4. resource
            bool,  # 5. manual host, port
            str,  # 6. host
            int,  # 7. port
            str,  # 8. stream features handling mode
            bool,  # 9. starttls
            str,  # 10. starttls necessarity
            str,  # 11. starttls truest
            bool,  # 12. register
            bool,  # 13 .login
            bool,  # 14. bind
            bool  # 15. session
            )

        if (self._profile.data
            and 'connection_presets' in self._profile.data
            and isinstance(self._profile.data['connection_presets'], list)
            ):

            for i in self._profile.data['connection_presets']:
                storage.append(
                    [
                    i['name'],
                    i['username'],
                    i['server'],
                    i['resource_mode'],
                    i['resource'],
                    i['manual_host_and_port'],
                    i['host'],
                    i['port'],
                    i['stream_features_handling'],
                    i['STARTTLS'],
                    i['starttls_necessarity_mode'],
                    i['cert_verification_mode'],
                    i['register'],
                    i['login'],
                    i['bind'],
                    i['session']
                    ]
                    )

        self._conn_table.set_model(storage)

    def _on_refresh_clicked(self, button):
        self._reload_list()


# TODO: remove this
class Dumb:
    pass


class ConnectionPresetWindow:

    def __init__(self, parent, preset_name=None, preset_data=None, typ='new'):

        self._iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        if not typ in ['new', 'edit']:
            raise ValueError("`typ' must be in ['new', 'edit']")

        if typ in ['edit']:
            if not isinstance(preset_name, str):
                raise ValueError("in ['edit'] mode `preset_name' must be str")

            if not isinstance(preset_data, dict):
                raise ValueError("in ['edit'] mode `preset_data' must be dict")

        self.window_elements = Dumb()

        self.typ = typ

        win = Gtk.Window()

        title = "Creating New Connection Preset"

        if typ == 'edit':
            title = "Editing Connection Preset `{}'".format(preset_name)

        win.set_title(title)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        preset_name_ff = Gtk.Frame()
        preset_name_ff.set_label("Preset Name")
        preset_name_entry = Gtk.Entry()
        preset_name_entry.set_margin_top(5)
        preset_name_entry.set_margin_bottom(5)
        preset_name_entry.set_margin_left(5)
        preset_name_entry.set_margin_right(5)
        preset_name_ff.add(preset_name_entry)
        b.pack_start(preset_name_ff, False, True, 0)

        jid_ff = Gtk.Frame()
        b.pack_start(jid_ff, True, True, 0)
        jid_ff.set_label("Username")
        jid_grid = Gtk.Grid()
        jid_ff.add(jid_grid)

        pwd_ff = Gtk.Frame()
        b.pack_start(pwd_ff, True, True, 0)
        pwd_ff.set_label("Password")
        pwd_grid = Gtk.Grid()
        pwd_ff.add(pwd_grid)

        username_entry = Gtk.Entry()
        server_entry = Gtk.Entry()
        resource_switch_combobox = Gtk.ComboBox()
        resource_entry = Gtk.Entry()

        jid_grid.attach(Gtk.Label("JID:"), 0, 0, 1, 1)
        jid_grid.attach(username_entry, 1, 0, 1, 1)
        jid_grid.attach(Gtk.Label("@"), 2, 0, 1, 1)
        jid_grid.attach(server_entry, 3, 0, 1, 1)

        jid_grid.attach(Gtk.Label("/"), 0, 1, 1, 1)
        jid_grid.attach(resource_switch_combobox, 1, 1, 1, 1)
        jid_grid.attach(resource_entry, 3, 1, 1, 1)

        jid_grid.set_row_homogeneous(True)
        jid_grid.set_column_homogeneous(True)
        jid_grid.set_column_spacing(5)
        jid_grid.set_margin_top(5)
        jid_grid.set_margin_bottom(5)
        jid_grid.set_margin_left(5)
        jid_grid.set_margin_right(5)

        resource_switch_combobox.set_valign(Gtk.Align.CENTER)

        password_entry = Gtk.Entry()
        password_entry2 = Gtk.Entry()
        password_entry.set_hexpand(True)
        password_entry2.set_hexpand(True)

        password_entry.set_visibility(False)
        password_entry2.set_visibility(False)

        _l = Gtk.Label("Password:")
#        _l.set_hexpand(False)
        pwd_grid.attach(_l, 0, 0, 1, 1)
        _l = Gtk.Label("Confirm:")
#        _l.set_hexpand(False)
        pwd_grid.attach(_l, 0, 1, 1, 1)
        pwd_grid.attach(password_entry, 1, 0, 1, 1)
        pwd_grid.attach(password_entry2, 1, 1, 1, 1)

        pwd_grid.set_row_homogeneous(True)
        pwd_grid.set_row_spacing(5)
#        pwd_grid.set_column_homogeneous(True)
        pwd_grid.set_column_spacing(5)
        pwd_grid.set_margin_top(5)
        pwd_grid.set_margin_bottom(5)
        pwd_grid.set_margin_left(5)
        pwd_grid.set_margin_right(5)

        resource_switch_combobox_model = Gtk.ListStore(int, str)
        resource_switch_combobox_model.append([0, "Manual"])
        resource_switch_combobox_model.append([1, "Generate Locally"])
        resource_switch_combobox_model.append([2, "Let Server Generate"])

        resource_switch_combobox.set_model(resource_switch_combobox_model)
        resource_switch_combobox.set_id_column(0)

        renderer_text = Gtk.CellRendererText()
        resource_switch_combobox.pack_start(renderer_text, True)
        resource_switch_combobox.add_attribute(renderer_text, "text", 1)

        manual_server_ff = Gtk.Frame()
        b.pack_start(manual_server_ff, True, True, 0)
        manual_server_cb = Gtk.CheckButton.new_with_label(
            "Manual Host And Port Specification"
            )
        manual_server_ff.set_label_widget(manual_server_cb)

        host_port_grid = Gtk.Grid()
        manual_server_ff.add(host_port_grid)

        host_entry = Gtk.Entry()
        port_entry = Gtk.Entry()

        host_port_grid.attach(Gtk.Label("Host:"), 0, 0, 1, 1)
        host_port_grid.attach(host_entry, 1, 0, 1, 1)
        host_port_grid.attach(Gtk.Label("Port:"), 2, 0, 1, 1)
        host_port_grid.attach(port_entry, 3, 0, 1, 1)

        host_port_grid.set_row_homogeneous(True)
        host_port_grid.set_row_spacing(5)
        host_port_grid.set_column_homogeneous(True)
        host_port_grid.set_column_spacing(5)
        host_port_grid.set_margin_top(5)
        host_port_grid.set_margin_bottom(5)
        host_port_grid.set_margin_left(5)
        host_port_grid.set_margin_right(5)

        connection_routines_ff = Gtk.Frame()
        connection_routines_ff.set_label("Stream Features Handling")
        connection_routines_grid = Gtk.Grid()
        connection_routines_ff.add(connection_routines_grid)

        b.pack_start(connection_routines_ff, True, True, 0)

        connection_routines_grid.set_row_homogeneous(True)
        connection_routines_grid.set_row_spacing(5)
        connection_routines_grid.set_column_homogeneous(True)
        connection_routines_grid.set_column_spacing(5)
        connection_routines_grid.set_margin_top(5)
        connection_routines_grid.set_margin_bottom(5)
        connection_routines_grid.set_margin_left(5)
        connection_routines_grid.set_margin_right(5)

        auto_routines_rb = Gtk.RadioButton()
        auto_routines_rb.set_label("Automatic")

        manual_routines_rb = Gtk.RadioButton.new_from_widget(
            auto_routines_rb
            )
        manual_routines_rb.set_label("Manual")

        auto_routines_ff = Gtk.Frame()
        auto_routines_grid_or_box = Gtk.Grid()
        auto_routines_ff.add(auto_routines_grid_or_box)

        use_starttls_cb = Gtk.CheckButton.new_with_label("STARTTLS")

        register_cb = Gtk.CheckButton.new_with_label(
            "Register"
            )

        login_cb = Gtk.CheckButton.new_with_label("SASL Login")

        bind_cb = Gtk.CheckButton.new_with_label("Bind Resource")

        session_cb = Gtk.CheckButton.new_with_label(
            "Acquire Session if proposed\n"
            "(deprecated but required by some modern servers)"
            )

        tls_routines_ff = Gtk.Frame()
        tls_routines_ff.set_label_widget(use_starttls_cb)
        tls_routines_box = Gtk.Box()
        tls_routines_box.set_orientation(Gtk.Orientation.VERTICAL)
        tls_routines_ff.add(tls_routines_box)
        tls_routines_box.set_homogeneous(True)
        tls_routines_box.set_spacing(5)
        tls_routines_box.set_margin_top(5)
        tls_routines_box.set_margin_bottom(5)
        tls_routines_box.set_margin_left(5)
        tls_routines_box.set_margin_right(5)

        starttls_necessarity_mode_combobox = Gtk.ComboBox()
        starttls_necessarity_mode_combobox.set_valign(Gtk.Align.CENTER)

        starttls_necessarity_mode_combobox_model = Gtk.ListStore(int, str)
        starttls_necessarity_mode_combobox_model.append([0, "Necessary"])
        starttls_necessarity_mode_combobox_model.append(
            [1, "Can continue without TLS"]
            )

        starttls_necessarity_mode_combobox.set_model(
            starttls_necessarity_mode_combobox_model
            )
        starttls_necessarity_mode_combobox.set_id_column(0)

        renderer_text = Gtk.CellRendererText()
        starttls_necessarity_mode_combobox.pack_start(renderer_text, True)
        starttls_necessarity_mode_combobox.add_attribute(
            renderer_text, "text", 1
            )

        cert_verification_mode_combobox = Gtk.ComboBox()
        cert_verification_mode_combobox.set_valign(Gtk.Align.CENTER)

        cert_verification_mode_combobox_model = Gtk.ListStore(int, str)
        cert_verification_mode_combobox_model.append([0, "Must be Trusted"])
        cert_verification_mode_combobox_model.append([1, "Can be Self-Signed"])
        cert_verification_mode_combobox_model.append(
            [2, "Can be Self-Signed or Untrusted"]
            )
        cert_verification_mode_combobox_model.append([3, "No verification"])

        cert_verification_mode_combobox.set_model(
            cert_verification_mode_combobox_model
            )
        cert_verification_mode_combobox.set_id_column(0)

        renderer_text = Gtk.CellRendererText()
        cert_verification_mode_combobox.pack_start(renderer_text, True)
        cert_verification_mode_combobox.add_attribute(renderer_text, "text", 1)

        tls_routines_box.pack_start(
            starttls_necessarity_mode_combobox, False, True, 0
            )
        tls_routines_box.pack_start(
            cert_verification_mode_combobox, False, True, 0
            )

        auto_routines_grid_or_box.attach(tls_routines_ff, 0, 0, 1, 1)
        auto_routines_grid_or_box.attach(register_cb, 0, 1, 1, 1)
        auto_routines_grid_or_box.attach(login_cb, 0, 2, 1, 1)
        auto_routines_grid_or_box.attach(bind_cb, 0, 3, 1, 1)
        auto_routines_grid_or_box.attach(session_cb, 0, 4, 1, 1)

#        auto_routines_grid_or_box.set_row_homogeneous(True)
        auto_routines_grid_or_box.set_column_homogeneous(True)
        auto_routines_grid_or_box.set_row_spacing(5)
        auto_routines_grid_or_box.set_column_spacing(5)
        auto_routines_grid_or_box.set_margin_top(5)
        auto_routines_grid_or_box.set_margin_bottom(5)
        auto_routines_grid_or_box.set_margin_left(5)
        auto_routines_grid_or_box.set_margin_right(5)

        manual_routines_ff = Gtk.Frame()
        manual_routines_label = Gtk.Label(
            "After connect, you'll be brought to Stream Features"
            " tab to manually press the buttons :)"
            )
        manual_routines_label.set_line_wrap(True)
        manual_routines_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        manual_routines_label.set_margin_top(5)
        manual_routines_label.set_margin_bottom(5)
        manual_routines_label.set_margin_left(5)
        manual_routines_label.set_margin_right(5)

        manual_routines_ff.add(manual_routines_label)

        auto_routines_ff.set_label_widget(auto_routines_rb)
        manual_routines_ff.set_label_widget(manual_routines_rb)

        connection_routines_grid.attach(auto_routines_ff, 0, 0, 1, 1)
        connection_routines_grid.attach(manual_routines_ff, 1, 0, 1, 1)

        bb = Gtk.ButtonBox()

        cancel_button = Gtk.Button('Cancel')
        ok_button = Gtk.Button('Save')

        bb.pack_start(cancel_button, False, False, 0)
        bb.pack_start(ok_button, False, False, 0)

        bb.set_margin_top(5)
        bb.set_margin_bottom(5)
        bb.set_margin_left(5)
        bb.set_margin_right(5)

        b.pack_start(bb, False, False, 0)

        win.add(b)
        win.set_modal(True)
        win.set_transient_for(parent)
        win.set_destroy_with_parent(True)
        win.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        ok_button.set_can_default(True)
        win.set_default(ok_button)

        ok_button.connect('clicked', self._ok)
        cancel_button.connect('clicked', self._cancel)

        resource_switch_combobox.connect(
            'changed', self._resource_mode_changed
            )
        manual_server_cb.connect('toggled', self._manual_server_toggled)
        auto_routines_rb.connect('toggled', self._auto_routines_rb_toggled)
        manual_routines_rb.connect('toggled', self._manual_routines_rb_toggled)

        win.connect('destroy', self._window_destroy)

        self.window_elements.win = win
        self.window_elements.preset_name_entry = preset_name_entry
        self.window_elements.username_entry = username_entry
        self.window_elements.server_entry = server_entry
        self.window_elements.resource_switch_combobox = \
            resource_switch_combobox
        self.window_elements.resource_entry = resource_entry
        self.window_elements.password_entry = password_entry
        self.window_elements.password_entry2 = password_entry2
        self.window_elements.manual_server_cb = manual_server_cb
        self.window_elements.host_entry = host_entry
        self.window_elements.port_entry = port_entry
        self.window_elements.auto_routines_rb = auto_routines_rb
        self.window_elements.manual_routines_rb = manual_routines_rb
        self.window_elements.use_starttls_cb = use_starttls_cb
        self.window_elements.starttls_necessarity_mode_combobox = \
            starttls_necessarity_mode_combobox
        self.window_elements.cert_verification_mode_combobox = \
            cert_verification_mode_combobox
        self.window_elements.register_cb = register_cb
        self.window_elements.login_cb = login_cb
        self.window_elements.bind_cb = bind_cb
        self.window_elements.session_cb = session_cb

        self.window_elements.host_port_grid = host_port_grid
        self.window_elements.auto_routines_grid_or_box = \
            auto_routines_grid_or_box
        self.window_elements.manual_routines_label = manual_routines_label
        self.window_elements.cancel_button = cancel_button

        self.result = {
            'button': 'cancel',
            'name': 'name',
            'username': '',
            'server': '',
            'resource_mode': 'client',
            'resource': '',
            'password': '123',
            'password2': '1234',
            'manual_host_and_port': False,
            'host': '',
            'port': 5222,
            'stream_features_handling': 'auto',
            'STARTTLS': True,
            'starttls_necessarity_mode': 'necessary',
            'cert_verification_mode': 'can_selfsigned',
            'register': False,
            'login': True,
            'bind': True,
            'session': True
            }

        if typ == 'new':
            pass
        elif typ == 'edit':
            self.result.update(preset_data)

        preset_name_entry.set_text(self.result['name'])
        username_entry.set_text(self.result['username'])
        server_entry.set_text(self.result['server'])
        resource_entry.set_text(self.result['resource'])
        password_entry.set_text(self.result['password'])
        password_entry2.set_text(self.result['password2'])
        host_entry.set_text(self.result['host'])
        port_entry.set_text(str(self.result['port']))

        active_cb_value = 1

        if self.result['resource_mode'] == 'manual':
            active_cb_value = 0
        elif self.result['resource_mode'] == 'client':
            active_cb_value = 1
        elif self.result['resource_mode'] == 'server':
            active_cb_value = 2
        else:
            raise ValueError("Invalid result['resource_mode'] value")

        resource_switch_combobox.set_active(active_cb_value)

        active_cb_value = 0

        if self.result['starttls_necessarity_mode'] == 'necessary':
            active_cb_value = 0
        elif self.result['starttls_necessarity_mode'] == 'unnecessary':
            active_cb_value = 1
        else:
            raise ValueError(
                "Invalid result['starttls_necessarity_mode'] value"
                )

        starttls_necessarity_mode_combobox.set_active(active_cb_value)

        active_cb_value = 0

        if self.result['cert_verification_mode'] == 'trusted':
            active_cb_value = 0

        elif self.result['cert_verification_mode'] == 'can_selfsigned':
            active_cb_value = 1

        elif self.result['cert_verification_mode'] == \
            'can_selfsigned_can_untrusted':
            active_cb_value = 2

        elif self.result['cert_verification_mode'] == 'no_verification':
            active_cb_value = 3

        else:
            raise ValueError("Invalid result['cert_verification_mode'] value")

        cert_verification_mode_combobox.set_active(active_cb_value)

        manual_server_cb.set_active(self.result['manual_host_and_port'])
        self._manual_server_toggled(manual_server_cb)

        if self.result['stream_features_handling'] == 'auto':
            auto_routines_rb.set_active(True)
        else:
            manual_routines_rb.set_active(True)

        self._auto_routines_rb_toggled(auto_routines_rb)
        self._manual_routines_rb_toggled(manual_routines_rb)

        use_starttls_cb.set_active(self.result['STARTTLS'])
        register_cb.set_active(self.result['register'])
        login_cb.set_active(self.result['login'])
        bind_cb.set_active(self.result['bind'])
        session_cb.set_active(self.result['session'])

        return

    def run(self):

        self.window_elements.win.show_all()

        self._iteration_loop.wait()

        return self.result

    def destroy(self):
        self.window_elements.win.destroy()
        self._iteration_loop.stop()

    def _ok(self, button):

        name = self.window_elements.preset_name_entry.get_text()
        pwd1 = self.window_elements.password_entry.get_text()
        pwd2 = self.window_elements.password_entry2.get_text()

        if name == '':
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.win,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Name must be not empty"
                )
            d.run()
            d.destroy()
        else:

            if self.typ in ['new', 'edit'] and pwd1 != pwd2:
                d = org.wayround.utils.gtk.MessageDialog(
                    self.window_elements.win,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Password confirmation mismatch"
                    )
                d.run()
                d.destroy()
            else:

                if pwd1 == '':
                    d = org.wayround.utils.gtk.MessageDialog(
                        self.window_elements.win,
                        Gtk.DialogFlags.MODAL
                        | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Password must be not empty"
                        )
                    d.run()
                    d.destroy()
                else:

                    self.result['button'] = 'ok'

                    self.result['name'] = \
                        self.window_elements.preset_name_entry.get_text()

                    self.result['username'] = \
                        self.window_elements.username_entry.get_text()

                    self.result['server'] = \
                        self.window_elements.server_entry.get_text()

                    self.result['resource'] = \
                        self.window_elements.resource_entry.get_text()

                    self.result['password'] = \
                        self.window_elements.password_entry.get_text()

                    self.result['password2'] = \
                        self.window_elements.password_entry2.get_text()

                    self.result['host'] = \
                        self.window_elements.host_entry.get_text()

                    self.result['port'] = \
                        int(self.window_elements.port_entry.get_text())

                    active_cb_value = \
                        self.window_elements.\
                        resource_switch_combobox.get_active()

                    if active_cb_value == 0:
                        self.result['resource_mode'] = 'manual'
                    elif active_cb_value == 1:
                        self.result['resource_mode'] = 'client'
                    elif active_cb_value == 2:
                        self.result['resource_mode'] = 'server'
                    else:
                        raise ValueError(
                            "Invalid result['resource_switch_combobox'] value"
                            )

                    active_cb_value = \
                        self.window_elements.\
                            starttls_necessarity_mode_combobox.get_active()

                    if active_cb_value == 0:
                        self.result['starttls_necessarity_mode'] = 'necessary'
                    elif active_cb_value == 1:
                        self.result['starttls_necessarity_mode'] = \
                            'unnecessary'
                    else:
                        raise ValueError(
                            "Invalid result['starttls_necessarity_mode'] value"
                            )

                    active_cb_value = \
                        self.window_elements.\
                            cert_verification_mode_combobox.get_active()

                    if active_cb_value == 0:
                        self.result['cert_verification_mode'] = \
                            'trusted'

                    elif active_cb_value == 1:
                        self.result['cert_verification_mode'] = \
                            'can_selfsigned'

                    elif active_cb_value == 2:
                        self.result['cert_verification_mode'] = \
                            'can_selfsigned_can_untrusted'

                    elif active_cb_value == 3:
                        self.result['cert_verification_mode'] = \
                            'no_verification'
                    else:
                        raise ValueError(
                            "Invalid result['cert_verification_mode'] value"
                            )

                    self.result['manual_host_and_port'] = \
                        self.window_elements.manual_server_cb.get_active()

                    if (self.window_elements.auto_routines_rb.get_active()
                        == True):
                        self.result['stream_features_handling'] = 'auto'
                    else:
                        self.result['stream_features_handling'] = 'manual'

                    self.result['STARTTLS'] = \
                        self.window_elements.use_starttls_cb.get_active()

                    self.result['register'] = \
                        self.window_elements.register_cb.get_active()

                    self.result['login'] = \
                        self.window_elements.login_cb.get_active()

                    self.result['bind'] = \
                        self.window_elements.bind_cb.get_active()

                    self.result['session'] = \
                        self.window_elements.session_cb.get_active()

                    self.window_elements.win.destroy()

    def _cancel(self, button):

        self.result['button'] = 'cancel'
        self.window_elements.win.destroy()

    def _resource_mode_changed(self, checkbox):

        self.window_elements.resource_entry.set_sensitive(
            checkbox.get_active() == 0
            )

        return

    def _manual_server_toggled(self, cb):

        self.window_elements.host_port_grid.set_sensitive(cb.get_active())

    def _auto_routines_rb_toggled(self, cb):

        self.window_elements.auto_routines_grid_or_box.set_sensitive(
            cb.get_active()
            )

    def _manual_routines_rb_toggled(self, cb):

        self.window_elements.manual_routines_label.set_sensitive(
            cb.get_active()
            )

    def _window_destroy(self, window):

        self._iteration_loop.stop()
