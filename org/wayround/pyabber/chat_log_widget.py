
from gi.repository import Gtk

class ChatLogWidget:

    def __init__(self):

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)

        text_view = Gtk.TextView()
        self._text_view = text_view

        frame = Gtk.Frame()
        sw = Gtk.ScrolledWindow()
        frame.add(sw)
        sw.add(text_view)

        self._root_widget = frame

    def get_widget(self):
        return self._root_widget

    def add_record(self, datetime_obj, text, from_jid=None):

        b = self._text_view.get_buffer()

        fj = ''
        if from_jid != None:
            fj = '{} '.format(str(from_jid))


        b.insert(
            b.get_end_iter(),
            '{date} {fj}{text}\n'.format(
                date=str(datetime_obj),
                text=text,
                fj=fj
                )
            )
