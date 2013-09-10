
from gi.repository import Gtk

class MessageEdit:

    def __init__(self):

        main_box = Gtk.Box()
        self._main_box = main_box
        main_box.set_orientation(Gtk.Orientation.VERTICAL)

        frame = Gtk.Frame()
        text_view_sw = Gtk.ScrolledWindow()
        frame.add(text_view_sw)

        text_view = Gtk.TextView()
        self._text_view = text_view

        text_view_sw.add(text_view)

        main_box.pack_start(frame, True, True, 0)

    def get_widget(self):
        return self._main_box

    def get_text(self):

        b = self._text_view.get_buffer()

        ret = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        return ret

    def set_text(self, txt):
        self._text_view.get_buffer().set_text(txt)

    def set_editable(self, val):
        self._text_view.set_editable(val)

    def set_cursor_to_end(self):
        b = self._text_view.get_buffer()
#        insert = b.get_insert()
#        iter = b.get_iter_at_mark(insert)
        b.place_cursor(b.get_end_iter())

    def grab_focus(self):
        self._text_view.grab_focus()

    def connect(self, signal, cb, *args):
        return self._text_view.connect(signal, cb, *args)

