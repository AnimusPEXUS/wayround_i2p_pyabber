
from gi.repository import Gtk
from gi.repository import Gdk

import org.wayround.xmpp.core
import org.wayround.pyabber.contact_editor
import org.wayround.pyabber.single_message_window
import org.wayround.pyabber.chat_pager

_contact_popup_menu = None

class ContactPopupMenu:

    def __init__(self):

        menu = Gtk.Menu()
        self.menu = menu
        self.jid = None

        subject_mi = Gtk.MenuItem.new_with_label("jid")
        jid_menu = Gtk.Menu()
        subject_mi.set_submenu(jid_menu)

        jid_copy_to_clipboard_mi = Gtk.MenuItem.new_with_label("Copy To Clipboard")
        jid_menu.append(jid_copy_to_clipboard_mi)
        self.subject_mi = subject_mi

        start_chat_mi = Gtk.MenuItem.new_with_label("Start Chat")
        send_message_mi = Gtk.MenuItem.new_with_label("Send Message")
        invite_to_muc_mi = Gtk.MenuItem.new_with_label("Invite to MUC")
        subscription_mi = Gtk.MenuItem.new_with_label("Subscription")
        remove_mi = Gtk.MenuItem.new_with_label("Remove From Roster")
        forget_mi = Gtk.MenuItem.new_with_label("Forget")

        commands_mi = Gtk.MenuItem.new_with_label("Commands")
        send_custom_presence_mi = Gtk.MenuItem.new_with_label("Send Custom Presence")
        vcard_mi = Gtk.MenuItem.new_with_label("vCard")
        send_users_mi = Gtk.MenuItem.new_with_label("Send Users")
        send_file_mi = Gtk.MenuItem.new_with_label("Send File")
        edit_mi = Gtk.MenuItem.new_with_label("Edit")

        menu.append(subject_mi)
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

        subscribe_mi.connect('activate', self._subs_activate, 'subscribe')
        unsubscribe_mi.connect('activate', self._subs_activate, 'unsubscribe')
        subscribed_mi.connect('activate', self._subs_activate, 'subscribed')
        unsubscribed_mi.connect('activate', self._subs_activate, 'unsubscribed')

        remove_mi.connect('activate', self._remove_activate)
        forget_mi.connect('activate', self._forget_activate)
        edit_mi.connect('activate', self._edit_activate)

        send_message_mi.connect('activate', self._send_message_activate)
        start_chat_mi.connect('activate', self._start_chat_activate)

        menu.connect('destroy', self._destroy)

    def show(self, controller, bare_or_full_jid, attach=None):

        self._controller = controller

        jid = org.wayround.xmpp.core.jid_from_str(bare_or_full_jid)
        self.jid = jid

        self.subject_mi.set_label(str(jid))

        while Gtk.events_pending():
            Gtk.main_iteration()

        if attach != None:
            self.menu.attach_to_widget(attach, None)

        self.menu.show_all()

        self.menu.popup(
            None,
            None,
            None,
            None,
            0,
            Gtk.get_current_event_time()
            )

        return

    def _subs_activate(self, menuitem, data):
        self._controller.presence.presence(
            typ=data,
            to_full_or_bare_jid=self.jid.bare()
            )

    def _remove_activate(self, menuitem):
        self._controller.roster.set(
            subscription='remove',
            jid_to=self._controller.jid.bare(),
            subject_jid=self.jid.bare()
            )

    def _forget_activate(self, menuitem):
        self._controller.main_window.roster_widget.forget(self.jid.bare())

    def _edit_activate(self, menuitem):
        w = org.wayround.pyabber.contact_editor.ContactEditor(
            self._controller,
            jid=self.jid.bare(),
            mode='edit'
            )
        w.show()

    def _send_message_activate(self, menuitem):
        org.wayround.pyabber.single_message_window.single_message(
            controller=self._controller,
            mode='new',
            to_jid=str(self.jid),
            from_jid=False,
            subject='HI!',
            body="How are You?"
            )

    def _start_chat_activate(self, menuitem):

        page = org.wayround.pyabber.chat_pager.Chat(
            self,
            controller=self._controller,
            contact_bare_jid=self.jid.bare(),
            contact_resource=None,  # TODO: really?
            thread_id=None
            )

        self._controller.main_window.chat_pager.add_page(page)


    def _destroy(self, *args):
        print("contact menu destroying")

def contact_popup_menu(controller, bare_or_full_jid, attach=None):

    global _contact_popup_menu

    if _contact_popup_menu == None:
        _contact_popup_menu = ContactPopupMenu()

    _contact_popup_menu.show(
        attach=attach,
        bare_or_full_jid=bare_or_full_jid,
        controller=controller
        )
