
from gi.repository import Gtk

import org.wayround.pyabber.ccc
import org.wayround.pyabber.chat_pager


class ChatWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.above.client.XMPPC2SClient"
                )

        self._controller = controller

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        window = Gtk.Window()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_left(5)
        b.set_margin_top(5)
        b.set_margin_right(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self.chat_pager = org.wayround.pyabber.chat_pager.ChatPager(controller)

        b.pack_start(self.chat_pager.get_widget(), True, True, 0)

        self._window = window

    def run(self):

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self.chat_pager.destroy()
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()
