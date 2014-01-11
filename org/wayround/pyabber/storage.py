
import logging
import threading
import datetime
import json

import sqlalchemy.ext.declarative
import sqlalchemy.orm

import org.wayround.utils.db
import org.wayround.utils.signal
import org.wayround.utils.types
import org.wayround.utils.sqlalchemy


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

#print(repr(HISTORY_RECORD_FIELDS))
##print(StorageDB.Base.metadata.tables['history'].columns)
#print(repr(dir(StorageDB.Base.metadata.tables['history'].columns['id'])))
#print(repr(StorageDB.Base.metadata.tables['history'].columns['id'].name))

for i in HISTORY_RECORD_FIELDS[:]:
    if i[0] == 'id':
        HISTORY_RECORD_FIELDS.remove(i)
        HISTORY_RECORD_FIELDS.append(('id_', 'id_',))

    if i[0] == 'type':
        HISTORY_RECORD_FIELDS.remove(i)
        HISTORY_RECORD_FIELDS.append(('type_', 'type_',))

del i

#print(repr(HISTORY_RECORD_FIELDS))


class Storage(org.wayround.utils.signal.Signal):

    def __init__(self, *args, **kwargs):
        super().__init__(
            [
             'history_update'
             ]
            )
        self._db = StorageDB(*args, **kwargs)

        self._lock = threading.Lock()
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

        self._lock.acquire()

        try:

            ret = None

            res = self._get_message_last_read_date(connection_jid_obj, jid_obj)
            if res != None:
                ret = res.date

        except:
            logging.exception("Error getting last read date")

        self._lock.release()

        return ret

    def set_message_last_read_date(
        self,
        connection_jid_obj, jid_obj,
        date
        ):

        self._lock.acquire()

        try:
            res = self._get_message_last_read_date(connection_jid_obj, jid_obj)
            res.date = date

            self._db.commit()

        except:
            logging.exception("Error setting last read date")

        self._lock.release()
        return

    def add_history_record(
        self,
        date, receive_date, delay_from, delay_message, incomming,
        connection_jid_obj, jid_obj, type_, parent_thread_id, thread_id,
        subject, plain, xhtml
        ):

        self._lock.acquire()

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

                self.emit_signal(
                    'history_update',
                    self,
                    date, receive_date, delay_from, delay_message, incomming,
                    connection_jid_obj, jid_obj, type_, parent_thread_id,
                    thread_id, subject, plain, xhtml
                    )

        except:
            logging.exception("Error adding history record")

        self._lock.release()

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

        self._lock.acquire()

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
                    q = q.filter(self._db.History.date >= starting_from_date)
                else:
                    q = q.filter(self._db.History.date > starting_from_date)

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

        self._lock.release()

        return ret

    def get_connection_presets_count(self):
        ret = None
        self._lock.acquire()

        try:
            ret = self._db.session.query(self.ConnectionPreset).count()
        except:
            logging.exception("Error getting connection presets count")

        self._lock.release()
        return ret

    def get_connection_presets_list(self):
        ret = []

        self._lock.acquire()
        try:
            res = self._db.session.query(self._db.ConnectionPreset).\
                add_columns(self._db.ConnectionPreset.name).\
                all()
            for i in res:
                ret.append(i.name)
        except:
            logging.exception("Error connection presets list")

        self._lock.release()
        return ret

    def get_connection_preset_by_name(self, name):
        ret = None

        self._lock.acquire()
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

        self._lock.release()

        return ret

    def set_connection_preset(self, name, preset):
        p = self.get_connection_preset_by_name(name)
        if p != None:
            self.del_connection_preset(name)

        self._lock.acquire()
        try:

            new_preset = self._db.ConnectionPreset()

            org.wayround.utils.types.attrs_dict_to_object(
                preset, new_preset, CONNECTION_PRESET_FIELDS
                )

            self._db.session.add(new_preset)
            self._db.commit()
        except:
            logging.exception("Error setting connection preset")

        self._lock.release()

        return

    def del_connection_preset(self, name):
        self._lock.acquire()
        try:
            p = self._db.session.query(self._db.ConnectionPreset).\
                filter(self._db.ConnectionPreset.name == name).\
                all()
            for i in p:
                self._db.session.delete(i)
            self._db.commit()
        except:
            logging.exception("Error deleting connection preset")

        self._lock.release()

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
