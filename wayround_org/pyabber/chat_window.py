
from gi.repository import Gtk

import wayround_org.pyabber.ccc
import wayround_org.pyabber.chat_pager
import wayround_org.utils.gtk


class ChatWindow:

    def __init__(self, controller):

        if not isinstance(
                controller,
                wayround_org.pyabber.ccc.ClientConnectionController
                ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller
        # self._title = ''

        window = Gtk.Window()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_start(5)
        b.set_margin_top(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        window.add(b)
        window.connect('destroy', self._on_destroy)
        window.connect(
            'delete-event', wayround_org.utils.gtk.hide_on_delete
            )

        self.chat_pager = wayround_org.pyabber.chat_pager.ChatPager(controller)

        b.pack_start(self.chat_pager.get_widget(), True, True, 0)

        self._window = window

        self.refresh_title()

        return

    def run(self):
        self.show()
        return

    def show(self):
        self._window.show_all()
        return

    def destroy(self):
        self.chat_pager.destroy()
        self._window.hide()
        self._window.destroy()
        return

    def _on_destroy(self, window):
        self.destroy()
        return

    def get_window_widget(self):
        return self._window

    def refresh_title(self):
        j = self._controller.jid.full()
        self._window.set_title("Chatting as `{}'".format(j))
        return
