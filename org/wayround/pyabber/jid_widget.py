
from gi.repository import Gtk, Gdk

import org.wayround.pyabber.contact_popup_menu
import org.wayround.pyabber.icondb


class JIDWidget:

    def __init__(self, controller, roster_storage, bare_jid):

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
            'button-release-event',
            self._on_widget_right_button
            )
#        self._userpic_i.connect('popup-menu', self._on_popup)

        self._roster_storage.connect_signal(
            True,
            self._roster_storage_set_bare_listener
            )

        jid_data = roster_storage.get_jid_data(bare_jid)

        if jid_data != None:
            self._set_jid_data(jid_data)

        return

    def _on_popup(self, box):

        self._popu_menu.show()

        return

    def get_jid(self):
        return self._bare_jid

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

    def _roster_storage_set_bare_listener(
        self,
        roster_storage, event, bare_jid, data, jid_data
        ):

        if bare_jid == self._bare_jid:
            self._set_jid_data(jid_data)

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
        self._jid_label.set_text(bare_jid)

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

    def _set_subscription(self, value):
        if value == None:
            value = 'none'

        self._subscription_i.set_from_pixbuf(
            org.wayround.pyabber.icondb.get('subscription_{}'.format(value))
            )

    def destroy(self):
        self.get_widget().destroy()

    def _on_widget_right_button(self, widget, event):

        if event.button == Gdk.BUTTON_SECONDARY:
#            bw = widget.get_bin_window()
#            if event.window == bw:
#                print("RMB _on_widget_right_button")
            self._popu_menu.set(self._bare_jid)
            self._popu_menu.show()

        return
