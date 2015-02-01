
import datetime
import logging
import threading

from gi.repository import Gdk, Gtk

import wayround_org.pyabber.chat_log_widget
import wayround_org.pyabber.jid_widget
import wayround_org.pyabber.message_edit_widget
import wayround_org.pyabber.muc_roster_widget
import wayround_org.pyabber.subject_widget
import wayround_org.pyabber.thread_widget
import wayround_org.utils.gtk
import wayround_org.xmpp.core


class Chat:

    def __init__(
        self, controller, pager, groupchat,
        contact_bare_jid, contact_resource, thread_id, mode='chat',
        muc_roster_storage=None, message_relay_listener_call_queue=None
        ):

        if not mode in ['chat', 'groupchat', 'private']:
            raise ValueError(
                "`mode' must be in ['chat', 'groupchat', 'private']"
                )

        if mode != 'chat':

            if muc_roster_storage == None:
                raise ValueError("`muc_roster_storage' must be defined")

        if mode == 'private':

            if contact_resource == None:
                raise ValueError("`contact_resource' must be defined")

        self._mode = mode
        self._pager = pager
        self._groupchat = groupchat
        self._message_relay_listener_call_queue = \
            message_relay_listener_call_queue

        self._unread = False

        self._controller = controller

        self.contact_bare_jid = contact_bare_jid
        self.contact_resource = contact_resource

        # as queue objects connected to signal objects weakly, firsts can not
        # survive the end of this method: GC destroys them. firsts must live,
        # as long, as instance is living
        self._queues = []

        _t = None
        if message_relay_listener_call_queue:
            _t = message_relay_listener_call_queue.copy()
        self._queues.append(_t)
        self._log = wayround_org.pyabber.chat_log_widget.ChatLogWidget(
            self._controller,
            self,
            mode,
            message_relay_listener_call_queue=_t
            )

        log_widget = self._log.get_widget()

        self._editor = wayround_org.pyabber.message_edit_widget.MessageEdit(
            self._controller
            )
        editor_widget = self._editor.get_widget()

        send_button = Gtk.Button("Send")

        bottom_box = Gtk.Box()
        bottom_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        bottom_box.set_spacing(5)

        bottom_box.pack_start(editor_widget, True, True, 0)
        bottom_box.pack_start(send_button, False, False, 0)

        main_paned = Gtk.Paned()
        main_paned.set_orientation(Gtk.Orientation.VERTICAL)
        main_paned.set_position(400)
        main_paned.add1(log_widget)
        main_paned.add2(bottom_box)

        log_widget.set_size_request(-1, 200)
        bottom_box.set_size_request(-1, 100)

        main_paned.child_set_property(log_widget, 'shrink', False)
        main_paned.child_set_property(bottom_box, 'shrink', False)
        main_paned.child_set_property(bottom_box, 'resize', False)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        if mode == 'chat':
            jid_widget = wayround_org.pyabber.jid_widget.JIDWidget(
                controller,
                controller.roster_storage,
                contact_bare_jid
                )
        else:
            jid_widget = wayround_org.pyabber.jid_widget.MUCRosterJIDWidget(
                contact_bare_jid,
                self.contact_resource,
                self._controller,
                muc_roster_storage
                )

        self._jid_widget = jid_widget

        self._title_label = Gtk.Box()
        self._title_label.set_orientation(Gtk.Orientation.HORIZONTAL)

        self._title_label.pack_start(jid_widget.get_widget(), True, True, 0)

        if self._mode != 'groupchat':

            self._on_tab_close_button_clicked_idle = \
                wayround_org.utils.gtk.to_idle(
                    self._on_tab_close_button_clicked
                    )

            tab_close_button = Gtk.Button('x')
            tab_close_button.connect(
                'clicked',
                self._on_tab_close_button_clicked_idle
                )

            self._title_label.pack_start(tab_close_button, False, False, 0)

        _t = None
        if message_relay_listener_call_queue:
            _t = message_relay_listener_call_queue.copy()
        self._queues.append(_t)
        self._subject_widget = \
            wayround_org.pyabber.subject_widget.SubjectWidget(
                controller, contact_bare_jid, contact_resource, mode,
                message_relay_listener_call_queue=_t
                )

        _t = None
        if message_relay_listener_call_queue:
            _t = message_relay_listener_call_queue.copy()
        self._queues.append(_t)
        self._thread_widget = \
            wayround_org.pyabber.thread_widget.ThreadWidget(
                controller, contact_bare_jid, contact_resource, mode,
                message_relay_listener_call_queue=_t
                )

        b.pack_start(self._subject_widget.get_widget(), False, False, 0)
        b.pack_start(self._thread_widget.get_widget(), False, False, 0)
        b.pack_start(main_paned, True, True, 0)

        self._root_widget = b

        self._editor.connect('key-press-event', self._on_key_press_event)

        send_button.connect('clicked', self._on_send_button_clicked)

        self._update_jid_widget()
        self._thread_widget.set_data(thread_id)

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

    def set_resource(self, value):
        self.contact_resource = value
        self._subject_widget.set_resource(value)
        self._thread_widget.set_resource(value)
        self._update_jid_widget()

    def get_resource(self, value):
        return self.contact_resource

    def _update_jid_widget(self):
        if self._mode != 'chat':
            self._jid_widget.set_nick(self.contact_resource)

    def get_tab_title_widget(self):
        return self._title_label

    def get_page_widget(self):
        return self._root_widget

    def make_available(self):
        j = wayround_org.xmpp.core.JID.new_from_str(self.contact_bare_jid)
        j.resource = self.contact_resource

        options = []
        if self._mode == 'groupchat':
            options.append('muc')

        self._controller.presence_client.presence(
            to_full_or_bare_jid=str(j),
            options=options
            )

    def make_unavailable(self):
        j = wayround_org.xmpp.core.JID.new_from_str(self.contact_bare_jid)
        j.resource = self.contact_resource

        options = []
        if self._mode == 'groupchat':
            options.append('muc')

        self._controller.presence_client.presence(
            to_full_or_bare_jid=str(j),
            typ='unavailable',
            options=options,
            wait=False
            )

    def destroy(self):

        self._controller.message_relay.signal.disconnect(
            self._message_relay_listener_idle
            )

        if self._mode == 'groupchat':
            self.make_unavailable()

        self._jid_widget.destroy()
        self._subject_widget.destroy()
        self._thread_widget.destroy()
        self._log.destroy()
        self._editor.destroy()
        self.get_page_widget().destroy()
        self.get_tab_title_widget().destroy()
        return

    def add_message(self, txt, from_jid, date=None):

        if not isinstance(from_jid, str):
            raise TypeError("`from_jid' must be str")

        if date == None:
            date = datetime.datetime.utcnow()

        self._log.add_record(
            datetime_obj=date,
            body=txt,
            from_jid=from_jid
            )

        return

    def _on_key_press_event(self, textview, event):

        ret = None

        if (
            (event.keyval == Gdk.KEY_Return)
            and
            (event.state & Gdk.ModifierType.CONTROL_MASK != 0)
            ):
            self.send_message()

            ret = True

        return ret

    def _on_send_button_clicked(self, button):
        self.send_message()

    def send_message(self):

        type_ = 'message_chat'
        message_type = 'chat'
        if self._mode == 'groupchat':
            type_ = 'message_groupchat'
            message_type = 'groupchat'

        plain, xhtml = self._editor.get_data()

        self._editor.set_data({'': ''}, None)

        to_jid = self.contact_bare_jid
        if self._mode == 'private':
            to_jid += '/{}'.format(self.contact_resource)

        thread = self._thread_widget.get_data()

        self._controller.message_client.message(
            to_jid=to_jid,
            from_jid=False,
            typ=message_type,
            thread=thread,
            subject=None,
            body=plain,
            xhtml=xhtml
            )

        if self._mode != 'groupchat':

            jid_obj = wayround_org.xmpp.core.JID.new_from_str(
                self.contact_bare_jid
                )
            jid_obj.resource = self.contact_resource

            d = datetime.datetime.utcnow()

            self._controller.message_relay.manual_addition(
                date=d,
                receive_date=d,
                delay_from=None,
                delay_message=None,
                incomming=False,
                connection_jid_obj=self._controller.jid,
                jid_obj=jid_obj,
                type_=type_,
                parent_thread_id=None,
                thread_id=thread,
                subject={},
                plain=plain,
                xhtml=xhtml
                )

        self._editor.clear()

        return

    def set_unread(self, value):
        if not isinstance(value, bool):
            raise ValueError("`unread' must be bool")

        self._unread = value

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if event == 'new_message':
            if type_ == 'message_chat':
                self.set_unread(True)

        return

    def _on_tab_close_button_clicked(self, button):
        self._pager.remove_page(self)


class ChatPager:

    def __init__(self, controller):

        self._controller = controller

        self.pages = []

        self._notebook = Gtk.Notebook()
        self._notebook.set_scrollable(True)
        self._notebook.set_tab_pos(Gtk.PositionType.LEFT)

        self._root_widget = self._notebook

        self._groupchat_addition_lock = threading.Lock()

        return

    def get_widget(self):
        return self._root_widget

    def add_chat(self, jid_obj, thread_id):
        res = self.search_page(jid_obj, thread_id, type_=Chat)

        ret = None

        if len(res) == 0:
            p = Chat(
                controller=self._controller,
                pager=self,
                groupchat=None,
                contact_bare_jid=jid_obj.bare(),
                contact_resource=None,
                thread_id=thread_id
                )
            self.add_page(p)
            ret = p

        return ret

    def add_groupchat(self, jid_obj, message_relay_listener_call_queue=None):
        self._groupchat_addition_lock.acquire()
        res = self.search_page(jid_obj, type_=GroupChat)

        ret = None

        if len(res) == 0:
            p = GroupChat(
                pager=self,
                controller=self._controller,
                room_bare_jid=jid_obj.bare(),
                own_resource=None,
                message_relay_listener_call_queue=(
                    message_relay_listener_call_queue
                    )
                )
            self.add_page(p)
            ret = p
        else:
            ret = res[0]
        self._groupchat_addition_lock.release()
        return ret

    def add_page(self, page):

        """
        :param ChatPage page:
        """

        if not page in self.pages:
            self.pages.append(page)

        self._sync_pages_with_list()

        return

    def add_private(self, full_jid):
        ret = None
        j = wayround_org.xmpp.core.JID.new_from_string(full_jid)
        j2 = j.copy()
        j2.resource = None
        gc = self.add_groupchat(j2)
        if gc != None:
            ret = gc.add_private(j)
        return ret

    def remove_page(self, page):
        while page in self.pages:
            num = self._notebook.page_num(page.get_page_widget())
            self._notebook.remove_page(num)
            page.destroy()
            self.pages.remove(page)

        self._sync_pages_with_list()

        return

    def remove_all_pages(self):
        for i in self.pages[:]:
            self.remove_page(i)

    def destroy(self):
        self.remove_all_pages()
        self.get_widget().destroy()

    def _get_all_notebook_pages(self):
        n = self._notebook.get_n_pages()
        l = []
        for i in range(n):
            l.append(self._notebook.get_nth_page(i))

        return l

    def _get_all_list_pages(self):
        l = []
        for i in self.pages:
            l.append(i.get_page_widget())

        return l

    def _sync_pages_with_list(self):

        _notebook_pages = self._get_all_notebook_pages()
        _list_pages = self._get_all_list_pages()

        for i in self.pages:
            p = i.get_page_widget()
            pp = i.get_tab_title_widget()
            if not p in _notebook_pages:
                self._notebook.append_page(p, pp)
                p.show_all()
                pp.show_all()
                self._notebook.set_tab_reorderable(p, True)

        for i in _notebook_pages:
            if not i in _list_pages:
                page_n = self._notebook.page_num(i)
                self._notebook.remove_page(page_n)

        return

    def search_page(self, jid_obj, thread_id=None, type_=None):

        if not isinstance(jid_obj, wayround_org.xmpp.core.JID):
            raise ValueError("`jid_obj' must be wayround_org.xmpp.core.JID")

        if type_ != None and not type_ in [Chat, GroupChat]:
            raise ValueError("`type_' must be in [Chat, GroupChat]")

        contact_bare_jid = jid_obj.bare()
        contact_resource = None

        if type == Chat:
            contact_resource = jid_obj.resource

        ret = []

        if type_ == Chat:
            for i in self.pages:

                if type(i) == Chat:

                    if (i.contact_bare_jid == contact_bare_jid
                        and i.contact_resource == contact_resource):

                        ret.append(i)

        if type_ == GroupChat:
            for i in self.pages:

                if type(i) == GroupChat:

                    if (i.contact_bare_jid == contact_bare_jid):

                        ret.append(i)

        return ret


class GroupChat:

    def __init__(
        self,
        pager, controller,
        room_bare_jid,
        own_resource=None,
        message_relay_listener_call_queue=None
        ):

        self._lock = threading.RLock()

        with self._lock:

            self._pager = pager
            self._controller = controller

            self.contact_bare_jid = room_bare_jid
            self.contact_resource = own_resource

            self._room_bare_jid_obj = wayround_org.xmpp.core.JID.new_from_str(
                room_bare_jid
                )

            self._storage = controller.roster_storage.get_muc_storage(
                self._room_bare_jid_obj.bare()
                )
            self.pages = []

            b = Gtk.Box()
            b.set_orientation(Gtk.Orientation.VERTICAL)
            b.set_margin_top(5)
            b.set_margin_start(5)
            b.set_margin_end(5)
            b.set_margin_bottom(5)
            b.set_spacing(5)

            self._roster_widget = \
                wayround_org.pyabber.muc_roster_widget.MUCRosterWidget(
                    self._room_bare_jid_obj,
                    controller,
                    self._storage
                    )

            # save it to not be distracted by GC
            self._message_relay_listener_call_queue = \
                message_relay_listener_call_queue

            main_chat_page = Chat(
                controller,
                pager,
                self,
                contact_bare_jid=self._room_bare_jid_obj.bare(),
                contact_resource=own_resource,
                thread_id=None,
                mode='groupchat',
                muc_roster_storage=self._storage,
                message_relay_listener_call_queue=(
                    message_relay_listener_call_queue
                    )
                )
            self._main_chat_page = main_chat_page

            self._notebook = Gtk.Notebook()
            self._notebook.set_scrollable(True)
            self._notebook.set_tab_pos(Gtk.PositionType.TOP)
            self._notebook.append_page(
                main_chat_page.get_page_widget(),
                main_chat_page.get_tab_title_widget()
                )
            self._notebook.set_tab_reorderable(
                main_chat_page.get_page_widget(),
                True
                )

            paned = Gtk.Paned()

            rw_f = Gtk.Frame()
            rw_f.add(self._roster_widget.get_widget())

            muc_box_available_button = Gtk.Button("Available")
            muc_box_available_button.connect(
                'clicked',
                self._on_muc_box_available_button_click
                )

            muc_box_unavailable_button = Gtk.Button("Unavailable")
            muc_box_unavailable_button.connect(
                'clicked',
                self._on_muc_box_unavailable_button_click
                )

            muc_box_cust_pres_button = Gtk.Button("Custom Presence..")
            muc_box_cust_pres_button.connect(
                'clicked',
                self._on_muc_box_cust_pres_button_click
                )

            muc_top_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
            muc_top_box.pack_start(muc_box_available_button, False, False, 0)
            muc_top_box.pack_start(muc_box_unavailable_button, False, False, 0)
            muc_top_box.pack_start(muc_box_cust_pres_button, False, False, 0)

            bbb = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
            bbb.pack_start(muc_top_box, False, False, 0)
            bbb.pack_start(self._notebook, True, True, 0)

            paned.add1(bbb)
            paned.add2(rw_f)

            paned.child_set_property(bbb, 'shrink', False)
            paned.child_set_property(rw_f, 'shrink', False)
            paned.child_set_property(rw_f, 'resize', False)

            b.pack_start(paned, True, True, 0)

            self._tab_widget = \
                wayround_org.pyabber.jid_widget.GroupChatTabWidget(
                    room_bare_jid,
                    own_resource,
                    self._controller,
                    self._storage,
                    self._controller.presence_client,
                    self._controller.client.stanza_processor
                    )

            self._title_label = Gtk.Box()
            self._title_label.set_orientation(Gtk.Orientation.HORIZONTAL)

            tab_close_button = Gtk.Button('x')

            tab_close_button.connect(
                'clicked',
                self._on_tab_close_button_clicked
                )

            self._title_label.pack_start(
                self._tab_widget.get_widget(), True, True, 0
                )

            self._title_label.pack_start(
                tab_close_button, False, False, 0
                )

            self._title_label.show_all()

            self._root_widget = b

            self._root_widget.show_all()

            self.set_own_resource(self._storage.get_own_resource())

            self._roster_widget.sync_with_storage()
            self._roster_widget.sort_jid_widgets()

            self._on_own_rename_storage_action_idle = \
                wayround_org.utils.gtk.to_idle(
                    self._on_own_rename_storage_action
                    )

            self._storage.signal.connect(
                'own_rename',
                self._on_own_rename_storage_action_idle
                )

            self._sync_pages_with_list()

        return

    def set_own_resource(self, value):
        with self._lock:
            logging.debug(
                "Setting GroupChat '{}' own resource '{}'".format(
                    self.contact_bare_jid,
                    value
                    )
                )
            self.contact_resource = value
            self._main_chat_page.set_resource(value)
            self._tab_widget.set_own_resource(value)

    def get_own_resource(self):
        with self._lock:
            ret = self.contact_resource
        return ret

    def destroy(self):
        self._storage.destroy()
        self._main_chat_page.destroy()
        self.remove_all_pages()
        self._roster_widget.destroy()
        self._tab_widget.destroy()
        self.get_tab_title_widget().destroy()
        self.get_page_widget().destroy()

    def get_tab_title_widget(self):
        with self._lock:
            ret = self._title_label
        return ret

    def get_page_widget(self):
        with self._lock:
            ret = self._root_widget
        return ret

    add_page = ChatPager.add_page

    remove_page = ChatPager.remove_page

    remove_all_pages = ChatPager.remove_all_pages

    def _get_all_notebook_pages(self):
        n = self._notebook.get_n_pages()
        l = []
        for i in range(n):
            l.append(self._notebook.get_nth_page(i))

        p = self._main_chat_page.get_page_widget()
        if p in l:
            l.remove(p)

        return l

    _get_all_list_pages = ChatPager._get_all_list_pages

    def search_page(self, resource):

        with self._lock:

            if not isinstance(resource, str):
                raise ValueError("`resource' must be str")

            ret = []

            for i in self.pages:

                if i.contact_resource == resource:

                    ret.append(i)

        return ret

    def _sync_pages_with_list(self):

        with self._lock:

            _notebook_pages = self._get_all_notebook_pages()
            _list_pages = self._get_all_list_pages()

            for i in self.pages:
                p = i.get_page_widget()
                pp = i.get_tab_title_widget()
                if not p in _notebook_pages:
                    self._notebook.append_page(p, pp)
                    p.show_all()
                    pp.show_all()
                    self._notebook.set_tab_reorderable(p, True)

            for i in _notebook_pages:
                if not i in _list_pages:
                    page_n = self._notebook.page_num(i)
                    self._notebook.remove_page(page_n)

            _notebook_pages = self._get_all_notebook_pages()
            w = self._main_chat_page.get_page_widget()
            if len(_notebook_pages) != 0:
                w.set_margin_top(5)
                w.set_margin_start(5)
                w.set_margin_end(5)
                w.set_margin_bottom(5)
                self._notebook.set_show_tabs(True)
                self._notebook.set_show_border(True)
            else:
                w.set_margin_top(0)
                w.set_margin_start(0)
                w.set_margin_end(0)
                w.set_margin_bottom(0)
                self._notebook.set_show_tabs(False)
                self._notebook.set_show_border(False)

        return

    def add_private(self, jid_obj):

        with self._lock:

            res = self.search_page(jid_obj.resource)

            ret = None

            if len(res) == 0:
                p = Chat(
                    controller=self._controller,
                    pager=self,
                    groupchat=None,
                    contact_bare_jid=jid_obj.bare(),
                    contact_resource=jid_obj.resource,
                    thread_id=None,
                    mode='private',
                    muc_roster_storage=self._storage
                    )
                self.add_page(p)
                ret = p

        return ret

    def _on_tab_close_button_clicked(self, button):
        with self._lock:
            self._pager.remove_page(self)
        return

    def _on_own_rename_storage_action(self, event, storage, own_nick):
        with self._lock:
            if event == 'own_rename':
                if own_nick != None:
                    logging.debug(
                        "{} Received new own nick {}".format(
                            self.contact_bare_jid,
                            own_nick
                            )
                        )
                    self.set_own_resource(own_nick)
        return

    def _on_muc_box_available_button_click(self, button):
        j = wayround_org.xmpp.core.JID.new_from_str(self.contact_bare_jid)
        j.resource = self.contact_resource
        self._controller.presence_client.presence(
            to_full_or_bare_jid=str(j),
            options=['muc']
            )
        return

    def _on_muc_box_unavailable_button_click(self, button):
        j = wayround_org.xmpp.core.JID.new_from_str(self.contact_bare_jid)
        j.resource = self.contact_resource
        self._controller.presence_client.presence(
            to_full_or_bare_jid=str(j),
            typ='unavailable',
            options=['muc']
            )
        return

    def _on_muc_box_cust_pres_button_click(self, button):
        j = wayround_org.xmpp.core.JID.new_from_str(self.contact_bare_jid)
        j.resource = self.contact_resource
        self._controller.show_presence_control_window(to_=str(j))
        return
