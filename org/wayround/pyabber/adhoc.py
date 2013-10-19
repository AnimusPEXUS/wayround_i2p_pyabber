
from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.xmpp.adhoc
import org.wayround.xmpp.xdata
import org.wayround.pyabber.xdata

class AD_HOC_Window:

    def __init__(self, controller, commands, to_jid):

        if not isinstance(commands, dict):
            raise TypeError("`commands' must be dict")

        self._to_jid = to_jid
        self._controller = controller
        self._selected_command = None
        self._commands = commands

        self._window = Gtk.Window()
        self._window.set_default_size(500, 500)

        b = Gtk.Box()
        self._window.add(b)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        sw = Gtk.ScrolledWindow()

        rbb = Gtk.Box()
        sw.add(rbb)
        rbb.set_orientation(Gtk.Orientation.VERTICAL)
        rbb.set_spacing(5)
        rbb.set_homogeneous(True)
        rbb.set_margin_top(5)
        rbb.set_margin_bottom(5)
        rbb.set_margin_left(5)
        rbb.set_margin_right(5)

        none_rb = Gtk.RadioButton()
        none_rb.connect('toggled', self._on_one_of_radios_toggled, None)
        none_rb.set_label("(None)")

        rbb.pack_start(none_rb, False, False, 0)

        keys_sorted = list(commands.keys())
        keys_sorted.sort()

        for i in keys_sorted:
            rb = Gtk.RadioButton()
            rb.join_group(none_rb)

            rb.connect('toggled', self._on_one_of_radios_toggled, i)
            rb.set_label(commands[i]['name'])

            rbb.pack_start(rb, False, False, 0)


        ok_button = Gtk.Button("Continue")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        b.pack_start(sw, True, True, 0)
        b.pack_start(ok_button, False, False, 0)

        return

    def show(self):

        self._window.show_all()

    def _on_ok_button_clicked(self, button):

        if not self._selected_command:
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Select some command, and then hit Continue"
                )
            d.run()
            d.destroy()
        else:

            com = org.wayround.xmpp.adhoc.Command(
                node=self._selected_command,
                sessionid=None,
                action='execute',
                actions=None,
                execute=None,
                status=None
                )

            stanza = org.wayround.xmpp.core.Stanza(
                tag='iq',
                from_jid=self._controller.jid.full(),
                to_jid=self._to_jid,
                typ='set',
                objects=[com]
                )

            res = self._controller.client.stanza_processor.send(stanza, wait=None)

            process_command_stanza_result(res, self._controller)

        return


    def _on_one_of_radios_toggled(self, button, name):

        self._selected_command = name

def adhoc_window(controller, commands, to_jid):

    a = AD_HOC_Window(controller, commands, to_jid)
    a.show()

    return

def adhoc_window_for_jid_and_node(
    controller, to_jid, from_jid
    ):

    commands = org.wayround.xmpp.adhoc.get_commands_list(
        to_jid, from_jid, controller.client.stanza_processor
        )

    if commands:
        adhoc_window(controller, commands, to_jid)
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

class AD_HOC_Response_Window:

    def __init__(self, controller, stanza_response, command_struct):

        if not isinstance(stanza_response, org.wayround.xmpp.core.Stanza):
            raise TypeError(
                "`stanza_response' must be org.wayround.xmpp.core.Stanza"
                )

        if not isinstance(command_struct, org.wayround.xmpp.adhoc.Command):
            raise TypeError(
                "`command_struct' must be org.wayround.xmpp.adhoc.Command"
                )

        self._controller = controller
        self._stanza_response = stanza_response
        self._command_data = command_struct

        self._window = Gtk.Window()
        self._window.set_default_size(500, 500)

        self._form_controller = None

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_spacing(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)

        info_box = Gtk.Grid()
        info_box.set_column_spacing(5)
        info_box.set_margin_left(5)
        info_box.set_margin_top(5)
        info_box.set_margin_right(5)
        info_box.set_margin_bottom(5)

        label = Gtk.Label("Node:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 0, 1, 1)

        label = Gtk.Label(command_struct.get_node())
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 0, 1, 1)

        label = Gtk.Label("Status:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 1, 1, 1)

        label = Gtk.Label(command_struct.get_status())
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 1, 1, 1)

        label = Gtk.Label("Session ID:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 2, 1, 1)

        label = Gtk.Label(command_struct.get_sessionid())
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 2, 1, 1)

        info_frame = Gtk.Frame()
        info_frame.add(info_box)

        b.pack_start(info_frame, False, False, 0)


        self._scrolled_box = Gtk.Box()
        self._scrolled_box.set_orientation(Gtk.Orientation.VERTICAL)
        self._scrolled_box.set_spacing(5)

        sw = Gtk.ScrolledWindow()
        sw.add(self._scrolled_box)

        for i in command_struct.get_note():
            self._add_note(i)

        for i in command_struct.get_xdata():
            if self._form_controller != None:
                d = org.wayround.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
"This program doesn't support more then one {jabber:x:data}x for single command\n"
"Please, make a bug report with title 'command with multiple data forms', if You see this message"
                    )
                d.run()
                d.destroy()
            else:
                self._add_x_form(i)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        buttons = {}

        if command_struct.get_actions():
            for i in command_struct.get_actions():
                button = Gtk.Button(i)
                button.connect('clicked', self._on_action_button_pressed, i)
                button.set_can_default(True)
                bb.pack_start(button, False, False, 0)

                buttons[i] = button

        if command_struct.get_status() == 'executing':

            for i in ['complete']:

                if not i in buttons:
                    button = Gtk.Button(i)
                    button.connect('clicked', self._on_action_button_pressed, i)
                    button.set_can_default(True)
                    bb.pack_start(button, False, False, 0)

                    buttons[i] = button

            if command_struct.get_execute():
                self._window.set_default(buttons[command_struct.get_execute()])
            else:
                self._window.set_default(buttons['complete'])


        b.pack_start(sw, True, True, 0)
        b.pack_start(bb, False, False, 0)

        self._window.add(b)


        return

    def show(self):

        self._window.show_all()

    def _add_note(self, note):

        if not isinstance(note, org.wayround.xmpp.adhoc.CommandNote):
            raise TypeError("`note' must be org.wayround.xmpp.adhoc.CommandNote")

        b = Gtk.Box()
        b.set_spacing(5)
        b.set_orientation(Gtk.Orientation.HORIZONTAL)

        icon = Gtk.Image()
        typ = note.get_typ()
        if typ == 'info':
            icon.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG)

        elif typ == 'warn':
            icon.set_from_stock(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.DIALOG)

        elif typ == 'error':
            icon.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.DIALOG)

        label = Gtk.Label(note.get_text())
        label.set_alignment(0.0, 0.5)

        b.pack_start(icon, False, False, 0)
        b.pack_start(label, True, True, 0)

        self._scrolled_box.pack_start(b, False, False, 0)

        return

    def _add_x_form(self, data):

        if not isinstance(data, org.wayround.xmpp.xdata.XData):
            raise TypeError("`data' must be org.wayround.xmpp.xdata.XData")

        res = org.wayround.pyabber.xdata.XDataFormWidgetController(data)

        self._form_controller = res

        self._scrolled_box.pack_start(res.get_widget(), True, True, 0)

        return

    def _on_action_button_pressed(self, button, action):

        if not self._form_controller:
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Form controller not found"
                )
            d.run()
            d.destroy()
        else:

            if self._command_data.get_status() != 'executing':
                d = org.wayround.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "This command not in 'executing' status"
                    )
                d.run()
                d.destroy()
            else:

                x_data = self._form_controller.gen_x_data()
                if x_data == None:
                    d = org.wayround.utils.gtk.MessageDialog(
                        None,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Some error while getting x_data"
                        )
                    d.run()
                    d.destroy()
                else:
                    x_data.set_form_type('submit')

                    command = org.wayround.xmpp.adhoc.Command()
                    command.set_action(action)
                    command.set_sessionid(self._command_data.get_sessionid())
                    command.set_node(self._command_data.get_node())

                    command.get_objects().append(x_data)

                    stanza = org.wayround.xmpp.core.Stanza(tag='iq')
                    stanza.set_typ('set')
                    stanza.set_to_jid(self._stanza_response.get_from_jid())
                    stanza.set_from_jid(self._controller.jid.full())
                    stanza.get_objects().append(command)

                    res = self._controller.client.stanza_processor.send(
                        stanza,
                        wait=None
                        )

                    process_command_stanza_result(res, self._controller)

                    self._window.destroy()

        return




def process_command_stanza_result(res, controller):
    if not isinstance(res, org.wayround.xmpp.core.Stanza):
        d = org.wayround.utils.gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Not a stanza response"
            )
        d.run()
        d.destroy()
    else:
        if res.is_error():
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Error"
                )
            d.run()
            d.destroy()
        else:
            commands = org.wayround.xmpp.adhoc.extract_element_commands(
                res.get_element()
                )

            if len(commands) == 0:
                d = org.wayround.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Response contains not command response"
                    )
                d.run()
                d.destroy()

            else:

                for i in commands:
                    w = AD_HOC_Response_Window(
                        controller,
                        res,
                        i
                        )
                    w.show()

    return

