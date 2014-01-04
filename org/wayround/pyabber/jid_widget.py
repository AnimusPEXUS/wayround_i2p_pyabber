
from gi.repository import Gtk, Gdk

import org.wayround.pyabber.contact_popup_menu
import org.wayround.pyabber.icondb


class JIDWidget:

    def __init__(
        self,
        controller, roster_storage, bare_jid
        ):

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
        self._approved_label = Gtk.Label()

        self._subscription_i = Gtk.Image()

        self._available_i = Gtk.Image()

        self._show_i = Gtk.Image()

        status_box.pack_start(self._available_i, False, False, 0)
        status_box.pack_start(self._show_i, False, False, 0)
        status_box.pack_start(self._subscription_i, False, False, 0)
        status_box.pack_start(self._ask_label, False, False, 3)
        status_box.pack_start(self._approved_label, False, False, 3)

        self._title_label = Gtk.Label()
        self._title_label.set_alignment(0, 0.5)

        self._jid_label = Gtk.Label()
        self._jid_label.set_alignment(0, 0.5)

        self._status_text_label = Gtk.Label()
        self._status_text_label.set_alignment(0, 0)

        self._userpic_i = Gtk.Image()
        self._userpic_i.set_alignment(0.5, 0)
        self._userpic_i.set_margin_right(5)

        text_info_box.pack_start(self._title_label, False, False, 0)
        text_info_box.pack_start(self._jid_label, False, False, 0)
        text_info_box.pack_start(self._status_text_label, True, True, 0)
        text_info_box.pack_start(status_box, False, False, 0)

        main_horizontal_box.pack_start(self._userpic_i, False, False, 0)
        main_horizontal_box.pack_start(text_info_box, True, True, 0)

        main_box.pack_start(main_horizontal_box, True, True, 0)

        self._popu_menu = \
            org.wayround.pyabber.contact_popup_menu.ContactPopupMenu(
                controller
                )

        event_box = Gtk.EventBox()
        event_box.add(main_box)

        event_box.show_all()

        self._main_widget = event_box

        event_box.connect(
            'button-press-event',
            self._on_widget_right_button
            )

        self._roster_storage.connect_signal(
            True,
            self._roster_storage_listener
            )

        self.reload_data()

        return

    def _on_popup(self, box):

        self._popu_menu.show()

        return

    def reload_data(self):
        jid_data = self._roster_storage.get_jid_data(self._bare_jid)

        if jid_data != None:
            self._set_jid_data(jid_data)

        return

    def get_jid(self):
        return self._bare_jid

    def get_title(self):
        return self._title_label.get_text()

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
        self._ask_label.set_text("ask: " + str(value))

    def _set_approved(self, value):
        self._approved_label.set_text("approved: " + str(value))

    def _set_available(self, value):
        if value:
            self._available_i.set_from_pixbuf(
                org.wayround.pyabber.icondb.get('contact_available')
                )
        else:
            self._available_i.set_from_pixbuf(
                org.wayround.pyabber.icondb.get('contact_unavailable')
                )

    def _set_title_label(self, name, nick, bare_jid):
        title_label_text = ''
        if isinstance(name, str) and name != '' and not name.isspace():
            title_label_text = name
        elif isinstance(nick, str) and nick != '' and  not nick.isspace():
            title_label_text = nick
        else:
            title_label_text = bare_jid

        self._title_label.set_text(title_label_text)

    def _set_jid_label(self, bare_jid):
        l = bare_jid

        self._jid_label.set_text(l)

    def _set_status(self, value):
        if value == None:
            value = ''
        self._status_text_label.set_text(value)

    def _set_userpic_image(self, userpic):
        if not userpic:
            self._userpic_i.set_from_stock(
                'gtk-missing-image', Gtk.IconSize.BUTTON
                )
        else:
            self._userpic_i.set_from_pixbuf(userpic)

    def _set_show(self, value):
        if not value in [
                'available', 'unavailable', 'dnd', 'away', 'xa', 'chat'
                ]:
            value = 'unknown'

        self._show_i.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('show_{}'.format(value))
            )

        self._show_i.set_tooltip_text(value)

    def _set_subscription(self, value):
        if value == None:
            value = 'none'

        self._subscription_i.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('subscription_{}'.format(value))
            )

        self._subscription_i.set_tooltip_text(value)

    def destroy(self):
        self.get_widget().destroy()

    def _on_widget_right_button(self, widget, event):

        if event.button == Gdk.BUTTON_SECONDARY:

            l = self._bare_jid

            self._popu_menu.set(l)
            self._popu_menu.show()

        return


class MUCRosterJIDWidget:

    def __init__(self, room_bare_jid, nick, controller, muc_roster_storage):

        self._room_bare_jid = room_bare_jid
        self._controller = controller
        self._nick = nick
        self._muc_roster_storage = muc_roster_storage

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)

        user_pic = Gtk.Image()
        self._user_pic = user_pic

        b2 = Gtk.Box()
        b2.set_orientation(Gtk.Orientation.VERTICAL)

        title_label = Gtk.Label(nick)
        self._title_label = title_label

        b3 = Gtk.Box()
        b3.set_orientation(Gtk.Orientation.HORIZONTAL)

        b.pack_start(user_pic, False, False, 0)
        b.pack_start(b2, True, True, 0)

        status_label = Gtk.Label()
        self._status_label = status_label

        b2.pack_start(title_label, False, False, 0)
        b2.pack_start(b3, False, False, 0)
        b2.pack_start(status_label, True, True, 0)

        online_icon = Gtk.Image()
        self._online_icon = online_icon

        show_icon = Gtk.Image()
        self._show_icon = show_icon

        affiliation_icon = Gtk.Image()
        self._affiliation_icon = affiliation_icon

        role_icon = Gtk.Image()
        self._role_icon = role_icon

        b3.pack_start(affiliation_icon, False, False, 0)
        b3.pack_start(role_icon, False, False, 0)
        b3.pack_start(online_icon, False, False, 0)
        b3.pack_start(show_icon, False, False, 0)

        self._popu_menu = \
            org.wayround.pyabber.contact_popup_menu.ContactPopupMenu(
                controller
                )

        event_box = Gtk.EventBox()
        event_box.add(b)

        event_box.show_all()

        self._main_widget = event_box

        event_box.connect(
            'button-press-event',
            self._on_widget_right_button
            )

        muc_roster_storage.connect_signal(
            True,
            self._on_storage_actions
            )

        self.set_nick(nick)

        return

    def get_nick(self):
        return self._nick

    def set_nick(self, value):
        self._nick = value
        self.reload_data()

    def reload_data(self, item=None):

        if item == None:
            item = self._muc_roster_storage.get_item(self.get_nick())

        if item != None:

            if item.get_nick() == self.get_nick():
                self._set_available(item.get_available())
                self._set_show(item.get_show())
                self._status_label.set_text(item.get_status())

        return

    def _set_available(self, value):
        if value:
            self._online_icon.set_from_pixbuf(
                org.wayround.pyabber.icondb.get('contact_available')
                )
        else:
            self._online_icon.set_from_pixbuf(
                org.wayround.pyabber.icondb.get('contact_unavailable')
                )

    def _set_show(self, value):
        if not value in [
                'available', 'unavailable', 'dnd', 'away', 'xa', 'chat'
                ]:
            value = 'unknown'

        self._show_icon.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('show_{}'.format(value))
            )

        self._show_icon.set_tooltip_text(value)

    def get_widget(self):
        return self._main_widget

    def destroy(self):
        self.get_widget().destroy()

    def _on_storage_actions(self, event, storage, nick, item):
        if event == 'set':
            if nick == self.get_nick():
                self.reload_data(item)
        return

    def _on_widget_right_button(self, widget, event):

        if event.button == Gdk.BUTTON_SECONDARY:

            l = self._room_bare_jid + '/' + self._nick

            self._popu_menu.set(l)
            self._popu_menu.show()

        return


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

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        self._mrjw = MUCRosterJIDWidget(
            room_bare_jid,
            own_resource,
            controller,
            muc_roster_storage
            )
        self._title_label = Gtk.Label()

        b.pack_start(self._title_label, False, False, 0)
        b.pack_start(self._mrjw.get_widget(), False, False, 0)

        self.set_own_resource(own_resource)

        b.show_all()

        self._main_widget = b

        return

    def get_widget(self):
        return self._main_widget

    def destroy(self):
        self.get_widget().destroy()

    def set_own_resource(self, value):
        self._own_resource = value
        self._mrjw.set_nick(value)
        self._title_label.set_text('MUC: {}'.format(self._room_bare_jid))

    def get_own_resource(self):
        return self._own_resource
