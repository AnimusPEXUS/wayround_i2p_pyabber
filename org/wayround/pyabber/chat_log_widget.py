
import json
import queue
import threading

from gi.repository import Gtk, Pango

import org.wayround.pyabber.ccc
import org.wayround.pyabber.chat_pager
import org.wayround.pyabber.message_filter
import org.wayround.utils.gtk
import org.wayround.utils.timer
import org.wayround.xmpp.core


CHAT_LOG_TABLE_ROW_MODE_ITEMS = Gtk.ListStore(str)
CHAT_LOG_TABLE_ROW_MODE_ITEMS.append(['plain'])
CHAT_LOG_TABLE_ROW_MODE_ITEMS.append(['xhtml'])


class ChatLogTableRow:

    def __init__(
        self,
        date, jid_to_display,
        plain, xhtml,
        default_language, default_mode,
        column_size_groups,
        delay_from,
        delay_message,
        subject
        ):

        self._plain = plain
        self._xhtml = xhtml
        self._date = date
        self._subject = subject

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        date_label = Gtk.Label(date)
        date_label.set_alignment(0.0, 0.0)

        jid_label = Gtk.Label(jid_to_display)
        jid_label.set_alignment(0.0, 0.0)

        subject_label_separator = Gtk.Separator()
        self._subject_label_separator = subject_label_separator
        subject_label_separator.set_no_show_all(True)
        subject_label_separator.set_margin_left(10)
        subject_label_separator.set_margin_right(10)
        subject_label_separator.hide()

        subject_label = Gtk.Label()
        self._subject_label = subject_label
        subject_label.set_alignment(0.0, 0.0)
        subject_label.set_no_show_all(True)
        subject_label.set_margin_left(10)
        subject_label.set_margin_right(10)
        subject_label.hide()

        if isinstance(subject, dict) and '' in subject:
            if subject[''] in ['', None]:
                subject_label.set_text("Subject Deleted")
            else:
                subject_label.set_text(
                    "Changed Subject to: {}".format(subject[''])
                    )
            subject_label.show()
            subject_label_separator.show()

        delay_label = Gtk.Label()
        delay_label.set_alignment(0.0, 0.0)

        delayed_text = ''

        if delay_from != None and delay_from != '':
            delayed_text += "Delay From: {}".format(delay_from)

        if delay_message != None and delay_message != '':
            if delayed_text != '':
                delayed_text += '\n'
            delayed_text += "Delay Message: {}".format(delay_message)

        delay_label.set_text(delayed_text)

        text_label = Gtk.Label()
        self._text_label = text_label
        text_label.set_alignment(0.0, 0.0)
        text_label.set_line_wrap(True)
        text_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        text_label.set_selectable(True)
        text_label.set_justify(Gtk.Justification.LEFT)
        text_label.set_margin_left(10)
        text_label.set_margin_top(10)
        text_label.set_margin_right(10)
        text_label.set_margin_bottom(10)
        text_label.set_no_show_all(True)

        mode_switch = Gtk.ComboBox()
        mode_switch.set_no_show_all(True)
        mode_switch.hide()
        self._mode_switch = mode_switch
        mode_switch.set_model(CHAT_LOG_TABLE_ROW_MODE_ITEMS)

        language_switch = Gtk.ComboBox()
        language_switch.set_no_show_all(True)
        language_switch.hide()
        self._language_switch = language_switch

        renderer_text = Gtk.CellRendererText()
        mode_switch.pack_start(renderer_text, True)
        mode_switch.add_attribute(renderer_text, "text", 0)

        renderer_text2 = Gtk.CellRendererText()
        language_switch.pack_start(renderer_text2, True)
        language_switch.add_attribute(renderer_text2, "text", 0)

        plain_langs = []
        if plain:
            plain_langs = list(plain.keys())
            plain_langs.sort()
        plain_language_switch_model = Gtk.ListStore(str)
        self._plain_language_switch_model = plain_language_switch_model
        for i in plain_langs:
            plain_language_switch_model.append([i])

        xhtml_langs = []
        if xhtml:
            xhtml_langs = list(xhtml.keys())
            xhtml_langs.sort()
        xhtml_language_switch_model = Gtk.ListStore(str)
        for i in xhtml_langs:
            xhtml_language_switch_model.append([i])
        self._xhtml_language_switch_model = xhtml_language_switch_model

        b.pack_start(jid_label, False, False, 0)
        b.pack_start(date_label, False, False, 0)
        b.pack_start(mode_switch, False, False, 0)
        b.pack_start(language_switch, False, False, 0)
        b.pack_start(delay_label, False, False, 0)

        column_size_groups[0].add_widget(jid_label)
        column_size_groups[1].add_widget(date_label)
        column_size_groups[2].add_widget(mode_switch)
        column_size_groups[3].add_widget(language_switch)
        column_size_groups[4].add_widget(delay_label)

        b2 = Gtk.Box()
        b2.set_margin_top(5)
        b2.set_margin_left(5)
        b2.set_margin_right(5)
        b2.set_margin_bottom(5)
        b2.set_spacing(5)
        b2.set_orientation(Gtk.Orientation.VERTICAL)

        b2.pack_start(b, False, False, 0)
        b2.pack_start(subject_label, False, False, 0)
        b2.pack_start(subject_label_separator, False, False, 0)
        b2.pack_start(text_label, False, False, 0)

        self._widget = b2
        self._widget.show_all()

        self.set_mode(default_mode)
        self.set_language(default_language)

        language_switch.connect('changed', self._on_lang_switch_chenged)

        return

    def get_widget(self):
        return self._widget

    def destroy(self):
        self.get_widget().destroy()

    def _update_text(self):

        mode = self.get_mode()
        language = self.get_language()

        if mode == 'plain':
            self._text_label.set_markup('')
            self._text_label.set_use_markup(False)
            if language in self._plain:
                self._text_label.set_text(self._plain[language])
            else:
                self._text_label.set_text("")

            self._text_label.set_visible(self._text_label.get_text() != '')

        else:
            self._text_label.set_text('')
            self._text_label.set_use_markup(True)
            if language in self._xhtml:
                self._text_label.set_markup(self._xhtml[language])
            else:
                self._text_label.set_markup("")

            self._text_label.set_visible(self._text_label.get_markup() != '')

        self._subject_label_separator.set_visible(
            self._text_label.get_visible()
            and self._subject_label.get_visible()
            )

        return

    def set_mode(self, mode):

        language = self.get_language()

        if mode == 'plain':
            self._language_switch.set_model(self._plain_language_switch_model)
#            self._mode_switch.set_active(0)
        else:
            self._language_switch.set_model(self._xhtml_language_switch_model)
#            self._mode_switch.set_active(1)

        self.set_language(language)

        self._update_text()

    def get_mode(self):
        ret = 'plain'
        r = self._mode_switch.get_active()
        if r == 1:
            ret = 'xhtml'
        return ret

    def get_language(self):
        ret = ''

        r = self._language_switch.get_active()

        if r != -1:
            mode = self.get_mode()

            if mode == 'plain':
                ret = self._plain_language_switch_model[r][0]
            else:
                ret = self._xhtml_language_switch_model[r][0]

        return ret

    def set_language(self, language):

        model = self._plain_language_switch_model
        if self.get_mode() == 'xhtml':
            model = self._xhtml_language_switch_model

        active = -1
        for i in range(len(model)):
            if model[i][0] == language:
                active = i
                break

        self._language_switch.set_active(active)

        self._update_text()

        return

    def get_date(self):
        return self._date

    def get_plain(self):
        return self._plain

    def get_xhtml(self):
        return self._xhtml

    def get_subject(self):
        return self._subject

    def _on_lang_switch_chenged(self, widget):
        self._update_text()


# TODO: make not dependent from Chat
class ChatLogWidget:

    def __init__(self, controller, chat, operation_mode='chat'):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        if not isinstance(chat, org.wayround.pyabber.chat_pager.Chat):
            raise TypeError(
                "`page' must be the instance of "
                "org.wayround.pyabber.chat_pager.Chat"
                )

        self._incomming_messages_lock = threading.Lock()
        self._incomming_messages_lock.acquire()

        self._operation_mode = None

        self._size_groups = []
        for i in range(5):
            sg = Gtk.SizeGroup()
            sg.set_mode(Gtk.SizeGroupMode.HORIZONTAL)
            self._size_groups.append(sg)

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

        self._controller.message_relay.connect_signal(
            'new_message', self.history_update_listener
            )

        self._looped_timer = org.wayround.utils.timer.LoopedTimer(
            0.25,
            self.scroll_down,
            tuple(),
            dict()
            )

        self._last_scroll_date = None

        self.set_operation_mode(operation_mode)

        self.load_history()

        self._incomming_messages_lock.release()

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
                default_language='',
                default_mode='plain',
                column_size_groups=self._size_groups,
                delay_from=delay_from,
                delay_message=delay_message,
                subject=subject
                )

            newer = None

            for i in self._rows:
                if type(i) == ChatLogTableRow:
                    if i.get_date() > date:
                        newer = self._rows.index(i)

            self._log_box.pack_start(clt.get_widget(), False, False, 0)

            if newer == None:

                self._rows.append(clt)

                if len(self._rows) > 100:
                    del_list = self._rows[:-100]
                    self._rows = self._rows[100:]

                    for i in del_list:
                        i.destroy()

                    del del_list

            else:
                self._rows.insert(newer, clt)

            for i in self._rows:
                self._log_box.reorder_child(i.get_widget(), -1)

            if self._last_date == None or date > self._last_date:
                self._last_date = date

        self._lock.release()

        return

    def destroy(self):
        # NOTE: not needed - read the docs
        #        for i in self._size_groups:
        #            i.destroy()
        self.get_widget().destroy()
        self._looped_timer.stop()

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
                    contact_bare_jid=self._chat.contact_bare_jid,
                    contact_resource=self._chat.contact_resource,
                    active_bare_jid=jid_obj.bare(),
                    active_resource=jid_obj.resource
                    ):

                    self._incomming_messages_lock.acquire()

                    if plain != {} or xhtml != {} or subject != {}:

                        self.add_record(
                            date,
                            self._jid(jid_obj.resource, incomming),
                            plain,
                            xhtml,
                            delay_from,
                            delay_message,
                            subject
                            )

                    self._incomming_messages_lock.release()

        return

    def load_history(self):

        records = []

        jid_resource, types_to_load = \
            org.wayround.pyabber.message_filter.\
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

    def _jid(self, resource, is_incomming):
        jid = ''
        if self._operation_mode == 'groupchat':
            jid = resource
        else:
            if is_incomming:
                jid = '-->'
            else:
                jid = '<--'

        return jid

    def _convert_record(self, rec):
        jid = self._jid(rec['jid_resource'], rec['incomming'])

#        plain = None
#        xhtml = None
#
#        if rec['plain'] != None:
#            plain = json.loads(rec['plain'])
#
#        if rec['xhtml'] != None:
#            xhtml = json.loads(rec['xhtml'])

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
