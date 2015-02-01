
from gi.repository import Gdk
from gi.repository import Gtk

import wayround_org.pyabber.disco
import wayround_org.utils.gtk
import wayround_org.xmpp.core


class ContactPopupMenu:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        menu = Gtk.Menu()
        self._menu = menu
        self._jid = None

        subject_mi = Gtk.MenuItem.new_with_label("jid")
        jid_menu = Gtk.Menu()
        subject_mi.set_submenu(jid_menu)

        jid_copy_to_clipboard_mi = Gtk.MenuItem.new_with_label(
            "Copy to Clipboard"
            )
        jid_menu.append(jid_copy_to_clipboard_mi)
        self.subject_mi = subject_mi

        jid_copy_to_clipboard_mi.connect(
            'activate', self._on_jid_copy_to_clipboard_mi
            )

        start_chat_mi = Gtk.MenuItem.new_with_label("Start Chat")
        send_message_mi = Gtk.MenuItem.new_with_label("Send Message..")
        invite_to_muc_mi = Gtk.MenuItem.new_with_label("Invite to MUC..")
        subscription_mi = Gtk.MenuItem.new_with_label("Subscription")
        remove_mi = Gtk.MenuItem.new_with_label("Remove From Roster")
        forget_mi = Gtk.MenuItem.new_with_label("Forget")

        commands_mi = Gtk.MenuItem.new_with_label("Commands")
        send_custom_presence_mi = Gtk.MenuItem.new_with_label(
            "Send Custom Presence.."
            )
        vcard_mi = Gtk.MenuItem.new_with_label("vCard")
        send_users_mi = Gtk.MenuItem.new_with_label("Send Users")
        send_file_mi = Gtk.MenuItem.new_with_label("Send File")
        edit_mi = Gtk.MenuItem.new_with_label("Edit")

        disco_mi = Gtk.MenuItem.new_with_label("Disco")

        misco_menu = wayround_org.pyabber.disco.DiscoMenu(controller)
        self._disco_menu = misco_menu

        disco_mi.set_submenu(misco_menu.get_widget())

        menu.append(subject_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(disco_mi)
        menu.append(Gtk.SeparatorMenuItem())

        menu.append(start_chat_mi)
        menu.append(send_message_mi)
        menu.append(invite_to_muc_mi)

        menu.append(Gtk.SeparatorMenuItem())
        menu.append(subscription_mi)
        menu.append(remove_mi)
        menu.append(forget_mi)

        menu.append(Gtk.SeparatorMenuItem())
        menu.append(commands_mi)
        menu.append(send_custom_presence_mi)
        menu.append(vcard_mi)

        menu.append(Gtk.SeparatorMenuItem())
        menu.append(send_users_mi)
        menu.append(send_file_mi)
        menu.append(edit_mi)

        subs_sub_menu = Gtk.Menu()
        subscription_mi.set_submenu(subs_sub_menu)

        subscribe_mi = Gtk.MenuItem.new_with_label(
            "Subscribe (ask to track contact activity)"
            )
        unsubscribe_mi = Gtk.MenuItem.new_with_label(
            "UnSubscribe (stop tracking contact activity)"
            )
        subscribed_mi = Gtk.MenuItem.new_with_label(
            "Subscribed (allow contact to track your activity)"
            )
        unsubscribed_mi = Gtk.MenuItem.new_with_label(
            "UnSubscribed (disallow contact to track your activity)"
            )

        subs_sub_menu.append(subscribe_mi)
        subs_sub_menu.append(unsubscribe_mi)
        subs_sub_menu.append(Gtk.SeparatorMenuItem())
        subs_sub_menu.append(subscribed_mi)
        subs_sub_menu.append(unsubscribed_mi)

        subscribe_mi.connect(
            'activate', self._subs_activate, 'subscribe'
            )
        unsubscribe_mi.connect(
            'activate', self._subs_activate, 'unsubscribe'
            )
        subscribed_mi.connect(
            'activate', self._subs_activate, 'subscribed'
            )
        unsubscribed_mi.connect(
            'activate', self._subs_activate, 'unsubscribed'
            )

        remove_mi.connect('activate', self._remove_activate)
        forget_mi.connect('activate', self._forget_activate)
        edit_mi.connect('activate', self._edit_activate)

        send_message_mi.connect('activate', self._send_message_activate)

        start_chat_mi.connect('activate', self._start_chat_activate)

        send_custom_presence_mi.connect(
            'activate',
            self._send_custom_presence_activate
            )

        vcard_mi.connect(
            'activate',
            self._vcard_activate
            )

        self._menu.show_all()

        return

    def destroy(self):
        self._disco_menu.destroy()
        self._menu.destroy()
        return

    def set(self, bare_or_full_jid):

        self._disco_menu.set(bare_or_full_jid, node=None)

        jid = wayround_org.xmpp.core.JID.new_from_str(bare_or_full_jid)
        self._jid = jid

        self.subject_mi.set_label(str(jid))

        return

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

    def get_widget(self):
        return self._menu

    def _subs_activate(self, menuitem, data):
        self._controller.presence_client.presence(
            typ=data,
            to_full_or_bare_jid=self._jid.bare()
            )
        return

    def _remove_activate(self, menuitem):
        self._controller.roster_client.set(
            self._jid.bare(),
            subscription='remove',
            to_jid=self._controller.jid.bare(),
            )
        return

    def _forget_activate(self, menuitem):
        self._controller.roster_storage.forget(self._jid.bare())
        return

    def _edit_activate(self, menuitem):
        self._controller.show_contact_editor_window(
            jid=self._jid.bare(),
            mode='edit'
            )
        return

    def _send_message_activate(self, menuitem):

        stanza = wayround_org.xmpp.core.Stanza(tag='message')
        stanza.set_to_jid(str(self._jid))
        stanza.set_from_jid(self._controller.jid.bare())
        stanza.set_subject(
            [wayround_org.xmpp.core.MessageSubject("HI!")]
            )

        stanza.set_body(
            [wayround_org.xmpp.core.MessageBody("How are You?")]
            )

        self._controller.show_single_message_window(
            mode='new',
            stanza=stanza
            )

        return

    def _start_chat_activate(self, menuitem):

        chat_window = self._controller.get_chat_window()
        if chat_window == None:
            self._controller.show_chat_window()
            chat_window = self._controller.get_chat_window()

        chat_window.show()
        chat_window.chat_pager.add_chat(self._jid, None)

        return

    def _send_custom_presence_activate(self, mi):
        self._controller.show_presence_control_window(to_=str(self._jid))
        return

    def _vcard_activate(self, mi):
        self._controller.show_xcard_window('')
        return

    def _on_jid_copy_to_clipboard_mi(self, mi):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(str(self._jid), -1)
        return
