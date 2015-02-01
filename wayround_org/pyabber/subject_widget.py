
import threading

from gi.repository import Gtk, Pango

import wayround_org.pyabber.message_edit_widget
import wayround_org.pyabber.message_filter
import wayround_org.pyabber.misc
import wayround_org.utils.gtk


# TODO: make classes in this module better
class SubjectTooltip:

    def __init__(self):
        self._window = Gtk.Window()
        self._window.connect('destroy', self._on_destroy)

        self._label = Gtk.Label()
        font_desc = Pango.FontDescription.from_string("Clean 9")
        self._label.override_font(font_desc)
#        self._label.set_ellipsize(Pango.EllipsizeMode.END)
        self._label.set_alignment(0.0, 0.0)
        self._label.set_line_wrap(True)
        self._label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self._label.set_justify(Gtk.Justification.LEFT)

        self._window.add(self._label)
        self._window.show_all()

        return

    def destroy(self):
        self.get_window().destroy()

    def get_window(self):
        return self._window

    def set_text(self, value):
        self._label.set_text(value)

    def _on_destroy(self, win):
        self.destroy()


class SubjectEditor:

    def __init__(self, controller, operation_mode='chat'):

        if not operation_mode in ['normal', 'chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in "
                "['normal', 'chat', 'groupchat', 'private']"
                )

        self._controller = controller
        self._operation_mode = operation_mode

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        target_entry = Gtk.Entry()
        self._target_entry = target_entry

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        ok_button = Gtk.Button("Send")
        self._ok_button = ok_button
        ok_button.connect('clicked', self._on_ok_button_clicked)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self._on_cancel_button_clicked)

        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        editor = wayround_org.pyabber.message_edit_widget.MessageEdit(
            controller,
            mode='subject'
            )

        self._editor = editor

        b.pack_start(target_entry, False, False, 0)
        b.pack_start(editor.get_widget(), True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._window = window

        self._result = {'button': 'cancel'}

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self, data, target_jid, operation_mode):

        self._operation_mode = operation_mode
        if operation_mode != 'normal':
            self._ok_button.set_label("Send")
        else:
            self._ok_button.set_label("Set")

        self._target_entry.set_text(target_jid)

        self._editor.set_data(data, None)

        self.show()

        ret = self._result

        self._iterated_loop.wait()

        return ret

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._editor.destroy()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_ok_button_clicked(self, button):

        subject = self._editor.get_data()[0]

        typ = 'chat'
        if self._operation_mode in  ['groupchat', 'normal']:
            typ = self._operation_mode

        if self._operation_mode != 'normal':
            self._controller.message_client.message(
                to_jid=self._target_entry.get_text(),
                from_jid=False,
                typ=typ,
                thread=None,
                subject=subject,
                body=None,
                xhtml=None
                )

        self._result = {'button': 'ok', 'data': subject}

        self.destroy()
        return

    def _on_cancel_button_clicked(self, button):
        self._result = {'button': 'cancel'}
        self.destroy()
        return


class SubjectWidget:

    def __init__(
        self,
        controller,
        contact_bare_jid, contact_resource=None,
        operation_mode='chat',
        message_relay_listener_call_queue=None
        ):

        if not operation_mode in ['normal', 'chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in "
                "['normal', 'chat', 'groupchat', 'private']"
                )

        self._controller = controller
        self._operation_mode = operation_mode
        self._contact_bare_jid = contact_bare_jid
        self._contact_resource = contact_resource

        self._incomming_messages_lock = threading.Lock()
        self._incomming_messages_lock.acquire()

#        self._tooltip = SubjectTooltip()

        self._data = {}

        self._last_date = None

        grid = Gtk.Box()
        grid.set_orientation(Gtk.Orientation.HORIZONTAL)
        grid.set_spacing(5)

        self._text = Gtk.Label()
        self._text.set_alignment(0.0, 0.5)
        font_desc = Pango.FontDescription.from_string("Clean 9")
        self._text.override_font(font_desc)
#        self._text.set_line_wrap(True)
#        self._text.set_line_wrap_mode(Pango.WrapMode.WORD)
        self._text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self._text.set_selectable(True)
        self._text.set_justify(Gtk.Justification.LEFT)
#        self._text.set_tooltip_window(self._tooltip.get_window())
#        self._text.set_has_tooltip(True)

#        self._send_button = Gtk.Button("Send")
##        self._edit_button.set_valign(Gtk.Align.START)
#        self._send_button.connect('clicked', self._on_send_button_clicked)
#        self._send_button.set_no_show_all(True)
#        self._send_button.set_visible(operation_mode == 'normal')

        self._edit_button = Gtk.Button("Edit..")
#        self._edit_button.set_valign(Gtk.Align.START)
        self._edit_button.connect('clicked', self._on_edit_button_clicked)

        self._delete_button = Gtk.Button("Del")
#        self._delete_button.set_valign(Gtk.Align.START)
        self._delete_button.connect('clicked', self._on_delete_button_clicked)

        self._lang_select_cb = Gtk.ComboBox()
#        self._lang_select_cb.set_valign(Gtk.Align.START)

        renderer_text = Gtk.CellRendererText()
        self._lang_select_cb.pack_start(renderer_text, True)
        self._lang_select_cb.add_attribute(renderer_text, "text", 0)

        self._languages_model = Gtk.ListStore(str)
        self._lang_select_cb.set_model(self._languages_model)

#        text_scrolled_win = Gtk.ScrolledWindow()
#        text_scrolled_win.set_hexpand(True)
#        text_scrolled_win.set_halign(Gtk.Align.FILL)
#        text_scrolled_win.add()
#        text_scrolled_win.set_size_request(-1, 100)

#        grid.pack_start(text_scrolled_win, True, True, 0)
#        grid.pack_start(self._lang_select_cb, False, False, 0)
#        grid.pack_start(self._edit_button, False, False, 0)
#        grid.pack_start(self._delete_button, False, False, 0)

        bb = Gtk.Box()
        bb.set_spacing(5)
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)
        bb.pack_start(self._lang_select_cb, False, False, 0)
        bb.pack_start(self._edit_button, False, False, 0)
#        bb.pack_start(self._send_button, False, False, 0)
        bb.pack_start(self._delete_button, False, False, 0)

        grid.pack_start(self._text, True, True, 0)
        grid.pack_start(bb, False, False, 0)

        self._main_widget = grid
        self._main_widget.show_all()

        self._lang_select_cb.connect('changed', self._on_lang_switch_chenged)

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
        self._controller.message_relay.signal.disconnect(
            self._message_relay_listener_idle
            )
#        self._tooltip.destroy()
        self.get_widget().destroy()

    def set_editable(self, value):
        self._edit_button.set_sensitive(value)
        self._delete_button.set_sensitive(value)
        return

    def get_editable(self):
        return self._edit_button.get_sensitive()

    def set_data(self, data):

        if not isinstance(data, dict):
            raise TypeError("input data must be dict")

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
            self._lang_select_cb.set_sensitive(True)

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

    def get_data(self):
        return self._data

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

        if not lang in self._data or self._data[lang] in ['', None]:
            self._text.set_text('')
            self._text.set_tooltip_text('')
        else:
            t = self._data[lang]
            self._text.set_text(t.replace('\n', r'\n'))
            self._text.set_tooltip_text(t)

        return

    def _on_lang_switch_chenged(self, widget):
        self._update_text()

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if self._operation_mode != 'normal':
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

                            self._incomming_messages_lock.acquire()

                            if (self._last_date == None
                                or date > self._last_date):
                                self.set_data(subject)
                                self._last_date = date

                            self._incomming_messages_lock.release()

        return

    def _on_delete_button_clicked(self, button):

        if self._operation_mode != 'normal':

            s = wayround_org.xmpp.core.Stanza(tag='message')
            s.set_to_jid(self._contact_bare_jid)
            s.set_subject([wayround_org.xmpp.core.MessageSubject(None)])
            if self._operation_mode == 'groupchat':
                s.set_typ('groupchat')
            elif self._operation_mode in ['chat', 'private']:
                s.set_typ('chat')
            else:
                s.set_typ('normal')

            res = self._controller.client.stanza_processor.send(
                s,
                wait=True
                )
            if isinstance(res, wayround_org.xmpp.core.Stanza):
                if res.is_error():
                    wayround_org.pyabber.misc.stanza_error_error_message(
                        None,
                        res.gen_error(),
                        "Can't delete subject"
                        )
        else:
            self.set_data({})

        return

    def _on_edit_button_clicked(self, button):

        j = wayround_org.xmpp.core.JID.new_from_string(self._contact_bare_jid)
        if self._operation_mode != 'groupchat':
            j.resource = self._contact_resource

        if self._operation_mode != 'normal':
            self._controller.show_subject_edit_window(
                self._data,
                str(j),
                self._operation_mode
                )
        else:
            res = self._controller.show_subject_edit_window_modal(
                self._data,
                str(j),
                self._operation_mode
                )
            if res['button'] == 'ok':
                self.set_data(res['data'])
        return
