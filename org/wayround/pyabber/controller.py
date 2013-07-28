
import logging
import socket
import threading

import lxml.etree

import org.wayround.xmpp.core
import org.wayround.xmpp.client

import org.wayround.gsasl.gsasl

import org.wayround.pyabber.mainwindow

class MainController:

    def __init__(self):

        self.main_window = None

        self.clear(init=True)

    def clear(self, init=False):

        self.client = None
        self._driven = False

        self.jid = None
        self.connection_info = None
        self.auth_info = None
        self.sock = None

        self.stanza_processor = None

        self.statuses = []

        self.waiting_for_stream_features = False

        self.stream_featires_arrived = threading.Event()

        self.last_features = None

        self._simple_gsasl = None

        self.resource = 'default'
        self.bound_jid = None



    def main_window_consistency_check_is_ok(self):

        """
        Checks whatever user of GUI is legitimate to access chat controls
        """

        ret = True

        if not isinstance(
            self.main_window, org.wayround.pyabber.mainwindow.MainWindow
            ):
            ret = False
        else:

            if (not self.main_window.profile_name or
                not self.main_window.profile_data or
                not self.main_window.profile_password or
                not self.main_window.preset_name or
                not self.main_window.preset_data):

                ret = False

        return ret

    def start(self, main_window):

        """
        Start Connection
        """

        ret = False

        self.main_window = main_window

        if not self.main_window_consistency_check_is_ok():
            ret = False
        else:

            self.waiting_for_stream_features = True

            self.jid = org.wayround.xmpp.core.JID(
                user=self.main_window.preset_data['username'],
                domain=self.main_window.preset_data['server']
                )

            self.connection_info = self.jid.make_connection_info()

            self.auth_info = self.jid.make_authentication()

            self.auth_info.password = self.main_window.preset_data['password']

            self.sock = socket.create_connection(
                (
                 self.connection_info.host,
                 self.connection_info.port
                 )
                )


            logging.debug("Starting socket watcher")

            self.client = org.wayround.xmpp.client.XMPPC2SClient(
                self.sock
                )

            self._reset_hubs()


            self.client.start()

            self.client.wait('working')

            self.stanza_processor = org.wayround.xmpp.core.StanzaProcessor()
            self.stanza_processor.connect_input_object_stream_hub(
                self.client.input_stream_objects_hub
                )
            self.stanza_processor.connect_io_machine(self.client.io_machine)

            auto = self.main_window.preset_data['stream_features_handling'] == 'auto'

            if auto:
                self.stream_featires_arrived.wait()
                self.waiting_for_stream_features = False

                drv = org.wayround.xmpp.client.STARTTLSClientDriver(
                    self._auto_starttls_controller
                    )

                res = drv.drive(self.last_features)

                if not org.wayround.xmpp.core.is_features_element(res):
                    print("Can't establish TLS encryption")
                else:
                    print("Encryption established")
                    print("Logging")

                    if not self._simple_gsasl:
                        self._simple_gsasl = org.wayround.gsasl.gsasl.GSASLSimple(
                            mechanism='DIGEST-MD5',
                            callback=self._gsasl_cb
                            )

                    drv = org.wayround.xmpp.client.SASLClientDriver(
                        self._auto_auth_controller
                        )

                    res = drv.drive(res)

                    self._simple_gsasl = None

                    if not org.wayround.xmpp.core.is_features_element(res):
                        print("Can't authenticate: {}".format(res))
                    else:
                        print("Authenticated")

                        res = org.wayround.xmpp.client.bind(
                            self.stanza_processor,
                            self.resource
                            )

                        if not isinstance(res, str):

                            print("bind error {}".format(res.determine_error()))
                        else:

                            self.bound_jid = org.wayround.xmpp.core.jid_from_str(res)

                            print("Bound jid is: {}".format(self.bound_jid.full()))

                            print("Starting session")

                            res = org.wayround.xmpp.client.session(
                                self.stanza_processor,
                                self.bound_jid.domain
                                )

                            if (not org.wayround.xmpp.core.is_stanza(res)
                                or res.is_error()):
                                print("Session establishing error")
                            else:
                                print("Session established")


            self.waiting_for_stream_features = False



        return ret

    def _reset_hubs(self):

        self.client.connection_events_hub.clear()
        self.client.input_stream_events_hub.clear()
        self.client.input_stream_objects_hub.clear()
        self.client.output_stream_events_hub.clear()

        self.client.connection_events_hub.set_waiter(
            'main', self._on_connection_event,
            )

        self.client.input_stream_events_hub.set_waiter(
            'main', self._on_stream_in_event,
            )

        self.client.input_stream_objects_hub.set_waiter(
            'main', self._on_stream_object,
            )

        self.client.output_stream_events_hub.set_waiter(
            'main', self._on_stream_out_event,
            )


    def _inbound_stanzas(self, obj):

        if obj.kind == 'message' and obj.typ == 'chat':

            cmd_line = org.wayround.utils.shlex.split(
                obj.body.find('{jabber:client}body').text.splitlines()[0]
                )

            if len(cmd_line) == 0:
                pass
            else:

                messages = []

#                self.stanza_processor.send(
#                    org.wayround.xmpp.core.Stanza(
#                        kind='message',
#                        typ='chat',
#                        jid_from=self.jid.full(),
#                        jid_to='animus@wayround.org',
#                        body='<body>TaskTracker bot is now online</body><subject>WOW!</subject>'
#                        )
#                    )

                ret_stanza = org.wayround.xmpp.core.Stanza(
                    jid_from=self.jid.bare(),
                    jid_to=obj.jid_from,
                    kind='message',
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

                self.stanza_processor.send(ret_stanza)

    def _on_connection_event(self, event, sock):

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


    def _on_stream_in_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream in event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_in = True

            elif event == 'stop':
                self._stream_in = False
                self.stop()

            elif event == 'error':
                self._stream_in = False
                self.stop()

    def _on_stream_out_event(self, event, attrs=None):

        if not self._driven:

            logging.debug("Stream out event `{}' : `{}'".format(event, attrs))

            if event == 'start':

                self._stream_out = True

            elif event == 'stop':
                self._stream_out = False
                self.stop()

            elif event == 'error':
                self._stream_out = False
                self.stop()

    def _on_stream_object(self, obj):

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



    def _auto_starttls_controller(self, driver, status, data):

        print("_auto_starttls_controller {}, {}, {}".format(driver, status, data))

        ret = None

        if status == 'bare_jid_from':
            ret = self.jid.bare()

        elif status == 'bare_jid_to':
            # TODO: fix self.connection_info.host
            ret = self.connection_info.host

        elif status == 'sock_streamer':
            ret = self.client.sock_streamer

        elif status == 'io_machine':
            ret = self.client.io_machine

        elif status == 'connection_events_hub':
            ret = self.client.connection_events_hub

        elif status == 'input_stream_events_hub':
            ret = self.client.input_stream_events_hub

        elif status == 'input_stream_objects_hub':
            ret = self.client.input_stream_objects_hub

        elif status == 'output_stream_events_hub':
            ret = self.client.output_stream_events_hub
#        elif status=='':
#            ret = self.client.sock_streamer
#        elif status=='':
#            ret = self.client.sock_streamer
#        elif status=='':
#            ret = self.client.sock_streamer


        else:
            raise ValueError("status `{}' not supported".format(status))

        return ret


    def _manual_starttls_controller(self):
        pass


    def _auto_auth_controller(self, driver, status, data):

        ret = ''

        print("_auto_auth_controller {}, {}, {}".format(driver, status, data))

        if status == 'mechanism_name':
            ret = 'DIGEST-MD5'

        elif status == 'bare_jid_from':
            ret = self.jid.bare()

        elif status == 'bare_jid_to':
            # TODO: fix self.connection_info.host
            ret = self.connection_info.host

        elif status == 'sock_streamer':
            ret = self.client.sock_streamer

        elif status == 'io_machine':
            ret = self.client.io_machine

        elif status == 'connection_events_hub':
            ret = self.client.connection_events_hub

        elif status == 'input_stream_events_hub':
            ret = self.client.input_stream_events_hub

        elif status == 'input_stream_objects_hub':
            ret = self.client.input_stream_objects_hub

        elif status == 'output_stream_events_hub':
            ret = self.client.output_stream_events_hub

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

