
import threading

from gi.repository import Gtk, Gdk, Pango

import wayround_org.pyabber.ccc
import wayround_org.pyabber.contact_popup_menu
import wayround_org.pyabber.icondb
import wayround_org.pyabber.roster_storage
import wayround_org.utils.gtk


class JIDWidget:

    def __init__(
            self,
            controller, roster_storage, bare_jid
            ):

        if not isinstance(
                controller,
                wayround_org.pyabber.ccc.ClientConnectionController
                ):
            raise ValueError(
                "`controller' must be "
                "wayround_org.pyabber.ccc.ClientConnectionController"
                )

        if not isinstance(
                roster_storage,
                wayround_org.pyabber.roster_storage.RosterStorage
                ):
            raise ValueError(
                "`roster_storage' must be "
                "wayround_org.pyabber.roster_storage.RosterStorage"
                )

        if not isinstance(bare_jid, str):
            raise ValueError("`bare_jid' must be str")

        self._controller = controller
        self._roster_storage = roster_storage
        self._bare_jid = bare_jid

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)

        main_horizontal_box = Gtk.Box()
        main_horizontal_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        text_info_box = Gtk.Box()
        text_info_box.set_orientation(Gtk.Orientation.VERTICAL)

        status_box = Gtk.Box()
        status_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        self._ask_label = Gtk.Label()
        self._ask_label.set_tooltip_text("Askings")

        self._approved_label = Gtk.Label()
        self._approved_label.set_tooltip_text("Approvements")

        self._subscription_i = Gtk.Image()

        self._available_i = Gtk.Image()

        self._show_i = Gtk.Image()

        status_box.pack_start(self._available_i, False, False, 0)
        status_box.pack_start(self._show_i, False, False, 0)
        status_box.pack_start(self._subscription_i, False, False, 0)
        status_box.pack_start(self._ask_label, False, False, 3)
        status_box.pack_start(self._approved_label, False, False, 3)

        self._title_button = Gtk.Button()

        self._jid_label = Gtk.Label()
        self._jid_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self._jid_label.set_alignment(0, 0.5)

        self._status_text_label = Gtk.Label()
        self._status_text_label.set_ellipsize(Pango.EllipsizeMode.END)
        self._status_text_label.set_alignment(0, 0)
        self._status_text_label.set_no_show_all(True)
        self._status_text_label.hide()

        self._userpic_i = Gtk.Image()
        self._userpic_i.set_alignment(0.5, 0)
        self._userpic_i.set_margin_right(5)

        text_info_box.pack_start(self._title_button, False, False, 0)
        text_info_box.pack_start(self._jid_label, False, False, 0)
        text_info_box.pack_start(self._status_text_label, True, True, 0)
        text_info_box.pack_start(status_box, False, False, 0)

        main_horizontal_box.pack_start(self._userpic_i, False, False, 0)
        main_horizontal_box.pack_start(text_info_box, True, True, 0)

        main_box.pack_start(main_horizontal_box, True, True, 0)

        self._menu = \
            wayround_org.pyabber.contact_popup_menu.ContactPopupMenu(
                controller
                )

        self._main_widget = main_box

        self._title_button.connect('clicked', self._on_title_button_clicked)

        self._roster_storage_listener_idle = \
            wayround_org.utils.gtk.to_idle(self._roster_storage_listener)

        self._roster_storage.signal.connect(
            True,
            self._roster_storage_listener_idle
            )

        self.reload_data()

        self.get_widget().show_all()

        return

    def reload_data(self):
        jid_data = self._roster_storage.get_jid_data(self._bare_jid)

        if jid_data is not None:
            self._set_jid_data(jid_data)

        return

    def get_jid(self):
        return self._bare_jid

    def get_title(self):
        return self._title_button.get_label()

    def _set_jid_data(self, jid_data):

        self._set_ask(jid_data['bare']['ask'])
        self._set_approved(jid_data['bare']['approved'])
        self._set_available(jid_data['bare']['available'])
        self._set_jid_label(self._bare_jid)
        self._set_show(jid_data['bare']['show'])
        self._set_status(jid_data['bare']['status'])
        self._set_subscription(jid_data['bare']['subscription'])
        self._set_title_label(
            jid_data['bare']['name_or_title'],
            None,
            self._bare_jid
            )
        self._set_userpic_image(None)

    def _roster_storage_listener(
            self,
            roster_storage, event, bare_jid, resource, data, jid_data
            ):

        if bare_jid == self._bare_jid:
            self._set_jid_data(jid_data)

        return

    def get_widget(self):
        return self._main_widget

    def _set_ask(self, value):
        self._ask_label.set_text(str(value))
        return

    def _set_approved(self, value):
        self._approved_label.set_text(str(value))
        return

    def _set_available(self, value):
        if value:
            self._available_i.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('contact_available')
                )
            self._available_i.set_tooltip_text('Available')
        else:
            self._available_i.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('contact_unavailable')
                )
            self._available_i.set_tooltip_text('Unavailable')

    def _set_title_label(self, name, nick, bare_jid):
        title_label_text = ''
        if isinstance(name, str) and name != '' and not name.isspace():
            title_label_text = name
        elif isinstance(nick, str) and nick != '' and not nick.isspace():
            title_label_text = nick
        else:
            title_label_text = bare_jid

        self._title_button.set_label(title_label_text)
        self._title_button.set_tooltip_text(title_label_text)
        return

    def _set_jid_label(self, bare_jid):
        l = bare_jid
        self._jid_label.set_text(l)
        return

    def _set_status(self, value):
        if value is None:
            value = ''
        self._status_text_label.set_text(value)
        self._status_text_label.set_tooltip_text(value)
        self._status_text_label.set_visible(value != '')
        return

    def _set_userpic_image(self, userpic):
        if not userpic:
            self._userpic_i.set_from_stock(
                'gtk-missing-image', Gtk.IconSize.BUTTON
                )
        else:
            self._userpic_i.set_from_pixbuf(userpic)
        return

    def _set_show(self, value):
        if not value in [
                'available', 'unavailable', 'dnd', 'away', 'xa', 'chat'
                ]:
            value = 'unknown'

        self._show_i.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('show_{}_10x10'.format(value))
            )

        self._show_i.set_tooltip_text(value)
        return

    def _set_subscription(self, value):
        if value is None:
            value = 'none'

        self._subscription_i.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('subscription_{}'.format(value))
            )

        self._subscription_i.set_tooltip_text(value)
        return

    def destroy(self):
        self._roster_storage.signal.disconnect(
            self._roster_storage_listener_idle
            )
        self._menu.destroy()
        self.get_widget().destroy()

    def _on_title_button_clicked(self, widget):

        l = self._bare_jid

        self._menu.set(l)
        self._menu.show()

        return


class MUCRosterJIDWidgetMenu:

    def __init__(self, controller, muc_roster_storage):

        if not isinstance(
                controller,
                wayround_org.pyabber.ccc.ClientConnectionController
                ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller
        self._muc_roster_storage = muc_roster_storage
        self._bare_or_full_jid = None

        menu = Gtk.Menu()
        self._menu = menu

        contact_submenu_mi = Gtk.MenuItem("MUC Roster Contact Menu")

        edit_entity_mi = Gtk.MenuItem("Full Entity Editor..")
        self._on_edit_entity_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_edit_entity_activated)
        edit_entity_mi.connect('activate', self._on_edit_entity_activated_idle)

        mini_edit_entity_mi = Gtk.MenuItem("Mini Entity Editor..")
        self._on_mini_edit_entity_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_mini_edit_entity_activated)
        mini_edit_entity_mi.connect(
            'activate', self._on_mini_edit_entity_activated_idle
            )

        open_private_mi = Gtk.MenuItem("Open Private Chat")
        open_private_mi.connect('activate', self._on_open_private_activated)

        menu.append(open_private_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(contact_submenu_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(edit_entity_mi)
        menu.append(mini_edit_entity_mi)

        menu.show_all()

        self._contact_menu = \
            wayround_org.pyabber.contact_popup_menu.ContactPopupMenu(
                controller
                )

        contact_submenu_mi.set_submenu(self._contact_menu.get_widget())

        return

    def destroy(self):
        self._contact_menu.destroy()
        self._menu.destroy()

    def set(self, bare_or_full_jid):

        self._bare_or_full_jid = bare_or_full_jid

        self._contact_menu.set(bare_or_full_jid)

    def show(self):

        self._menu.popup(
            None,
            None,
            None,
            None,
            0,
            Gtk.get_current_event_time()
            )

        return

    def _on_edit_entity_activated(self, mi):

        jid = wayround_org.xmpp.core.JID.new_from_str(
            self._bare_or_full_jid
            )

        self._controller.show_muc_identity_editor_window(
            target_jid=jid.bare(),
            editing_preset=self._muc_roster_storage.get_item(jid.resource)
            )
        return

    def _on_open_private_activated(self, mi):

        cw = self._controller.get_chat_window()
        cw.chat_pager.add_private(self._bare_or_full_jid)

        return

    def _on_mini_edit_entity_activated(self, mi):
        room_resource_jid = wayround_org.xmpp.core.JID.new_from_str(
            self._bare_or_full_jid
            )

        storage_item = self._muc_roster_storage.get_item(
            room_resource_jid.resource
            )

        room_resource_jid_true_jid = storage_item.get_jid()

        target_jid = None
        if room_resource_jid_true_jid is not None:
            target_jid = wayround_org.xmpp.core.JID.new_from_str(
                room_resource_jid_true_jid
                ).bare()

        self._controller.show_muc_mini_identity_editor_window(
            room_jid=room_resource_jid.bare(),
            target_jid=target_jid,
            editing_preset=storage_item
            )
        return


class MUCRosterJIDWidget:

    def __init__(self, room_bare_jid, nick, controller, muc_roster_storage):

        self._lock = threading.RLock()

        with self._lock:

            self._room_bare_jid = room_bare_jid
            self._controller = controller
            self._nick = nick
            self._muc_roster_storage = muc_roster_storage

            b = Gtk.Box()
            b.set_orientation(Gtk.Orientation.HORIZONTAL)

            user_pic = Gtk.Image()
            self._user_pic = user_pic

            title_label = Gtk.Label()
            self._title_label = title_label
            title_label.set_ellipsize(Pango.EllipsizeMode.END)
            title_label.set_size_request(50, -1)
            title_label.set_alignment(0.0, 0.0)

            b3 = Gtk.Box()
            b3.set_orientation(Gtk.Orientation.HORIZONTAL)
            b3.set_spacing(5)

            event_box2 = Gtk.EventBox()

            jid_label = Gtk.Label()
            jid_label.set_alignment(0.0, 0.0)
            jid_label.set_ellipsize(Pango.EllipsizeMode.END)
            jid_label.set_no_show_all(True)
            self._jid_label = jid_label

            event_box2.add(jid_label)

            online_icon = Gtk.Image()
            self._online_icon = online_icon

            show_icon = Gtk.Image()
            self._show_icon = show_icon

            affiliation_icon = Gtk.Image()
            self._affiliation_icon = affiliation_icon

            role_icon = Gtk.Image()
            self._role_icon = role_icon

            b4 = Gtk.Box()
            b4.set_orientation(Gtk.Orientation.VERTICAL)

            icon_grid = Gtk.Grid()
            icon_grid.attach(online_icon, 0, 0, 1, 1)
            icon_grid.attach(show_icon, 1, 0, 1, 1)
            icon_grid.attach(affiliation_icon, 0, 1, 1, 1)
            icon_grid.attach(role_icon, 1, 1, 1, 1)

            b4.pack_start(title_label, True, True, 0)
            b4.pack_start(event_box2, False, False, 0)

            b3.pack_start(user_pic, False, False, 0)
            b3.pack_start(icon_grid, False, False, 0)
            b3.pack_start(b4, False, False, 0)

            self._menu = \
                MUCRosterJIDWidgetMenu(
                    controller,
                    muc_roster_storage
                    )

            self._jid_menu = \
                wayround_org.pyabber.contact_popup_menu.ContactPopupMenu(
                    controller
                    )

            event_box = Gtk.EventBox()
            event_box.add(b3)

            event_box.show_all()

            self._main_widget = event_box

            self.set_nick(nick)

            event_box.connect(
                'button-press-event',
                self._on_widget_right_button
                )

            event_box2.connect(
                'button-press-event',
                self._on_jid_right_button
                )

            self._on_storage_actions_idle = \
                wayround_org.utils.gtk.to_idle(self._on_storage_actions)

            muc_roster_storage.signal.connect(
                'set',
                self._on_storage_actions_idle
                )

            self._on_storage_rename_idle = \
                wayround_org.utils.gtk.to_idle(self._on_storage_rename)

            muc_roster_storage.signal.connect(
                'rename',
                self._on_storage_rename_idle
                )

        return

    def get_nick(self):
        with self._lock:
            ret = self._nick
        return ret

    def set_nick(self, value):
        with self._lock:
            self._nick = value
            self.reload_data()
        return

    def reload_data(self, item=None):

        with self._lock:

            if item is None:
                item = self._muc_roster_storage.get_item(self.get_nick())

            self._user_pic.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('q_10x10')
                )
            self._affiliation_icon.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('q_10x10')
                )
            self._role_icon.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('q_10x10')
                )

            if item is not None:

                if item.get_nick() == self.get_nick():
                    self._set_title(self.get_nick())
                    self._set_available(item.get_available())
                    self._set_show(item.get_show())
                    self._set_affiliation(item.get_affiliation())
                    self._set_role(item.get_role())
                    self._set_jid(item.get_jid())
                    self._main_widget.set_tooltip_text(
                        """Status text: {}""".format(item.get_status())
                        )

            else:
                self._set_available(False)
                self._set_show('unknown')
                self._main_widget.set_tooltip_text("No status")

        return

    def _set_title(self, value):
        if value is None:
            value = ''
        self._title_label.set_text(value)
        self._title_label.set_tooltip_text(value)

    def _set_jid(self, value):

        if value is None:
            self._jid_label.set_text('')
            self._jid_label.hide()
        else:
            self._jid_label.set_text(value)
            self._jid_label.set_tooltip_text(value)
            self._jid_label.show()
            self._jid_menu.set(value)

        return

    def _set_available(self, value):

        if value:
            self._online_icon.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('contact_available')
                )
            self._online_icon.set_tooltip_text('Available')
        else:
            self._online_icon.set_from_pixbuf(
                wayround_org.pyabber.icondb.get('contact_unavailable')
                )
            self._online_icon.set_tooltip_text('Unavailable')

        return

    def _set_show(self, value):

        if not value in [
                'available', 'unavailable', 'dnd', 'away', 'xa', 'chat'
                ]:
            value = 'unknown'

        self._show_icon.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('show_{}_10x10'.format(value))
            )

        self._show_icon.set_tooltip_text("Show: {}".format(value))

        return

    def _set_affiliation(self, value):

        if value is None:
            value = 'unknown'

        self._affiliation_icon.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('aff_{}_10x10'.format(value))
            )

        self._affiliation_icon.set_tooltip_text(
            "Affiliation: {}".format(value)
            )

        return

    def _set_role(self, value):

        if value is None:
            value = 'unknown'

        self._role_icon.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('role_{}_10x10'.format(value))
            )

        self._role_icon.set_tooltip_text("Role: {}".format(value))

        return

    def get_widget(self):
        return self._main_widget

    def destroy(self):
        self._muc_roster_storage.signal.disconnect(
            self._on_storage_actions_idle
            )
        self._menu.destroy()
        self._jid_menu.destroy()
        self.get_widget().destroy()

        return

    def _on_storage_actions(self, event, storage, nick, item):
        with self._lock:
            if event == 'set':
                if nick == self.get_nick():
                    self.reload_data(item)
        return

    def _on_storage_rename(self, event, storage, nick, new_nick):
        with self._lock:
            if event == 'rename':
                if self.get_nick() is not None:
                    if nick == self.get_nick():
                        if new_nick is not None:
                            self.set_nick(new_nick)
        return

    def _on_jid_right_button(self, widget, event):

        ret = None

        if event.button == Gdk.BUTTON_SECONDARY:

            self._jid_menu.show()

            ret = True

        return ret

    def _on_widget_right_button(self, widget, event):

        ret = None

        if event.button == Gdk.BUTTON_SECONDARY:

            l = '{}/{}'.format(self._room_bare_jid, self._nick)

            self._menu.set(l)
            self._menu.show()

            ret = True

        return ret


class GroupChatTabWidget:

    def __init__(
            self,
            room_bare_jid, own_resource, controller, muc_roster_storage,
            presence_client, stanza_processor
            ):

        self._controller = controller
        self._room_bare_jid = room_bare_jid
        self._own_resource = None
        self._muc_roster_storage = muc_roster_storage
        self._presence_client = presence_client
        self._stanza_processor = stanza_processor

        self._lock = threading.RLock()

        with self._lock:

            b = Gtk.Box()
            b.set_orientation(Gtk.Orientation.VERTICAL)

            self._mrjw = MUCRosterJIDWidget(
                room_bare_jid,
                own_resource,
                controller,
                muc_roster_storage
                )
            self._title_label = Gtk.Label()
            self._title_label.set_ellipsize(Pango.EllipsizeMode.END)
            self._title_label.set_size_request(50, -1)
            self._title_label.set_alignment(0.0, 0.0)

            b.pack_start(self._title_label, False, False, 0)
            b.pack_start(self._mrjw.get_widget(), False, False, 0)

            self._menu = \
                wayround_org.pyabber.muc.MUCPopupMenu(
                    controller
                    )

            event_box = Gtk.EventBox()
            event_box.add(b)

            event_box.show_all()

            self._main_widget = event_box

            self.set_own_resource(own_resource)

            event_box.connect(
                'button-press-event',
                self._on_widget_right_button
                )

        return

    def get_widget(self):
        with self._lock:
            ret = self._main_widget
        return ret

    def destroy(self):
        self._mrjw.destroy()
        self._menu.destroy()
        self._title_label.destroy()
        self.get_widget().destroy()
        return

    def set_own_resource(self, value):
        with self._lock:
            self._own_resource = value
            self._mrjw.set_nick(value)
            self._menu.set(self._room_bare_jid)
            t = 'MUC: {}/{}'.format(
                self._room_bare_jid,
                self._own_resource
                )
            self._title_label.set_text(t)
            self._title_label.set_tooltip_text(t)
        return

    def get_own_resource(self):
        with self._lock:
            ret = self._own_resource
        return ret

    def _on_widget_right_button(self, widget, event):
        with self._lock:

            if event.button == Gdk.BUTTON_SECONDARY:

                self._menu.set(self._room_bare_jid)
                self._menu.show()

        return
