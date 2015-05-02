
import logging
import os.path
import threading

from gi.repository import Gtk, Gdk, GObject

import wayround_org.pyabber.connection_window
import wayround_org.pyabber.icondb
import wayround_org.pyabber.profile_window
import wayround_org.pyabber.status_icon
import wayround_org.utils.gtk


class Main:

    def __init__(self, pyabber_config='~/.config/pyabber'):

        pyabber_config = os.path.expanduser(pyabber_config)

        self.profile = None

        self.profiles_path = '{pyabber_config}/profiles'.format(
            pyabber_config=pyabber_config
            )

        self.status_icon = None

        self._rel_win_ctl = wayround_org.utils.gtk.RelatedWindowCollector()
        self._rel_win_ctl.set_constructor_cb(
            'profile_selection_dialog',
            self._profile_selection_dialog_constructor,
            single=True
            )

        self._working = False

        self._iteration_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def _profile_selection_dialog_constructor(self):
        return wayround_org.pyabber.profile_window.ProfileMgrWindow(self)

    def run(self):
        if not self._working:
            self._working = True
            self.status_icon = wayround_org.pyabber.status_icon.MainStatusIcon(
                self
                )
            self._iteration_loop.wait()
            self._working = False
        return

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
        ret = self._rel_win_ctl.get('profile_selection_dialog')
        ret.run()
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

        self._rel_win_ctl = wayround_org.utils.gtk.RelatedWindowCollector()
        self._rel_win_ctl.set_constructor_cb(
            'connection_mgr_dialog',
            self._connection_mgr_dialog_constructor
            )

        return

    def _connection_mgr_dialog_constructor(self):
        return wayround_org.pyabber.connection_window.ConnectionMgrWindow(
            self._main, self
            )

    def show_connection_mgr_dialog(self):
        res = self._rel_win_ctl.get('connection_mgr_dialog')
        res.run()
        return

    def destroy(self):
        self._rel_win_ctl.destroy()
        for i in list(self.connection_controllers):
            i.destroy()
        return

    def save(self):
        # TODO: remove this method
        return


def main(opts, args):

#    Gdk.threads_init()
#    GObject.threads_init()

    wayround_org.pyabber.icondb.set_dir(
        wayround_org.utils.path.join(
            os.path.dirname(wayround_org.utils.path.abspath(__file__)),
            'icons'
            )
        )

    m = Main()
    m.run()
    logging.debug(repr(threading.enumerate()))
