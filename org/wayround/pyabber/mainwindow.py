
import os.path
import glob
import sys
import threading
import pprint
import logging

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango

import org.wayround.utils.path
import org.wayround.utils.crypto
import org.wayround.utils.error
import org.wayround.utils.gtk

import org.wayround.pyabber.profilewindow
import org.wayround.pyabber.connpresetwindow
import org.wayround.pyabber.controller
import org.wayround.pyabber.rosterwidget
import org.wayround.pyabber.presence_control_popup
import org.wayround.pyabber.contact_popup_menu
import org.wayround.pyabber.icondb
import org.wayround.pyabber.contact_editor

class Dumb: pass

# testing account at wayround.org: tests@wayround.org : frtsAJlPIfCLdVn7qdzbLA==

class MainWindow:

    def __init__(self, pyabber_config='~/.config/pyabber'):

        self.controller = org.wayround.pyabber.controller.MainController(self)

        self.iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        pyabber_config = os.path.expanduser(pyabber_config)

        profiles_path = '{pyabber_config}/profiles'.format(
            pyabber_config=pyabber_config
            )

        self.profiles_path = profiles_path

        if not os.path.isdir(self.profiles_path):
            os.makedirs(self.profiles_path)


        self.window_elements = Dumb()

        org.wayround.pyabber.icondb.set_dir(
            org.wayround.utils.path.join(
                os.path.dirname(org.wayround.utils.path.abspath(__file__)),
                'icons'
                )
            )

        self.window_elements.window = Gtk.Window()

        window = self.window_elements.window

        window.set_icon(org.wayround.pyabber.icondb.get('pyabber'))
        window.set_title("Pyabber :P")
        window.maximize()
        window.set_hide_titlebar_when_maximized(True)
#        self.window_elements.window.set_decorated(False)
#        self.window_elements.window.set_resizable(False)

        main_box = Gtk.Box()

        main_notebook = Gtk.Notebook()

        xmpp_core_box = Gtk.Box()

        main_box.set_orientation(Gtk.Orientation.VERTICAL)


        main_notebook.set_property('tab-pos', Gtk.PositionType.TOP)

        xmpp_core_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        xmpp_core_box.pack_start(Gtk.Label("Text"), True, True, 0)


        _l = Gtk.Label("Program")
        _b = Gtk.Button("Exit")
        _b.connect('clicked', self.app_exit)
        _b.set_relief(Gtk.ReliefStyle.NONE)
        main_notebook.append_page(_b, _l)
        main_notebook.child_set_property(_b, 'tab-expand', True)

        _l = Gtk.Label("Profile")
        profile_tab = self._build_profile_tab()
        main_notebook.append_page(profile_tab, _l)
        main_notebook.child_set_property(profile_tab, 'tab-expand', True)

        _l = Gtk.Label("Connection")
        connection_tab = self._build_connection_tab()
        main_notebook.append_page(connection_tab, _l)
        main_notebook.child_set_property(connection_tab, 'tab-expand', True)

        _l = Gtk.Label("Stream Features")
        stream_features_tab = self._build_stream_features_tab()
        main_notebook.append_page(stream_features_tab, _l)
        main_notebook.child_set_property(stream_features_tab, 'tab-expand', True)

        _l = Gtk.Label("Messaging and Presence")
        messaging_and_presence_tab = self._build_messaging_and_presence()
        main_notebook.append_page(messaging_and_presence_tab, _l)
        main_notebook.child_set_property(messaging_and_presence_tab, 'tab-expand', True)

        _l = Gtk.Label("PubSub")
        main_notebook.append_page(Gtk.Label(""), _l)
#        main_notebook.child_set_property(profile_tab, 'tab-expand', True)

        _l = Gtk.Label("XMPP Explorer")
        main_notebook.append_page(Gtk.Label(""), _l)
#        main_notebook.child_set_property(profile_tab, 'tab-expand', True)

        _l = Gtk.Label("Status")
        status_tab = self._build_status_tab()
        main_notebook.append_page(status_tab, _l)
        main_notebook.child_set_property(status_tab, 'tab-expand', True)

        main_box.pack_start(main_notebook, True, True, 0)

        main_notebook.connect('switch-page', self.main_notebook_switch_page)

        window.add(main_box)

        self.profile_name = None
        self.profile_data = None
        self.profile_password = None
        self.preset_name = None
        self.preset_data = None

        self.client_working = False


        self.window_elements.window = window
        self.window_elements.profile_tab = profile_tab
        self.window_elements.connection_tab = connection_tab
        self.window_elements.stream_features_tab = stream_features_tab
        self.window_elements.main_notebook = main_notebook

        return

    def run(self):

        self.window_elements.window.show_all()

        self.window_elements.main_notebook.set_current_page(
            self.window_elements.main_notebook.page_num(
                self.window_elements.profile_tab
                )
            )

        self.iteration_loop.wait()

        return 0

    def _build_profile_tab(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        b2 = Gtk.Box()
        b2.set_orientation(Gtk.Orientation.HORIZONTAL)

        b3 = Gtk.Box()
        b3.set_orientation(Gtk.Orientation.VERTICAL)
        b3.set_spacing(5)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.VERTICAL)
        bb.set_spacing(3)

        but1 = Gtk.Button("Activate")
        but2 = Gtk.Button("Deactivate")
        but3 = Gtk.Button("New...")
        but4 = Gtk.Button("Change Password...")
        but5 = Gtk.Button("Save Now")
        but6 = Gtk.Button("Delete")
        but7 = Gtk.Button("Refresh List")

        but1.connect('clicked', self.profile_tab_activate_clicked)
        but2.connect('clicked', self.profile_tab_deactivate_clicked)
        but3.connect('clicked', self.profile_tab_new_clicked)
        but5.connect('clicked', self.profile_tab_save_clicked)
        but6.connect('clicked', self.profile_tab_delete_clicked)
        but7.connect('clicked', self.profile_tab_refresh_list_clicked)

        bb.pack_start(but1, False, True, 0)
        bb.pack_start(but2, False, True, 0)
        bb.pack_start(but3, False, True, 0)
        bb.pack_start(but4, False, True, 0)
        bb.pack_start(but5, False, True, 0)
        bb.pack_start(but6, False, True, 0)
        bb.pack_start(but7, False, True, 0)

        bb.set_homogeneous(True)

        bb.set_margin_left(5)
        bb.set_margin_right(5)
        bb.set_margin_top(5)
        bb.set_margin_bottom(5)

        ff1 = Gtk.Frame()
        ff1.add(bb)
        ff1.set_label("Actions")

        icon_view = Gtk.IconView()

        ff = Gtk.Frame()
        ff.add(icon_view)
        ff.set_margin_right(5)
        ff.set_label("Available Profiles")
        b2.pack_start(ff, True, True, 0)
        b2.pack_start(b3, False, True, 0)

        b3.pack_start(ff1, False, True, 0)

        profile_info_label = Gtk.Label("Currently opened profile info")

        ff2 = Gtk.Frame()
        ff2.add(profile_info_label)
        ff2.set_label("Current Profile")

        profile_info_label.set_margin_left(5)
        profile_info_label.set_margin_right(5)
        profile_info_label.set_margin_top(5)
        profile_info_label.set_margin_bottom(5)
        profile_info_label.set_line_wrap(True)
        profile_info_label.set_max_width_chars(10)

        b3.pack_start(ff2, True, True, 0)

        b.pack_start(b2, True, True, 0)

        self.window_elements.profile_icon_view = icon_view
        self.window_elements.profile_info_label = profile_info_label

        icon_view.connect('item-activated', self.profile_tab_iconview_item_activated)
#        b.set_sensitive(False)

        return b

    def _build_connection_tab(self):

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_spacing(5)

        b.set_orientation(Gtk.Orientation.VERTICAL)

        conn_table = Gtk.TreeView()

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
        conn_table_f.add(conn_table)
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

        bb01_ff = Gtk.Frame()
        bb01_ff.add(bb01)
        bb01_ff.set_label("Actions")

        but6 = Gtk.Button('Refresh')
        but1 = Gtk.Button('Connect')
        but2 = Gtk.Button('Disconnect')
        but3 = Gtk.Button('New...')
        but4 = Gtk.Button('Edit...')
        but5 = Gtk.Button('Delete')

        bb01.pack_start(but6, False, True, 0)
        bb01.pack_start(but1, False, True, 0)
        bb01.pack_start(but2, False, True, 0)
        bb01.pack_start(but3, False, True, 0)
        bb01.pack_start(but4, False, True, 0)
        bb01.pack_start(but5, False, True, 0)

        but1.connect('clicked', self.connections_tab_connect_clicked)
        but3.connect('clicked', self.connections_tab_new_clicked)
        but6.connect('clicked', self.connections_tab_refresh_clicked)
        but4.connect('clicked', self.connections_tab_edit_clicked)
        but5.connect('clicked', self.connections_tab_delete_clicked)


        b.pack_start(bb01_ff, False, True, 0)
        b.pack_start(conn_table_f, True, True, 0)

        self.window_elements.conn_table = conn_table
        self.window_elements.connection_tab_box = b

        return b

    def _build_stream_features_tab(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        featuress_grid_ff = Gtk.Frame()
        featuress_grid_ff.set_label("Proposed Stream Features")
        featuress_grid = Gtk.Grid()
        featuress_grid_ff.add(featuress_grid)

        featuress_grid.set_margin_top(5)
        featuress_grid.set_margin_bottom(5)
        featuress_grid.set_margin_left(5)
        featuress_grid.set_margin_right(5)


        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        activate_button = Gtk.Button('Activate')

        bb.pack_start(activate_button, True, True, 0)

        b.pack_start(featuress_grid_ff, True, True, 0)
        b.pack_start(bb, False, True, 0)

        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        return b

    def _build_messaging_and_presence(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        roster_box = Gtk.Box()
        roster_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        roster_tools_box = Gtk.Box()
        roster_tools_box.set_orientation(Gtk.Orientation.VERTICAL)

        roster_treeview = Gtk.TreeView()

        scrolled = Gtk.ScrolledWindow(None, None)
        scrolled.add(roster_treeview)

        scrolled.set_size_request(200, -1)

        roster_box.pack_start(roster_tools_box, False, False, 0)
        roster_box.pack_start(scrolled, True, True, 0)

        roster_toolbar_add_contact_button = Gtk.Button()
        roster_toolbar_initial_presence_button = Gtk.Button()
        roster_toolbar_bye_presence_button = Gtk.Button()
        roster_toolbar_get_roster_button = Gtk.Button()
        roster_toolbar_change_presence_button = Gtk.Button()
        roster_prind_data_button = Gtk.Button()

        self.presence_control_popup_window = (
            org.wayround.pyabber.presence_control_popup.PresenceControlPopup(
                self.window_elements.window,
                self
                )
            )

        add_contact_image = Gtk.Image()
        add_contact_image.set_from_pixbuf(org.wayround.pyabber.icondb.get('plus'))

        initial_presence_image = Gtk.Image()
        initial_presence_image.set_from_pixbuf(org.wayround.pyabber.icondb.get('initial_presence'))

        bye_presence_image = Gtk.Image()
        bye_presence_image.set_from_pixbuf(org.wayround.pyabber.icondb.get('bye_presence'))

        get_roster_image = Gtk.Image()
        get_roster_image.set_from_pixbuf(org.wayround.pyabber.icondb.get('refresh_roster'))

        new_presence_image = Gtk.Image()
        new_presence_image.set_from_pixbuf(org.wayround.pyabber.icondb.get('new_presence_button'))

        roster_toolbar_add_contact_button.set_image(add_contact_image)
        roster_toolbar_add_contact_button.connect(
            'clicked', self._on_add_contact_button_clicked
            )

        roster_toolbar_initial_presence_button.set_image(initial_presence_image)
        roster_toolbar_initial_presence_button.connect(
            "clicked", self._on_initial_presence_button_clicked
            )

        roster_toolbar_bye_presence_button.set_image(bye_presence_image)
        roster_toolbar_bye_presence_button.connect(
            "clicked", self._on_print_debug_data
            )


        roster_toolbar_get_roster_button.set_image(get_roster_image)
        roster_toolbar_get_roster_button.connect(
            "clicked", self._on_get_roster_button_clicked
            )


        roster_toolbar_change_presence_button.set_image(new_presence_image)
        roster_toolbar_change_presence_button.connect(
            "clicked", self._on_change_presence_button_clicked
            )

        roster_prind_data_button.connect(
            "clicked", self._on_prind_data_button_clicked
            )

        roster_tools_box.pack_start(roster_toolbar_add_contact_button, False, False, 0)
        roster_tools_box.pack_start(roster_toolbar_initial_presence_button, False, False, 0)
        roster_tools_box.pack_start(roster_toolbar_bye_presence_button, False, False, 0)
        roster_tools_box.pack_start(roster_toolbar_get_roster_button, False, False, 0)
        roster_tools_box.pack_start(roster_toolbar_change_presence_button, False, False, 0)
        roster_tools_box.pack_start(roster_prind_data_button, False, False, 0)

        main_paned = Gtk.Paned()
        main_paned.set_orientation(Gtk.Orientation.HORIZONTAL)

        messaging_notebook = Gtk.Notebook()


        main_paned.pack1(roster_box, False, True)
        main_paned.pack2(messaging_notebook, True, False)

        self.roster_widget = org.wayround.pyabber.rosterwidget.RosterWidget(
            roster_treeview, main_window=self
            )


#        print('333')
#        print(
#            "Result contacts:\n{}".format(
#                pprint.pformat(self.roster_widget.get_contacts())
#                )
#            )
#        print('444')

        b.pack_start(main_paned, True, True, 0)

        return b

    def _build_status_tab(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        return b

    def app_exit(self, user_data):
        self.iteration_loop.stop()

    def main_notebook_switch_page(self, notebook, page, pagenum):

        if page == self.window_elements.profile_tab:
            self.profile_tab_refresh_list()
            self.display_open_profile_info()

        elif page == self.window_elements.connection_tab:
            self.connections_tab_reload_list()
            self.window_elements.connection_tab_box.set_sensitive(
                isinstance(self.profile_data, dict)
                )
            self.connections_tab_reload_list()

    def new_stream_features(self, obj, attract_attention=False, disable_controls=True):
        # TODO: here must be a stream features tab constructor
        pass

    def connect(self, name, data):

        if not self.client_working:

            self.client_working = True
            self.preset_name = name
            self.preset_data = data

#            self.controller.start(
#                self,
#                self.profile_name,
#                self.profile_password,
#                self.profile_data,
#                self.preset_name,
#                self.preset_data
#                )

            threading.Thread(
                name="Chat Controller Thread",
                target=self.controller.start,
                args=(
                    self.profile_name,
                    self.profile_password,
                    self.profile_data,
                    self.preset_name,
                    self.preset_data,
                    )
                ).start()

    def disconnect(self):

        self.preset_name = None
        self.preset_data = None
        if self.client_working:

            if self.controller:
                self.controller.stop()

            self.controller = None


    def profile_tab_new_clicked(self, button):

        w = org.wayround.pyabber.profilewindow.ProfileWindow(
            self.window_elements.window, typ='new'
            )
        r = w.run()

        if r['button'] == 'ok':

            self.profile_tab_save(r['name'], {}, r['password'])

            self.profile_tab_refresh_list()

    def profile_tab_save_clicked(self, button):
        self.profile_tab_save_active()

    def profile_tab_save_active(self):
        self.profile_tab_save(
            self.profile_name,
            self.profile_data,
            self.profile_password
            )

    def profile_tab_save(self, name, data, password):

        if not isinstance(name, str) or not isinstance(data, dict):
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Profile not open - nothing to save"
                )
            d.run()
            d.destroy()

        else:

            if not 'connection_presets' in data:
                data['connection_presets'] = []

            by = org.wayround.utils.crypto.encrypt_data(data, password)

            f = open(
                org.wayround.utils.path.join(self.profiles_path, name + '.pfl'),
                'w'
                )

            f.write(by)

            f.close()


    def profile_tab_delete_clicked(self, button):

        items = self.window_elements.profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Profile not selected"
                )
            d.run()
            d.destroy()

        else:

            name = self.window_elements.profile_icon_view.get_model()[items[0]][0][:-4]

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
                pp = self.profiles_path

                profiles = org.wayround.utils.path.join(
                    pp, '{}.pfl'.format(name)
                    )

                try:
                    os.unlink(profiles)
                except:
                    d = org.wayround.utils.gtk.MessageDialog(
                        self.window_elements.window,
                        Gtk.DialogFlags.MODAL
                        | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Error while removing profile:\n\n{}".format(
                            org.wayround.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        )
                    d.run()
                    d.destroy()

            self.profile_tab_refresh_list()


    def profile_tab_deactivate_clicked(self, button):
        self.profile_name = None
        self.profile_data = None
        self.profile_password = None
        self.display_open_profile_info()

    def profile_tab_activate_clicked(self, button):

        items = self.window_elements.profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Profile not selected"
                )
            d.run()
            d.destroy()

        else:

            name = self.window_elements.profile_icon_view.get_model()[items[0]][0][:-4]

            w = org.wayround.pyabber.profilewindow.ProfileWindow(
                self.window_elements.window, typ='open', profile=name
                )
            r = w.run()

            if r['button'] == 'ok':

                self.profile_name = name

                f = open(
                    org.wayround.utils.path.join(
                        self.profiles_path, name + '.pfl'
                        ),
                    'r'
                    )

                by = f.read()

                f.close()

                self.profile_data = org.wayround.utils.crypto.decrypt_data(
                    by, r['password']
                    )

                self.profile_password = r['password']

                self.window_elements.main_notebook.set_current_page(
                    self.window_elements.main_notebook.page_num(
                        self.window_elements.connection_tab
                        )
                    )

        self.display_open_profile_info()

        return



    def profile_tab_refresh_list_clicked(self, button):

        self.profile_tab_refresh_list()
        self.display_open_profile_info()

    def profile_tab_refresh_list(self):

        selected = None

        items = self.window_elements.profile_icon_view.get_selected_items()

        if len(items) != 0:

            selected = items[0]

        pp = self.profiles_path

        profiles = glob.glob(org.wayround.utils.path.join(pp, '*.pfl'))

        profiles = org.wayround.utils.path.bases(profiles)

        profiles.sort()

        tree = Gtk.ListStore(str, GdkPixbuf.Pixbuf)

        for i in profiles:

            tree.append([i, org.wayround.pyabber.icondb.get('profile')])

        self.window_elements.profile_icon_view.set_model(tree)
        self.window_elements.profile_icon_view.set_text_column(0)
        self.window_elements.profile_icon_view.set_pixbuf_column(1)

        if selected:

            self.window_elements.profile_icon_view.select_path(selected)

    def profile_tab_iconview_item_activated(self, icon_view, path):
        self.profile_tab_activate_clicked(None)

    def display_open_profile_info(self):

        if not hasattr(self, 'profile_name') or not isinstance(self.profile_data, dict):
            self.window_elements.profile_info_label.set_text("Profile not activated")

        else:
            self.window_elements.profile_info_label.set_text(
                "Active profile is `{}'".format(self.profile_name)
                )

    def connections_tab_new_clicked(self, button):

        w = org.wayround.pyabber.connpresetwindow.ConnectionPresetWindow(
            self.window_elements.window, typ='new'
            )
        r = w.run()

        result_code = r['button']

        del r['button']

        if result_code == 'ok':
            new_preset = {}
            new_preset.update(r)

#            print("preset: {}".format(new_preset))

            for i in range(len(self.profile_data['connection_presets']) - 1, -1, -1):

                if self.profile_data['connection_presets'][i]['name'] == new_preset['name']:
                    del self.profile_data['connection_presets'][i]

            self.profile_data['connection_presets'].append(new_preset)
            self.connections_tab_reload_list()
            self.profile_tab_save_active()

    def connections_tab_get_selection_name_and_data(self):

        items = self.window_elements.conn_table.get_selection().get_selected_rows()[1]

        i_len = len(items)

        name = None
        data = None

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

            name = self.window_elements.conn_table.get_model()[items[0][0]][0]
            data = None

            for i in self.profile_data['connection_presets']:
                if i['name'] == name:
                    data = i
                    break

            if not data:

                d = org.wayround.utils.gtk.MessageDialog(
                    self.window_elements.window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Something isn't right here >:-|"
                    )
                d.run()
                d.destroy()

        if not name or not data:
            name = None
            data = None

        return name, data


    def connections_tab_edit_clicked(self, button):

        name, data = self.connections_tab_get_selection_name_and_data()

        if name and data:

            w = org.wayround.pyabber.connpresetwindow.ConnectionPresetWindow(
                self.window_elements.window,
                typ='edit',
                preset_name=name,
                preset_data=data
                )

            r = w.run()

            result_code = r['button']

            del r['button']

            if result_code == 'ok':
                new_preset = {}
                new_preset.update(r)

                for i in range(
                    len(self.profile_data['connection_presets']) - 1, -1, -1
                    ):

                    if self.profile_data['connection_presets'][i]['name'] == new_preset['name']:
                        del self.profile_data['connection_presets'][i]

                    elif self.profile_data['connection_presets'][i]['name'] == name:
                        del self.profile_data['connection_presets'][i]

                self.profile_data['connection_presets'].append(new_preset)
                self.profile_tab_save_active()

        self.connections_tab_reload_list()

    def connections_tab_delete_clicked(self, button):

        name, data = self.connections_tab_get_selection_name_and_data()

        if name and data:

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
                    len(self.profile_data['connection_presets']) - 1, -1, -1
                    ):

                    if self.profile_data['connection_presets'][i]['name'] == name:
                        del self.profile_data['connection_presets'][i]

                self.profile_tab_save_active()

        self.connections_tab_reload_list()

    def connections_tab_connect_clicked(self, button):
        name, data = self.connections_tab_get_selection_name_and_data()
        if name and data:
            self.connect(name, data)

    def connections_tab_disconnect_clicked(self):
        self.disconnect()


    def connections_tab_reload_list(self):

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

        if (self.profile_data
            and 'connection_presets' in self.profile_data
            and isinstance(self.profile_data['connection_presets'], list)
            ):

            for i in self.profile_data['connection_presets']:
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

        self.window_elements.conn_table.set_model(storage)


    def connections_tab_refresh_clicked(self, button):
        self.connections_tab_reload_list()

    def _on_get_roster_button_clicked(self, button):

        res = self.controller.roster.get(jid_from=self.controller.jid.full())
        logging.debug("Roster Get Result: {}".format(pprint.pformat(res)))

        if res == None:
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Roster retrieval attempt returned not a stanza"
                )
            d.run()
            d.destroy()
        else:
            if org.wayround.xmpp.core.is_stanza(res) and res.is_error():
                d = org.wayround.utils.gtk.MessageDialog(
                    self.window_elements.window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting roster:\n{}".format(repr(res.get_error()))
                    )
                d.run()
                d.destroy()

            elif org.wayround.xmpp.core.is_stanza(res) and not res.is_error():

                d = org.wayround.utils.gtk.MessageDialog(
                    self.window_elements.window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Unexpected return value:\n{}".format(res)
                    )
                d.run()
                d.destroy()

            elif isinstance(res, dict):
                conts = self.roster_widget.get_contacts()

                for i in res.keys():
                    self.roster_widget.set_contact(
                        name_or_title=res[i]['name'],
                        bare_jid=i,
                        groups=res[i]['groups'],
                        approved=res[i]['approved'],
                        ask=res[i]['ask'],
                        subscription=res[i]['subscription']
                        )

                for i in conts:
                    if not i in res:
                        self.roster_widget.set_contact(
                            bare_jid=i,
                            not_in_roster=True
                            )
            else:
                raise Exception("DNA error")

    def _on_add_contact_button_clicked(self, button):

        w = org.wayround.pyabber.contact_editor.ContactEditor(
            self.controller
            )
        w.show()

    def _on_initial_presence_button_clicked(self, button):
        self.controller.presence.presence()

    def _on_print_debug_data(self, button):
        pass

    def _on_change_presence_button_clicked(self, button):
        self.presence_control_popup_window.show()

    def _on_prind_data_button_clicked(self, button):
        pprint.pprint(self.roster_widget.get_data())
