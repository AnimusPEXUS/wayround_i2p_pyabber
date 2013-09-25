
import pprint

from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.xmpp.adhoc
import org.wayround.xmpp.xdata
import org.wayround.pyabber.xdata

class AD_HOC_Window:

    def __init__(self, controller, commands, jid_to):

        if not isinstance(commands, dict):
            raise TypeError("`commands' must be dict")

        self._jid_to = jid_to
        self._controller = controller
        self._selected_command = None
        self._commands = commands

        self._window = Gtk.Window()

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

        for i in commands.keys():
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
                jid_from=self._controller.jid.full(),
                jid_to=self._jid_to,
                typ='set',
                body=[com]
                )

            res = self._controller.client.stanza_processor.send(stanza, wait=None)

            process_command_stanza_result(res, self._controller)

        return


    def _on_one_of_radios_toggled(self, button, name):

        self._selected_command = name

def adhoc_window(controller, commands, jid_to):

    a = AD_HOC_Window(controller, commands, jid_to)
    a.show()

    return

def adhoc_window_for_jid_and_node(
    controller, jid_to, jid_from
    ):

    commands = org.wayround.xmpp.adhoc.get_commands_list(
        jid_to, jid_from, controller.client.stanza_processor
        )

    if commands:
        adhoc_window(controller, commands, jid_to)
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

    def __init__(self, controller, stanza_response, command_data):

        if not isinstance(stanza_response, org.wayround.xmpp.core.Stanza):
            raise TypeError(
                "`stanza_response' must be org.wayround.xmpp.core.Stanza"
                )

        if not isinstance(command_data, org.wayround.xmpp.adhoc.Command):
            raise TypeError(
                "`command_data' must be org.wayround.xmpp.adhoc.Command"
                )

        self._controller = controller
        self._stanza_response = stanza_response
        self._command_data = command_data

        self._window = Gtk.Window()
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

        label = Gtk.Label("Node:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 0, 1, 1)

        label = Gtk.Label(command_data.node)
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 0, 1, 1)

        label = Gtk.Label("Status:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 1, 1, 1)

        label = Gtk.Label(command_data.status)
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 1, 1, 1)

        label = Gtk.Label("Session ID:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 2, 1, 1)

        label = Gtk.Label(command_data.sessionid)
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

        for i in command_data.body:
            if i.tag == '{http://jabber.org/protocol/commands}note':
                self._add_note(i.text, typ=i.get('type'))

            elif i.tag == '{jabber:x:data}x':
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

        if command_data.actions:
            for i in command_data.actions:
                button = Gtk.Button(i)
                button.connect('clicked', self._on_action_button_pressed, i)
                button.set_can_default(True)
                bb.pack_start(button, False, False, 0)

                buttons[i] = button

        if command_data.status == 'executing':

            for i in ['complete']:

                if not i in buttons:
                    button = Gtk.Button(i)
                    button.connect('clicked', self._on_action_button_pressed, i)
                    button.set_can_default(True)
                    bb.pack_start(button, False, False, 0)

                    buttons[i] = button

            if command_data.execute:
                self._window.set_default(buttons[command_data.execute])
            else:
                self._window.set_default(buttons['complete'])


        b.pack_start(sw, True, True, 0)
        b.pack_start(bb, False, False, 0)

        self._window.add(b)


        return

    def show(self):

        self._window.show_all()

    def _add_note(self, text, typ='info'):

        if not typ in ['info', 'warn', 'error']:
            raise ValueError("Invalid `typ' value")

        if not isinstance(text, str):
            raise TypeError("text must be str")

        b = Gtk.Box()
        b.set_spacing(5)
        b.set_orientation(Gtk.Orientation.HORIZONTAL)

        icon = Gtk.Image()
        if typ == 'info':
            icon.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG)

        elif typ == 'warn':
            icon.set_from_stock(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.DIALOG)

        elif typ == 'error':
            icon.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.DIALOG)

        label = Gtk.Label(text)
        label.set_alignment(0.0, 0.5)

        b.pack_start(icon, False, False, 0)
        b.pack_start(label, True, True, 0)

        self._scrolled_box.pack_start(b, False, False, 0)

        return

    def _add_x_form(self, xform_element):

        data = org.wayround.xmpp.xdata.element_to_data(xform_element)

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

            if self._command_data.status != 'executing':
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
                    x_data['form_type'] = 'submit'

                    element = org.wayround.xmpp.xdata.data_to_element(x_data)

                    command = org.wayround.xmpp.adhoc.Command()
                    command.action = action
                    command.sessionid = self._command_data.sessionid
                    command.node = self._command_data.node

                    command.body.append(element)

                    stanza = org.wayround.xmpp.core.Stanza('iq')
                    stanza.typ = 'set'
                    stanza.jid_to = self._stanza_response.jid_from
                    stanza.jid_from = self._controller.jid.full()
                    stanza.body.append(command.body)

                    res = self._controller.client.stanza_processor.send(stanza, wait=None)

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
                res.body
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
                        org.wayround.xmpp.adhoc.Command(body=i)
                        )
                    w.show()

    return

