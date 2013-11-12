
raise Exception("Deprecated")

import os.path
import glob
import sys
import threading
import pprint
import logging

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango

import org.wayround.utils.path
import org.wayround.utils.crypto
import org.wayround.utils.error
import org.wayround.utils.gtk

import org.wayround.pyabber.profile_window
import org.wayround.pyabber.connection_window
import org.wayround.pyabber.controller
import org.wayround.pyabber.roster_widget
import org.wayround.pyabber.presence_control_popup
import org.wayround.pyabber.icondb
import org.wayround.pyabber.contact_editor
import org.wayround.pyabber.chat_pager
import org.wayround.pyabber.disco


class Dumb:
    pass


class MainWindow:

    def __init__(self, pyabber_config='~/.config/pyabber'):

        self.controller = org.wayround.pyabber.controller.MainController(self)

        self.iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        pyabber_config = os.path.expanduser(pyabber_config)

        profiles_path = '{pyabber_config}/profiles'.format(
            pyabber_config=pyabber_config
            )

        self.profiles_path = profiles_path

        if not os.path.isdir(self.profiles_path):
            os.makedirs(self.profiles_path)

        self.window_elements = Dumb()

        org.wayround.pyabber.icondb.set_dir(
            org.wayround.utils.path.join(
                os.path.dirname(org.wayround.utils.path.abspath(__file__)),
                'icons'
                )
            )

        self.window_elements.window = Gtk.Window()

        window = self.window_elements.window

        window.set_icon(org.wayround.pyabber.icondb.get('pyabber'))
        window.set_title("Pyabber :P")
        window.maximize()
        window.set_hide_titlebar_when_maximized(True)

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)

        main_notebook = Gtk.Notebook()
        main_notebook.set_property('tab-pos', Gtk.PositionType.TOP)

        xmpp_core_box = Gtk.Box()
        xmpp_core_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        xmpp_core_box.pack_start(Gtk.Label("Text"), True, True, 0)

        _l = Gtk.Label("Program")
        _b = Gtk.Button("Exit")
        _b.connect('clicked', self.app_exit)
        _b.set_relief(Gtk.ReliefStyle.NONE)
        main_notebook.append_page(_b, _l)

        _l = Gtk.Label("Connection")
        connection_tab = self._build_connection_tab()
        main_notebook.append_page(connection_tab, _l)

        _l = Gtk.Label("Stream Features")
        stream_features_tab = self._build_stream_features_tab()
        stream_features_tab.set_sensitive(False)
        main_notebook.append_page(stream_features_tab, _l)

        _l = Gtk.Label("Messaging and Presence")
        messaging_and_presence_tab = self._build_messaging_and_presence()
        main_notebook.append_page(messaging_and_presence_tab, _l)

        _l = Gtk.Label("Status")
        status_tab = self._build_status_tab()
        main_notebook.append_page(status_tab, _l)

        main_box.pack_start(main_notebook, True, True, 0)

        main_notebook.connect('switch-page', self.main_notebook_switch_page)

        window.add(main_box)

        self.profile_name = None
        self.profile_data = None
        self.profile_password = None
        self.preset_name = None
        self.preset_data = None

        self.client_working = False

        self.window_elements.window = window
        self.window_elements.connection_tab = connection_tab
        self.window_elements.stream_features_tab = stream_features_tab
        self.window_elements.main_notebook = main_notebook

        return

    def run(self):

        self.window_elements.window.show_all()

        self.window_elements.main_notebook.set_current_page(
            self.window_elements.main_notebook.page_num(
                self.window_elements.profile_tab
                )
            )

        self.iteration_loop.wait()

        return 0

    def _build_profile_tab(self):
        pass

    def _build_connection_tab(self):
        pass

    def _build_stream_features_tab(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        featuress_grid_ff = Gtk.Frame()
        featuress_grid_ff.set_label("Proposed Stream Features")
        featuress_grid = Gtk.Grid()
        featuress_grid_ff.add(featuress_grid)

        featuress_grid.set_margin_top(5)
        featuress_grid.set_margin_bottom(5)
        featuress_grid.set_margin_left(5)
        featuress_grid.set_margin_right(5)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        activate_button = Gtk.Button('Activate')

        bb.pack_start(activate_button, True, True, 0)

        b.pack_start(featuress_grid_ff, True, True, 0)
        b.pack_start(bb, False, True, 0)

        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        return b

    def _build_messaging_and_presence(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        b2 = Gtk.Box()
        b2.set_orientation(Gtk.Orientation.HORIZONTAL)

        roster_box = Gtk.Box()
        roster_box.set_orientation(Gtk.Orientation.VERTICAL)

        roster_tools_box = Gtk.Toolbar()
        roster_tools_box.set_orientation(Gtk.Orientation.VERTICAL)

        self.roster_widget = org.wayround.pyabber.roster_widget.RosterWidget(
            main_window=self
            )

        roster_treeview_widg = self.roster_widget.get_widget()

        roster_box.pack_start(roster_treeview_widg, True, True, 0)

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

        main_paned = Gtk.Paned()
        main_paned.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.chat_pager = org.wayround.pyabber.chat_pager.ChatPager(
            self.controller
            )

        chat_pager_widget = self.chat_pager.get_widget()

        main_paned.pack1(roster_box, False, True)
        main_paned.pack2(chat_pager_widget, True, False)

        b2.pack_start(roster_tools_box, False, False, 0)
        b2.pack_start(main_paned, True, True, 0)

        b.pack_start(b2, True, True, 0)

        return b

    def _build_status_tab(self):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        return b

    def app_exit(self, user_data):
        self.iteration_loop.stop()

    def main_notebook_switch_page(self, notebook, page, pagenum):

        if page == self.window_elements.profile_tab:
            self.profile_tab_refresh_list()
            self.display_open_profile_info()

        elif page == self.window_elements.connection_tab:
            self._reload_list()
            self.window_elements.connection_tab_box.set_sensitive(
                isinstance(self.profile_data, dict)
                )
            self._reload_list()

    def connect(self, name, data):

        if not self.client_working:

            self.client_working = True
            self.preset_name = name
            self.preset_data = data

#            self.controller.start(
#                self,
#                self.profile_name,
#                self.profile_password,
#                self.profile_data,
#                self.preset_name,
#                self.preset_data
#                )

            threading.Thread(
                name="Chat Controller Thread",
                target=self.controller.start,
                args=(
                    self.profile_name,
                    self.profile_password,
                    self.profile_data,
                    self.preset_name,
                    self.preset_data,
                    )
                ).start()

    def disconnect(self):

        self.preset_name = None
        self.preset_data = None
        if self.client_working:

            if self.controller:
                self.controller.stop()

            self.controller = None

    def display_open_profile_info(self):

        if (not hasattr(self, 'profile_name')
            or not isinstance(self.profile_data, dict)):

            self.window_elements.profile_info_label.set_text(
                "Profile not activated"
                )

        else:
            self.window_elements.profile_info_label.set_text(
                "Active profile is `{}'".format(self.profile_name)
                )

    def _on_get_roster_button_clicked(self, button):

        res = self.controller.roster.get(from_jid=self.controller.jid.full())
        logging.debug("Roster Get Result: {}".format(pprint.pformat(res)))

        if res == None:
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.window,
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
                    self.window_elements.window,
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
                    self.window_elements.window,
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
        self.controller.presence.presence()

    def _on_change_presence_button_clicked(self, button):

        presence_control_popup_window = (
            org.wayround.pyabber.presence_control_popup.PresenceControlPopup(
                self.window_elements.window,
                self
                )
            )
        presence_control_popup_window.show()

    def _on_show_disco_button(self, button):
        org.wayround.pyabber.disco.disco(
            self.controller,
            self.controller.jid.bare(),
            node=None
            )

    def _on_send_space_button_clicked(self, button):
        self.controller.client.io_machine.send(' ')
