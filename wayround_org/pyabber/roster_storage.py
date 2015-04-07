
import copy
import logging
import threading

import wayround_org.pyabber.muc_roster_storage
import wayround_org.utils.threading
import wayround_org.xmpp.muc


class RosterStorage:

    def __init__(self, own_jid_obj, roster_client, presence_client):

        if not isinstance(roster_client, wayround_org.xmpp.client.Roster):
            raise TypeError(
                "`roster_client' must be wayround_org.xmpp.client.Roster"
                )

        if not isinstance(presence_client, wayround_org.xmpp.client.Presence):
            raise TypeError(
                "`presence_client' must be wayround_org.xmpp.client.Presence"
                )

        if not isinstance(own_jid_obj, wayround_org.xmpp.core.JID):
            raise TypeError(
                "`own_jid_obj' must be wayround_org.xmpp.core.JID"
                )

        self._jid = own_jid_obj
        self._roster_client = roster_client
        self._presence_client = presence_client

        self._lock = threading.Lock()
        self._muc_storage_creation_lock = threading.Lock()

        self._data = {}
        self._muc_rosters = {}

        self.signal = wayround_org.utils.threading.Signal(
            self,
            ['set_bare', 'set_resource', 'unset_bare']
            )

        roster_client.signal.connect(
            ['push'], self._on_roster_push
            )

        presence_client.signal.connect(
            ['presence'], self._on_presence
            )

        return

    def set_resource(
            self,
            bare_jid,
            resource,
            available=None,
            show=None,
            status=None,
            not_in_roster=None
            ):

        self.set_bare(
            bare_jid=bare_jid,
            available=available,
            show=show,
            status=status
            )

        self._lock.acquire()

        if not resource in self._data[bare_jid]['full']:
            self._data[bare_jid]['full'][resource] = {}

        for i in [
                'available',
                'show',
                'status'
                ]:

            ev = eval(i)
            if ev is not None:
                self._data[bare_jid]['full'][resource][i] = ev

            if not i in self._data[bare_jid]['full'][resource]:
                self._data[bare_jid]['full'][resource][i] = None

        data = self._get_data()

        self._lock.release()

        jid_data = data[bare_jid]

        self.signal.emit(
            'set_resource', self, bare_jid, resource, data, jid_data
            )

        return

    def set_bare(
            self,
            bare_jid,
            name_or_title=None, groups=None,
            approved=None, ask=None, subscription=None,
            nick=None, userpic=None, available=None, show=None, status=None,
            not_in_roster=None
            ):
        """
        Change indication parameters

        For all parameters (except bare_jid off course) None value means - do
        no change current indication.

        threadsafe using Lock()
        """

        self._lock.acquire()

        if not bare_jid in self._data:
            self._data[bare_jid] = {
                'bare': {},
                'full': {}
                }

        for i in [
                'name_or_title', 'groups',
                'approved', 'ask', 'subscription',
                'nick', 'userpic', 'available', 'show', 'status',
                'not_in_roster'
                ]:

            ev = eval(i)
            if ev is not None:
                self._data[bare_jid]['bare'][i] = ev

            if not i in self._data[bare_jid]['bare']:
                self._data[bare_jid]['bare'][i] = None

        if ask is None:
            self._data[bare_jid]['bare']['ask'] = None

        if self._data[bare_jid]['bare']['groups'] is None:
            self._data[bare_jid]['bare']['groups'] = set()

        data = self._get_data()

        self._lock.release()

        jid_data = data[bare_jid]

        self.signal.emit('set_bare', self, bare_jid, None, data, jid_data)

        return

    def unset_bare(self, bare_jid):
        """
        About signal: at the time of emission jid_data and it's jid will not be
        found in storage
        """

        self._lock.acquire()

        data = self._get_data()
        jid_data = data[bare_jid]

        if bare_jid in self._data:
            del self._data[bare_jid]

        self._lock.release()

        self.signal.emit('unset_bare', self, bare_jid, None, data, jid_data)

        return

    def get_contacts(self):

        self._lock.acquire()

        ret = list(self._data.keys())

        self._lock.release()

        return ret

    def get_groups(self):

        self._lock.acquire()

        groups = set()

        for i in self._data.keys():
            groups |= set(self._data[i]['bare']['groups'])

        ret = list(groups)

        self._lock.release()

        return ret

    def _get_data(self):
        return copy.deepcopy(self._data)

    def get_jid_data(self, bare_jid):
        data = self.get_data()
        if not bare_jid in data:
            self.set_bare(
                bare_jid,
                not_in_roster=True,
                )
            data = self.get_data()
        ret = data[bare_jid]
        return ret

    def get_data(self):

        self._lock.acquire()

        ret = copy.deepcopy(self._data)

        self._lock.release()

        return ret

    def load_from_server(self):

        ret = 'ok'

        res = self._roster_client.get(from_jid=self._jid.full())

        if res is None:
            ret = 'wrong_answer'
        else:
            if (isinstance(res, wayround_org.xmpp.core.Stanza)
                    and res.is_error()):

                ret = 'error'

            elif (isinstance(res, wayround_org.xmpp.core.Stanza)
                  and not res.is_error()):

                ret = 'invalid_value_returned'

            elif isinstance(res, dict):

                conts = self.get_contacts()

                for i in res.keys():
                    self.set_bare(
                        name_or_title=res[i].get_name(),
                        bare_jid=i,
                        groups=res[i].get_group(),
                        approved=res[i].get_approved(),
                        ask=res[i].get_ask(),
                        subscription=res[i].get_subscription()
                        )

                for i in conts:
                    if not i in res:
                        self.set_bare(
                            bare_jid=i,
                            not_in_roster=True
                            )
            else:
                raise Exception("DNA error")

        return ret, res

    def _on_roster_push(self, event, roster_obj, stanza_data):

        if event != 'push':
            pass
        else:

            jid = list(stanza_data.keys())[0]
            data = stanza_data[jid]

            not_in_roster = data.get_subscription() == 'remove'

            self.set_bare(
                name_or_title=data.get_name(),
                bare_jid=jid,
                groups=data.get_group(),
                approved=data.get_approved(),
                ask=data.get_ask(),
                subscription=data.get_subscription(),
                not_in_roster=not_in_roster
                )

        return

    def _on_presence(self, event, presence_obj, from_jid, to_jid, stanza):

        if event == 'presence':

            if not wayround_org.xmpp.muc.has_muc_elements(
                    stanza.get_element()
                    ):

                if not stanza.get_typ() in [
                        'unsubscribe', 'subscribed', 'unsubscribed'
                        ]:

                    f_jid = None

                    if from_jid:
                        f_jid = wayround_org.xmpp.core.JID.new_from_str(
                            from_jid
                            )
                    else:
                        f_jid = self._jid.copy()
                        f_jid.user = None

                    not_in_roster = None
                    if stanza.get_typ() == 'remove':
                        not_in_roster = True

                    if (not f_jid.bare() in
                            self.get_data()):
                        not_in_roster = True

                    status = None
                    s = stanza.get_status()
                    if len(s) != 0:
                        status = s[0].get_text()
                    else:
                        status = ''

                    show = stanza.get_show()
                    if show:
                        show = show.get_text()
                    else:
                        show = 'available'
                        if stanza.get_typ() == 'unavailable':
                            show = 'unavailable'

                    if f_jid.is_full():
                        self.set_resource(
                            bare_jid=f_jid.bare(),
                            resource=f_jid.resource,
                            available=stanza.get_typ() != 'unavailable',
                            show=show,
                            status=status,
                            not_in_roster=not_in_roster
                            )
                    elif f_jid.is_bare():
                        self.set_bare(
                            bare_jid=f_jid.bare(),
                            available=stanza.get_typ() != 'unavailable',
                            show=show,
                            status=status,
                            not_in_roster=not_in_roster
                            )
                    else:
                        logging.error("Don't know what to do")

                else:
                    logging.warning(
                        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stanza.typ is {}".format(
                            stanza.get_typ()
                            )
                        )
                    # TODO: WARNING:root:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stanza.typ is subscribed
                    # TODO: WARNING:root:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stanza.typ is unsubscribe
                    # TODO: WARNING:root:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stanza.typ is unsubscribed

            else:
                f_jid = wayround_org.xmpp.core.JID.new_from_str(
                    from_jid
                    )
                f_jid_bare = f_jid.bare()

                muc_storage = self.get_muc_storage(f_jid_bare)

                muc_storage.pass_presence_signal(
                    event,
                    presence_obj,
                    from_jid,
                    to_jid,
                    stanza
                    )
        return

    def get_muc_storage(self, room_bare_jid):
        with self._muc_storage_creation_lock:
            f_jid = wayround_org.xmpp.core.JID.new_from_str(
                room_bare_jid
                )
            f_jid_bare = f_jid.bare()
            if not f_jid_bare in self._muc_rosters:
                self._muc_rosters[f_jid_bare] = \
                    wayround_org.pyabber.muc_roster_storage.Storage(
                        f_jid.bare_obj(),
                        self._presence_client
                        )
            muc_storage = self._muc_rosters[f_jid_bare]
        return muc_storage
