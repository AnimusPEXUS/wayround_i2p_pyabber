
import datetime
import logging
import uuid

from gi.repository import Gdk, Gtk

import org.wayround.pyabber.chat_log_widget
import org.wayround.pyabber.jid_widget
import org.wayround.pyabber.message_edit_widget
import org.wayround.pyabber.muc_roster_storage
import org.wayround.pyabber.muc_roster_widget
import org.wayround.xmpp.core


class Chat:

    def __init__(
        self, pager, controller,
        contact_bare_jid, contact_resource, thread_id, mode='chat',
        muc_roster_storage=None, parrent_groupchat=None
        ):

        if not mode in ['chat', 'groupchat', 'private']:
            raise ValueError(
                "`mode' must be in ['chat', 'groupchat', 'private']"
                )

        if mode != 'chat':

            if muc_roster_storage == None:
                raise ValueError("`muc_roster_storage' must be defined")

            if contact_resource == None:
                raise ValueError("`contact_resource' must be defined")

        if mode == 'private':
            if parrent_groupchat == None:
                raise ValueError("`parrent_groupchat' must be defined")

        self._mode = mode

        self._unread = False

        if thread_id == None:
            thread_id = uuid.uuid4().hex

        self._controller = controller

        self.contact_bare_jid = contact_bare_jid
        self.contact_resource = contact_resource
        self.thread_id = thread_id
        self.parrent_groupchat = parrent_groupchat

        self._log = org.wayround.pyabber.chat_log_widget.ChatLogWidget(
            self._controller,
            self,
            mode
            )

        log_widget = self._log.get_widget()

        self._editor = org.wayround.pyabber.message_edit_widget.MessageEdit()
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
        main_paned.child_set_property(bottom_box, 'shrink', False)
        main_paned.child_set_property(log_widget, 'shrink', False)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        if mode == 'chat':
            jid_widget = org.wayround.pyabber.jid_widget.JIDWidget(
                controller,
                controller.roster_storage,
                contact_bare_jid,
                None
                )
        else:
            jid_widget = org.wayround.pyabber.jid_widget.MUCRosterJIDWidget(
                contact_bare_jid,
                self.contact_resource,
                self._controller,
                muc_roster_storage
                )

        self._jid_widget = jid_widget

        self._title_label = jid_widget.get_widget()

        b.pack_start(main_paned, True, True, 0)

        self._root_widget = b

        self._editor.connect('key-press-event', self._on_key_press_event)
        send_button.connect('clicked', self._on_send_button_clicked)

        self._update_jid_widget()

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

        return

    def set_resource(self, value):
        self.contact_resource = value
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

    def destroy(self):
        self._jid_widget.destroy()
        self._title_label.destroy()
        self._editor.destroy()
        self._log.destroy()
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

        txt = self._editor.get_text()

        self._editor.set_text('')

        to_jid = self.contact_bare_jid
        if self._mode == 'private':
            to_jid += '/{}'.format(self.contact_resource)

        self._controller.message_client.message(
            to_jid=to_jid,
            from_jid=False,
            typ=message_type,
            thread=self.thread_id,
            subject=None,
            body=txt
            )

        if self._mode != 'groupchat':

            jid_obj = org.wayround.xmpp.core.JID.new_from_str(
                self.contact_bare_jid
                )
            jid_obj.resource = self.contact_resource

            self._controller.storage.add_history_record(
                date=datetime.datetime.utcnow(),
                incomming=False,
                connection_jid_obj=self._controller.jid,
                jid_obj=jid_obj,
                type_=type_,
                parent_thread_id=None,
                thread_id=self.thread_id,
                subject=None,
                plain={'': txt},
                xhtml=None
                )

    def set_unread(self, value):
        if not isinstance(value, bool):
            raise ValueError("`unread' must be bool")

        self._unread = value

    def history_update_listener(
        self, event, storage,
        date, incomming, connection_jid_obj, jid_obj, type_,
        parent_thread_id, thread_id, subject, plain, xhtml
        ):

        if event == 'history_update':
            if type_ == 'message_chat':
                self.set_unread(True)

        return


class ChatPager:

    def __init__(self, controller):

        self._controller = controller

        self.pages = []

        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.LEFT)

        self._root_widget = self._notebook

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

    def get_widget(self):
        return self._root_widget

    def add_chat(self, jid_obj, thread_id):
        res = self._search_page(jid_obj, thread_id, type_=Chat)

        ret = None

        if len(res) == 0:
            p = Chat(
                pager=self,
                controller=self._controller,
                contact_bare_jid=jid_obj.bare(),
                contact_resource=None,
                thread_id=thread_id
                )
            self.add_page(p)
            ret = p

        return ret

    def add_groupchat(self, jid_obj):
        res = self._search_page(jid_obj, type_=GroupChat)

        ret = None

        if len(res) == 0:
            p = GroupChat(
                pager=self,
                controller=self._controller,
                room_bare_jid=jid_obj.bare(),
                own_resource=jid_obj.resource
                )
            self.add_page(p)
            ret = p

        return ret

    def add_page(self, page):

        """
        :param ChatPage page:
        """

        if not page in self.pages:
            self.pages.append(page)

        self._sync_pages_with_list()

        return

    def remove_page(self, page):
        while page in self.pages:
            page.destroy()
            self.pages.remove(page)
        return

    def close_all_pages(self):
        for i in self.pages[:]:
            self.remove_page(i)

    def destroy(self):
        self.close_all_pages()

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
            if not i.get_page_widget() in _notebook_pages:
                self._notebook.append_page(p, pp)
                p.show_all()
                pp.show_all()

        for i in _notebook_pages:
            if not i in _list_pages:
                page_n = self._notebook.page_num(i)
                self._notebook.remove_page(page_n)

        return

    def _search_page(self, jid_obj, thread_id=None, type_=None):

        if not isinstance(jid_obj, org.wayround.xmpp.core.JID):
            raise ValueError("`jid_obj' must be org.wayround.xmpp.core.JID")

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

    def history_update_listener(
        self, event, storage,
        date, incomming, connection_jid_obj, jid_obj, type_,
        parent_thread_id, thread_id, subject, plain, xhtml
        ):

        if event == 'history_update':

            if type_ in ['message_chat', 'message_groupchat']:

                if type_ == 'message_chat':

                    # TODO: rework this shet

                    group_chat_found = None
                    for i in self.pages:
                        if i.contact_bare_jid == jid_obj.bare():
                            group_chat_found = i
                            break

                    if group_chat_found == None:
                        self.add_chat(jid_obj, thread_id)

                if type_ == 'message_groupchat':
                    #                    jo = jid_obj.copy()
                    #                    jo.resource = None
                    #                    self.add_groupchat(jo)
                    self.add_groupchat(jid_obj)

        return


class GroupChat:

    def __init__(
        self,
        pager, controller,
        room_bare_jid,
        own_resource=None
        ):

        self.contact_bare_jid = room_bare_jid
        self.contact_resource = own_resource
        self.thread_id = None

        self._controller = controller
        self._room_bare_jid_obj = org.wayround.xmpp.core.JID.new_from_str(
            room_bare_jid
            )

        self.pages = []

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        self._storage = org.wayround.pyabber.muc_roster_storage.Storage(
            self._room_bare_jid_obj,
            controller.presence_client
            )

        self._roster_widget = \
            org.wayround.pyabber.muc_roster_widget.MUCRosterWidget(
                self._room_bare_jid_obj,
                controller,
                self._storage
                )

        main_chat_page = Chat(
            pager,
            controller,
            contact_bare_jid=self._room_bare_jid_obj.bare(),
            contact_resource=own_resource,
            thread_id=None,
            mode='groupchat',
            muc_roster_storage=self._storage
            )

        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.TOP)
        self._notebook.append_page(
            main_chat_page.get_page_widget(),
            main_chat_page.get_tab_title_widget()
            )

        paned = Gtk.Paned()

        paned.add1(self._notebook)
        paned.add2(self._roster_widget.get_widget())

        b.pack_start(paned, True, True, 0)

        self._tab_widget = org.wayround.pyabber.jid_widget.GroupChatTabWidget(
            room_bare_jid,
            own_resource,
            self._controller,
            self._storage,
            self._controller.presence_client,
            self._controller.client.stanza_processor
            )

        self._title_label = self._tab_widget.get_widget()

        self._main_chat_page = main_chat_page

        self._root_widget = b

        self._root_widget.show_all()

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

        self.set_own_resource(own_resource)

        return

    def set_own_resource(self, value):
        self.contact_resource = value
        self._main_chat_page.set_resource(value)
        self._tab_widget.set_own_resource(value)
#        self._jid_widget.set_resource(value)

    def get_own_resource(self):
        return self.contact_resource

    def destroy(self):
        self.close_all_pages()
        self._roster_widget.destroy()
#        self._jid_widget.destroy()
        self._main_chat_page.destroy()
        self._tab_widget.destroy()

    def get_tab_title_widget(self):
        return self._title_label

    def get_page_widget(self):
        return self._root_widget

    add_page = ChatPager.add_page

    remove_page = ChatPager.remove_page

    close_all_pages = ChatPager.close_all_pages

    _get_all_notebook_pages = ChatPager._get_all_notebook_pages

    _get_all_list_pages = ChatPager._get_all_list_pages

    _search_page = ChatPager._search_page

    def _sync_pages_with_list(self):

        _notebook_pages = self._get_all_notebook_pages()
        _list_pages = self._get_all_list_pages()

        for i in self.pages:
            p = i.get_page_widget()
            pp = i.get_tab_title_widget()
            if not i.get_page_widget() in _notebook_pages:
                self._notebook.append_page(p, pp)
                p.show_all()
                pp.show_all()

        for i in _notebook_pages[1:]:
            if not i in _list_pages:
                page_n = self._notebook.page_num(i)
                self._notebook.remove_page(page_n)

        return

    def add_private(self, jid_obj, parrent_groupchat):
        res = self._search_page(jid_obj, type_=Chat)

        ret = None

        if len(res) == 0:
            p = Chat(
                pager=self,
                controller=self._controller,
                contact_bare_jid=jid_obj.bare(),
                contact_resource=jid_obj.resource,
                thread_id=None,
                parrent_groupchat=parrent_groupchat,
                mode='private'
                )
            self.add_page(p)
            ret = p

        return ret

    def history_update_listener(
        self, event, storage,
        date, incomming, connection_jid_obj, jid_obj, type_,
        parent_thread_id, thread_id, subject, plain, xhtml
        ):

        if event == 'history_update':

            if type_ == 'message_chat':

                if self.contact_bare_jid == jid_obj.bare():

                    self.add_private(jid_obj, self._main_chat_page)

        return
