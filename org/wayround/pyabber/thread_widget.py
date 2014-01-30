
import threading
import uuid

from gi.repository import Gtk, Pango

import org.wayround.pyabber.message_filter


class ThreadWidget:

    def __init__(
        self,
        controller,
        contact_bare_jid, contact_resource=None,
        operation_mode='chat',
        message_relay_listener_call_queue=None
        ):

        if not operation_mode in ['chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in ['chat', 'groupchat', 'private']"
                )

        self._controller = controller
        self._operation_mode = operation_mode
        self._contact_bare_jid = contact_bare_jid
        self._contact_resource = contact_resource

        self._last_date = None

        self._incomming_messages_lock = threading.Lock()

        self._data = {}

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        self._text = Gtk.Label()
        font_desc = Pango.FontDescription.from_string("Clean 9")
        self._text.override_font(font_desc)
        self._text.set_alignment(0.0, 0.5)
        self._text.set_line_wrap(True)
        self._text.set_line_wrap_mode(Pango.WrapMode.WORD)
        self._text.set_selectable(True)
        self._text.set_justify(Gtk.Justification.LEFT)

        self._main_widget = b
        self._main_widget.show_all()

        thread_generate_button = Gtk.Button("Generate New UUID")
        thread_generate_button.set_no_show_all(True)
        thread_generate_button.connect(
            'clicked',
            self._on_thread_generate_button_clicked
            )
        self._thread_generate_button = thread_generate_button

        b.pack_start(self._text, True, True, 0)
        b.pack_start(thread_generate_button, False, False, 0)

        if message_relay_listener_call_queue:
            message_relay_listener_call_queue.set_callable_target(
                self._message_relay_listener
                )
            message_relay_listener_call_queue.dump()
        else:
            self._controller.message_relay.signal.connect(
                'new_message', self._message_relay_listener
                )

        return

    def get_widget(self):
        return self._main_widget

    def set_resource(self, value):
        self._contact_resource = value

    def get_resource(self, value):
        return self._contact_resource

    def destroy(self):
        self._controller.message_relay.signal.disconnect(
            self._message_relay_listener
            )
        self.get_widget().destroy()

    def set_editable(self, value):
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
            self._text.set_text(self._data)
        else:
            self._text.set_text("(no thread identifier)")

        return

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if event == 'new_message':
            if type_ in ['message_chat', 'message_groupchat']:

                if org.wayround.pyabber.message_filter.is_message_acceptable(
                    operation_mode=self._operation_mode,
                    message_type=type_,
                    contact_bare_jid=self._contact_bare_jid,
                    contact_resource=self._contact_resource,
                    active_bare_jid=jid_obj.bare(),
                    active_resource=jid_obj.resource
                    ):

                    self._incomming_messages_lock.acquire()

                    if self._last_date == None or date > self._last_date:

                        if thread_id != None:
                            if thread_id != '':
                                self.set_data(thread_id)
                            else:
                                self.set_data(None)

                        self._last_date = date

                    self._incomming_messages_lock.release()

        return

    def _on_thread_generate_button_clicked(self, button):
        self.generate_new_thread_entry()

    def generate_new_thread_entry(self):

        self.set_data(uuid.uuid4().hex)
