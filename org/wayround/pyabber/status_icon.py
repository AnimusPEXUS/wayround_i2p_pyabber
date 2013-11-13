
import logging
import gc
import threading

from gi.repository import Gtk

import org.wayround.pyabber.icondb
import org.wayround.pyabber.ccc


class MainStatusIconMenu:

    def __init__(self, main):

        self._main = main

        m = Gtk.Menu()
        mm = Gtk.Menu()

        profiles_mi = Gtk.MenuItem("Profiles..")

        connection_presets_mi = Gtk.MenuItem("Connection presets..")

        connections_mi = Gtk.MenuItem("Connections")

        close_profile_mi = Gtk.MenuItem("Close Profile")

        about_mi = Gtk.MenuItem("About..")
        garbage_mi = Gtk.MenuItem("print garbage")

        exit_mi = Gtk.MenuItem("Exit")

        m.append(profiles_mi)
        m.append(close_profile_mi)
        m.append(Gtk.SeparatorMenuItem())
        m.append(connection_presets_mi)
        m.append(connections_mi)
        m.append(Gtk.SeparatorMenuItem())
        m.append(about_mi)
        m.append(garbage_mi)
        m.append(Gtk.SeparatorMenuItem())
        m.append(exit_mi)

        m.show_all()

        profiles_mi.connect('activate', self._on_open_activate)
        connection_presets_mi.connect(
            'activate',
            self._on_connection_presets_activate
            )

        exit_mi.connect('activate', self._on_exit_activate)
        close_profile_mi.connect(
            'activate',
            self._on_close_profile_mi_activate
            )

        garbage_mi.connect('activate', self._on_print_threads)

        connections_mi.set_submenu(mm)

        self._connections_submenu = mm

        self.widget = m

        return

    def destroy(self):
        self.widget.destroy()

    def add_connection_menu(self, name, menu):

        if not isinstance(name, str):
            raise ValueError("`name' must be str")

        if not isinstance(menu, org.wayround.pyabber.ccc.ConnectionStatusMenu):
            raise ValueError(
                "`menu' must be org.wayround.pyabber.ccc.ConnectionStatusMenu"
                )

        mi = Gtk.MenuItem(name)
        self._connections_submenu.append(mi)
        mi.set_submenu(menu.widget)
        menu.set_connections_submenu_item(mi)
        mi.show()

        return

    def _on_open_activate(self, mi):
        self._main.show_profile_selection_dialog()

    def _on_connection_presets_activate(self, mi):
        self._main.profile.show_connection_mgr_dialog()

    def _on_exit_activate(self, mi):
        self._main.destroy()

    def _on_close_profile_mi_activate(self, mi):
        self._main.unset_profile()

    def _on_print_threads(self, mi):
        logging.debug(repr(threading.enumerate()))


class MainStatusIcon:

    def __init__(self, main):

        icon = Gtk.StatusIcon()
        icon.set_title('main')
        icon.set_tooltip_text("main")
        icon.set_from_pixbuf(org.wayround.pyabber.icondb.get('main'))
        icon.set_visible(True)
        icon.connect('popup-menu', self._on_popup)

        menu = MainStatusIconMenu(main)

        self.menu = menu
        self.widget = icon

    def destroy(self):
        self.menu.destroy()

    def _on_popup(self, icon, button, activate_time):
        self.menu.widget.popup(
            None, None, self.widget.position_menu, icon, button, activate_time
            )

        return
