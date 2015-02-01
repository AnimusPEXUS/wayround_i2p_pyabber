
import copy
import logging
import threading

import lxml.etree
import wayround_org.utils.threading
import wayround_org.xmpp.client
import wayround_org.xmpp.core
import wayround_org.xmpp.muc


class Item:

    def __init__(
        self,
        nick,
        affiliation=None, role=None,
        available=None, show=None, status=None,
        jid=None
        ):

        self.set_nick(nick)
        self.set_affiliation(affiliation)
        self.set_role(role)
        self.set_available(available)
        self.set_show(show)
        self.set_status(status)
        self.set_jid(jid)

    check_nick = wayround_org.xmpp.muc.Item.check_nick
    check_affiliation = wayround_org.xmpp.muc.Item.check_affiliation
    check_role = wayround_org.xmpp.muc.Item.check_role
    check_jid = wayround_org.xmpp.muc.Item.check_jid

    def check_available(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError("`available' must be None or bool")

    def check_show(self, value):
        if value is not None and not value in ['available', 'unavailable']:
            wayround_org.xmpp.core.PresenceShow.check_text(self, value)

    def check_status(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("`status' must be None or str")

    def __repr__(self):
        return \
            ("MUCRosterItem: nick == {}, affiliation == {}, role == {},"
             " available == {}, show == {}, status == {}, jid == {}".format(
                self.get_nick(),
                self.get_affiliation(),
                self.get_role(),
                self.get_available(),
                self.get_show(),
                self.get_status(),
                self.get_jid()
                )
             )

wayround_org.utils.factory.class_generate_attributes(
    Item,
    ['nick', 'affiliation', 'role', 'available', 'show', 'status', 'jid']
    )


class Storage:

    def __init__(self, room_jid, presence_client):

        if not isinstance(presence_client, wayround_org.xmpp.client.Presence):
            raise TypeError(
                "`presence_client' must be wayround_org.xmpp.client.Presence"
                )

        if not isinstance(room_jid, wayround_org.xmpp.core.JID):
            raise TypeError(
                "`room_jid' must be wayround_org.xmpp.core.JID"
                )

        self._room_jid = room_jid
        self._presence_client = presence_client

        self._lock = threading.RLock()

        self._items = []

        self._own_resource = None

        self.signal = wayround_org.utils.threading.Signal(
            self,
            ['set', 'own_rename', 'rename']
            )

        return

    def destroy(self):
        return

    def get_own_resource(self):
        with self._lock:
            ret = self._own_resource
        return ret

    def _on_presence(
        self, event, presence_client_obj, from_jid, to_jid, stanza
        ):

        with self._lock:

            if event == 'presence':

                fj = wayround_org.xmpp.core.JID.new_from_str(from_jid)

                if fj.bare() == self._room_jid.bare():

                    show = stanza.get_show()
                    show_val = None
                    if show:
                        show_val = show.get_text()
                    else:
                        show_val = 'available'
                        if stanza.get_typ() == 'unavailable':
                            show_val = 'unavailable'

                    status = stanza.get_status()
                    status_val = None
                    if len(status) != 0:
                        status_val = status[0].get_text()
                    else:
                        status_val = ''

                    available_val = stanza.get_typ() != 'unavailable'

                    self.set(
                        nick=fj.resource,
                        show=show_val,
                        status=status_val,
                        available=available_val
                        )

                    muc_elem_list = wayround_org.xmpp.muc.get_muc_elements(
                        stanza.get_element()
                        )

                    len_muc_elem_list = len(muc_elem_list)

                    if len_muc_elem_list == 1:

                        e = muc_elem_list[0]

                        if e.tag == \
                            '{http://jabber.org/protocol/muc#user}x':

                            muc_obj = \
                                wayround_org.xmpp.muc.X.new_from_element(e)

                            item = muc_obj.get_item()

                            self.set(
                                nick=fj.resource,
                                affiliation=item.get_affiliation(),
                                role=item.get_role(),
                                new_nick=item.get_nick(),
                                jid=item.get_jid()
                                )

                            # FIXME: this is ejabberd 2.1.11 hack. the later
                            #        does not support xep-0045 correctly.
                            #        please, somebody, make them suffer
                            #        http://www.ejabberd.im/node/17036
                            #        this comment was added 1 Feb 2014
                            if (303 in muc_obj.get_status()
                                and stanza.get_typ() == 'unavailable'
                                and fj.resource == self._own_resource
                                and self._own_resource != None
                                ):

                                nn = item.get_nick()

                                if nn != None:
                                    if self._own_resource != nn:
                                        self._own_resource = nn
                                        logging.debug(
                                            "own_rename by 303 in {} to {}".format(
                                                str(fj.bare()),
                                                self._own_resource
                                                )
                                            )
                                        self.signal.emit(
                                            'own_rename',
                                            self,
                                            self._own_resource
                                            )

                            if ((110 in muc_obj.get_status()
                                 or 210 in muc_obj.get_status())
                                and stanza.get_typ() != 'unavailable'
                                ):

                                nn = fj.resource

                                if self._own_resource != nn:
                                    self._own_resource = nn
                                    logging.debug(
                                        "own_rename by 110 or 210 in {} to {}".format(
                                            str(fj.bare()),
                                            self._own_resource
                                            )
                                        )
                                    self.signal.emit(
                                        'own_rename',
                                        self,
                                        self._own_resource
                                        )

                    elif len_muc_elem_list > 1:
                        logging.error(
                            "Not supported more then one muc element in stanza"
                            ", error stanza is:\n----\n{}\n----".format(
                                lxml.etree.tostring(stanza.get_element())
                                )
                            )

        return

    pass_presence_signal = _on_presence

    def set(
        self,
        nick,
        affiliation=None, role=None, new_nick=None,
        available=None, show=None, status=None, jid=None
        ):

        with self._lock:
            d = None

            for i in self._items:
                if i.get_nick() == nick:
                    d = i

            if d == None:
                d = Item(nick)
                self._items.append(d)

            for i in [
                'affiliation',
                'role',
                'available',
                'show',
                'status',
                'jid'
                ]:
                val = eval(i)
                if val != None:
                    setter = getattr(d, 'set_{}'.format(i))
                    setter(val)

            if new_nick != None:
                d.set_nick(new_nick)

            self.signal.emit('set', self, nick, d)
            if nick != self._own_resource and nick != new_nick:
                self.signal.emit('rename', self, nick, new_nick)

        return

    def get_item(self, nick):
        with self._lock:
            ret = None
            for i in self._items:
                if i.get_nick() == nick:
                    ret = copy.deepcopy(i)
                    break
        return ret

    def get_items(self):
        with self._lock:
            ret = copy.deepcopy(self._items)
        return ret
