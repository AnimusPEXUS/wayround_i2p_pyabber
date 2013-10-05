
import logging
import socket
import threading

import lxml.etree

import org.wayround.gsasl.gsasl

import org.wayround.utils.gtk

import org.wayround.xmpp.core
import org.wayround.xmpp.client
import org.wayround.xmpp.muc

import org.wayround.pyabber.mainwindow
import org.wayround.pyabber.single_message_window
import org.wayround.pyabber.muc

from gi.repository import Gtk

class MainController:

    def __init__(self, main_window):

        self.main_window = main_window
        self.clear(init=True)

    def clear(self, init=False):

        self.client = None
        self._driven = False

        self.profile_name = None
        self.profile_password = None
        self.profile_data = None
        self.preset_name = None
        self.preset_data = None

        self.jid = None
        self.connection_info = None
        self.auth_info = None
        self.sock = None

        self.statuses = []

        self.waiting_for_stream_features = False

        self.stream_featires_arrived = threading.Event()

        self.last_features = None

        self._simple_gsasl = None

        self.resource = 'default'
        self.bound_jid = None



    def input_data_consistency_check_is_ok(self):

        """
        Checks whatever user of GUI is legitimate to access chat controls
        """

        ret = True

        if not isinstance(
            self.main_window, org.wayround.pyabber.mainwindow.MainWindow
            ):
            ret = False
        else:

            if (not self.profile_name or
                not self.profile_data or
                not self.profile_password or
                not self.preset_name or
                not self.preset_data):

                ret = False

        return ret

    def start(
        self,
        profile_name,
        profile_password,
        profile_data,
        preset_name,
        preset_data
        ):

        """
        Start Connection
        """

        ret = 0

        self.profile_name = profile_name
        self.profile_password = profile_password
        self.profile_data = profile_data
        self.preset_name = preset_name
        self.preset_data = preset_data

        if not self.input_data_consistency_check_is_ok():
            ret = 1
        else:

            self.waiting_for_stream_features = True

            self.jid = org.wayround.xmpp.core.JID(
                user=self.preset_data['username'],
                domain=self.preset_data['server']
                )

            self.main_window.roster_widget.set_self(self.jid.bare())

            self.connection_info = self.jid.make_connection_info()

            self.auth_info = self.jid.make_authentication()

            self.auth_info.password = self.preset_data['password']

            self.sock = socket.create_connection(
                (
                 self.connection_info.host,
                 self.connection_info.port
                 )
                )

            self.sock.settimeout(0)

            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            logging.debug(
                "Socket Options: {}".format(
                    self.sock.getsockopt(
                        socket.SOL_SOCKET,
                        socket.SO_KEEPALIVE
                        )
                    )
                )

            logging.debug("creating client")

            self.client = org.wayround.xmpp.client.XMPPC2SClient(
                self.sock
                )

            self.roster = org.wayround.xmpp.client.Roster(
                self.client,
                self.jid
                )

            self.presence = org.wayround.xmpp.client.Presence(
                self.client,
                self.jid
                )

            self.message = org.wayround.xmpp.client.Message(
                self.client,
                self.jid
                )

            self.muc = org.wayround.xmpp.muc.Client(
                self.client,
                self.jid
                )

            logging.debug("client created")

            self.client.sock_streamer.connect_signal(
                ['start', 'stop', 'error'],
                self._on_connection_event
                )

            logging.debug("streamer connected")

            self.client.io_machine.connect_signal(
                ['in_start', 'in_stop', 'in_error',
                 'out_start', 'out_stop', 'out_error'],
                self._on_stream_io_event
                )

            logging.debug("io connected")

            self.client.io_machine.connect_signal(
                'in_element_readed',
                self._on_stream_object
                )

            logging.debug("in_element_readed connected")

            self.client.start()
            logging.debug("client started")

            self.client.wait('working')
            logging.debug("working")


            auto = self.preset_data['stream_features_handling'] == 'auto'

            if auto:
                self.stream_featires_arrived.wait()
                self.waiting_for_stream_features = False

                ret = 0
                res = None

                if self.preset_data['STARTTLS'] and ret == 0:
                    print("Starting TLS")

                    res = org.wayround.xmpp.client.drive_starttls(
                        self.client,
                        self.last_features,
                        self.jid.bare(),
                        self.connection_info.host,
                        self._auto_starttls_controller
                        )

                    if not org.wayround.xmpp.core.is_features_element(res):
                        print("Can't establish TLS encryption")
                        ret = 2
                    else:
                        print("Encryption established")

                if self.preset_data['register'] and ret == 0:
                    # TODO: registration need to be done
                    pass

                if self.preset_data['login'] and ret == 0:
                    print("Logging in")

                    if not self._simple_gsasl:
                        self._simple_gsasl = org.wayround.gsasl.gsasl.GSASLSimple(
                            mechanism='DIGEST-MD5',
                            callback=self._gsasl_cb
                            )

                    res = org.wayround.xmpp.client.drive_sasl(
                        self.client,
                        self.last_features,
                        self.jid.bare(),
                        self.connection_info.host,
                        self._auto_auth_controller
                        )

                    self._simple_gsasl = None

                    if not org.wayround.xmpp.core.is_features_element(res):
                        print("Can't authenticate: {}".format(res))
                        ret = 3
                    else:
                        print("Authenticated")

                if self.preset_data['bind'] and ret == 0:
                    res = org.wayround.xmpp.client.bind(
                        self.client,
                        self.resource
                        )
                    if not isinstance(res, str):
                        print("bind error {}".format(res.get_error()))
                        ret = 4
                    else:
                        self.jid.update(org.wayround.xmpp.core.jid_from_str(res))
                        print("Bound jid is: {}".format(self.jid.full()))
                        self.main_window.roster_widget.set_contact(
                            bare_jid=self.jid.bare()
                            )

                if self.preset_data['session'] and ret == 0:

                    print("Starting session")

                    res = org.wayround.xmpp.client.session(
                        self.client,
                        self.jid.domain
                        )

                    if (not org.wayround.xmpp.core.is_stanza(res)
                        or res.is_error()):
                        print("Session establishing error")
                        ret = 5
                    else:
                        print("Session established")

                if ret == 0:
                    self.roster.connect_signal(['push'], self._on_roster_push)

                    self.presence.connect_signal(['presence'],
                                                 self._on_presence
                                                 )

                    self.message.connect_signal(['message'],
                                                 self._on_message
                                                 )



            self.waiting_for_stream_features = False

        return ret


    def _inbound_stanzas(self, obj):

        if obj.tag == 'message' and obj.typ == 'chat':

            cmd_line = org.wayround.utils.shlex.split(
                obj.body.find('{jabber:client}body').text.splitlines()[0]
                )

            if len(cmd_line) == 0:
                pass
            else:

                messages = []

#                self.stanza_processor.send(
#                    org.wayround.xmpp.core.Stanza(
#                        tag='message',
#                        typ='chat',
#                        jid_from=self.jid.full(),
#                        jid_to='animus@wayround.org',
#                        body='<body>TaskTracker bot is now online</body><subject>WOW!</subject>'
#                        )
#                    )

                ret_stanza = org.wayround.xmpp.core.Stanza(
                    jid_from=self.jid.bare(),
                    jid_to=obj.jid_from,
                    tag='message',
                    typ='chat',
                    body=[
                        org.wayround.xmpp.stanza_elements.Body(
                            text=''
                            )
                        ]
                    )

                asker_jid = org.wayround.xmpp.core.jid_from_string(
                    obj.jid_from
                    ).bare()

                res = org.wayround.utils.program.command_processor(
                    command_name=None,
                    commands=self._commands,
                    opts_and_args_list=cmd_line,
                    additional_data={
                        'asker_jid':asker_jid,
                        'stanza':obj,
                        'messages':messages,
                        'ret_stanza':ret_stanza
                        }
                    )

                messages_text = ''

                for i in messages:

                    typ = i['type']
                    text = i['text']

                    messages_text += '[{typ}]: {text}\n'.format(
                        typ=typ,
                        text=text
                        )

                for i in ret_stanza.body:

                    if isinstance(i, org.wayround.xmpp.stanza_elements.Body):

                        i.text = '\n{}\n{}\n'.format(
                            messages_text,
                            i.text
                            )

                        i.text += '{}\n'.format(res['message'])

                        i.text += 'Exit Code: {}\n'.format(
                            res['code']
                            )
                        break

                self.client.stanza_processor.send(ret_stanza)

    def _on_connection_event(self, event, streamer, sock):

        if not self._driven:

            logging.debug("_on_connection_event `{}', `{}'".format(event, sock))

            if event == 'start':
                print("Connection started")

                self.connection = True

                self.client.wait('working')

                logging.debug("Ended waiting for connection. Opening output stream")


                self.client.io_machine.send(
                    org.wayround.xmpp.core.start_stream_tpl(
                        jid_from=self.jid.bare(),
                        jid_to=self.connection_info.host
                        )
                    )

                logging.debug("Stream opening tag was started")

            elif event == 'stop':
                print("Connection stopped")
                self.connection = False
                self.stop()

            elif event == 'error':
                print("Connection error")
                self.connection = False
                self.stop()


    def _on_stream_io_event(self, event, io_machine, attrs=None):

        if not self._driven:

            logging.debug("Stream io event `{}' : `{}'".format(event, attrs))

            if event == 'in_start':
                self._stream_in = True

            elif event == 'in_stop':
                self._stream_in = False
                self.stop()

            elif event == 'in_error':
                self._stream_in = False
                self.stop()

            elif event == 'out_start':
                self._stream_out = True

            elif event == 'out_stop':
                self._stream_out = False
                self.stop()

            elif event == 'out_error':
                self._stream_out = False
                self.stop()


    def _on_stream_object(self, event, io_machine, obj):

        logging.debug(
            "_on_stream_object (first 255 bytes):`{}'".format(
                repr(lxml.etree.tostring(obj)[:255])
                )
            )

        if org.wayround.xmpp.core.is_features_element(obj):
            self._handle_stream_features(obj)


    def _handle_stream_features(self, obj):

        ret = False

        if self.waiting_for_stream_features:
            self.last_features = obj
            self.stream_featires_arrived.set()

        return ret



    def _auto_starttls_controller(self, status, data):

        print("_auto_starttls_controller {}, {}".format(status, data))

        ret = None

        raise ValueError("status `{}' not supported".format(status))

        return ret


    def _manual_starttls_controller(self):
        pass


    def _auto_auth_controller(self, status, data):

        ret = ''

        print("_auto_auth_controller {}, {}".format(status, data))

        if status == 'mechanism_name':
            ret = 'DIGEST-MD5'

        elif status == 'bare_jid_from':
            ret = self.jid.bare()

        elif status == 'bare_jid_to':
#            TODO: fix self.connection_info.host
            ret = self.connection_info.host

        elif status == 'sock_streamer':
            ret = self.client.sock_streamer

        elif status == 'io_machine':
            ret = self.client.io_machine

        elif status == 'challenge':
            res = self._simple_gsasl.step64(data['text'])

            if res[0] == org.wayround.gsasl.gsasl.GSASL_OK:
                pass
            elif res[0] == org.wayround.gsasl.gsasl.GSASL_NEEDS_MORE:
                pass
            else:
                # TODO: this is need to be hidden
                raise Exception(
                    "step64 returned error: {}".format(
                        org.wayround.gsasl.gsasl.strerror_name(res[0])
                        )
                    )

            ret = str(res[1], 'utf-8')

        elif status == 'success':
            pass

        else:
            raise ValueError("status `{}' not supported".format(status))

        return ret

    def _manual_auth_controller(self):
        pass

    def _gsasl_cb(self, context, session, prop):

        # TODO: maybe all this method need to be separated and standardized

        ret = org.wayround.gsasl.gsasl.GSASL_OK

        logging.debug(
            "SASL client requested for: {} ({}) {}".format(
                org.wayround.gsasl.gsasl.strproperty_name(prop),
                prop,
                org.wayround.gsasl.gsasl.strproperty(prop)
                )
            )

        if prop == org.wayround.gsasl.gsasl.GSASL_QOP:

            server_allowed_qops = str(
                session.property_get(
                    org.wayround.gsasl.gsasl.GSASL_QOPS
                    ),
                'utf-8'
                ).split(',')

            value = ''
            if not 'qop-auth' in server_allowed_qops:
                value = ''
            else:
                value = 'qop-auth'

            session.property_set(
                org.wayround.gsasl.gsasl.GSASL_QOP,
                bytes(value, 'utf-8')
                )

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHID:

            value = None
            if self.auth_info.authid:
                value = bytes(self.auth_info.authid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_SERVICE:

            value = None
            if self.auth_info.service:
                value = bytes(self.auth_info.service, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_HOSTNAME:

            value = None
            if self.auth_info.hostname:
                value = bytes(self.auth_info.hostname, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_REALM:

            value = None
            if self.auth_info.realm:
                value = bytes(self.auth_info.realm, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_AUTHZID:

            value = None
            if self.auth_info.authzid:
                value = bytes(self.auth_info.authzid, 'utf-8')

            session.property_set(prop, value)

        elif prop == org.wayround.gsasl.gsasl.GSASL_PASSWORD:

            value = None
            if self.auth_info.password:
                value = bytes(self.auth_info.password, 'utf-8')

            session.property_set(prop, value)

        else:
            logging.error("Requested SASL property not available")
            ret = 1

        return ret

    def _on_roster_push(self, event, roster_obj, stanza_data):

        if event != 'push':
            pass
        else:

            jid = list(stanza_data.keys())[0]
            data = stanza_data[jid]

            not_in_roster = data['subscription'] == 'remove'

            self.main_window.roster_widget.set_contact(
                name_or_title=data['name'],
                bare_jid=jid,
                groups=data['groups'],
                approved=data['approved'],
                ask=data['ask'],
                subscription=data['subscription'],
                not_in_roster=not_in_roster
                )

        return

    def _on_presence(self, event, presence_obj, jid_from, jid_to, stanza):

        if event == 'presence':

            if not stanza.typ in [
                'unsubscribe', 'subscribed', 'unsubscribed'
                ]:

                f_jid = None

                if jid_from:
                    f_jid = org.wayround.xmpp.core.jid_from_str(jid_from)
                else:
                    f_jid = self.jid.copy()
                    f_jid.user = None

                show = None
                status = None

                show_elm = stanza.body.find('{jabber:client}show')
                if show_elm != None:
                    show = show_elm.text
                else:
                    show = 'available'
                    if stanza.typ == 'unavailable':
                        show = 'unavailable'

                status_elm = stanza.body.find('{jabber:client}status')
                if status_elm != None:
                    status = status_elm.text
                else:
                    status = ''

                not_in_roster = None
                if stanza.typ == 'remove':
                    not_in_roster = True

                if not f_jid.bare() in self.main_window.roster_widget.get_data():
                    not_in_roster = True

                if f_jid.is_full():
                    self.main_window.roster_widget.set_contact_resource(
                        bare_jid=f_jid.bare(),
                        resource=f_jid.resource,
                        available=stanza.typ != 'unavailable',
                        show=show,
                        status=status,
                        not_in_roster=not_in_roster
                        )
                elif f_jid.is_bare():
                    self.main_window.roster_widget.set_contact(
                        bare_jid=f_jid.bare(),
                        available=stanza.typ != 'unavailable',
                        show=show,
                        status=status,
                        not_in_roster=not_in_roster
                        )
                else:
                    logging.error("Don't know what to do")

            else:
                logging.warning(
                    "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stanza.typ is {}".format(
                        stanza.typ
                        )
                    )

    def _on_message(self, event, message_obj, stanza):

        if event == 'message':

            if stanza.typ in [None, 'normal']:

                subject = None
                thread = None
                body = None

                subject_el = stanza.body.find('{jabber:client}subject')
                # TODO: fix for multiple subjects
                if subject_el != None:
                    subject = subject_el.text

                thread_el = stanza.body.find('{jabber:client}thread')
                # TODO: fix for multiple threads
                if thread_el != None:
                    thread = thread_el.text

                body_el = stanza.body.find('{jabber:client}body')
                # TODO: fix for multiple bodies
                if body_el != None:
                    body = body_el.text

                org.wayround.pyabber.single_message_window.single_message(
                    self, mode='view',
                    to_jid=stanza.jid_to,
                    from_jid=stanza.jid_from,
                    subject=subject,
                    thread=thread,
                    body=body
                    )

            else:
                self.main_window.chat_pager.feed_stanza(stanza)


def stanza_error_message(parent, stanza, message=None):

    if not isinstance(stanza, org.wayround.xmpp.core.Stanza):
        raise TypeError("`stanza' must be org.wayround.xmpp.core.Stanza")

    if stanza.is_error():

        message2 = ''
        if message:
            message2 = '{}\n\n'.format(message)

        d = org.wayround.utils.gtk.MessageDialog(
            parent,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "{}{}".format(
                message2,
                org.wayround.xmpp.core.stanza_error_to_text(stanza.get_error())
                )
            )
        d.run()
        d.destroy()

    return
