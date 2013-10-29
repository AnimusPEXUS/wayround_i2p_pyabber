
from gi.repository import Gtk
from gi.repository import Gdk


class PresenceControlPopup:

    def __init__(self, parent_window, mainwindow):

        self.parent_window = parent_window
        self.mainwindow = mainwindow
        self.window = Gtk.Window()
        win = self.window

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
        status_cb.set_label("Add status description")
        self.status_cb = status_cb

        status_frame = Gtk.Frame()
        status_frame.set_label_widget(status_cb)

        text_view = Gtk.TextView()
        self.status = text_view
        text_view.set_margin_top(5)
        text_view.set_margin_bottom(5)
        text_view.set_margin_left(5)
        text_view.set_margin_right(5)
        status_frame.add(text_view)

        to_entry = Gtk.Entry()
        self.to = to_entry
        to_entry.set_margin_top(5)
        to_entry.set_margin_bottom(5)
        to_entry.set_margin_left(5)
        to_entry.set_margin_right(5)

        to_cb = Gtk.CheckButton()
        self.to_cb = to_cb
        to_cb.set_label("Add `to' destination")
        to_frame = Gtk.Frame()
        to_frame.set_label_widget(to_cb)
        to_frame.add(to_entry)

        b.pack_start(to_frame, False, False, 0)
        b.pack_start(status_frame, True, True, 5)
        b.pack_start(bb, False, False, 0)

        win.add(b)
        win.set_title("Send new presence status")
#        win.set_transient_for(parent_window)
#        win.set_keep_above(True)
        win.set_default_size(300, 200)

#        ok_button.set_can_default(True)
#        win.set_default(ok_button)
#
#        ok_button.connect('clicked', self._ok)
#        cancel_button.connect('clicked', self._cancel)

    def show(self):
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.show_all()

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
            if self.to_cb.get_active():
                to = self.to.get_text()

            status = None
            if self.status_cb.get_active():
                b = self.status.get_buffer()
                status = b.get_text(
                    b.get_start_iter(),
                    b.get_end_iter(),
                    False
                    )

            self.mainwindow.controller.presence.presence(
                show=show,
                to_full_or_bare_jid=to,
                status=status,
                typ=typ
                )
