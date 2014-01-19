
import logging
import threading

from gi.repository import Gtk, Pango

import org.wayround.pyabber.misc
import org.wayround.pyabber.message_filter
import org.wayround.pyabber.message_edit_widget


class SubjectEditor:

    def __init__(self, controller):

        self._controller = controller

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        target_entry = Gtk.Entry()
        self._target_entry = target_entry

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        ok_button = Gtk.Button("Send")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self._on_cancel_button_clicked)

        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        editor = org.wayround.pyabber.message_edit_widget.MessageEdit(
            controller,
            mode='subject'
            )

        self._editor = editor

        b.pack_start(target_entry, False, False, 0)
        b.pack_start(editor.get_widget(), True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._window = window

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        return

    def run(self, data, target_jid):

        self._target_entry.set_text(target_jid)

        self._editor.set_data(data, None)

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._editor.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_ok_button_clicked(self, button):

        subject = self._editor.get_data()[0]

        self._controller.message_client.message(
            to_jid=self._target_entry.get_text(),
            from_jid=False,
            typ='groupchat',
            thread=None,
            subject=subject,
            body=None,
            xhtml=None
            )

        self.destroy()
        return

    def _on_cancel_button_clicked(self, button):
        self.destroy()


class SubjectWidget:

    def __init__(
        self,
        controller,
        contact_bare_jid, contact_resource=None,
        operation_mode='chat'
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
        self._incomming_messages_lock.acquire()

        self._data = {}

        self._last_date = None

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        self._text = Gtk.Label()
        self._text.set_alignment(0.0, 0.5)
        font_desc = Pango.FontDescription.from_string("Clean 9")
        self._text.override_font(font_desc)
        self._text.set_line_wrap(True)
        self._text.set_line_wrap_mode(Pango.WrapMode.WORD)
        self._text.set_selectable(True)
        self._text.set_justify(Gtk.Justification.LEFT)

        self._edit_button = Gtk.Button("Edit..")
        self._edit_button.connect('clicked', self._on_edit_button_clicked)

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
        b.pack_start(self._edit_button, False, False, 0)
        b.pack_start(self._delete_button, False, False, 0)

        self._main_widget = b
        self._main_widget.show_all()

        self._lang_select_cb.connect('changed', self._on_lang_switch_chenged)

        self._controller.message_relay.connect_signal(
            'new_message', self.history_update_listener
            )

        self.set_selected_language('')

        self._incomming_messages_lock.release()

        return

    def get_widget(self):
        return self._main_widget

    def set_resource(self, value):
        self._contact_resource = value

    def get_resource(self, value):
        return self._contact_resource

    def destroy(self):
        self._controller.message_relay.disconnect_signal(
            self.history_update_listener
            )
        self.get_widget().destroy()

    def set_data(self, data):

        if len(data.keys()) != 0:

            lang = self.get_selected_language()

            self._data = data

            plain_langs = list(self._data.keys())
            plain_langs.sort()

            while len(self._languages_model) != 0:
                del self._languages_model[0]

            for i in plain_langs:
                self._languages_model.append([i])

            l = len(self._data.keys())

            if l == 1:
                self.set_selected_language(
                    self._data[list(self._data.keys())[0]]
                    )
                self._lang_select_cb.set_sensitive(False)

            elif l == 0:
                self.set_selected_language('')
                self._lang_select_cb.set_sensitive(False)

            else:
                if lang in self._data:
                    self.set_selected_language(lang)
                else:
                    self.set_selected_language('')

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

        if self._data[lang] in ['', None]:
            self._text.set_text('')
        else:
            self._text.set_text(
                self._data[lang]
                )

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
                    message_type=type_,
                    contact_bare_jid=self._contact_bare_jid,
                    contact_resource=self._contact_resource,
                    active_bare_jid=jid_obj.bare(),
                    active_resource=jid_obj.resource
                    ):

                    self._incomming_messages_lock.acquire()

                    if self._last_date == None or date > self._last_date:
                        self.set_data(subject)
                        self._last_date = date

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

        res = self._controller.client.stanza_processor.send(
            s,
            wait=True,
            pass_new_stanza_anyway=True
            )
        if res != None:
            if res.is_error():
                org.wayround.pyabber.misc.stanza_error_error_message(
                    None,
                    res.gen_error(),
                    "Can't delete subject"
                    )

        return

    def _on_edit_button_clicked(self, button):

        j = org.wayround.xmpp.core.JID.new_from_string(self._contact_bare_jid)

        self._controller.show_subject_edit_window(
            self._data,
            str(j)
            )

        return