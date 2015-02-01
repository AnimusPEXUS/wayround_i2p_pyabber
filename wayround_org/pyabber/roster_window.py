
from gi.repository import Gtk

import wayround_org.utils.gtk

import wayround_org.pyabber.roster_widget
import wayround_org.pyabber.ccc


class RosterWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller
        self._own_jid = self._controller.jid
        self._client = self._controller.client
        self._roster_client = self._controller.roster_client
        self._presence_client = self._controller.presence_client
        self._roster_storage = self._controller.roster_storage
#        self._message_client = message_client

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_spacing(5)

        roster_tools_box = Gtk.Toolbar()
        roster_tools_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        roster_toolbar_add_contact_button = Gtk.ToolButton()
        roster_toolbar_initial_presence_button = Gtk.ToolButton()
        roster_toolbar_change_presence_button = Gtk.ToolButton()
        roster_toolbar_get_roster_button = Gtk.ToolButton()
        roster_toolbar_show_disco_button = Gtk.ToolButton()
        roster_send_space_button = Gtk.ToolButton()

        add_contact_image = Gtk.Image()
        add_contact_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('plus')
            )

        initial_presence_image = Gtk.Image()
        initial_presence_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('initial_presence')
            )

        show_disco_image = Gtk.Image()
        show_disco_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('disco')
            )

        get_roster_image = Gtk.Image()
        get_roster_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('refresh_roster')
            )

        new_presence_image = Gtk.Image()
        new_presence_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('new_presence_button')
            )

        send_space_image = Gtk.Image()
        send_space_image.set_from_pixbuf(
            wayround_org.pyabber.icondb.get('send_keepalive_space')
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

        jid_widget = wayround_org.pyabber.jid_widget.JIDWidget(
            controller,
            controller.roster_storage,
            controller.jid.bare()
            )
        self._jid_widget = jid_widget

        server_jid_widget = wayround_org.pyabber.jid_widget.JIDWidget(
            controller,
            controller.roster_storage,
            controller.jid.domain
            )
        self._server_jid_widget = server_jid_widget

        roster_notebook = Gtk.Notebook()
        roster_notebook.set_scrollable(True)
        roster_notebook.set_tab_pos(Gtk.PositionType.RIGHT)

        self._roster_widgets = []

        for i in [
            ('grouped', "Grouped"),
            ('ungrouped', "Ungrouped"),
            ('services', 'Services'),
            ('all', "All"),
            ('ask', "Asking"),
            ('to', "Only To"),
            ('from', "Only From"),
            ('none', "None"),
            ('unknown', "Unknown")
            ]:
            _rw = wayround_org.pyabber.roster_widget.\
                RosterWidget(
                    self._controller,
                    self._controller.roster_storage,
                    i[0]
                    )
            self._roster_widgets.append(_rw)

            _t = _rw.get_widget()
            _t.set_margin_start(5)
            _t.set_margin_end(5)
            _t.set_margin_top(5)
            _t.set_margin_bottom(5)
            _l = Gtk.Label(i[1])

            roster_notebook.append_page(_t, _l)

        own_contacts_box = Gtk.Box()
        own_contacts_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        own_contacts_box.set_spacing(5)

        own_contacts_box_sep = Gtk.Separator()
        own_contacts_box_sep.set_orientation(Gtk.Orientation.VERTICAL)

        own_contacts_box.pack_start(jid_widget.get_widget(), True, True, 0)
        own_contacts_box.pack_start(own_contacts_box_sep, False, False, 0)
        own_contacts_box.pack_start(
            server_jid_widget.get_widget(), True, True, 0
            )

        b.pack_start(roster_tools_box, False, False, 0)
        b.pack_start(own_contacts_box, False, False, 0)
        b.pack_start(roster_notebook, True, True, 0)

        window = Gtk.Window()

        window.add(b)
        window.connect('destroy', self._on_destroy)
        window.connect(
            'delete-event', wayround_org.utils.gtk.hide_on_delete
            )

        self._window = window

        window.set_title(str(self._controller.jid.full()))
        
        self._controller.jid.signal.connect(
            'changed', 
            self._on_own_jid_changed
            )

        return

    def run(self):
        self.show()
        return

    def show(self):
        self._window.show_all()
        return

    def destroy(self):
        self._jid_widget.destroy()
        self._server_jid_widget.destroy()
        for i in self._roster_widgets[:]:
            i.destroy()
            self._roster_widgets.remove(i)

        self._window.destroy()
        return

    def _on_destroy(self, window):
        self.destroy()
        return

    def _on_get_roster_button_clicked(self, button):
        self._controller.load_roster_from_server(True, self._window)
        return

    def _on_add_contact_button_clicked(self, button):
        self._controller.show_contact_editor_window()
        return

    def _on_initial_presence_button_clicked(self, button):
        self._presence_client.presence()
        return

    def _on_change_presence_button_clicked(self, button):
        self._controller.show_presence_control_window()
        return

    def _on_show_disco_button(self, button):
        self._controller.show_disco_window(self._own_jid.domain, None)
        return

    def _on_send_space_button_clicked(self, button):
        self._client.io_machine.send(' ')
        return

    def _on_own_jid_changed(self, signal, jid_obj, old_value):
        rw = self._controller.jid
        if rw:
            self._window.set_title(rw.full())
        return
