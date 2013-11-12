
import copy
import logging
import socket
import threading

import lxml.etree

from gi.repository import Gtk

import org.wayround.gsasl.gsasl
import org.wayround.utils.signal

import org.wayround.xmpp.client
import org.wayround.xmpp.core
import org.wayround.xmpp.muc
import org.wayround.xmpp.privacy

import org.wayround.pyabber.main
import org.wayround.pyabber.roster_window


class ConnectionStatusMenu:

    def __init__(self, client_connetion_controller):

        self._client_connetion_controller = client_connetion_controller

        m = Gtk.Menu()

        roster_mi = Gtk.MenuItem("Roster..")
        messages_mi = Gtk.MenuItem("Messages..")

        reconnect_mi = Gtk.MenuItem("(re)Connect")
        disconnect_mi = Gtk.MenuItem("Disconnect")

        destroy_mi = Gtk.MenuItem("Destroy")

        m.append(roster_mi)
        m.append(messages_mi)
        m.append(Gtk.SeparatorMenuItem())
        m.append(reconnect_mi)
        m.append(disconnect_mi)
        m.append(Gtk.SeparatorMenuItem())
        m.append(destroy_mi)

        roster_mi.connect('activate', self._on_roster_mi_activated)

        reconnect_mi.connect('activate', self._on_reconnect_mi_activated)
        disconnect_mi.connect('activate', self._on_disconnect_mi_activated)

        destroy_mi.connect('activate', self._on_destroy_mi_activated)

        m.show_all()

        self._connections_submenu_item = None

        self.widget = m

        return

    def destroy(self):
        self._connections_submenu_item.destroy()

    def set_connections_submenu_item(self, menuitem):
        self._connections_submenu_item = menuitem

    def _on_roster_mi_activated(self, mi):
        if self._client_connetion_controller.roster_window == None:
            self._client_connetion_controller.roster_window = \
                org.wayround.pyabber.roster_window.RosterWindow(
                    client=self._client_connetion_controller.client,
                    own_jid=self._client_connetion_controller.jid
                    )
            self._client_connetion_controller.roster_window.run()
            self._client_connetion_controller.roster_window = None
        else:
            self._client_connetion_controller.roster_window.show()
        return

    def _on_reconnect_mi_activated(self, mi):
        self._client_connetion_controller.disconnect()
        self._client_connetion_controller.connect()

    def _on_disconnect_mi_activated(self, mi):
        self._client_connetion_controller.disconnect()

    def _on_destroy_mi_activated(self, mi):
        self._client_connetion_controller.destroy()


class ClientConnetionController:

    def __init__(self, main, profile, preset_name):

        """
        :param org.wayround.pyabber.main.ProfileSession profile:
        """

        if not isinstance(main, org.wayround.pyabber.main.Main):
            raise ValueError(
                "`main' must be org.wayround.pyabber.main.Main"
                )

        if not isinstance(profile, org.wayround.pyabber.main.ProfileSession):
            raise ValueError(
                "`profile' must be org.wayround.pyabber.main.ProfileSession"
                )

        if not isinstance(preset_name, str):
            raise ValueError("`preset_name' must be str")

        self.main = main
        self.profile = profile
        self.preset_name = preset_name
        self.preset_data = None

        for i in profile.data['connection_presets']:
            if i['name'] == preset_name:
                self.preset_data = copy.copy(i)
                break

        if self.preset_data == None:
            raise ValueError(
                "preset with name '{}' isn't found".format(preset_name)
                )

        logging.debug("adding conn status menu")

        self.menu = ConnectionStatusMenu(self)

        self.main.status_icon.menu.add_connection_menu(
            self.preset_name,
            self.menu
            )

        self.profile.connection_controllers.add(self)

        self.clear(init=True)

    def __del__(self):
        self._remove_self_from_list()

    def _remove_self_from_list(self):
        if self in self.profile.connection_controllers:
            self.profile.connection_controllers.remove(self)

    def clear(self, init=False):

        self._simple_gsasl = None
        self.auth_info = None
        self.client = None
        self.connection_info = None
        self.jid = None
        self.message = None
        self.muc = None
        self.presence = None
        self.privacy = None
        self.roster = None
        self.sock = None
        self.is_driven = False

        self.roster_window = None

        if init:
            self._disconnection_flag = threading.Event()
        else:
            self._disconnection_flag.clear()

    def destroy(self):
        self.menu.destroy()
        self.menu = None
        self.disconnect()
        self._remove_self_from_list()

    def connect(self):

        ret = 0

        self.clear()

        self.jid = org.wayround.xmpp.core.JID(
            user=self.preset_data['username'],
            domain=self.preset_data['server']
            )

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

        self.privacy = org.wayround.xmpp.privacy.PrivacyClient(
            self.client,
            self.jid
            )

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

#        self.client.io_machine.connect_signal(
#            'in_element_readed',
#            self._on_stream_object
#            )

        features_waiter = org.wayround.utils.signal.SignalWaiter(
            self.client,
            'features'
            )
        features_waiter.start()

        self.is_driven = True

        self.client.start()
        self.client.wait('working')

        auto = self.preset_data['stream_features_handling'] == 'auto'

        if auto:
            ret = 0
            res = None

            features = features_waiter.pop()
            features_waiter.stop()
            del(features_waiter)

            if features == None:
                logging.error("Timedout waiting for initial server features")
                ret = 1
            else:
                last_features = features['args'][1]

            if (not self._disconnection_flag.is_set()
                and self.preset_data['STARTTLS']
                and ret == 0):

                logging.debug("Starting TLS")

                res = org.wayround.xmpp.client.drive_starttls(
                    self.client,
                    last_features,
                    self.jid.bare(),
                    self.connection_info.host,
                    self._auto_starttls_controller
                    )

                if not org.wayround.xmpp.core.is_features_element(res):
                    logging.debug("Can't establish TLS encryption")
                    ret = 2
                else:
                    logging.debug("Encryption established")
                    last_features = res

            if (not self._disconnection_flag.is_set()
                and self.preset_data['register']
                and ret == 0):
                # TODO: registration need to be done
                pass

            if (not self._disconnection_flag.is_set()
                and self.preset_data['login']
                and ret == 0):

                logging.debug("Logging in")

                if not self._simple_gsasl:
                    self._simple_gsasl = (
                        org.wayround.gsasl.gsasl.GSASLSimple(
                            mechanism='DIGEST-MD5',
                            callback=self._gsasl_cb
                            )
                        )

                logging.debug(
                    "Passing following features to sasl driver:\n{}".format(
                        lxml.etree.tostring(last_features)
                        )
                    )

                res = org.wayround.xmpp.client.drive_sasl(
                    self.client,
                    last_features,
                    self.jid.bare(),
                    self.connection_info.host,
                    self._auto_auth_controller
                    )

                self._simple_gsasl = None

                if not org.wayround.xmpp.core.is_features_element(res):
                    logging.debug("Can't authenticate: {}".format(res))
                    ret = 3
                else:
                    logging.debug("Authenticated")
                    last_features = res

            if (not self._disconnection_flag.is_set()
                and self.preset_data['bind']
                and ret == 0):

                res = org.wayround.xmpp.client.bind(
                    self.client,
                    self.jid.resource
                    )
                if not isinstance(res, str):
                    logging.debug("bind error {}".format(res.gen_error()))
                    ret = 4
                else:
                    self.jid.update(
                        org.wayround.xmpp.core.JID.new_from_str(res)
                        )
                    logging.debug(
                        "Bound jid is: {}".format(self.jid.full())
                        )

            if (not self._disconnection_flag.is_set()
                and self.preset_data['session']
                and ret == 0):

                logging.debug("Starting session")

                res = org.wayround.xmpp.client.session(
                    self.client,
                    self.jid.domain
                    )

                if (not isinstance(res, org.wayround.xmpp.core.Stanza)
                    or res.is_error()):
                    logging.debug("Session establishing error")
                    ret = 5
                else:
                    logging.debug("Session established")

            if (not self._disconnection_flag.is_set()
                and ret == 0):
                self.roster.connect_signal(['push'], self._on_roster_push)

                self.presence.connect_signal(['presence'],
                                             self._on_presence
                                             )

                self.message.connect_signal(['message'],
                                             self._on_message
                                             )

            if ret != 0:
                threading.Thread(
                    target=self.disconnect,
                    name="Disconnecting by connection error"
                    ).start()

        self.is_driven = False

        return

    def disconnect(self):
        self._disconnection_flag.set()
        self.clear()

    def _on_connection_event(self, event, streamer, sock):

        if self.is_driven:

            logging.debug(
                "_on_connection_event `{}', `{}'".format(event, sock)
                )

            if event == 'start':
                logging.debug("Connection started")

                self.client.wait('working')

                logging.debug(
                    "Ended waiting for connection. Opening output stream"
                    )

                self.client.io_machine.send(
                    org.wayround.xmpp.core.start_stream_tpl(
                        from_jid=self.jid.bare(),
                        to_jid=self.connection_info.host
                        )
                    )

                logging.debug("Stream opening tag was started")

            elif event == 'stop':
                logging.debug("Connection stopped")
                self.disconnect()

            elif event == 'error':
                logging.debug("Connection error")
                self.disconnect()

        return

    def _on_stream_io_event(self, event, io_machine, attrs=None):

        if self.is_driven:

            logging.debug("Stream io event `{}' : `{}'".format(event, attrs))

            if event == 'in_start':
                pass

            elif event == 'in_stop':
                self.disconnect()

            elif event == 'in_error':
                self.disconnect()

            elif event == 'out_start':
                pass

            elif event == 'out_stop':
                self.disconnect()

            elif event == 'out_error':
                self.disconnect()

        return

    def _auto_starttls_controller(self, status, data):

        logging.debug("_auto_starttls_controller {}, {}".format(status, data))

        ret = None

        raise ValueError("status `{}' not supported".format(status))

        return ret

    def _manual_starttls_controller(self):
        pass

    def _auto_auth_controller(self, status, data):

        ret = ''

        logging.debug("_auto_auth_controller {}, {}".format(status, data))

        if status == 'mechanism_name':
            ret = 'DIGEST-MD5'

        elif status == 'bare_from_jid':
            ret = self.jid.bare()

        elif status == 'bare_to_jid':
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
        pass

    def _on_presence(self, event, presence_obj, from_jid, to_jid, stanza):
        pass

    def _on_message(self, event, message_obj, stanza):
        pass
