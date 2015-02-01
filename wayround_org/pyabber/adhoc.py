
import threading
import logging

from gi.repository import Gtk

import wayround_org.utils.gtk

import wayround_org.xmpp.adhoc
import wayround_org.xmpp.core
import wayround_org.xmpp.client
import wayround_org.xmpp.xdata

import wayround_org.pyabber.xdata


class AD_HOC_Window:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._client = self._controller.client
        self._own_jid = self._controller.jid

        self._selected_command = None

        self._window = Gtk.Window()
        self._window.connect('destroy', self._on_destroy)
        self._window.set_default_size(500, 500)

        b = Gtk.Box()
        self._window.add(b)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)

        sw = Gtk.ScrolledWindow()

        rbb = Gtk.Box()
        self._rbb = rbb
        sw.add(rbb)
        rbb.set_orientation(Gtk.Orientation.VERTICAL)
        rbb.set_spacing(5)
        rbb.set_homogeneous(True)
        rbb.set_margin_top(5)
        rbb.set_margin_bottom(5)
        rbb.set_margin_start(5)
        rbb.set_margin_end(5)

        none_rb = Gtk.RadioButton()
        self._none_rb = none_rb
        none_rb.connect('toggled', self._on_one_of_radios_toggled, None)
        none_rb.set_label("(None)")

        rbb.pack_start(none_rb, False, False, 0)

        ok_button = Gtk.Button("Continue")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        b.pack_start(sw, True, True, 0)
        b.pack_start(ok_button, False, False, 0)

        return

    def run(self, commands, to_jid):

        if not isinstance(commands, dict):
            raise TypeError("`commands' must be dict")

        if to_jid is not None and not isinstance(to_jid, str):
            raise ValueError("`to_jid' must be None or str")

        self._commands = commands
        self._to_jid = to_jid

        rbb = self._rbb
        none_rb = self._none_rb

        keys_sorted = list(commands.keys())
        keys_sorted.sort()

        for i in keys_sorted:
            rb = Gtk.RadioButton()
            rb.join_group(none_rb)

            rb.connect('toggled', self._on_one_of_radios_toggled, i)
            rb.set_label(commands[i]['name'])

            rbb.pack_start(rb, False, False, 0)

        self.show()

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()

    def _on_destroy(self, window):
        self.destroy()

    def _on_ok_button_clicked(self, button):

        if not self._selected_command:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Select some command, and then hit Continue"
                )
            d.run()
            d.destroy()
        else:

            com = wayround_org.xmpp.adhoc.Command(
                node=self._selected_command,
                sessionid=None,
                action='execute',
                actions=None,
                execute=None,
                status=None
                )

            stanza = wayround_org.xmpp.core.Stanza(
                tag='iq',
                from_jid=self._own_jid.full(),
                to_jid=self._to_jid,
                typ='set',
                objects=[com]
                )

            res = self._client.stanza_processor.send(
                stanza,
                wait=None
                )

            threading.Thread(
                target=process_command_stanza_result_idled,
                args=(res, self._controller)
                ).start()

        return

    def _on_one_of_radios_toggled(self, button, name):

        self._selected_command = name


class AD_HOC_Response_Window:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._own_jid = self._controller.jid
        self._client = self._controller.client

        self._window = Gtk.Window()
        self._window.connect('destroy', self._on_destroy)
        self._window.set_default_size(500, 500)

        self._form_controller = None

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_spacing(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)

        info_box = Gtk.Grid()
        info_box.set_column_spacing(5)
        info_box.set_margin_start(5)
        info_box.set_margin_top(5)
        info_box.set_margin_end(5)
        info_box.set_margin_bottom(5)

        label = Gtk.Label("Node:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 0, 1, 1)

        label = Gtk.Label()
        self._node_label = label
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 0, 1, 1)

        label = Gtk.Label("Status:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 1, 1, 1)

        label = Gtk.Label()
        self._status_label = label
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 1, 1, 1, 1)

        label = Gtk.Label("Session ID:")
        label.set_alignment(0.0, 0.5)
        info_box.attach(label, 0, 2, 1, 1)

        label = Gtk.Label()
        self._sessionid_label = label
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

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        self._bb = bb

        b.pack_start(sw, True, True, 0)
        b.pack_start(bb, False, False, 0)

        self._window.add(b)

        return

    def run(self, stanza_response, command_struct):

        if not isinstance(stanza_response, wayround_org.xmpp.core.Stanza):
            raise TypeError(
                "`stanza_response' must be wayround_org.xmpp.core.Stanza"
                )

        if not isinstance(command_struct, wayround_org.xmpp.adhoc.Command):
            raise TypeError(
                "`command_struct' must be wayround_org.xmpp.adhoc.Command"
                )

        self._stanza_response = stanza_response
        self._command_struct = command_struct

        bb = self._bb

        self._node_label.set_text(command_struct.get_node())
        self._status_label.set_text(command_struct.get_status())
        self._sessionid_label.set_text(command_struct.get_sessionid())

        for i in command_struct.get_note():
            self._add_note(i)

        for i in command_struct.get_xdata():
            if self._form_controller != None:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
"This program doesn't support more then one {jabber:x:data}x "
"for single command\n"
"Please, make a bug report with title 'command with multiple data forms', "
"if You see this message"
                    )
                d.run()
                d.destroy()
            else:
                self._add_x_form(i, self._stanza_response)

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
                    button.connect(
                        'clicked', self._on_action_button_pressed, i
                        )
                    button.set_can_default(True)
                    bb.pack_start(button, False, False, 0)

                    buttons[i] = button

            if command_struct.get_execute():
                self._window.set_default(buttons[command_struct.get_execute()])
            else:
                self._window.set_default(buttons['complete'])

        self.show()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        if self._form_controller:
            self._form_controller.destroy()
        self._window.hide()
        self._window.destroy()

    def _on_destroy(self, window):
        self.destroy()

    def _add_note(self, note):

        if not isinstance(note, wayround_org.xmpp.adhoc.CommandNote):
            raise TypeError(
                "`note' must be wayround_org.xmpp.adhoc.CommandNote"
                )

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

    def _add_x_form(self, data, stanza):

        if not isinstance(data, wayround_org.xmpp.xdata.XData):
            raise TypeError("`data' must be wayround_org.xmpp.xdata.XData")

        res = wayround_org.pyabber.xdata.XDataFormWidget(
            self._controller,
            data,
            stanza
            )

        self._form_controller = res

        self._scrolled_box.pack_start(res.get_widget(), True, True, 0)

        return

    def _on_action_button_pressed(self, button, action):

        if not self._form_controller:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Form controller not found"
                )
            d.run()
            d.destroy()
        else:

            if self._command_struct.get_status() != 'executing':
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "This command not in 'executing' status"
                    )
                d.run()
                d.destroy()
            else:

                x_data = self._form_controller.gen_stanza_subobject()
                if x_data == None:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Some error while getting x_data"
                        )
                    d.run()
                    d.destroy()
                else:
                    x_data.set_typ('submit')

                    command = wayround_org.xmpp.adhoc.Command()
                    command.set_action(action)
                    command.set_sessionid(self._command_struct.get_sessionid())
                    command.set_node(self._command_struct.get_node())

                    command.get_objects().append(x_data)

                    stanza = wayround_org.xmpp.core.Stanza(tag='iq')
                    stanza.set_typ('set')
                    stanza.set_to_jid(self._stanza_response.get_from_jid())
                    stanza.set_from_jid(self._own_jid.full())
                    stanza.get_objects().append(command)

                    res = self._client.stanza_processor.send(
                        stanza,
                        wait=None
                        )

                    threading.Thread(
                        target=process_command_stanza_result_idled,
                        args=(res, self._controller)
                        ).start()

                    self.destroy()

        return


def adhoc_window_for_jid_and_node(to_jid, controller):

    if to_jid is not None and not isinstance(to_jid, str):
        raise ValueError("`to_jid' must be None or str")

    if not isinstance(
        controller,
        wayround_org.pyabber.ccc.ClientConnectionController
        ):
        raise ValueError(
            "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
            )

    own_jid = controller.jid
    client = controller.client

    own_jid2 = None
    if own_jid != None:
        own_jid2 = str(own_jid)

    commands = wayround_org.xmpp.adhoc.get_commands_list(
        to_jid, own_jid2, client.stanza_processor
        )

    if commands:
        controller.show_adhoc_window(commands, to_jid)
    else:
        d = wayround_org.utils.gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Can't get commands list"
            )
        d.run()
        d.destroy()

    return


def process_command_stanza_result(res, controller):

    if not isinstance(
        controller,
        wayround_org.pyabber.ccc.ClientConnectionController
        ):
        raise ValueError(
            "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
            )

    if not isinstance(res, wayround_org.xmpp.core.Stanza):
        d = wayround_org.utils.gtk.MessageDialog(
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
            d = wayround_org.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Error"
                )
            d.run()
            d.destroy()
        else:
            commands = wayround_org.xmpp.adhoc.extract_element_commands(
                res.get_element()
                )

            if len(commands) == 0:
                d = wayround_org.utils.gtk.MessageDialog(
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
                    controller.show_adhoc_response_window(
                        res, i
                        )

    return


process_command_stanza_result_idled = \
    wayround_org.utils.gtk.to_idle(process_command_stanza_result)
