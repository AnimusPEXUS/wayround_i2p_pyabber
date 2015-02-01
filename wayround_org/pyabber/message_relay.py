
import datetime
import threading

import wayround_org.xmpp.delay
import wayround_org.utils.threading


class MessageRelay:

    def __init__(self, controller):

        self._controller = controller
        self.signal = wayround_org.utils.threading.Signal(
            self,
            ['new_message']
            )

        return

    def on_message(self, event, message_obj, stanza):

        if event == 'message':

#            logging.debug("Received stanza for relay: {}".format(stanza))

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
                delay_object = wayround_org.xmpp.delay.Delay.new_from_element(
                    delay_elements[0]
                    )
                delay_from = delay_object.get_from_()
                delay_message = delay_object.get_text()
                date = delay_object.get_stamp()

                if date.tzinfo != None:
                    date = date.astimezone(datetime.timezone.utc)
                    date = date.replace(tzinfo=None)

                if delay_message == None:
                    delay_message = ''

            self.internal_addition(
                original_stanza=stanza,
                date=date,
                receive_date=receive_date,
                delay_from=delay_from,
                delay_message=delay_message,
                incomming=True,
                connection_jid_obj=self._controller.jid,
                jid_obj=wayround_org.xmpp.core.JID.new_from_str(
                    stanza.get_from_jid()
                    ),
                type_=type_,
                parent_thread_id=parent,
                thread_id=thread,
                subject=stanza.get_subject_dict(),
                plain=stanza.get_body_dict(),
                xhtml={}
                )

        return

    def manual_addition(
        self,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        original_stanza = wayround_org.xmpp.core.Stanza(tag='message')
        original_stanza.set_from_jid(str(jid_obj))
        original_stanza.set_to_jid(str(connection_jid_obj))
        _t = type_
        if _t.startswith('message_'):
            _t = _t[len('message_'):]
        if _t == 'normal':
            _t = None
        original_stanza.set_typ(_t)
        original_stanza.set_body_dict(plain)
        original_stanza.set_subject_dict(subject)

        ret = self.internal_addition(
            original_stanza, date, receive_date, delay_from, delay_message,
            incomming, connection_jid_obj, jid_obj, type_, parent_thread_id,
            thread_id, subject, plain, xhtml
            )

        return ret

    def internal_addition(
        self,
        original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        if not isinstance(subject, dict):
            raise TypeError("`subject' must be dict")

        if not isinstance(plain, dict):
            raise TypeError("`plain' must be dict")

        if not isinstance(xhtml, dict):
            raise TypeError("`xhtml' must be dict")

        t = threading.Thread(
            target=self._controller.profile.data.add_history_record,
            args=(
                date, receive_date, delay_from, delay_message, incomming,
                connection_jid_obj, jid_obj, type_, parent_thread_id,
                thread_id, subject, plain, xhtml,
                )
            )
        t.start()

        self.signal.emit(
            'new_message',
            self,
            original_stanza,
            date, receive_date, delay_from, delay_message, incomming,
            connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
            subject, plain, xhtml
            )

        return
