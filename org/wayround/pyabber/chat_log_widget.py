
import json
import logging
import sched
import threading
import time
import weakref

from gi.repository import Gtk, Pango

import org.wayround.pyabber.ccc
import org.wayround.pyabber.chat_pager
import org.wayround.utils.gtk
import org.wayround.utils.timer
import org.wayround.xmpp.core


CHAT_LOG_TABLE_ROW_MODE_ITEMS = Gtk.ListStore(str)
CHAT_LOG_TABLE_ROW_MODE_ITEMS.append(['plain'])
CHAT_LOG_TABLE_ROW_MODE_ITEMS.append(['xhtml'])


class ChatLogTableRow:

    def __init__(
        self,
        date, jid_to_display, plain, xhtml,
        default_language, default_mode,
        column_size_groups
        ):

        self._plain = plain
        self._xhtml = xhtml

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        date_label = Gtk.Label(date)
        date_label.set_alignment(0.0, 0.0)

        jid_label = Gtk.Label(jid_to_display)
        jid_label.set_alignment(0.0, 0.0)

        text_label = Gtk.Label()
        self._text_label = text_label
        text_label.set_alignment(0.0, 0.0)
        text_label.set_line_wrap(True)
        text_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        text_label.set_selectable(True)
        text_label.set_justify(Gtk.Justification.LEFT)

        mode_switch = Gtk.ComboBox()
        self._mode_switch = mode_switch
        mode_switch.set_model(CHAT_LOG_TABLE_ROW_MODE_ITEMS)

        language_switch = Gtk.ComboBox()
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

        b.pack_start(date_label, False, False, 0)
        b.pack_start(jid_label, False, False, 0)
        b.pack_start(text_label, True, True, 0)
        b.pack_start(mode_switch, False, False, 0)
        b.pack_start(language_switch, False, False, 0)

        column_size_groups[0].add_widget(date_label)
        column_size_groups[1].add_widget(jid_label)
        column_size_groups[2].add_widget(text_label)
        column_size_groups[3].add_widget(mode_switch)
        column_size_groups[4].add_widget(language_switch)

        self._widget = b

        self.set_mode(default_mode)
        self.set_language(default_language)

        b.show_all()

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
            self._text_label.set_text(self._plain[language])

        else:
            self._text_label.set_text('')
            self._text_label.set_use_markup(True)
            self._text_label.set_markup(self._xhtml[language])

        return

    def set_mode(self, mode):

        language = self.get_language()

        if mode == 'plain':
            self._language_switch.set_model(self._plain_language_switch_model)
            self._mode_switch.set_active(0)
        else:
            self._language_switch.set_model(self._xhtml_language_switch_model)
            self._mode_switch.set_active(1)

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

    def _on_mode_switch_changed(self):
        pass


class ChatLogWidget:

    def __init__(self, controller, chat):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        if not isinstance(chat, org.wayround.pyabber.chat_pager.ChatPage):
            raise TypeError(
                "`page' must be the instance of "
                "org.wayround.pyabber.chat_pager.ChatPage"
                )

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

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

        self._looped_timer = org.wayround.utils.timer.LoopedTimer(
            0.25,
            self.scroll_down,
            tuple(),
            dict()
            )

        self._last_scroll_date = None

        self.update()

        self._looped_timer.start()

        return

    def get_widget(self):
        return self._root_widget

    def add_record(self, date, jid, plain, xhtml):

        self._lock.acquire()

        clt = ChatLogTableRow(
            date,
            jid,
            plain,
            xhtml,
            default_language='',
            default_mode='plain',
            column_size_groups=self._size_groups
            )

        self._rows.append(clt)

        self._log_box.pack_start(clt.get_widget(), False, False, 0)

        if len(self._rows) > 100:
            del_list = self._rows[:-100]
            self._rows = self._rows[100:]

            for i in del_list:
                i.destroy()

            del del_list

        self._lock.release()

    def destroy(self):
        self._looped_timer.stop()
        self.get_widget().destroy()

    def history_update_listener(
        self, event, storage,
        date, incomming, connection_jid_obj, jid_obj, type_,
        parent_thread_id, thread_id, subject, plain, xhtml
        ):

        if event == 'history_update':
            if type_ == 'message_chat':
                self.update()

        return

    def update(self):

        records = []

        if self._last_date == None:

            records = self._controller.storage.get_history_records(
                connection_bare_jid=self._controller.jid.bare(),
                connection_jid_resource=None,
                bare_jid=self._chat.contact_bare_jid,
                jid_resource=None,
                starting_from_date=None,
                starting_includingly=True,
                ending_with_date=None,
                ending_includingly=True,
                limit=100,
                offset=None,
                types=['message_chat']
                )

        else:

            records = self._controller.storage.get_history_records(
                connection_bare_jid=self._controller.jid.bare(),
                connection_jid_resource=None,
                bare_jid=self._chat.contact_bare_jid,
                jid_resource=None,
                starting_from_date=self._last_date,
                starting_includingly=False,
                ending_with_date=None,
                ending_includingly=True,
                limit=None,
                offset=None,
                types=['message_chat']
                )

        for i in records:
            jid = '??JID??'
            if i['incomming']:
                jid = '-->'
            else:
                jid = '<--'

            plain = None
            xhtml = None

            if i['plain'] != None:
                plain = json.loads(i['plain'])

            if i['xhtml'] != None:
                xhtml = json.loads(i['xhtml'])

            self.add_record(
                i['date'],
                jid,
                plain,
                xhtml
                )

            self._last_date = i['date']

        return

    def scroll_down(self):
        if self._last_scroll_date != self._last_date:
            self._last_scroll_date = self._last_date
            sb = self._sw.get_vscrollbar()
            adj = sb.get_adjustment()
            sb.set_value(adj.get_upper())
