
import logging
import socket
import threading

from gi.repository import Gtk, GLib

import lxml.etree
import org.wayround.gsasl.gsasl
import org.wayround.pyabber.adhoc
import org.wayround.pyabber.bob
import org.wayround.pyabber.chat_window
import org.wayround.pyabber.contact_editor
import org.wayround.pyabber.disco
import org.wayround.pyabber.main
import org.wayround.pyabber.message_edit_widget
import org.wayround.pyabber.message_relay
import org.wayround.pyabber.muc
import org.wayround.pyabber.presence_control_window
import org.wayround.pyabber.registration
import org.wayround.pyabber.roster_storage
import org.wayround.pyabber.roster_window
import org.wayround.pyabber.single_message_window
import org.wayround.pyabber.subject_widget
import org.wayround.pyabber.thread_widget
import org.wayround.pyabber.xcard
import org.wayround.utils.gtk
import org.wayround.utils.threading
import org.wayround.xmpp.client
import org.wayround.xmpp.core
import org.wayround.xmpp.disco
import org.wayround.xmpp.muc
import org.wayround.xmpp.privacy


SUBWINDOWS = [
    # 1. registered window name;
    # 2. single?;
    # 3. threaded?.
    ('add_mode_language_window', False, False),
    ('adhoc_response_window', False, True),
    ('adhoc_window', False, True),
    ('chat_window', True, True),
    ('contact_editor_window', False, True),
    ('disco_window', False, True),
    ('muc_config_window', False, True),
    ('muc_destruction_dialog', False, True),
    ('muc_identity_editor_window', False, True),
    ('muc_jid_entry_dialog', False, False),
    ('muc_join_dialog', False, True),
    ('muc_mini_identity_editor_window', False, True),
    ('muc_voice_request_window', False, True),
    ('presence_control_window', False, True),
    ('registration_window', False, False),
    ('registration_window_threaded', False, True),
    ('roster_window', True, True),
    ('single_message_window', False, True),
    ('subject_edit_window', False, True),
    ('subject_edit_window_modal', False, False),
    ('thread_edit_window', False, False),
    ('xcard_window', False, True)
    ]


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
        messages_mi.connect('activate', self._on_messages_mi_activated)

        reconnect_mi.connect('activate', self._on_reconnect_mi_activated)
        disconnect_mi.connect('activate', self._on_disconnect_mi_activated)

        destroy_mi.connect('activate', self._on_destroy_mi_activated)

        m.show_all()

        self._connections_submenu_item = None

        self._widget = m

        return

    def get_widget(self):
        return self._widget

    def destroy(self):
        self._connections_submenu_item.destroy()

    def set_connections_submenu_item(self, menuitem):
        self._connections_submenu_item = menuitem

    def _on_roster_mi_activated(self, mi):
        self._client_connetion_controller.show_roster_window()

    def _on_messages_mi_activated(self, mi):
        self._client_connetion_controller.show_chat_window()

    def _on_reconnect_mi_activated(self, mi):
        self._client_connetion_controller.disconnect()
        #threading.Thread(
        #    target=lambda: GLib.idle_add(
        #        self._client_connetion_controller.connect
        #        ),
        #    name="Connection Thread {}".format(
        #        self._client_connetion_controller
        #        )
        #    ).start()

        threading.Thread(
            target=self._client_connetion_controller.connect,
            name="Connection Thread {}".format(
                self._client_connetion_controller
                )
            ).start()

    def _on_disconnect_mi_activated(self, mi):
        self._client_connetion_controller.disconnect()

    def _on_destroy_mi_activated(self, mi):
        self._client_connetion_controller.destroy()


class ClientConnectionController:

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
        self.storage = profile.data

        for i in profile.data.get_connection_presets_list():
            if i == preset_name:
                self.preset_data = \
                    profile.data.get_connection_preset_by_name(i)
                break

        if self.preset_data == None:
            raise ValueError(
                "preset with name '{}' isn't found".format(preset_name)
                )

        logging.debug("adding conn status menu")

        self._menu = ConnectionStatusMenu(self)

        self.main.status_icon.menu.add_connection_menu(
            self.preset_name,
            self._menu
            )

        self.profile.connection_controllers.add(self)

        self._rel_win_ctl = org.wayround.utils.gtk.RelatedWindowCollector()

        for i in SUBWINDOWS:
            exec(
                """\
self._rel_win_ctl.set_constructor_cb(
    '{i}',
    self._{i}_constructor,
    {s}
    )
""".format(i=i[0], s=i[1]))

        self.self_disco_info = org.wayround.xmpp.disco.IQDisco(mode='info')

        self.self_disco_info.set_identity(
            [
             org.wayround.xmpp.disco.IQDiscoIdentity(
                'client', 'pc', 'pyabber'
                )
             ]
            )

#        self.self_disco_info.set_feature(
#            [
#             'http://jabber.org/protocol/xhtml-im'
#             ]
#            )

        self.clear(init=True)

        return

    def __del__(self):
        self._remove_self_from_list()

    def _remove_self_from_list(self):
        if self in self.profile.connection_controllers:
            self.profile.connection_controllers.remove(self)

    def _roster_window_constructor(self):
        return org.wayround.pyabber.roster_window.RosterWindow(self)

    def _disco_window_constructor(self):
        return org.wayround.pyabber.disco.Disco(self)

    def _add_mode_language_window_constructor(self):
        return org.wayround.pyabber.message_edit_widget.AddModeLang()

    def _adhoc_window_constructor(self):
        return org.wayround.pyabber.adhoc.AD_HOC_Window(self)

    def _adhoc_response_window_constructor(self):
        return org.wayround.pyabber.adhoc.AD_HOC_Response_Window(self)

    def _contact_editor_window_constructor(self):
        return org.wayround.pyabber.contact_editor.ContactEditor(self)

    def _presence_control_window_constructor(self):
        return \
            org.wayround.pyabber.presence_control_window.PresenceControlWindow(
                self
                )

    def _muc_jid_entry_dialog_constructor(self):
        return org.wayround.pyabber.muc.MUCJIDEntryDialog()

    def _muc_config_window_constructor(self):
        return org.wayround.pyabber.muc.MUCConfigWindow(self)

    def _muc_destruction_dialog_constructor(self):
        return org.wayround.pyabber.muc.MUCDestructionDialog(self)

    def _muc_identity_editor_window_constructor(self):
        return org.wayround.pyabber.muc.MUCIdentityEditorWindow(self)

    def _muc_join_dialog_constructor(self):
        return org.wayround.pyabber.muc.MUCJoinDialog(self)

    def _chat_window_constructor(self):
        return org.wayround.pyabber.chat_window.ChatWindow(self)

    def _single_message_window_constructor(self):
        return org.wayround.pyabber.single_message_window.SingleMessageWindow(
            self
            )

    def _registration_window_constructor(self):
        return org.wayround.pyabber.registration.RegistrationWindow(self)

    def _registration_window_threaded_constructor(self):
        return org.wayround.pyabber.registration.RegistrationWindow(self)

    def _subject_edit_window_constructor(self):
        return org.wayround.pyabber.subject_widget.SubjectEditor(self)

    def _subject_edit_window_modal_constructor(self):
        return org.wayround.pyabber.subject_widget.SubjectEditor(self)

    def _thread_edit_window_constructor(self):
        return org.wayround.pyabber.thread_widget.ThreadEditor(self)

    def _muc_voice_request_window_constructor(self):
        return org.wayround.pyabber.muc.MUCVoiceRequestWindow(self)

    def _muc_mini_identity_editor_window_constructor(self):
        return org.wayround.pyabber.muc.MUCMiniIdentityEditorWindow(self)

    def _xcard_window_constructor(self):
        return org.wayround.pyabber.xcard.XCardWindow(self)

    for i in SUBWINDOWS:
        exec(
            """\
def destroy_{i}(self):
    return self._rel_win_ctl.destroy_window('{i}')

def get_{i}(self):
    ret = self._rel_win_ctl.get('{i}')
    if ret == None:
        self.show_{i}()
    ret = self._rel_win_ctl.get('{i}')
    return ret

def show_{i}(self, *args, **kwargs):
    ret = None
    if {threaded}:
        self._rel_win_ctl.show_threaded('{i}', *args, **kwargs)
    else:
        ret = self._rel_win_ctl.show('{i}', *args, **kwargs)
    return ret

""".format(i=i[0], threaded=i[2]))

    def clear(self, init=False):

        self._simple_gsasl = None
        self.auth_info = None
        self.client = None
        self.connection_info = None
        self.is_driven = False
        self.jid = None
        self.message_client = None
        self.muc_client = None
        self.presence_client = None
        self.privacy_client = None
        self.roster_client = None
        self.roster_storage = None
        self.sock = None

        if init:
            self._disconnection_flag = threading.Event()
        else:
            self._disconnection_flag.clear()

        self._incomming_message_lock = threading.RLock()

    def destroy(self):
        self.destroy_chat_window()
        self.disconnect()
        self._rel_win_ctl.destroy()
        self._menu.destroy()
        self._menu = None
        self._remove_self_from_list()

    def connect(self):

        ret = 0

        self.disconnect()

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

        # make non-blocking socket
        self.sock.settimeout(0)

        self.message_relay = org.wayround.pyabber.message_relay.MessageRelay(
            self
            )

        self.client = org.wayround.xmpp.client.XMPPC2SClient(
            self.sock
            )

        self.roster_client = org.wayround.xmpp.client.Roster(
            self.client,
            self.jid
            )

        self.presence_client = org.wayround.xmpp.client.Presence(
            self.client,
            self.jid
            )

        self.message_client = org.wayround.xmpp.client.Message(
            self.client,
            self.jid
            )

        self.muc_client = org.wayround.xmpp.muc.Client(
            self.client,
            self.jid
            )

        self.privacy_client = org.wayround.xmpp.privacy.PrivacyClient(
            self.client,
            self.jid
            )

        self.bob_mgr = org.wayround.pyabber.bob.BOBMgr(self)

#        self.muc_pool = org.wayround.pyabber.muc.MUCControllerPool(self)

        self.client.sock_streamer.signal.connect(
            ['start', 'stop', 'error'],
            self._on_connection_event
            )

        logging.debug("streamer connected")

        self.client.io_machine.signal.connect(
            ['in_start', 'in_stop', 'in_error',
             'out_start', 'out_stop', 'out_error'],
            self._on_stream_io_event
            )

        features_waiter = org.wayround.utils.threading.SignalWaiter(
            self.client.signal,
            'features'
            )
        features_waiter.start()

        self.is_driven = True

        self.client.start(
            from_jid=self.jid.bare(),
            to_jid=self.connection_info.host
            )
        self.client.wait('working')

        auto = self.preset_data['stream_features_handling'] == 'auto'

        if auto:
            ret = 0
            res = None

            if ret == 0:

                features = features_waiter.pop()
                features_waiter.stop()

                if features == None:
                    logging.error(
                        "Timedout waiting for initial server features"
                        )
                    ret = 1
                else:
                    last_features = features['args'][1]

            if (not self._disconnection_flag.is_set()
                and self.preset_data['starttls']
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

                if (
                    last_features.find(
                        '{http://jabber.org/features/iq-register}register'
                        )
                    != None
                    ):

                    res = self.show_registration_window(
                        get_reg_form=True,
                        pred_username=self.preset_data['username'],
                        pred_password=self.preset_data['password']
                        )

                    if res != 'REGISTERED':
                        ret = 6

                else:
                    ret = 10

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

                self.roster_storage = \
                    org.wayround.pyabber.roster_storage.RosterStorage(
                        self.jid,
                        self.roster_client,
                        self.presence_client
                        )

                self.presence_client.signal.connect(
                    ['presence'], self._on_presence
                    )

                self.message_client.signal.connect(
                    ['message'], self.message_relay.on_message
                    )

                self.disco_service = org.wayround.xmpp.disco.DiscoService(
                    self.client.stanza_processor,
                    self.jid,
                    info=self.self_disco_info,
                    items=None
                    )

                self.message_relay.signal.connect(
                    'new_message', self._message_relay_listener
                    )

        self.is_driven = False

        if ret != 0:
            threading.Thread(
                target=self.disconnect,
                name="Disconnecting by connection error"
                ).start()

        return ret

    def disconnect(self):
        if not self._disconnection_flag.is_set():
            self._disconnection_flag.set()

            if self._rel_win_ctl != None:
                self._rel_win_ctl.destroy_windows()

            if self.client != None:

                self.client.stop()
                logging.debug("Now waiting for client to stop...")
                self.client.wait('stopped')

                sock = self.client.get_socket()

                logging.debug("Shutting down socket")
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except:
                    logging.exception(
                        "Can't shutdown socket. Maybe it's already dead"
                        )

                logging.debug("Closing socket object")
                try:
                    sock.close()
                except:
                    logging.exception(
                        "Can't close socket. Maybe it's already dead"
                        )

            self.clear()

    def load_roster_from_server(
        self,
        display_errors=False, parent_window=None
        ):

        ret, res = self.roster_storage.load_from_server()

        if ret == 'wrong_answer':

            if display_errors:
                d = org.wayround.utils.gtk.MessageDialog(
                    parent_window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Roster retrieval attempt returned not a stanza"
                    )
                d.run()
                d.destroy()

        if ret == 'invalid_value_returned':

            if display_errors:
                d = org.wayround.utils.gtk.MessageDialog(
                    parent_window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Unexpected return value:\n{}".format(res)
                    )
                d.run()
                d.destroy()

        if ret == 'error':
            if display_errors:
                err = res.gen_error()
                d = org.wayround.utils.gtk.MessageDialog(
                    parent_window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting roster:\n{}".format(repr(err))
                    )
                d.run()
                d.destroy()

        return

    def _on_connection_event(self, event, streamer, sock):

        if not self.is_driven:

            logging.debug(
                "_on_connection_event `{}', `{}'".format(event, sock)
                )

            if event == 'start':
                logging.debug("Connection started")

            elif event == 'stop':
                logging.debug("Connection stopped")
                self.disconnect()

            elif event == 'error':
                logging.debug("Connection error")
                self.disconnect()

        return

    def _on_stream_io_event(self, event, io_machine, attrs=None):

        if not self.is_driven:

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

    def _message_relay_listener(
        self,
        event, storage, original_stanza,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        with self._incomming_message_lock:

            if event == 'new_message':
                if type_ in [
                    'message_normal',
                    'message_error',
                    'message_headline'
                    ]:
                    self.show_single_message_window(
                        'view',
                        original_stanza,
                        receive_date
                        )

                elif type_ in ['message_chat', 'message_groupchat']:
                    self.show_chat_window()
                    w = self.get_chat_window()
                    cp = w.chat_pager

                    if type_ == 'message_chat':

                        group_chat_found = None
                        for i in cp.pages:
                            if (type(i) == \
                                org.wayround.pyabber.chat_pager.GroupChat
                                and i.contact_bare_jid == jid_obj.bare()):
                                group_chat_found = i
                                break

                        if group_chat_found == None:
                            cp.add_chat(jid_obj, thread_id)
                        else:
                            cp.add_private(str(jid_obj))

                    if type_ == 'message_groupchat':
                        message_relay_listener_call_queue = \
                            self.message_relay.signal.gen_call_queue(
                                ['new_message']
                                )
                        cp.add_groupchat(
                            jid_obj,
                            message_relay_listener_call_queue=
                                message_relay_listener_call_queue
                            )

                    win = w.get_window_widget()
                    win.set_title("Message from {}".format(jid_obj))
                    win.present()

        return

    def _on_presence(self, event, presence_obj, from_jid, to_jid, stanza):

        with self._incomming_message_lock:

            if event == 'presence':
                if org.wayround.xmpp.muc.has_muc_elements(
                    stanza.get_element()
                    ):
                    message_relay_listener_call_queue = \
                        self.message_relay.signal.gen_call_queue(
                            ['new_message']
                            )
                    self.show_chat_window()
                    w = self.get_chat_window()
                    jid = org.wayround.xmpp.core.JID.new_from_str(
                        stanza.get_from_jid()
                        )
                    w.chat_pager.add_groupchat(
                        jid,
                        message_relay_listener_call_queue=
                            message_relay_listener_call_queue
                        )

        return
