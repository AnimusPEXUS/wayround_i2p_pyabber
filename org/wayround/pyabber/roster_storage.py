
import copy
import threading

from gi.repository import Gtk

import org.wayround.utils.signal


class RosterStorage(org.wayround.utils.signal.Signal):

    def __init__(self):

        self._lock = threading.Lock()

        self._data = {}

        super().__init__(['set_bare', 'set_resource', 'unset_bare'])

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
            if ev != None:
                self._data[bare_jid]['full'][resource][i] = ev

            if not i in self._data[bare_jid]['full'][resource]:
                self._data[bare_jid]['full'][resource][i] = None

        data = self._get_data()

        self._lock.release()

        jid_data = data[bare_jid]

        self.emit_signal('set_resource', self, bare_jid, data, jid_data)

        return

    def set_bare(
        self,
        bare_jid,
        name_or_title=None, groups=None,
        approved=None, ask=None, subscription=None,
        nick=None, userpic=None, available=None, show=None, status=None,
        has_new_messages=None,
        not_in_roster=None, is_transport=None
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
            'has_new_messages',
            'not_in_roster', 'is_transport'
            ]:

            ev = eval(i)
            if ev != None:
                self._data[bare_jid]['bare'][i] = ev

            if not i in self._data[bare_jid]['bare']:
                self._data[bare_jid]['bare'][i] = None

        if ask == None:
            self._data[bare_jid]['bare']['ask'] = None

        if self._data[bare_jid]['bare']['groups'] == None:
            self._data[bare_jid]['bare']['groups'] = set()

        data = self._get_data()

        self._lock.release()

        jid_data = data[bare_jid]

        self.emit_signal('set_bare', self, bare_jid, data, jid_data)

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

        self.emit_signal('unset_bare', self, bare_jid, data, jid_data)

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

    def get_data(self):

        self._lock.acquire()

        ret = copy.deepcopy(self._data)

        self._lock.release()

        return ret

    def load_from_server(
        self,
        own_jid,
        roster_client, display_errors=False, parent_window=None
        ):

        ret = 'ok'

        res = roster_client.get(from_jid=own_jid.full())

        if res == None:
            ret = 'wrong_answer'
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
        else:
            if (isinstance(res, org.wayround.xmpp.core.Stanza)
                and res.is_error()):
                err = res.gen_error()
                ret = err
                if display_errors:
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

            elif (isinstance(res, org.wayround.xmpp.core.Stanza)
                  and not res.is_error()):

                ret = 'invalid value returned'

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

        return ret
