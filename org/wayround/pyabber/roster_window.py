
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

    def __init__(self, client, own_jid):

        if not isinstance(client, org.wayround.xmpp.client.XMPPC2SClient):
            raise ValueError(
                "`client' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        if not isinstance(own_jid, org.wayround.xmpp.core.JID):
            raise ValueError(
                "`own_jid' must be org.wayround.xmpp.core.JID"
                )

        self._own_jid = own_jid
        self._client = client

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

        self.roster_widget.set_self(self._own_jid.bare())

        self._roster_client = org.wayround.xmpp.client.Roster(
            self._client,
            self._own_jid
            )

        self._presence_client = org.wayround.xmpp.client.Presence(
            self._client,
            self._own_jid
            )

        self._roster_client.connect_signal(
            ['push'],
            self._on_roster_push
            )

        self._presence_client.connect_signal(
            ['presence'],
            self._on_presence
            )

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
        self._destroy()

    def _on_roster_push(self, event, roster_obj, stanza_data):

        if event != 'push':
            pass
        else:

            jid = list(stanza_data.keys())[0]
            data = stanza_data[jid]

            not_in_roster = data.get_subscription() == 'remove'

            self.roster_widget.set_contact(
                name_or_title=data.get_name(),
                bare_jid=jid,
                groups=data.get_groups(),
                approved=data.get_approved(),
                ask=data.get_ask(),
                subscription=data.get_subscription(),
                not_in_roster=not_in_roster
                )

        return

    def _on_presence(self, event, presence_obj, from_jid, to_jid, stanza):

        if event == 'presence':

            if not stanza.get_typ() in [
                'unsubscribe', 'subscribed', 'unsubscribed'
                ]:

                f_jid = None

                if from_jid:
                    f_jid = org.wayround.xmpp.core.JID.new_from_str(from_jid)
                else:
                    f_jid = self.jid.copy()
                    f_jid.user = None

                not_in_roster = None
                if stanza.get_typ() == 'remove':
                    not_in_roster = True

                if (not f_jid.bare() in
                    self.roster_widget.get_data()):
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
                    self.roster_widget.set_contact_resource(
                        bare_jid=f_jid.bare(),
                        resource=f_jid.resource,
                        available=stanza.get_typ() != 'unavailable',
                        show=show,
                        status=status,
                        not_in_roster=not_in_roster
                        )
                elif f_jid.is_bare():
                    self.roster_widget.set_contact(
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

        return

    def _on_get_roster_button_clicked(self, button):

        res = self._roster_client.get(from_jid=self._own_jid.full())

        if res == None:
            d = org.wayround.utils.gtk.MessageDialog(
                self._window,
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
                d = org.wayround.utils.gtk.MessageDialog(
                    self._window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting roster:\n{}".format(repr(res.gen_error()))
                    )
                d.run()
                d.destroy()

            elif (isinstance(res, org.wayround.xmpp.core.Stanza)
                  and not res.is_error()):

                d = org.wayround.utils.gtk.MessageDialog(
                    self._window,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Unexpected return value:\n{}".format(res)
                    )
                d.run()
                d.destroy()

            elif isinstance(res, dict):
                conts = self.roster_widget.get_contacts()

                for i in res.keys():
                    self.roster_widget.set_contact(
                        name_or_title=res[i].get_name(),
                        bare_jid=i,
                        groups=res[i].get_group(),
                        approved=res[i].get_approved(),
                        ask=res[i].get_ask(),
                        subscription=res[i].get_subscription()
                        )

                for i in conts:
                    if not i in res:
                        self.roster_widget.set_contact(
                            bare_jid=i,
                            not_in_roster=True
                            )
            else:
                raise Exception("DNA error")

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
