
import os.path
import weakref

from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.pyabber.connection_window
import org.wayround.pyabber.icondb
import org.wayround.pyabber.profile_window
import org.wayround.pyabber.status_icon


class Main:

    def __init__(self, pyabber_config='~/.config/pyabber'):

        pyabber_config = os.path.expanduser(pyabber_config)

        self.profile = None

        self.profiles_path = '{pyabber_config}/profiles'.format(
            pyabber_config=pyabber_config
            )

        self.status_icon = None

        self._iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._profile_selection_dialog = None
        self._working = False

    def run(self):
        if not self._working:
            self._working = True
            self.status_icon = org.wayround.pyabber.status_icon.MainStatusIcon(
                self
                )
            self._iteration_loop.wait()
            self._working = False

    def destroy(self):
        self.unset_profile()
        self.status_icon.destroy()
        if self._profile_selection_dialog:
            self._profile_selection_dialog.destroy()
        self._iteration_loop.stop()
        return

    def show_profile_selection_dialog(self):

        if self._profile_selection_dialog == None:
            self._profile_selection_dialog = \
                org.wayround.pyabber.profile_window.ProfileMgrWindow(self)
            self._profile_selection_dialog.run()
            self._profile_selection_dialog.destroy()
            self._profile_selection_dialog = None
        else:
            self._profile_selection_dialog.show()

        return

    def set_profile(self, pfl):
        self.unset_profile()
        self.profile = pfl

    def unset_profile(self):
        if self.profile:
            self.profile.destroy()
        self.profile = None

    def get_profile(self):
        return self.profile

    def open(self, name):

        w = org.wayround.pyabber.profile_window.ProfileWindow(
            None, typ='open', profile=name
            )
        r = w.run()

        if r['button'] == 'ok':

            password = r['password']

            self.set_profile(
                ProfileSession(
                    self,
                    name,
                    org.wayround.pyabber.profile.open_pfl(
                        org.wayround.utils.path.join(
                            self.profiles_path, name + '.pfl'
                            ),
                        password
                        ),
                    password
                    )
                )

        return

    def save(self, name, data, password):

        if not isinstance(name, str) or not isinstance(data, dict):

            d = org.wayround.utils.gtk.MessageDialog(
                None,
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

            org.wayround.pyabber.profile.save_pfl(
                org.wayround.utils.path.join(
                    self.profiles_path, name + '.pfl'
                    ),
                password,
                data
                )


class ProfileSession:

    def __init__(self, main, name, data, password):

        self._main = main

        self.name = name
        self.data = data
        self.password = password

        self.connection_controllers = set()

        self._connection_mgr_dialog = None

    def show_connection_mgr_dialog(self):

        if self._connection_mgr_dialog == None:
            self._connection_mgr_dialog = \
                org.wayround.pyabber.connection_window.ConnectionMgrWindow(
                    self._main, self
                    )
            self._connection_mgr_dialog.run()
            self._connection_mgr_dialog.destroy()
            self._connection_mgr_dialog = None
        else:
            self._connection_mgr_dialog.show()

        return

    def destroy(self):

        if self._connection_mgr_dialog:
            self._connection_mgr_dialog.destroy()

        for i in list(self.connection_controllers):
            i.destroy()

        return

    def save(self):
        self.save(
            self._main.profile.name,
            self._main.profile.data,
            self._main.profile.password
            )


def main(opts, args):

    org.wayround.pyabber.icondb.set_dir(
        org.wayround.utils.path.join(
            os.path.dirname(org.wayround.utils.path.abspath(__file__)),
            'icons'
            )
        )

    m = Main()
    m.run()
