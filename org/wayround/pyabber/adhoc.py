
from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.xmpp.adhoc

class AD_HOC_Window:

    def __init__(self, controller, commands):

        if not isinstance(commands, dict):
            raise TypeError("`commands' must be dict")

        self._controller = controller
        self._selected_command = None
        self._commands = commands

        self._window = Gtk.Window()

        b = Gtk.Box()
        self._window.add(b)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_homogeneous(True)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        first = True
        first_el = None
        for i in commands.keys():
            rb = Gtk.RadioButton()

            if first:
                first = False
                first_el = rb

            else:
                rb.join_group(first_el)

            rb.connect('toggled', self._on_one_of_radios_toggled, i)
            rb.set_label(commands[i]['name'])

            b.pack_start(rb, False, False, 0)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)
        bb.set_spacing(5)

        ok_button = Gtk.Button("Continue")
        cancel_button = Gtk.Button("Cancel")

        ok_button.connect('clicked', self._on_ok_button_clicked)
        cancel_button.connect('clicked', self._on_cancel_button_clicked)

        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        b.pack_start(bb, False, False, 0)

        return

    def show(self):

        self._window.show_all()

    def _on_ok_button_clicked(self, button):
        pass

    def _on_cancel_button_clicked(self, button):
        pass

    def _on_one_of_radios_toggled(self, button, name):

        self._selected_command = name

def adhoc_window(controller, commands):

    a = AD_HOC_Window(controller, commands)
    a.show()

    return

def adhoc_window_for_jid_and_node(
    controller, jid_to, jid_from
    ):

    commands = org.wayround.xmpp.adhoc.get_commands_list(
        jid_to, jid_from, controller.client.stanza_processor
        )

    if commands:
        adhoc_window(controller, commands)
    else:
        d = org.wayround.utils.gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Can't get commands list"
            )
        d.run()
        d.destroy()

    return
