
from gi.repository import Gtk
from gi.repository import Gdk

import org.wayround.xmpp.client


class PresenceControlWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        window = Gtk.Window()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)
        bb.set_spacing(3)

        available_button = Gtk.Button("Available")
        unavailable_button = Gtk.Button("Unavailable")
        xa_button = Gtk.Button("XA")
        away_button = Gtk.Button("Away")
        chat_button = Gtk.Button("Chat")
        dnd_button = Gtk.Button("DND")

        available_button.connect(
            'clicked', self._on_button_pressed, 'available'
            )
        unavailable_button.connect(
            'clicked', self._on_button_pressed, 'unavailable'
            )
        xa_button.connect('clicked', self._on_button_pressed, 'xa')
        away_button.connect('clicked', self._on_button_pressed, 'away')
        chat_button.connect('clicked', self._on_button_pressed, 'chat')
        dnd_button.connect('clicked', self._on_button_pressed, 'dnd')

        bb.pack_start(available_button, False, False, 0)
        bb.pack_start(unavailable_button, False, False, 0)
        bb.pack_start(xa_button, False, False, 0)
        bb.pack_start(away_button, False, False, 0)
        bb.pack_start(chat_button, False, False, 0)
        bb.pack_start(dnd_button, False, False, 0)

        status_cb = Gtk.CheckButton()
        status_cb.set_label("Add _status description")

        status_frame = Gtk.Frame()
        status_frame.set_label_widget(status_cb)

        status_sw = Gtk.ScrolledWindow()

        text_view = Gtk.TextView()
        status_sw.add(text_view)
        text_view.set_margin_top(5)
        text_view.set_margin_bottom(5)
        text_view.set_margin_left(5)
        text_view.set_margin_right(5)
        status_frame.add(status_sw)

        to_entry = Gtk.Entry()
        to_entry.set_margin_top(5)
        to_entry.set_margin_bottom(5)
        to_entry.set_margin_left(5)
        to_entry.set_margin_right(5)

        to_cb = Gtk.CheckButton()
        to_cb.set_label("Add `to' destination")
        to_frame = Gtk.Frame()
        to_frame.set_label_widget(to_cb)
        to_frame.add(to_entry)

        b.pack_start(to_frame, False, False, 0)
        b.pack_start(status_frame, True, True, 5)
        b.pack_start(bb, False, False, 0)

        window.add(b)
        window.set_title("Send new presence _status")
#        window.set_transient_for(parent_window)
#        window.set_keep_above(True)
        window.set_default_size(300, 200)
        window.connect('destroy', self._on_destroy)
        window.set_position(Gtk.WindowPosition.CENTER)

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._presence_client = self._controller.presence_client
        self._status = text_view
        self._status_cb = status_cb
        self._to = to_entry
        self._to_cb = to_cb
        self._window = window

#        ok_button.set_can_default(True)
#        window.set_default(ok_button)
#
#        ok_button.connect('clicked', self._ok)
#        cancel_button.connect('clicked', self._cancel)

    def run(self):

        self.show()

        self._iterated_loop.wait()

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_button_pressed(self, button, value):

        if not value in [
            'available', 'unavailable', 'xa', 'away', 'dnd', 'chat'
            ]:
            raise ValueError("Invalid `value'")
        else:
            show = None
            if not value in ['available', 'unavailable']:
                show = value

            typ = None
            if value == 'unavailable':
                typ = 'unavailable'

            to = None
            if self._to_cb.get_active():
                to = self._to.get_text()

            status = None
            if self._status_cb.get_active():
                b = self._status.get_buffer()
                status = b.get_text(
                    b.get_start_iter(),
                    b.get_end_iter(),
                    False
                    )

            self._presence_client.presence(
                show=show,
                to_full_or_bare_jid=to,
                status=status,
                typ=typ
                )
