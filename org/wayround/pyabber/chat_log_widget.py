
import datetime
import logging

from gi.repository import Gtk

import org.wayround.pyabber.ccc
import org.wayround.pyabber.chat_pager
import org.wayround.xmpp.core


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

        self._controller = controller
        self._chat = chat

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)

        text_view = Gtk.TextView()
        self._text_view = text_view

        frame = Gtk.Frame()
        sw = Gtk.ScrolledWindow()
        frame.add(sw)
        sw.add(text_view)

        self._root_widget = frame

        self._controller.storage.connect_signal(
            'history_update', self.history_update_listener
            )

        self._last_date = None
        self.update()

        return

    def get_widget(self):
        return self._root_widget

    def add_record(self, datetime_obj, body, from_jid=None):

        b = self._text_view.get_buffer()

        fj = ''
        if from_jid != None:
            fj = '{} '.format(str(from_jid))

        b.insert(
            b.get_end_iter(),
            '{date} {fj} {body}\n'.format(
                date=str(datetime_obj),
                body=body,
                fj=fj
                )
            )

    def destroy(self):
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

            logging.debug("First History records:\n{}".format(records))

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

            logging.debug("History records:\n{}".format(records))

        for i in records:
            logging.debug("adding record")
            logging.debug(repr(i))
            logging.debug('')
            jid = '??JID??'
            if i['incomming']:
                jid = i['bare_jid']
            else:
                jid = i['connection_bare_jid']
            self.add_record(i['date'], i['plain'], jid)
            self._last_date = i['date']

        logging.debug("Message Log update complete")

        return
