
import datetime
import uuid

from gi.repository import Gtk
from gi.repository import Gdk

import org.wayround.xmpp.core

import org.wayround.pyabber.chat_log_widget
import org.wayround.pyabber.message_edit_widget


class ChatPage:

    """
    Chat page interface

    This is interface for creating page classes which can be used and
    interacted in cooperation with ChatPager.
    """

    # this attributes must be changed by __init__
    contact_bare_jid = 'none'
    # resource is needed in MUC conversations
    contact_resource = None
    thread_id = '0'

    def __init__(self, pager, controller, contact_bare_jid, thread_id):
        pass

    def get_tab_title_widget(self):
        pass

    def get_page_widget(self):
        pass

    def set_visible(self, value):
        pass

    def destroy(self):
        pass

    def close(self):
        self.destroy()


class Chat(ChatPage):
    """
    This is for single chat, not for MUCs
    """

    def __init__(
        self, pager, controller,
        contact_bare_jid, thread_id
        ):

        self._unread = False

        if thread_id == None:
            thread_id = uuid.uuid4().hex

        self._controller = controller

        self.contact_bare_jid = contact_bare_jid
        self.thread_id = thread_id

        self._title_label = Gtk.Label(contact_bare_jid)

        self._log = org.wayround.pyabber.chat_log_widget.ChatLogWidget(
            self._controller,
            self
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
        main_paned.set_margin_top(5)
        main_paned.set_margin_left(5)
        main_paned.set_margin_right(5)
        main_paned.set_margin_bottom(5)
        main_paned.set_position(400)
        main_paned.add1(log_widget)
        main_paned.add2(bottom_box)

        log_widget.set_size_request(-1, 200)
        bottom_box.set_size_request(-1, 100)
        main_paned.child_set_property(bottom_box, 'shrink', False)
        main_paned.child_set_property(log_widget, 'shrink', False)

        self._root_widget = main_paned

        self._editor.connect('key-press-event', self._on_key_press_event)
        send_button.connect('clicked', self._on_send_button_clicked)

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

        return

    def get_tab_title_widget(self):
        return self._title_label

    def get_page_widget(self):
        return self._root_widget

    def destroy(self):
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
        txt = self._editor.get_text()
        self._editor.set_text('')
        self._controller.message_client.message(
            to_jid=self.contact_bare_jid,
            from_jid=False,
            typ='chat',
            thread=self.thread_id,
            subject=None,
            body=txt
            )

        self._controller.storage.add_history_record(
            date=datetime.datetime.utcnow(),
            incomming=False,
            connection_jid_obj=self._controller.jid,
            jid_obj=org.wayround.xmpp.core.JID.new_from_str(
                self.contact_bare_jid
                ),
            type_='message_chat',
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

    def add_page(self, page):

        """
        :param ChatPage page:
        """

        if not isinstance(page, ChatPage):
            raise TypeError("`page' must be the instance of ChatPage")

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

    def feed_stanza(self, stanza):

        if not isinstance(stanza, org.wayround.xmpp.core.Stanza):
            raise TypeError(
                "`stanza' must be of type org.wayround.xmpp.core.Stanza"
                )

        if stanza.tag != '{jabber:client}message':
            # do nothing
            pass
        else:

            jid = org.wayround.xmpp.core.JID.new_from_str(stanza.from_jid)
            thread = None
            thread_e = stanza.get_element().find('{jabber:client}thread')
            if thread_e != None:
                thread = thread_e.text

            body = None
            body_e = stanza.get_element().find('{jabber:client}body')
            if body_e != None:
                body = body_e.text

            res = self.search_page(
                contact_bare_jid=jid.bare(),
                thread_id=thread,
                type_=Chat
                )

            page = None

            if len(res) == 0:

                page = Chat(
                    self,
                    controller=self._controller,
                    contact_bare_jid=jid.bare(),
                    contact_resource=None,  # TODO: really?
                    thread_id=thread
                    )

                self.add_page(page)
            else:

                page = res[0]

            if page:

                page.add_message(body, str(jid))

        return

    def search_page(self, jid_obj, thread_id=None, type_=None):

        if not isinstance(jid_obj, org.wayround.xmpp.core.JID):
            raise ValueError("`jid_obj' must be org.wayround.xmpp.core.JID")

        if type_ != None and not issubclass(type_, ChatPage):
            raise ValueError("`type_' must be subclass of ChatPage")

        contact_bare_jid = jid_obj.bare()
        contact_resource = jid_obj.resource

        ret = []

        for i in self.pages:

            if (contact_bare_jid != None
                and i.contact_bare_jid != contact_bare_jid):
                continue

            if (i.contact_resource != None and contact_resource != None
                and i.contact_resource != contact_resource):
                continue

            if (i.thread_id != None and thread_id != None
                and i.thread_id != thread_id
                ):
                continue

            if type_ != None and type(i) != type_:
                continue

            ret.append(i)

        return ret

    def history_update_listener(
        self, event, storage,
        date, incomming, connection_jid_obj, jid_obj, type_,
        parent_thread_id, thread_id, subject, plain, xhtml
        ):

        if event == 'history_update':

            if type_ in ['message_chat', 'message_groupchat']:

                typ_ = None

                if type_ == 'message_chat':
                    typ_ = Chat

                if type_ == 'message_groupchat':
                    typ_ = Chat

                res = self.search_page(jid_obj, thread_id, typ_)
                if len(res) == 0:
                    p = Chat(
                        self,
                        self._controller,
                        jid_obj.bare(),
                        thread_id
                        )
                    self.add_page(p)
                    res.append(p)

        return
