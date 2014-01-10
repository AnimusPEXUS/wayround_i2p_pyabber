
import datetime
import threading

import org.wayround.xmpp.delay
import org.wayround.utils.signal


class MessageRelay(org.wayround.utils.signal.Signal):

    def __init__(self, controller):

        self._controller = controller
        super().__init__(['new_message'])

    def on_message(self, event, message_obj, stanza):

        if event == 'message':

            type_ = 'message_normal'
            typ = stanza.get_typ()
            if typ != None and typ != 'normal':
                type_ = 'message_{}'.format(typ)

            thread = None
            parent = None

            _t = stanza.get_thread()
            if _t:
                thread = _t.get_thread()
                parent = _t.get_parent()

                if thread == None:
                    thread = ''

                if parent == None:
                    parent = ''

            date = datetime.datetime.utcnow()
            receive_date = date

            delay_elements = stanza.get_element().findall(
                '{urn:xmpp:delay}delay'
                )

            delay_from = None
            delay_message = None

            if len(delay_elements) != 0:
                delay_object = org.wayround.xmpp.delay.Delay.new_from_element(
                    delay_elements[0]
                    )
                delay_from = delay_object.get_from_()
                delay_message = delay_object.get_text()
                date = delay_object.get_stamp()

                if delay_message == None:
                    delay_message = ''

            self.manual_addition(
                date=date,
                receive_date=receive_date,
                delay_from=delay_from,
                delay_message=delay_message,
                incomming=True,
                connection_jid_obj=self._controller.jid,
                jid_obj=org.wayround.xmpp.core.JID.new_from_str(
                    stanza.get_from_jid()
                    ),
                type_=type_,
                parent_thread_id=parent,
                thread_id=thread,
                subject=stanza.get_subject_dict(),
                plain=stanza.get_body_dict(),
                xhtml={}
                )

    def manual_addition(
        self,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        t = threading.Thread(
            target=self._controller.profile.data.add_history_record,
            args=(
                date, receive_date, delay_from, delay_message, incomming,
                connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
                subject, plain, xhtml,
                )
            )
        t.start()

        self.emit_signal(
            'new_message',
            self,
            date, receive_date, delay_from, delay_message, incomming,
            connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
            subject, plain, xhtml
            )
