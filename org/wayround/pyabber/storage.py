
import logging
import threading
import datetime
import hashlib

import sqlalchemy.ext.declarative

import org.wayround.utils.db
import org.wayround.utils.threading
import org.wayround.utils.types
import org.wayround.utils.sqlalchemy
import org.wayround.xmpp.bob


class StorageDB(org.wayround.utils.db.BasicDB):

    Base = sqlalchemy.ext.declarative.declarative_base()

    class MessagesLastRead(Base):

        __tablename__ = 'messages_last_read'

        id_ = sqlalchemy.Column(
            name='id',
            type_=sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        connection_bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False
            )

        connection_jid_resource = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True
            )

        bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False
            )

        jid_resource = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True
            )

        date = sqlalchemy.Column(
            type_=sqlalchemy.DateTime,
            nullable=True,
            default=None
            )

    class History(Base):

        __tablename__ = 'history'

        id_ = sqlalchemy.Column(
            name='id',
            type_=sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        date = sqlalchemy.Column(
            type_=sqlalchemy.DateTime,
            nullable=False,
            default=datetime.datetime(1, 1, 1),
            index=True
            )

        receive_date = sqlalchemy.Column(
            type_=sqlalchemy.DateTime,
            nullable=False,
            default=datetime.datetime(1, 1, 1),
            index=True
            )

        delay_from = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True,
            index=True
            )

        delay_message = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True,
            index=True
            )

        incomming = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        connection_bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            index=True
            )

        connection_jid_resource = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True,
            index=True
            )

        bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            index=True
            )

        jid_resource = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True,
            index=True
            )

        type_ = sqlalchemy.Column(
            name='type',
            type_=sqlalchemy.String(length=10),
            nullable=False,
            default=''
            )

        parent_thread_id = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True
            )

        thread_id = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=True
            )

        subject = sqlalchemy.Column(
            type_=sqlalchemy.PickleType,
            nullable=False
            )

        plain = sqlalchemy.Column(
            type_=sqlalchemy.PickleType,
            nullable=False
            )

        xhtml = sqlalchemy.Column(
            type_=sqlalchemy.PickleType,
            nullable=False
            )

    class ConnectionPreset(Base):

        __tablename__ = 'connection_presets'

        name = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            primary_key=True,
            )

        username = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False
            )

        server = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False
            )

        resource_mode = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='client'
            )

        resource = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False
            )

        password = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='123'
            )

        password2 = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='1234'
            )

        manual_host_and_port = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=False
            )

        host = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        port = sqlalchemy.Column(
            type_=sqlalchemy.BigInteger,
            nullable=False,
            default=5222
            )

        stream_features_handling = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='auto'
            )

        starttls = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        starttls_necessarity_mode = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='necessary'
            )

        cert_verification_mode = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            default='can_selfsigned'
            )

        register = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=False
            )

        login = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        bind = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        session = sqlalchemy.Column(
            type_=sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

    class BoBCache(Base):

        __tablename__ = 'bob_cache'

        id_ = sqlalchemy.Column(
            name='id',
            type_=sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        date = sqlalchemy.Column(
            type_=sqlalchemy.DateTime,
            nullable=False,
            default=datetime.datetime(1, 1, 1),
            index=True
            )

        maxage = sqlalchemy.Column(
            type_=sqlalchemy.Integer,
            nullable=False,
            default=0
            )

        type_ = sqlalchemy.Column(
            name='type',
            type_=sqlalchemy.UnicodeText,
            nullable=True,
            index=True
            )

        sha1 = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            index=True
            )

        data = sqlalchemy.Column(
            type_=sqlalchemy.LargeBinary,
            nullable=True
            )

    class VCard(Base):

        __tablename__ = 'vcard'

        id_ = sqlalchemy.Column(
            name='id',
            type_=sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        connection_bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            index=True
            )

        bare_jid = sqlalchemy.Column(
            type_=sqlalchemy.UnicodeText,
            nullable=False,
            index=True
            )

        version = sqlalchemy.Column(
            type_=sqlalchemy.DateTime,
            nullable=False,
            index=True
            )

        photo = sqlalchemy.Column(
            type_=sqlalchemy.LargeBinary,
            nullable=True
            )

        data = sqlalchemy.Column(
            type_=sqlalchemy.PickleType,
            nullable=True
            )

#        for i in [
#            'source', 'kind', 'xml', 'fn', 'n', 'nickname', 'photo', 'bday',
#            'anniversary', 'gender', 'adr', 'tel', 'email', 'impp', 'lang',
#            'tz', 'geo', 'title', 'role', 'logo', 'org', 'member', 'related',
#            'categories', 'note', 'prodid', 'rev', 'sound', 'uid',
#            'clientpidmap', 'url', 'key', 'fburl', 'caladruri', 'caluri'
#            ]:


CONNECTION_PRESET_FIELDS = \
    org.wayround.utils.types.attrs_dict_to_object_same_names(
        org.wayround.utils.sqlalchemy.get_column_names(
            StorageDB.Base.metadata,
            'connection_presets'
            )
        )

HISTORY_RECORD_FIELDS = \
    org.wayround.utils.types.attrs_dict_to_object_same_names(
        org.wayround.utils.sqlalchemy.get_column_names(
            StorageDB.Base.metadata,
            'history'
            )
        )


for i in HISTORY_RECORD_FIELDS[:]:
    if i[0] == 'id':
        HISTORY_RECORD_FIELDS.remove(i)
        HISTORY_RECORD_FIELDS.append(('id_', 'id_',))

    if i[0] == 'type':
        HISTORY_RECORD_FIELDS.remove(i)
        HISTORY_RECORD_FIELDS.append(('type_', 'type_',))

del i


BOB_CACHE_FIELDS = \
    org.wayround.utils.types.attrs_dict_to_object_same_names(
        org.wayround.utils.sqlalchemy.get_column_names(
            StorageDB.Base.metadata,
            'bob_cache'
            )
        )

for i in BOB_CACHE_FIELDS[:]:
    if i[0] == 'id':
        BOB_CACHE_FIELDS.remove(i)
        BOB_CACHE_FIELDS.append(('id_', 'id_',))

    if i[0] == 'type':
        BOB_CACHE_FIELDS.remove(i)
        BOB_CACHE_FIELDS.append(('type_', 'type_',))


VCARD_FIELDS = \
    org.wayround.utils.types.attrs_dict_to_object_same_names(
        org.wayround.utils.sqlalchemy.get_column_names(
            StorageDB.Base.metadata,
            'vcard'
            )
        )

for i in VCARD_FIELDS[:]:
    if i[0] == 'id':
        VCARD_FIELDS.remove(i)
        VCARD_FIELDS.append(('id_', 'id_',))


class Storage:

    def __init__(self, *args, **kwargs):
        self.signal = org.wayround.utils.threading.Signal(
            self,
            [
             'history_update'
             ]
            )
        self._db = StorageDB(*args, **kwargs)

        self._lock = threading.RLock()

        self._cleaning_bob = False

        return

    def create(self):
        return self._db.create_all()

    def commit(self):
        return self._db.commit()

    save = commit

    def close(self):
        return self._db.close()

    destroy = close

    def _get_message_last_read_date(
        self,
        connection_jid_obj, jid_obj
        ):

        ret = None

        connection_bare_jid = connection_jid_obj.bare()
        connection_jid_resource = connection_jid_obj.resource
        bare_jid = jid_obj.bare()
        jid_resource = jid_obj.resource

        res = self._db.session.query(self._db.MessagesLastRead).\
            filter(
                self._db.MessagesLastRead.connection_bare_jid
                    == connection_bare_jid,
                self._db.MessagesLastRead.connection_jid_resource
                    == connection_jid_resource,
                self._db.MessagesLastRead.bare_jid == bare_jid,
                self._db.MessagesLastRead.jid_resource == jid_resource
                ).\
                all()

        n = None

        if len(res) == 0:

            n = self._db.MessagesLastRead()
            n.connection_bare_jid = connection_bare_jid
            n.connection_jid_resource = connection_jid_resource
            n.bare_jid = bare_jid
            n.jid_resource = jid_resource

            self._db.session.add(n)

            ret = n

        else:
            n = res[0]

            ret = n

        if len(res) > 1:
            for i in res[1:]:
                self._db.session.delete(i)

        self._db.commit()

        return ret

    def get_message_last_read_date(
        self,
        connection_jid_obj, jid_obj
        ):

        with self._lock:

            try:

                ret = None

                res = self._get_message_last_read_date(
                    connection_jid_obj,
                    jid_obj
                    )
                if res != None:
                    ret = res.date

            except:
                logging.exception("Error getting last read date")

        return ret

    def set_message_last_read_date(
        self,
        connection_jid_obj, jid_obj,
        date
        ):

        with self._lock:

            try:
                res = self._get_message_last_read_date(
                    connection_jid_obj,
                    jid_obj
                    )
                res.date = date

                self._db.commit()

            except:
                logging.exception("Error setting last read date")

        return

    def add_history_record(
        self,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        with self._lock:

            try:

                connection_bare_jid = connection_jid_obj.bare()
                connection_jid_resource = connection_jid_obj.resource
                bare_jid = jid_obj.bare()
                jid_resource = jid_obj.resource

                if self._is_history_record_already_in(
                    date,
                    connection_bare_jid, connection_jid_resource,
                    bare_jid, jid_resource,
                    subject, plain, xhtml
                    ):
                    logging.debug(
                        "Message dated {} assumed to be already in DB".format(
                            date
                            )
                        )
                else:

                    h = self._db.History()
                    h.date = date
                    h.receive_date = receive_date
                    h.delay_from = delay_from
                    h.delay_message = delay_message
                    h.incomming = incomming
                    h.connection_bare_jid = connection_bare_jid
                    h.connection_jid_resource = connection_jid_resource
                    h.bare_jid = bare_jid
                    h.jid_resource = jid_resource
                    h.type_ = type_
                    h.thread_id = thread_id
                    h.parent_thread_id = parent_thread_id
                    h.subject = subject
                    h.plain = plain
                    h.xhtml = xhtml

                    self._db.session.add(h)

                    self._db.session.commit()

                    self.signal.emit(
                        'history_update',
                        self,
                        date, receive_date, delay_from, delay_message,
                        incomming, connection_jid_obj, jid_obj, type_,
                        parent_thread_id, thread_id, subject, plain, xhtml
                        )

            except:
                logging.exception("Error adding history record")

        return

    def _is_history_record_already_in(
        self,
        date,
        connection_bare_jid, connection_jid_resource,
        bare_jid, jid_resource,
        subject, plain, xhtml
        ):

        q = self._db.session.query(self._db.History)

        q = q.filter(
            self._db.History.date
                == date,
            self._db.History.connection_bare_jid
                == connection_bare_jid,
            self._db.History.bare_jid == bare_jid,

            self._db.History.subject == subject,
            self._db.History.plain == plain,
            self._db.History.xhtml == xhtml
            )

#        if connection_jid_resource != None:
#            q = q.filter(
#                self._db.History.connection_jid_resource
#                    == connection_jid_resource
#                )

        if jid_resource != None:
            q = q.filter(
                self._db.History.jid_resource
                    == jid_resource
                )

        res = q.all()

        return len(res) != 0

    def get_history_records(
        self,
        connection_bare_jid=None, connection_jid_resource=None,
        bare_jid=None, jid_resource=None,

        starting_from_date=None, starting_includingly=True,
        ending_with_date=None, ending_includingly=True,
        limit=None, offset=None,
        types=None
        ):

        with self._lock:

            try:

                if types == None:
                    types = []

                q = self._db.session.query(self._db.History)

                q = q.filter(
                    self._db.History.connection_bare_jid
                        == connection_bare_jid,
                    self._db.History.bare_jid == bare_jid
                    )

                if connection_jid_resource != None:
                    q = q.filter(
                        self._db.History.connection_jid_resource
                            == connection_jid_resource
                        )

                if jid_resource != None:
                    q = q.filter(
                        self._db.History.jid_resource
                            == jid_resource
                        )

                if starting_from_date != None:

                    if starting_includingly:
                        q = q.filter(
                            self._db.History.date >= starting_from_date
                            )
                    else:
                        q = q.filter(
                            self._db.History.date > starting_from_date
                            )

                if ending_with_date != None:

                    if ending_includingly:
                        q = q.filter(self._db.History.date <= ending_with_date)
                    else:
                        q = q.filter(self._db.History.date < ending_with_date)

                if len(types) != 0:
                    q = q.filter(self._db.History.type_.in_(types))

                q = q.order_by(self._db.History.date.desc())

                if limit != None:
                    q = q.limit(limit)

                if offset != None:
                    q = q.offset(offset)

                q = q.from_self()

                q = q.order_by(self._db.History.date)

            except:
                logging.exception("Error getting history record")

            ret = convert_history_query_result_list(q.all())

        return ret

    def get_connection_presets_count(self):
        ret = None

        with self._lock:

            try:
                ret = self._db.session.query(self.ConnectionPreset).count()
            except:
                logging.exception("Error getting connection presets count")

        return ret

    def get_connection_presets_list(self):
        ret = []

        with self._lock:

            try:
                res = self._db.session.query(self._db.ConnectionPreset).\
                    add_columns(self._db.ConnectionPreset.name).\
                    all()
                for i in res:
                    ret.append(i.name)
            except:
                logging.exception("Error connection presets list")

        return ret

    def get_connection_preset_by_name(self, name):
        ret = None

        with self._lock:

            try:
                res = self._db.session.query(self._db.ConnectionPreset).\
                    filter(self._db.ConnectionPreset.name == name).\
                    all()

                if len(res) != 0:
                    ret = res[0]

                if len(res) > 1:

                    for i in res[1:]:
                        self._db.session.delete(i)

                    self._db.commit()

                if ret != None:
                    res = {}
                    org.wayround.utils.types.attrs_object_to_dict(
                        ret, res, CONNECTION_PRESET_FIELDS
                        )
                    ret = res
            except:
                logging.exception("Error getting connection preset by name")

        return ret

    def set_connection_preset(self, name, preset):
        p = self.get_connection_preset_by_name(name)
        if p != None:
            self.del_connection_preset(name)

        with self._lock:

            try:

                new_preset = self._db.ConnectionPreset()

                org.wayround.utils.types.attrs_dict_to_object(
                    preset, new_preset, CONNECTION_PRESET_FIELDS
                    )

                self._db.session.add(new_preset)
                self._db.commit()
            except:
                logging.exception("Error setting connection preset")

        return

    def del_connection_preset(self, name):
        with self._lock:
            try:
                p = self._db.session.query(self._db.ConnectionPreset).\
                    filter(self._db.ConnectionPreset.name == name).\
                    all()
                for i in p:
                    self._db.session.delete(i)
                self._db.commit()
            except:
                logging.exception("Error deleting connection preset")
        return

    def _get_count_bob_data(self, method, sum_val, _mode='count'):

        if not _mode in ['get', 'count']:
            raise ValueError("invalid `_mode'")

        if not method in ['sha1']:
            raise ValueError(
                "acceptable methods are ['sha1']"
                )

        table_field = eval('self._db.BoBCache.{}'.format(method))

        ret = 0
        if _mode == 'get':
            ret = None

        with self._lock:

            try:
                ret = self._db.session.query(self._db.BoBCache).\
                    filter(table_field == sum_val)

                if _mode == 'count':
                    ret = ret.count()
                elif _mode == 'get':
                    ret = ret.all()
                    if len(ret) > 0:
                        ret = ret[0]
                    else:
                        ret = None

            except:
                logging.exception("Error '{}' bob data".format(_mode))
            else:
                if _mode == 'get' and ret != None:
                    res = org.wayround.xmpp.bob.Data(
                        org.wayround.xmpp.bob.format_cid(method, sum_val)
                        )
                    res.set_type_(ret.type_)
                    res.set_data(ret.data)
                    res.set_maxage(ret.maxage)

                    ret = res

        return ret

    def count_bob_data(self, method, sum_val):
        return self._get_count_bob_data(method, sum_val, _mode='count')

    def get_bob_data(self, method, sum_val):
        return self._get_count_bob_data(method, sum_val, _mode='get')

    def add_bob_data(self, date, bob):

        if not isinstance(date, datetime.datetime):
            raise ValueError("`date' must be datetime")

        if not isinstance(bob, org.wayround.xmpp.bob.Data):
            raise ValueError("`bob' must be org.wayround.xmpp.bob.Data")

        d = hashlib.sha1()
        d.update(bob.get_data())
        sha1 = d.hexdigest()

        if self.count_bob_data('sha1', sha1) == 0:

            with self._lock:

                try:
                    n = self._db.BoBCache()
                    n.data = bob.get_data()
                    n.date = date
                    n.maxage = int(bob.get_maxage())
                    n.sha1 = sha1
                    n.type_ = bob.get_type_()

                    self._db.session.add(n)
                    self._db.commit()
                except:
                    logging.exception("Error adding bob data")

        return

    def clean_bob_data(self):

        if not self._cleaning_bob:

            self._cleaning_bob = True

            with self._lock:

                try:
                    all1 = self._db.session.query(self._db.BoBCache).all()
                    curdat = datetime.datetime.utcnow()
                    for i in all1:
                        if (i.date + datetime.timedelta(seconds=int(i.maxage))
                            < curdat):
                            self._db.session.delete(i)
                    self._db.commit()

                except:
                    logging.exception("Error cleaning bob data")

            self._cleaning_bob = False

        return

    def get_latest_vcard(
        self, connection_bare_jid, bare_jid
        ):

        connection_bare_jid = connection_bare_jid.lower()
        bare_jid = bare_jid.lower()

        with self._lock:

            res = self._db.session.query(self._db.VCard).\
                filter(
                    self._db.VCard.connection_bare_jid == connection_bare_jid,
                    self._db.VCard.bare_jid == bare_jid
                    ).\
                orded_by(
                    self._db.VCard.version.desc()
                    ).\
                limit(1).\
                all()

            ret = None
            if len(res) != 0:
                ret = {}
                org.wayround.utils.types.attrs_object_to_dict(
                    res, ret, VCARD_FIELDS
                    )

        return ret

    def set_vcard(
        self,
        connection_bare_jid, bare_jid,
        data
        ):

        with self._lock:
            if (data
                != self.get_latest_vcard(
                    connection_bare_jid,
                    bare_jid)['data']
                ):

                vcard = self._db.VCard()
                vcard.connection_bare_jid = connection_bare_jid
                vcard.bare_jid = bare_jid
                vcard.data = data

                self._db.session.add(vcard)

                self._db.session.commit()

        return



def convert_history_query_result_list(lst):

    ret = []

    for i in lst:

        d = {}

        org.wayround.utils.types.attrs_object_to_dict(
            i, d, HISTORY_RECORD_FIELDS
            )

        ret.append(d)

    return ret
