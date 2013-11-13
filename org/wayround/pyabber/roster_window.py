
import logging

from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.xmpp.client
import org.wayround.xmpp.core

import org.wayround.pyabber.contact_editor
import org.wayround.pyabber.disco
import org.wayround.pyabber.presence_control_popup
import org.wayround.pyabber.roster_widget


class RosterWindow:

    def __init__(
        self,
        client, own_jid,
        roster_client, presence_client,
        roster_storage
        ):

        if not isinstance(client, org.wayround.xmpp.client.XMPPC2SClient):
            raise ValueError(
                "`client' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        if not isinstance(own_jid, org.wayround.xmpp.core.JID):
            raise ValueError(
                "`own_jid' must be org.wayround.xmpp.core.JID"
                )

        if not isinstance(
            roster_client,
            org.wayround.xmpp.client.Roster
            ):
            raise ValueError(
                "`roster_client' must be org.wayround.xmpp.client.Roster"
                )

        if not isinstance(
            presence_client,
            org.wayround.xmpp.client.Presence
            ):
            raise ValueError(
                "`presence_client' must be org.wayround.xmpp.client.Presence"
                )

        if not isinstance(
            roster_storage,
            org.wayround.pyabber.roster_storage.RosterStorage
            ):
            raise ValueError(
                "`roster_storage' must be "
                "org.wayround.pyabber.roster_storage.RosterStorage"
                )


#        if not isinstance(
#            message_client,
#            org.wayround.xmpp.client.Message
#            ):
#            raise ValueError(
#                "`message_client' must be org.wayround.xmpp.client.Message"
#                )

        self._own_jid = own_jid
        self._client = client
        self._roster_client = roster_client
        self._presence_client = presence_client
        self._roster_storage = roster_storage
#        self._message_client = message_client

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_spacing(5)

        roster_tools_box = Gtk.Toolbar()
        roster_tools_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.roster_widget = org.wayround.pyabber.roster_widget.RosterWidget()

        roster_treeview_widg = self.roster_widget.get_widget()

        roster_toolbar_add_contact_button = Gtk.ToolButton()
        roster_toolbar_initial_presence_button = Gtk.ToolButton()
        roster_toolbar_change_presence_button = Gtk.ToolButton()
        roster_toolbar_get_roster_button = Gtk.ToolButton()
        roster_toolbar_show_disco_button = Gtk.ToolButton()
        roster_send_space_button = Gtk.ToolButton()

        add_contact_image = Gtk.Image()
        add_contact_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('plus')
            )

        initial_presence_image = Gtk.Image()
        initial_presence_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('initial_presence')
            )

        show_disco_image = Gtk.Image()
        show_disco_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('disco')
            )

        get_roster_image = Gtk.Image()
        get_roster_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('refresh_roster')
            )

        new_presence_image = Gtk.Image()
        new_presence_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('new_presence_button')
            )

        send_space_image = Gtk.Image()
        send_space_image.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('send_keepalive_space')
            )

        roster_toolbar_add_contact_button.set_icon_widget(add_contact_image)
        roster_toolbar_add_contact_button.connect(
            'clicked', self._on_add_contact_button_clicked
            )

        roster_toolbar_show_disco_button.set_icon_widget(show_disco_image)
        roster_toolbar_show_disco_button.connect(
            'clicked', self._on_show_disco_button
            )

        roster_toolbar_initial_presence_button.set_icon_widget(
            initial_presence_image
            )
        roster_toolbar_initial_presence_button.connect(
            'clicked', self._on_initial_presence_button_clicked
            )

        roster_toolbar_change_presence_button.set_icon_widget(
            new_presence_image
            )
        roster_toolbar_change_presence_button.connect(
            'clicked', self._on_change_presence_button_clicked
            )

        roster_toolbar_get_roster_button.set_icon_widget(get_roster_image)
        roster_toolbar_get_roster_button.connect(
            'clicked', self._on_get_roster_button_clicked
            )

        roster_send_space_button.set_icon_widget(send_space_image)
        roster_send_space_button.connect(
            'clicked', self._on_send_space_button_clicked
            )

        roster_tools_box.insert(roster_toolbar_initial_presence_button, -1)
        roster_tools_box.insert(roster_toolbar_get_roster_button, -1)
        roster_tools_box.insert(roster_send_space_button, -1)
        roster_tools_box.insert(roster_toolbar_change_presence_button, -1)
        roster_tools_box.insert(Gtk.SeparatorToolItem(), -1)
        roster_tools_box.insert(roster_toolbar_add_contact_button, -1)
        roster_tools_box.insert(Gtk.SeparatorToolItem(), -1)
        roster_tools_box.insert(roster_toolbar_show_disco_button, -1)

        b.pack_start(roster_tools_box, False, False, 0)
        b.pack_start(roster_treeview_widg, True, True, 0)

        window = Gtk.Window()

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self.roster_widget.set_self(self._own_jid.bare())
        self.roster_widget.set_storage_connection(self._roster_storage)

        self._window = window

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        return

    def run(self):
        self.show()
        self._iterated_loop.wait()
        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._iterated_loop.stop()
        self.roster_widget.destroy()

    def _on_destroy(self, window):
        self.destroy()

    def _on_get_roster_button_clicked(self, button):

        self._roster_storage.load_from_server(
            self._own_jid,
            self._roster_client, True, self._window
            )

        return

    def _on_add_contact_button_clicked(self, button):

        w = org.wayround.pyabber.contact_editor.ContactEditor(
            self.controller
            )
        w.show()

    def _on_initial_presence_button_clicked(self, button):
        self._presence_client.presence()

    def _on_change_presence_button_clicked(self, button):

        presence_control_popup_window = (
            org.wayround.pyabber.presence_control_popup.PresenceControlPopup(
                self._presence_client
                )
            )
        presence_control_popup_window.show()

    def _on_show_disco_button(self, button):
        org.wayround.pyabber.disco.disco(
            self._own_jid.domain, None, self._own_jid, self._client
            )

    def _on_send_space_button_clicked(self, button):
        self._client.io_machine.send(' ')
