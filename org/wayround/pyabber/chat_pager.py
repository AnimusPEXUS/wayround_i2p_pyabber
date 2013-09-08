
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

    This is interface for creating page classes which can be used and interacted
    in cooperation with ChatPager.
    """

    # this attributes must be changed by __init__
    contact_jid = 'none'
    thread_id = '0'

    def __init__(
        self, pager, controller,
        contact_bare_jid, contact_resource, thread_id
        ):
        pass

    def get_tab_title_widget(self):
        pass

    def get_page_widget(self):
        pass

    def set_visible(self, value):
        pass

    def close(self):
        pass


class Chat(ChatPage):
    """
    This is for single chat, not for MUCs
    """

    def __init__(
        self, pager, controller,
        contact_bare_jid, contact_resource, thread_id
        ):

        if thread_id == None:
            thread_id = uuid.uuid4().hex

        self._controller = controller

        self.contact_bare_jid = contact_bare_jid
        self.contact_resource = contact_resource
        self.thread_id = thread_id

        self._latest_full_jid = contact_bare_jid

        self._title_label = Gtk.Label(contact_bare_jid)

        self._log = org.wayround.pyabber.chat_log_widget.ChatLogWidget()
        self._editor = org.wayround.pyabber.message_edit_widget.MessageEdit()

        send_button = Gtk.Button("Send")

        bottom_box = Gtk.Box()
        bottom_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        bottom_box.pack_start(self._editor.get_widget(), True, True, 0)
        bottom_box.pack_start(send_button, False, False, 0)

        main_paned = Gtk.Paned()
        main_paned.set_orientation(Gtk.Orientation.VERTICAL)
        main_paned.add1(self._log.get_widget())
        main_paned.add2(bottom_box)

        self._root_widget = main_paned

        self._editor.connect('key-press-event', self._on_key_press_event)
        send_button.connect('clicked', self._on_send_button_clicked)

        return


    def get_tab_title_widget(self):
        return self._title_label

    def get_page_widget(self):
        return self._root_widget

    def close(self):
        return

    def add_message(self, txt, from_jid):

        if not isinstance(from_jid, str):
            raise TypeError("`from_jid' must be str")

        self._log.add_record(
            datetime_obj=datetime.datetime.now(),
            text=txt,
            from_jid=from_jid
            )

        self._latest_full_jid = from_jid

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
        self._controller.message.message(
            to_jid=self._latest_full_jid,
            from_jid=False,
            typ='chat',
            thread=self.thread_id,
            subject=None,
            body=txt
            )

class ChatPager:

    def __init__(self, controller):

        self._controller = controller

        self.pages = []

        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.LEFT)

        self._root_widget = self._notebook

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

    def close_page(self, page):


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

            jid = org.wayround.xmpp.core.jid_from_str(stanza.jid_from)
            thread = None
            thread_e = stanza.body.find('{jabber:client}thread')
            if thread_e != None:
                thread = thread_e.text

            body = None
            body_e = stanza.body.find('{jabber:client}body')
            if body_e != None:
                body = body_e.text

            res = self.search_page(
                contact_bare_jid=jid.bare(),
                thread_id=thread,
                typ=Chat
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

    def search_page(
        self,
        contact_bare_jid=None, contact_resource=None, thread_id=None,
        typ=None
        ):

        if contact_bare_jid == None and (contact_resource != None or thread_id != None):
            raise Exception(
                "`contact_resource' and `thread_id' can not be"
                " not None if contact_bare_jid is None\n"
                "It is a security consideration"
                )

        ret = []

        for i in self.pages:

            if contact_bare_jid != None and i.contact_bare_jid != contact_bare_jid:
                continue

            if contact_resource != None and i.contact_resource != contact_resource:
                continue

            if thread_id != None and i.thread_id != thread_id:
                continue

            if typ != None and type(i) != typ:
                continue

            ret.append(i)

        return ret
