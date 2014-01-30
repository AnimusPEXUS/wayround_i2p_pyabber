
import copy
import logging
import threading

import lxml.etree
import org.wayround.utils.threading
import org.wayround.xmpp.client
import org.wayround.xmpp.core
import org.wayround.xmpp.muc


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

    check_nick = org.wayround.xmpp.muc.Item.check_nick
    check_affiliation = org.wayround.xmpp.muc.Item.check_affiliation
    check_role = org.wayround.xmpp.muc.Item.check_role
    check_jid = org.wayround.xmpp.muc.Item.check_jid

    def check_available(self, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError("`available' must be None or bool")

    def check_show(self, value):
        if value is not None and not value in ['available', 'unavailable']:
            org.wayround.xmpp.core.PresenceShow.check_text(self, value)

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

org.wayround.utils.factory.class_generate_attributes(
    Item,
    ['nick', 'affiliation', 'role', 'available', 'show', 'status', 'jid']
    )


class Storage:

    def __init__(self, room_jid, presence_client):

        if not isinstance(presence_client, org.wayround.xmpp.client.Presence):
            raise TypeError(
                "`presence_client' must be org.wayround.xmpp.client.Presence"
                )

        if not isinstance(room_jid, org.wayround.xmpp.core.JID):
            raise TypeError(
                "`room_jid' must be org.wayround.xmpp.core.JID"
                )

        self._room_jid = room_jid
        self._presence_client = presence_client

        self._lock = threading.Lock()

        self._items = []

        self._own_resource = None

        self.signal = org.wayround.utils.threading.Signal(
            self,
            ['set',
             'own_rename']
            )

        presence_client.signal.connect(
            ['presence'], self._on_presence
            )

        return

    def destroy(self):
        self._presence_client.signal.disconnect(
            self._on_presence
            )

    def _on_presence(
        self, event, presence_client_obj, from_jid, to_jid, stanza
        ):

        if event == 'presence':

            fj = org.wayround.xmpp.core.JID.new_from_str(from_jid)

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

                muc_elem_list = org.wayround.xmpp.muc.get_muc_elements(
                    stanza.get_element()
                    )

                logging.debug(
                    "{}: found muc elements:\n{}".format(self, muc_elem_list)
                    )

                len_muc_elem_list = len(muc_elem_list)

                if len_muc_elem_list == 1:

                    e = muc_elem_list[0]

                    if e.tag == \
                        '{http://jabber.org/protocol/muc#user}x':

                        muc_obj = org.wayround.xmpp.muc.X.new_from_element(e)

                        item = muc_obj.get_item()

                        self.set(
                            nick=fj.resource,
                            affiliation=item.get_affiliation(),
                            role=item.get_role(),
                            new_nick=item.get_nick(),
                            jid=item.get_jid()
                            )

                        if 110 in muc_obj.get_status():
                            if stanza.get_typ() != 'unavailable':
                                self._own_resource = fj.resource
                            else:
                                self._own_resource = None

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

        return

    def get_item(self, nick):
        ret = None
        for i in self._items:
            if i.get_nick() == nick:
                ret = copy.deepcopy(i)
                break
        return ret

    def get_items(self):
        ret = copy.deepcopy(self._items)
        return ret
