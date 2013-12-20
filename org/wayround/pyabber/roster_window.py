
from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.pyabber.roster_widget
import org.wayround.pyabber.ccc


class RosterWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
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
        b.set_margin_left(5)
        b.set_margin_right(5)
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

        jid_widget = org.wayround.pyabber.jid_widget.JIDWidget(
            controller,
            controller.roster_storage,
            controller.jid.bare()
            )
        self._jid_widget = jid_widget

        server_jid_widget = org.wayround.pyabber.jid_widget.JIDWidget(
            controller,
            controller.roster_storage,
            controller.jid.domain
            )
        self._server_jid_widget = server_jid_widget

        roster_notebook = Gtk.Notebook()
        roster_notebook.set_tab_pos(Gtk.PositionType.LEFT)

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
            _rw = org.wayround.pyabber.roster_widget.\
                RosterWidget(
                    self._controller,
                    self._controller.roster_storage,
                    i[0]
                    )
            self._roster_widgets.append(_rw)

            _t = _rw.get_widget()
            _t.set_margin_left(5)
            _t.set_margin_right(5)
            _t.set_margin_top(5)
            _t.set_margin_bottom(5)
            _l = Gtk.Label(i[1])
#            _l.set_angle(90)

            roster_notebook.append_page(_t, _l)

        exp1 = Gtk.Expander()
        exp1.add(jid_widget.get_widget())
        exp1.set_label("Own JID")
        exp1.set_expanded(False)

        exp2 = Gtk.Expander()
        exp2.add(server_jid_widget.get_widget())
        exp2.set_label("Domain JID")
        exp2.set_expanded(False)

        b.pack_start(roster_tools_box, False, False, 0)
        b.pack_start(exp2, False, False, 0)
        b.pack_start(exp1, False, False, 0)
        b.pack_start(roster_notebook, True, True, 0)

        window = Gtk.Window()

        window.add(b)
        window.connect('destroy', self._on_destroy)

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
        self._jid_widget.destroy()
        self._server_jid_widget.destroy()
        for i in self._roster_widgets:
            i.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_get_roster_button_clicked(self, button):

        self._roster_storage.load_from_server(
            self._own_jid,
            self._roster_client, True, self._window
            )

        return

    def _on_add_contact_button_clicked(self, button):

        self._controller.show_contact_editor_window()

    def _on_initial_presence_button_clicked(self, button):
        self._presence_client.presence()

    def _on_change_presence_button_clicked(self, button):

        self._controller.show_presence_control_window()

    def _on_show_disco_button(self, button):
        self._controller.show_disco_window(self._own_jid.domain, None)

    def _on_send_space_button_clicked(self, button):
        self._client.io_machine.send(' ')
