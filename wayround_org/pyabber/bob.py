
import logging
import datetime

from gi.repository import Gtk, GdkPixbuf, Gio

import wayround_org.xmpp.bob
import wayround_org.xmpp.core
import wayround_org.pyabber.misc


class BOBMgr:

    def __init__(self, controller):

        self._controller = controller

    def get_data_by_cid(
        self, cid, source_jid_obj, stanza_with_bob_data=None
        ):

        ret = None

        res = wayround_org.xmpp.bob.parse_cid(cid)

        if res != None:
            ret = self.get_data(
                res['method'],
                res['value'],
                source_jid_obj,
                stanza_with_bob_data
                )

        return ret

    def get_data(
        self, method, value, source_jid_obj, stanza_with_bob_data=None
        ):

        method = method.lower()
        value = value.lower()

        ret = None

        if (stanza_with_bob_data != None
            and not isinstance(
                stanza_with_bob_data,
                wayround_org.xmpp.core.Stanza
                )
            ):
            raise ValueError("invalid `stanza_with_bob_data'")

        if stanza_with_bob_data != None:

            bob_elements = stanza_with_bob_data.get_element().findall(
                './/{urn:xmpp:bob}data'
                )

            for i in bob_elements:
                if wayround_org.utils.lxml.is_lxml_tag_element(i):

                    i_cid = wayround_org.xmpp.bob.parse_cid(i.get('cid'))
                    req_cid = {'method': method, 'value': value}

                    logging.debug(
                        "Comparing {} with {}".format(i_cid, req_cid)
                        )

                    if i_cid == req_cid:
                        bob = wayround_org.xmpp.bob.Data.new_from_element(i)
                        ret = bob
                        break

        if ret == None:

            res = self._controller.storage.get_bob_data(method, value)

            if res == None:

                self.request(
                    source_jid_obj,
                    wayround_org.xmpp.bob.format_cid(method, value)
                    )

                res = self._controller.storage.get_bob_data(method, value)

                if res == None:
                    ret = None

                else:
                    ret = res

        return ret

    def request(self, source_jid_obj, cid):

        stanza = wayround_org.xmpp.core.Stanza(tag='iq')
        stanza.set_typ('get')
        stanza.set_to_jid(source_jid_obj.full())

        cir_req = wayround_org.xmpp.bob.Data(cid)

        stanza.set_objects([cir_req])

        res = self._controller.client.stanza_processor.send(stanza, wait=True)

        if isinstance(res, wayround_org.xmpp.core.Stanza):

            if res.is_error():
                wayround_org.pyabber.misc.stanza_error_message(
                    None,
                    res,
                    "Can't get bob for cid `{}'\nfrom {}".format(
                        cid,
                        source_jid_obj
                        )
                    )
            else:
                bob = res.get_element().find('{urn:xmpp:bob}data')

                if bob == None:
                    pass
                else:
                    bob = wayround_org.xmpp.bob.Data.new_from_element(bob)

                    if bob.is_data_error():
                        logging.error(
        "'{}' sent us data which does not consists with it's checksum".format(
                                res.get_from_jid()
                                )
                            )
                    else:

                        self._controller.storage.add_bob_data(
                            datetime.datetime.utcnow(),
                            bob
                            )
        return


class BOBWidget:

    def __init__(self, controller):

        self._controller = controller

        b = Gtk.Box()
        self._b = b
        b.set_orientation(Gtk.Orientation.VERTICAL)

        image = Gtk.Image()
        self._image = image

        desc_label = Gtk.Label("Info Label")
        self._desc_label = desc_label

        b.pack_start(image, False, False, 0)
        b.pack_start(desc_label, False, False, 0)

        b.show_all()

        return

    def set_data(self, cid, source_jid_obj, stanza_with_bob_data=None):

        res = self._controller.bob_mgr.get_data_by_cid(
            cid,
            source_jid_obj,
            stanza_with_bob_data
            )

        if res != None:

            data = res.get_data()

            if data != None:

                stream = Gio.MemoryInputStream.new_from_data(data, None)

                pb = GdkPixbuf.Pixbuf.new_from_stream(stream, None)

                self._image.set_from_pixbuf(pb)

                stream.close(None)

        return

    def get_widget(self):
        return self._b

    def destroy(self):
        self.get_widget().destroy()
