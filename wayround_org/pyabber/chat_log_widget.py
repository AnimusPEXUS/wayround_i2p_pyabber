
import json
import queue
import threading

from gi.repository import Gtk, Pango, Gdk

import wayround_org.pyabber.ccc
import wayround_org.pyabber.chat_pager
import wayround_org.pyabber.l10n
import wayround_org.pyabber.message_filter
import wayround_org.utils.gtk
import wayround_org.utils.timer


class ChatLogTableRow:

    def __init__(
        self,
        date, jid_to_display,
        plain, xhtml,
        delay_from,
        delay_message,
        subject
        ):

        self._plain = plain
        self._xhtml = xhtml
        self._date = date
        self._subject = subject

        font_desc = Pango.FontDescription.from_string("Clean 9")

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)
        b.override_background_color(
            Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0.7, 0.7, 0.7, 1)
            )

        date_label = Gtk.Label(date)
        date_label.set_alignment(0.0, 0.5)
        date_label.set_selectable(True)

        jid_label = Gtk.Label(jid_to_display)
        jid_label.set_alignment(0.0, 0.5)
        jid_label.set_selectable(True)

        subject_label = Gtk.Label()
        subject_label.override_font(font_desc)
        self._subject_label = subject_label
        subject_label.set_alignment(0.0, 0.5)
        subject_label.set_margin_start(20)
        subject_label.set_margin_end(10)
        subject_label.set_line_wrap(True)
        subject_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        subject_label.set_selectable(True)
        subject_label.set_no_show_all(True)
        subject_label.hide()

        # TODO: redo those overrides to set parameters line by line
        font_desc = Pango.FontDescription.from_string("Clean 9 bold")
        subject_anno_label = Gtk.Label()
        subject_anno_label.set_alignment(0.0, 0.5)
        subject_anno_label.override_font(font_desc)

        subject_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        subject_box.override_background_color(
            Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0.8, 0.8, 0.8, 1)
            )
        subject_box.set_no_show_all(True)
        subject_box.hide()

        subject_box.pack_start(subject_anno_label, False, False, 0)
        subject_box.pack_start(subject_label, False, False, 0)

        if isinstance(subject, dict) and '' in subject:
            if subject[''] in ['', None]:
                subject_anno_label.set_text("Subject Deleted")
            else:
                subject_anno_label.set_text("Changed Subject")
                subject_label.set_text(subject[''])
                subject_label.show()

            subject_anno_label.show()
            subject_box.show()

        delay_label = Gtk.Label()
        delay_label.set_line_wrap(True)
        delay_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        delay_label.set_selectable(True)
        delay_label.set_alignment(0.0, 0.5)

        delayed_text = ''

        if delay_from != None and delay_from != '':
            delayed_text += "Delay From: {}".format(delay_from)

        if delay_message != None and delay_message != '':
            if delayed_text != '':
                delayed_text += '\n'
            delayed_text += "Delay Message: {}".format(delay_message)

        delay_label.set_text(delayed_text)

        font_desc = Pango.FontDescription.from_string("Clean 9")

        text_label = Gtk.Label()
        text_label.override_font(font_desc)
        self._text_label = text_label
        text_label.set_alignment(0.0, 0.0)
        text_label.set_line_wrap(True)
        text_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_selectable(True)
        text_label.set_justify(Gtk.Justification.LEFT)
        text_label.set_margin_start(10)
        text_label.set_margin_top(10)
        text_label.set_margin_end(10)
        text_label.set_margin_bottom(10)
        text_label.set_no_show_all(True)

        mode_lang_switch_combo = Gtk.ComboBox()
        mode_lang_switch_combo.set_no_show_all(True)
        mode_lang_switch_combo.hide()
        self._mode_lang_switch_combo = mode_lang_switch_combo

        self._modes_langs = Gtk.ListStore(str)

        mode_lang_switch_combo.set_model(self._modes_langs)

        renderer_text = Gtk.CellRendererText()
        mode_lang_switch_combo.pack_start(renderer_text, True)
        mode_lang_switch_combo.add_attribute(renderer_text, "text", 0)

        b.pack_start(jid_label, False, False, 5)
        b.pack_start(date_label, False, False, 0)
        b.pack_start(mode_lang_switch_combo, False, False, 0)
        b.pack_start(delay_label, False, False, 5)

        b2 = Gtk.Box()
        b2.set_margin_top(5)
        b2.set_margin_start(5)
        b2.set_margin_end(5)
        b2.set_margin_bottom(5)
        b2.set_spacing(5)
        b2.set_orientation(Gtk.Orientation.VERTICAL)

        b2.pack_start(
            Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), False, False, 0
            )
        b2.pack_start(b, False, False, 0)
        b2.pack_start(subject_box, False, False, 0)
        b2.pack_start(
            Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), False, False, 0
            )
        b2.pack_start(text_label, False, False, 0)

        self._widget = b2
        self._widget.show_all()

        mode_lang_switch_combo.connect(
            'changed',
            self._on_mode_lang_switch_combo_changed
            )

        self._update_mode_combobox()
        self.set_mode_lang_switch_status('', 'plain')

        return

    def get_widget(self):
        return self._widget

    def destroy(self):
        self.get_widget().destroy()

    def get_date(self):
        return self._date

    def get_plain(self):
        return self._plain

    def get_xhtml(self):
        return self._xhtml

    def get_subject(self):
        return self._subject

    def _on_mode_lang_switch_combo_changed(self, combo):
        lang, mode = self.get_mode_lang_switch_status()

        m = self._plain
        if mode == 'xhtml':
            m = self._xhtml

        if lang in m:
            self._text_label.set_text(m[lang])
        else:
            self._text_label.set_text('')

        self._text_label.set_visible(self._text_label.get_text() != '')

        return

    def _update_mode_combobox(self):
        lang, mode = self.get_mode_lang_switch_status()

        modes = ['plain', 'xhtml']

        while len(self._modes_langs) != 0:
            del self._modes_langs[0]

        for i in modes:

            lng_lst = self._plain
            if i == 'xhtml':
                lng_lst = self._xhtml

            lng_lst_names = list(lng_lst.keys())
            lng_lst_names.sort()

            for j in lng_lst_names:
                mod_lang = self._format_mode_lang_name(i, j)
                self._modes_langs.append([mod_lang])

        self._mode_lang_switch_combo.set_sensitive(
            len(self._mode_lang_switch_combo.get_model()) > 1
            )

        self._mode_lang_switch_combo.set_visible(
            self._plain != {}
            or self._xhtml != {}
            )

        self.set_mode_lang_switch_status(lang, mode)

        return

    def get_mode_lang_switch_status(self):

        ret = '', 'plain'

        active = self._mode_lang_switch_combo.get_active()

        if active != -1:

            active_text = self._modes_langs[active][0]

            res = wayround_org.pyabber.l10n.LANG_MODE_RE.match(active_text)

            if res != None:
                lang = res.group('lang')
                if lang == None:
                    lang = ''
                ret = lang, res.group('mode')

        return ret

    def find_mode_lang_index(self, lang, mode):
        mod_lang = self._format_mode_lang_name(mode, lang)
        ret = -1
        for i in range(len(self._modes_langs)):
            if self._modes_langs[i][0] == mod_lang:
                ret = i
                break

        return ret

    def set_mode_lang_switch_status(self, lang, mode):

        if lang == None:
            lang = ''

        if mode == None:
            mode = 'plain'

        if not isinstance(lang, str):
            raise TypeError("`lang' must be str")

        if not isinstance(mode, str):
            raise TypeError("`mode' must be str")

        active = self.find_mode_lang_index(lang, mode)

        if active == -1:
            active = self.find_mode_lang_index('', 'plain')

        self._mode_lang_switch_combo.set_active(active)

        return

    def _format_mode_lang_name(self, mode, lang):

        if lang == None:
            lang = ''

        if mode == None:
            mode = 'plain'

        minus = ''
        if lang != '':
            minus = '-'
        ret = '{}{}{}'.format(mode, minus, lang)

        return ret


# TODO: make not dependent from Chat
class ChatLogWidget:

    def __init__(
        self, controller, chat, operation_mode='chat',
        message_relay_listener_call_queue=None
        ):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        if not isinstance(chat, wayround_org.pyabber.chat_pager.Chat):
            raise TypeError(
                "`page' must be the instance of "
                "wayround_org.pyabber.chat_pager.Chat"
                )

        self.add_record_idle = wayround_org.utils.gtk.to_idle(self.add_record)

        self._incomming_messages_lock = threading.Lock()

        with self._incomming_messages_lock:

            self._operation_mode = None
            self.set_operation_mode(operation_mode)

            self._controller = controller
            self._chat = chat

            main_box = Gtk.Box()
            main_box.set_orientation(Gtk.Orientation.VERTICAL)

            log_box = Gtk.Box()
            self._log_box = log_box
            log_box.set_orientation(Gtk.Orientation.VERTICAL)

            frame = Gtk.Frame()
            sw = Gtk.ScrolledWindow()
            self._sw = sw
            frame.add(sw)
            sw.add(log_box)

            main_box.pack_start(frame, True, True, 0)

            self._root_widget = main_box

            self._last_date = None
            self._rows = []
            self._lock = threading.Lock()

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

            self.load_history()

        self._last_scroll_date = None
        self.scroll_down()

        self.scroll_down_idle = \
            wayround_org.utils.gtk.to_idle(self.scroll_down)

        self._looped_timer = wayround_org.utils.timer.LoopedTimer(
            0.25,
            self.scroll_down_idle,
            tuple(),
            dict()
            )

        self._looped_timer.start()

        return

    def set_operation_mode(self, value):
        if not value in ['chat', 'groupchat', 'private']:
            raise ValueError(
                "`operation_mode' must be in ['chat', 'groupchat', 'private']"
                )
        self._operation_mode = value

    def get_operation_mode(self):
        return self._operation_mode

    def get_widget(self):
        return self._root_widget

    def add_record(
        self,
        date, jid, plain, xhtml, delay_from, delay_message, subject
        ):

        self._lock.acquire()

        found = False

        for i in self._rows:
            if (i.get_date() == date
                and i.get_plain() == plain
                and i.get_xhtml() == xhtml
                and i.get_subject() == subject
                ):
                found = True
                break

        if not found:

            clt = ChatLogTableRow(
                date,
                jid,
                plain,
                xhtml,
                delay_from=delay_from,
                delay_message=delay_message,
                subject=subject
                )

            self._log_box.pack_start(clt.get_widget(), False, False, 0)

            self._rows.append(clt)

            self._rows.sort(key=lambda x:  x.get_date())

            for i in self._rows:
                self._log_box.reorder_child(i.get_widget(), -1)

            if len(self._rows) > 100:
                del_list = self._rows[:-100]
                self._rows = self._rows[100:]

                for i in del_list:
                    i.destroy()

                del del_list

            if self._last_date == None or date > self._last_date:
                self._last_date = date

        self._lock.release()

        return

    def destroy(self):
        self._controller.message_relay.signal.disconnect(
            self._message_relay_listener_idle
            )
        self.get_widget().destroy()
        self._looped_timer.stop()

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        with self._incomming_messages_lock:

            if event == 'new_message':
                if type_ in ['message_chat', 'message_groupchat']:

                    if wayround_org.pyabber.message_filter.\
                        is_message_acceptable(
                            operation_mode=self._operation_mode,
                            message_type=type_,
                            contact_bare_jid=self._chat.contact_bare_jid,
                            contact_resource=self._chat.contact_resource,
                            active_bare_jid=jid_obj.bare(),
                            active_resource=jid_obj.resource
                            ):

                            if plain != {} or xhtml != {} or subject != {}:

                                self.add_record(
                                    date,
                                    self._format_jid_text(
                                        jid_obj.resource,
                                        incomming
                                        ),
                                    plain,
                                    xhtml,
                                    delay_from,
                                    delay_message,
                                    subject
                                    )

        return

    def load_history(self):

        records = []

        jid_resource, types_to_load = \
            wayround_org.pyabber.message_filter.\
                gen_get_history_records_parameters(
                    operation_mode=self._operation_mode,
                    contact_bare_jid=self._chat.contact_bare_jid,
                    contact_resource=self._chat.contact_resource
                    )

        if self._last_date == None:

            records = self._controller.storage.get_history_records(
                connection_bare_jid=self._controller.jid.bare(),
                connection_jid_resource=None,
                bare_jid=self._chat.contact_bare_jid,
                jid_resource=jid_resource,
                starting_from_date=None,
                starting_includingly=True,
                ending_with_date=None,
                ending_includingly=True,
                limit=100,
                offset=None,
                types=types_to_load
                )

        else:

            records = self._controller.storage.get_history_records(
                connection_bare_jid=self._controller.jid.bare(),
                connection_jid_resource=None,
                bare_jid=self._chat.contact_bare_jid,
                jid_resource=jid_resource,
                starting_from_date=self._last_date,
                starting_includingly=False,
                ending_with_date=None,
                ending_includingly=True,
                limit=None,
                offset=None,
                types=types_to_load
                )

        for i in records:

            d, jid, plain, xhtml, delay_from, delay_message, subject = \
                self._convert_record(i)

            self.add_record(
                d,
                jid,
                plain,
                xhtml,
                delay_from,
                delay_message,
                subject
                )

        return

    def _format_jid_text(self, resource, is_incomming):
        jid = ''
        if self._operation_mode == 'groupchat':
            jid = resource
        else:
            if is_incomming:
                jid = '\u2192'
            else:
                jid = '\u2190'

        return jid

    def _convert_record(self, rec):
        jid = self._format_jid_text(rec['jid_resource'], rec['incomming'])

        return \
            rec['date'], \
            jid, \
            rec['plain'], \
            rec['xhtml'], \
            rec['delay_from'], \
            rec['delay_message'], \
            rec['subject']

    def scroll_down(self):
        if self._last_scroll_date != self._last_date:
            self._last_scroll_date = self._last_date
            sb = self._sw.get_vscrollbar()
            adj = sb.get_adjustment()
            sb.set_value(adj.get_upper())
