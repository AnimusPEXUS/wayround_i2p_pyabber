
import os.path
import glob

from gi.repository import Gtk
from gi.repository import GdkPixbuf

import org.wayround.utils.path

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


        self.window.set_title("Pyabber :)")
        self.window.maximize()
        self.window.set_hide_titlebar_when_maximized(True)

        main_box = Gtk.Box()

        main_notebook = Gtk.Notebook()

        xmpp_core_box = Gtk.Box()

        main_box.set_orientation(Gtk.Orientation.VERTICAL)


        main_notebook.set_property('tab-pos', Gtk.PositionType.TOP)

        xmpp_core_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        xmpp_core_box.pack_start(Gtk.Label("Text"), False, True, 0)


        _l = Gtk.Label("Program")
#        _l.set_width_chars(15)
        _b = Gtk.Button("Exit")
        _b.connect('clicked', self.app_exit)
        _b.set_relief(Gtk.ReliefStyle.NONE)
        main_notebook.append_page(_b, _l)

        _l = Gtk.Label("Profile")
#        _l.set_width_chars(15)
        main_notebook.append_page(self._build_profile_tab(), _l)

        _l = Gtk.Label("Connection")
#        _l.set_width_chars(15)
        main_notebook.append_page(Gtk.Label(), _l)

        _l = Gtk.Label("Server Features")
#        _l.set_width_chars(15)
        main_notebook.append_page(Gtk.Label(), _l)

        _l = Gtk.Label("Roster and Stanzas")
#        _l.set_width_chars(15)
        main_notebook.append_page(xmpp_core_box, _l)

        main_box.pack_start(main_notebook, True, True, 0)

        self.window.add(main_box)


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

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.VERTICAL)

        but1 = Gtk.Button("Activate")
        but2 = Gtk.Button("Deactivate")
        but3 = Gtk.Button("New...")
        but4 = Gtk.Button("Change Password...")
        but5 = Gtk.Button("Save Now")
        but6 = Gtk.Button("Delete")
        but7 = Gtk.Button("Refresh List")

        but3.connect('clicked', self.profile_tab_new_clicked)
        but7.connect('clicked', self.profile_tab_refresh_list_clicked)

        bb.pack_start(but1, False, True, 0)
        bb.pack_start(but2, False, True, 0)
        bb.pack_start(but3, False, True, 0)
        bb.pack_start(but4, False, True, 0)
        bb.pack_start(but5, False, True, 0)
        bb.pack_start(but6, False, True, 0)
        bb.pack_start(but7, False, True, 0)

        bb.set_homogeneous(True)

        icon_view = Gtk.IconView()
        icon_view.set_margin_right(5)
        b2.pack_start(icon_view, True, True, 0)
        b2.pack_start(bb, False, True, 0)

        b.pack_start(b2, True, True, 0)

        self.profile_icon_view = icon_view

        return b

    def app_exit(self, user_data):

        Gtk.main_quit()

    def profile_tab_new_clicked(self, user_data):

        w = org.wayround.pyabber.profilewindow.ProfileWindow(self.window, typ='new')
        w.run()

    def profile_tab_refresh_list_clicked(self, user_data):

        self.profile_tab_refresh_list()

    def profile_tab_refresh_list(self):

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

