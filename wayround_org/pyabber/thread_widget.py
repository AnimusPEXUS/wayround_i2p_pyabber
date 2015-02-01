
import threading
import uuid

from gi.repository import Gtk, Pango

import wayround_org.pyabber.message_filter
import wayround_org.xmpp.core


class ThreadEditor:

    def __init__(self, controller):

        self._controller = controller

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        ok_button = Gtk.Button("Ok")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self._on_cancel_button_clicked)

        generate_button = Gtk.Button("Generate")
        generate_button.connect('clicked', self._on_generate_clicked)

        delete_button = Gtk.Button("Delete")
        delete_button.connect('clicked', self._on_delete_clicked)

        bb.pack_start(generate_button, False, False, 0)
        bb.pack_start(delete_button, False, False, 0)
        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        self._editor = Gtk.Entry()

        b.pack_start(self._editor, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._window = window

        self._result = None

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self, data):

        if data != None:
            self._editor.set_text(data)
        self._editor.set_sensitive(data != None)

        self.show()

        self._iterated_loop.wait()

        return self._result

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_ok_button_clicked(self, button):

        value = None
        if self._editor.get_sensitive():
            value = self._editor.get_text()

            if value.isspace():
                value = None

        if isinstance(value, str):
            value = value.lower()

        self._result = {
            'button': 'ok',
            'value': value
            }

        self.destroy()
        return

    def _on_cancel_button_clicked(self, button):
        self._result = {
            'button': 'cancel'
            }
        self.destroy()

    def _on_generate_clicked(self, button):
        self._editor.set_sensitive(True)
        self._editor.set_text(uuid.uuid4().hex)

    def _on_delete_clicked(self, button):
        self._editor.set_text('')
        self._editor.set_sensitive(False)


class ThreadWidget:

    def __init__(
        self,
        controller,
        contact_bare_jid, contact_resource=None,
        operation_mode='chat',
        message_relay_listener_call_queue=None
        ):

        if not operation_mode in ['normal', 'chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in ['chat', 'groupchat', 'private']"
                )

        self._controller = controller
        self._operation_mode = operation_mode
        self._contact_bare_jid = contact_bare_jid
        self._contact_resource = contact_resource

        self._last_date = None

        self._incomming_messages_lock = threading.Lock()

        self._data = None

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        self._text = Gtk.Label()
        font_desc = Pango.FontDescription.from_string("Clean 9")
        self._text.override_font(font_desc)
        self._text.set_alignment(0.0, 0.5)
        self._text.set_line_wrap(True)
        self._text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self._text.set_selectable(True)
        self._text.set_justify(Gtk.Justification.LEFT)

        self._main_widget = b
        self._main_widget.show_all()

        edit_button = Gtk.Button("Edit..")
        self._edit_button = edit_button
        edit_button.connect(
            'clicked',
            self._on_edit_button_clicked
            )

        send_button = Gtk.Button("Send")
        self._send_button = send_button
        send_button.set_no_show_all(True)
        send_button.set_visible(operation_mode != 'normal')
        send_button.connect(
            'clicked',
            self._on_send_button_clicked
            )

        b.pack_start(self._text, True, True, 0)
        b.pack_start(edit_button, False, False, 0)
        b.pack_start(send_button, False, False, 0)

        self.set_data(self._data)

        self._message_relay_listener_idle = \
            wayround_org.utils.gtk.to_idle(self._message_relay_listener)

        if message_relay_listener_call_queue:
            message_relay_listener_call_queue.set_callable_target(
                self._message_relay_listener_idle
                )
            message_relay_listener_call_queue.dump()
        else:
            self._controller.message_relay.signal.connect(
                'new_message', self._message_relay_listener_idle
                )

        return

    def get_widget(self):
        return self._main_widget

    # TODO: do we really need this?
    def set_resource(self, value):
        self._contact_resource = value

    # TODO: do we really need this?
    def get_resource(self, value):
        return self._contact_resource

    def destroy(self):
        self._controller.message_relay.signal.disconnect(
            self._message_relay_listener_idle
            )
        self.get_widget().destroy()

    def set_editable(self, value):
        self._edit_button.set_sensitive(value)
        self._send_button.set_sensitive(value)
        return

    def get_editable(self):
        return

    def set_data(self, data):

        if data != None and not isinstance(data, str):
            raise ValueError("`data' must be str or None")

        self._data = data

        self._update_text()

        return

    def get_data(self):
        return self._data

    def _update_text(self):

        if self._data != None:
            d = self._data
            self._text.set_text(d)
            self._text.set_tooltip_text(d)
        else:
            d = "(no thread identifier)"
            self._text.set_text(d)
            self._text.set_tooltip_text(d)

        return

    def generate_new_thread_entry(self):
        self.set_data(uuid.uuid4().hex)

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if self._operation_mode != 'message_normal':
            if event == 'new_message':
                if type_ in ['message_chat', 'message_groupchat']:

                    if wayround_org.pyabber.message_filter.\
                        is_message_acceptable(
                            operation_mode=self._operation_mode,
                            message_type=type_,
                            contact_bare_jid=self._contact_bare_jid,
                            contact_resource=self._contact_resource,
                            active_bare_jid=jid_obj.bare(),
                            active_resource=jid_obj.resource
                            ):

                            with self._incomming_messages_lock:

                                if (self._last_date == None
                                    or date > self._last_date):

                                    if thread_id != None:
                                        if thread_id != '':
                                            self.set_data(thread_id)
                                        else:
                                            self.set_data(None)

                                    self._last_date = date

        return

    def _on_edit_button_clicked(self, button):
        result = self._controller.show_thread_edit_window(self.get_data())
        if result['button'] == 'ok':
            self.set_data(result['value'])
        return

    def _on_send_button_clicked(self, button):

        j = wayround_org.xmpp.core.JID.new_from_string(self._contact_bare_jid)

        if self._operation_mode != 'groupchat':
            j.resource = self._contact_resource

        typ = 'chat'
        if self._operation_mode == 'groupchat':
            typ = 'groupchat'

        self._controller.message_client.message(
            to_jid=str(j),
            from_jid=False,
            typ=typ,
            thread=self.get_data(),
            subject=None,
            body=None,
            xhtml=None
            )

        return
