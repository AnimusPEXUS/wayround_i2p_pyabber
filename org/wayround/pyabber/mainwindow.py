
import os.path
import glob
import sys

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango

import org.wayround.utils.path
import org.wayround.utils.crypto
import org.wayround.utils.error

import org.wayround.pyabber.profilewindow

class MainWindow:

    def __init__(self, pyabber_config='~/.config/pyabber'):

        pyabber_config = os.path.expanduser(pyabber_config)

        profiles_path = '{pyabber_config}/profiles'.format(
            pyabber_config=pyabber_config
            )

        self.profiles_path = profiles_path

        if not os.path.isdir(self.profiles_path):
            os.makedirs(self.profiles_path)

        self._load_pixbufs()

        self.window = Gtk.Window()

        self.window.set_icon(self.icons['pyabber'])
        self.window.set_title("Pyabber :P")
        self.window.maximize()
        self.window.set_hide_titlebar_when_maximized(True)
#        self.window.set_decorated(False)
#        self.window.set_resizable(False)

        main_box = Gtk.Box()

        main_notebook = Gtk.Notebook()

        xmpp_core_box = Gtk.Box()

        main_box.set_orientation(Gtk.Orientation.VERTICAL)


        main_notebook.set_property('tab-pos', Gtk.PositionType.TOP)

        xmpp_core_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        xmpp_core_box.pack_start(Gtk.Label("Text"), True, True, 0)


        _l = Gtk.Label("Program")
#        _l.set_width_chars(25)
        _b = Gtk.Button("Exit")
        _b.connect('clicked', self.app_exit)
        _b.set_relief(Gtk.ReliefStyle.NONE)
        main_notebook.append_page(_b, _l)

        _l = Gtk.Label("Profile")
#        _l.set_width_chars(25)
        self.profile_tab = self._build_profile_tab()
        main_notebook.append_page(self.profile_tab, _l)

        _l = Gtk.Label("Connection")
#        _l.set_width_chars(25)
        main_notebook.append_page(self._build_connection_tab(), _l)

        _l = Gtk.Label("Server Features")
#        _l.set_width_chars(25)
        main_notebook.append_page(Gtk.Label(), _l)

        _l = Gtk.Label("Roster and Stanzas")
#        _l.set_width_chars(25)
        main_notebook.append_page(xmpp_core_box, _l)

        main_box.pack_start(main_notebook, True, True, 0)

        main_notebook.connect('switch-page', self.main_notebook_switch_page)

        self.window.add(main_box)

        self.profile_name = None
        self.profile_data = None

        return

    def _load_pixbufs(self):

        _dir = os.path.dirname(org.wayround.utils.path.abspath(__file__))

        icons = {}
        for i in ['pyabber', 'profile']:
            icons[i] = GdkPixbuf.Pixbuf.new_from_file(
                org.wayround.utils.path.join(_dir, 'icons', i + '.png')
                )

        self.icons = icons


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

        self.profile_info_label = Gtk.Label("Currently opened profile info")

        ff2 = Gtk.Frame()
        ff2.add(self.profile_info_label)
        ff2.set_label("Current Profile")

        self.profile_info_label.set_margin_left(5)
        self.profile_info_label.set_margin_right(5)
        self.profile_info_label.set_margin_top(5)
        self.profile_info_label.set_margin_bottom(5)

        b3.pack_start(ff2, True, True, 0)

        self.profile_info_label.set_line_wrap(True)
        self.profile_info_label.set_max_width_chars(10)



        b.pack_start(b2, True, True, 0)

        self.profile_icon_view = icon_view

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

        b01 = Gtk.Box()
        b01.set_spacing(5)
        b01.set_orientation(Gtk.Orientation.VERTICAL)

        conn_table = Gtk.TreeView()

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

        but1 = Gtk.Button('Connect')
        but2 = Gtk.Button('Disconnect')
        but3 = Gtk.Button('New...')
        but4 = Gtk.Button('Edit...')
        but5 = Gtk.Button('Delete')

        bb01.pack_start(but1, False, True, 0)
        bb01.pack_start(but2, False, True, 0)
        bb01.pack_start(but3, False, True, 0)
        bb01.pack_start(but4, False, True, 0)
        bb01.pack_start(but5, False, True, 0)


        b01.pack_start(bb01_ff, False, True, 0)
        b01.pack_start(conn_table_f, True, True, 0)

        b.pack_start(b01, True, True, 0)

        return b

    def app_exit(self, user_data):

        Gtk.main_quit()

    def main_notebook_switch_page(self, notebook, page, pagenum):

        if page == self.profile_tab:
            self.profile_tab_refresh_list()
            self.display_open_profile_info()

    def profile_tab_new_clicked(self, button):

        w = org.wayround.pyabber.profilewindow.ProfileWindow(self.window, typ='new')
        r = w.run()

        if r['button'] == 'ok':

            by = org.wayround.utils.crypto.encrypt_data({}, r['password'])

            f = open(
                org.wayround.utils.path.join(self.profiles_path, r['name'] + '.pfl'),
                'w'
                )

            f.write(by)

            f.close()

            self.profile_tab_refresh_list()

    def profile_tab_delete_clicked(self, button):

        items = self.profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Select something first"
                )
            d.run()
            d.destroy()

        else:

            name = self.profile_icon_view.get_model()[items[0]][0][:-4]

            d = Gtk.MessageDialog(
                self.window,
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
                    d = Gtk.MessageDialog(
                        self.window,
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
        self.display_open_profile_info()

    def profile_tab_activate_clicked(self, button):

        items = self.profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Select something first"
                )
            d.run()
            d.destroy()

        else:

            name = self.profile_icon_view.get_model()[items[0]][0][:-4]

            w = org.wayround.pyabber.profilewindow.ProfileWindow(
                self.window, typ='open', profile=name
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

        self.display_open_profile_info()

        return



    def profile_tab_refresh_list_clicked(self, button):

        self.profile_tab_refresh_list()
        self.display_open_profile_info()

    def profile_tab_refresh_list(self):

        selected = None

        items = self.profile_icon_view.get_selected_items()

        if len(items) != 0:

            selected = items[0]

        pp = self.profiles_path

        profiles = glob.glob(org.wayround.utils.path.join(pp, '*.pfl'))

        profiles = org.wayround.utils.path.bases(profiles)

        profiles.sort()

        tree = Gtk.ListStore(str, GdkPixbuf.Pixbuf)

        for i in profiles:

            tree.append([i, self.icons['profile']])

        self.profile_icon_view.set_model(tree)
        self.profile_icon_view.set_text_column(0)
        self.profile_icon_view.set_pixbuf_column(1)

        if selected:

            self.profile_icon_view.select_path(selected)

    def display_open_profile_info(self):

        if not hasattr(self, 'profile_name') or not isinstance(self.profile_data, dict):
            self.profile_info_label.set_text("Profile not activated")

        else:
            self.profile_info_label.set_text(
                "Active profile is `{}'".format(self.profile_name)
                )

