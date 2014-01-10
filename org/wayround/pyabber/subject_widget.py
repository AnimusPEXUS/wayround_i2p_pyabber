
import logging
import threading

from gi.repository import Gtk

import org.wayround.pyabber.misc
import org.wayround.pyabber.message_filter


class SubjectWidget:

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

        self._delete_button = Gtk.Button("Del")
        self._delete_button.connect('clicked', self._on_delete_button_clicked)

        self._lang_select_cb = Gtk.ComboBox()

        renderer_text = Gtk.CellRendererText()
        self._lang_select_cb.pack_start(renderer_text, True)
        self._lang_select_cb.add_attribute(renderer_text, "text", 0)

        self._languages_model = Gtk.ListStore(str)
        self._lang_select_cb.set_model(self._languages_model)

        b.pack_start(Gtk.Label("Subject:"), False, False, 0)
        b.pack_start(self._text, True, True, 0)
        b.pack_start(self._lang_select_cb, False, False, 0)
        b.pack_start(self._delete_button, False, False, 0)

        self._main_widget = b
        self._main_widget.show_all()

        self._lang_select_cb.connect('changed', self._on_lang_switch_chenged)

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

        lang = self.get_selected_language()

        self._data = data

        plain_langs = list(data.keys())
        plain_langs.sort()

        while len(self._languages_model) != 0:
            del self._languages_model[0]

        for i in plain_langs:
            self._languages_model.append([i])

        l = len(self._data.keys())

        if l == 1:
            self.set_selected_language(list(self._data.keys())[0])
            self._lang_select_cb.set_sensitive(False)

        elif l == 0:
            self.set_selected_language('')
            self._lang_select_cb.set_sensitive(False)

        else:
            self.set_selected_language(lang)
            self._lang_select_cb.set_sensitive(True)

        self._update_text()

        return

    def get_selected_language(self):

        ret = ''

        r = self._lang_select_cb.get_active()

        if r != -1:

            ret = self._languages_model[r][0]

        return ret

    def set_selected_language(self, value):

        model = self._languages_model

        active = -1
        for i in range(len(model)):
            if model[i][0] == value:
                active = i
                break

        self._lang_select_cb.set_active(active)

        return

    def _update_text(self):

        lang = self.get_selected_language()

        if not lang in self._data or self._data[lang] == None:
            self._text.set_text("")
        else:
            self._text.set_text(self._data[lang])

        return

    def _on_lang_switch_chenged(self, widget):
        self._update_text()

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

                    self.set_data(subject)

                    self._incomming_messages_lock.release()

        return

    def _on_delete_button_clicked(self, button):

        s = org.wayround.xmpp.core.Stanza(tag='message')
        s.set_to_jid(self._contact_bare_jid)
        s.set_subject([org.wayround.xmpp.core.MessageSubject(None)])
        if self._operation_mode == 'groupchat':
            s.set_typ('groupchat')
        else:
            s.set_typ('chat')

        res = self._controller.client.stanza_processor.send(s, wait=True)
        if res != None:
            if res.is_error():
                org.wayround.pyabber.misc.stanza_error_error_message(
                    None,
                    res.gen_error(),
                    "Can't delete subject"
                    )

        return
