
from gi.repository import Gtk


class OOBField:

    def __init__(self, oob_data):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        entry = Gtk.Entry()
        self._entry = entry
        entry.set_text(oob_data.get_url())

        b.pack_start(entry, False, False, 0)

        desc = oob_data.get_desc()
        if desc != None:
            desc_label = Gtk.Label(desc)
            b.pack_start(desc_label, False, False, 0)

        self._b = b

        return

    def get_widget(self):
        return self._b

    def destroy(self):
        return self.get_widget().destroy()
