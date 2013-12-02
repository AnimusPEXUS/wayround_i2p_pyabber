
import threading
import logging
import os.path

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

        self._rel_win_ctl = org.wayround.utils.gtk.RelatedWindowCollector()
        self._rel_win_ctl.set_constructor_cb(
            'profile_selection_dialog',
            self._profile_selection_dialog_constructor
            )

        self._iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._working = False

    def _profile_selection_dialog_constructor(self):
        return org.wayround.pyabber.profile_window.ProfileMgrWindow(self)

    def run(self):
        if not self._working:
            self._working = True
            self.status_icon = org.wayround.pyabber.status_icon.MainStatusIcon(
                self
                )
            self._iteration_loop.wait()
            self._working = False

    def destroy(self):
        logging.debug("main destroy 1")
        self.unset_profile()
        logging.debug("main destroy 2")
        self.status_icon.destroy()
        logging.debug("main destroy 3")
        self._rel_win_ctl.destroy()
        logging.debug("main destroy 4")
        self._iteration_loop.stop()
        logging.debug("main destroy 5")
        return

    def show_profile_selection_dialog(self):

        self._rel_win_ctl.show('profile_selection_dialog')

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


class ProfileSession:

    def __init__(self, main, data):

        self._main = main

        self.data = data

        self.connection_controllers = set()

        self._rel_win_ctl = org.wayround.utils.gtk.RelatedWindowCollector()
        self._rel_win_ctl.set_constructor_cb(
            'connection_mgr_dialog',
            self._connection_mgr_dialog_constructor
            )

#        self._connection_mgr_dialog = None

    def _connection_mgr_dialog_constructor(self):
        return org.wayround.pyabber.connection_window.ConnectionMgrWindow(
            self._main, self
            )

    def show_connection_mgr_dialog(self):

        self._rel_win_ctl.show('connection_mgr_dialog')

        return

    def destroy(self):

        self._rel_win_ctl.destroy()

        for i in list(self.connection_controllers):
            i.destroy()

        return

    def save(self):
        self.data.commit()


def main(opts, args):

    org.wayround.pyabber.icondb.set_dir(
        org.wayround.utils.path.join(
            os.path.dirname(org.wayround.utils.path.abspath(__file__)),
            'icons'
            )
        )

    m = Main()
    m.run()
    logging.debug(repr(threading.enumerate()))
