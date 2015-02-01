
from gi.repository import Gtk

import wayround_org.pyabber.ccc
import wayround_org.pyabber.bob
import wayround_org.xmpp.bob
import wayround_org.xmpp.xdata_media_element


class MediaElementWidget:

    def __init__(self, controller, media_data, origin_stanza):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise TypeError(
    "`controller' must be wayround_org.pyabber.ccc.ClientConnectionController"
                )

        if not isinstance(
            media_data,
            wayround_org.xmpp.xdata_media_element.Media
            ):
            raise TypeError(
    "`media_data' must be wayround_org.xmpp.xdata_media_element.Media"
                )

        self._controller = controller
        self._media_data = media_data
        self._origin_stanza = origin_stanza

        self._uris = []

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        uris = media_data.get_uri()

        for i in uris:
            _t = URIWidget(controller, i, origin_stanza)
            b.pack_start(_t.get_widget(), False, False, 0)
            self._uris.append(_t)

        self._b = b
        b.show_all()

        return

    def destroy(self):
        for i in self._uris[:]:
            i.destroy()
            self._uris.remove(i)

        self.get_widget().destroy()

    def get_widget(self):
        return self._b


class URIWidget:

    def __init__(self, controller, uri_data, origin_stanza):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise TypeError(
    "`controller' must be wayround_org.pyabber.ccc.ClientConnectionController"
                )

        if not isinstance(
            uri_data,
            wayround_org.xmpp.xdata_media_element.URI
            ):
            raise TypeError(
    "`media_data' must be wayround_org.xmpp.xdata_media_element.URI"
                )

        self._controller = controller
        self._uri_data = uri_data
        self._origin_stanza = origin_stanza

        typ = uri_data.get_type_()
        cid = uri_data.get_text()
        cid_parsed = wayround_org.xmpp.bob.parse_cid(cid)

        is_cid = cid_parsed != None

        is_cid_picture = typ in ['image/png', 'image/jpeg'] and is_cid

        b = Gtk.Box()
        b.set_spacing(5)

        type_label = Gtk.Label(typ)

        self._bob_widget = None

        b.pack_start(type_label, False, False, 0)
        if is_cid_picture:
            b.set_orientation(Gtk.Orientation.VERTICAL)
            self._bob_widget = wayround_org.pyabber.bob.BOBWidget(controller)
            self._bob_widget.set_data(
                cid,
                wayround_org.xmpp.core.JID.new_from_str(
                    self._origin_stanza.get_from_jid()
                    ),
                self._origin_stanza
                )

            b.pack_start(self._bob_widget.get_widget(), False, False, 0)

        else:
            b.set_orientation(Gtk.Orientation.HORIZONTAL)

            link_label = Gtk.Label(uri_data.get_text())
            link_label.set_selectable(True)

            b.pack_start(link_label, False, False, 0)

        self._b = b
        self._b.show_all()

        return

    def destroy(self):
        self._bob_widget.destroy()
        self.get_widget().destroy()

    def get_widget(self):
        return self._b
