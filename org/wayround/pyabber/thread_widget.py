
import threading

from gi.repository import Gtk

import org.wayround.pyabber.message_filter


class ThreadWidget:

    def __init__(
        self,
        controller,
        contact_bare_jid, contact_resource=None,
        operation_mode='chat',
        ):

        if not operation_mode in ['chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in ['chat', 'groupchat', 'private']"
                )

        self._controller = controller
        self._operation_mode = operation_mode
        self._contact_bare_jid = contact_bare_jid
        self._contact_resource = contact_resource

        self._incomming_messages_lock = threading.Lock()

        self._data = {}

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        self._text = Gtk.Label()

        b.pack_start(Gtk.Label("Thread:"), False, False, 0)
        b.pack_start(self._text, True, True, 0)

        self._main_widget = b
        self._main_widget.show_all()

        self._controller.message_relay.connect_signal(
            'new_message', self.history_update_listener
            )

        return

    def get_widget(self):
        return self._main_widget

    def set_resource(self, value):
        self._contact_resource = value

    def get_resource(self, value):
        return self._contact_resource

    def destroy(self):
        self.get_widget().destroy()

    def set_data(self, data):

        self._data = data

        self._update_text()

        return

    def _update_text(self):

        if self._data != None:
            self._text.set_text(self._data)
        else:
            self._text.set_text("(no thread identifier)")

        return

    def history_update_listener(
        self,
        event, storage,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if event == 'new_message':
            if type_ in ['message_chat', 'message_groupchat']:

                if org.wayround.pyabber.message_filter.is_message_acceptable(
                    operation_mode=self._operation_mode,
                    contact_bare_jid=self._contact_bare_jid,
                    contact_resource=self._contact_resource,
                    active_bare_jid=jid_obj.bare(),
                    active_resource=jid_obj.resource
                    ):

                    self._incomming_messages_lock.acquire()

                    if thread_id != None:
                        if thread_id != '':
                            self.set_data(thread_id)
                        else:
                            self.set_data(None)

                    self._incomming_messages_lock.release()

        return
