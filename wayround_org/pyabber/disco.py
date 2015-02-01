
import threading

from gi.repository import Gdk, GdkPixbuf, Gtk, Pango

import wayround_org.pyabber.adhoc
import wayround_org.pyabber.muc
import wayround_org.pyabber.privacy
import wayround_org.utils.gtk
import wayround_org.xmpp.core
import wayround_org.xmpp.disco


class DiscoMenu:

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

        self._client = self._controller.client
        self._own_jid = self._controller.jid

        addr_mi = Gtk.MenuItem("target_jid and node")
        error_mi = Gtk.MenuItem("no errors")

        commands_mi = Gtk.MenuItem("Commands")
        muc_mi = Gtk.MenuItem("MUC")
        privacy_mi = Gtk.MenuItem("Privacy..")
        registration_mi = Gtk.MenuItem("Registration..")

        menu.append(addr_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(error_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(commands_mi)
        menu.append(muc_mi)
        menu.append(privacy_mi)
        menu.append(registration_mi)

        addr_submenu = Gtk.Menu()
        addr_mi.set_submenu(addr_submenu)

        addr_open_mi = Gtk.MenuItem("Open")
        addr_copy_mi = Gtk.MenuItem("Copy to Clipboard")

        addr_copy_mi.connect('activate', self._on_jid_copy_to_clipboard_mi)

        addr_submenu.append(addr_open_mi)
        addr_submenu.append(Gtk.SeparatorMenuItem())
        addr_submenu.append(addr_copy_mi)

        mucmenu = wayround_org.pyabber.muc.MUCPopupMenu(
            controller=controller
            )

        muc_mi.set_submenu(mucmenu.get_widget())

        menu.show_all()

        self._on_addr_open_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_addr_open_activated)

        addr_open_mi.connect('activate', self._on_addr_open_activated_idle)

        self._on_commands_mi_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_commands_mi_activated)

        commands_mi.connect('activate', self._on_commands_mi_activated_idle)

        self._on_privacy_mi_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_privacy_mi_activated)

        privacy_mi.connect('activate', self._on_privacy_mi_activated_idle)

        self._on_registration_mi_activated_idle = \
            wayround_org.utils.gtk.to_idle(self._on_registration_mi_activated)

        registration_mi.connect(
            'activate',
            self._on_registration_mi_activated_idle
            )

        self._addr_mi = addr_mi
        self._commands_mi = commands_mi
        self._error_mi = error_mi
        self._menu = menu
        self._muc_mi = muc_mi
        self._mucmenu = mucmenu
        self._registration_mi = registration_mi

        return

    def set(self, target_jid_str, node=None):

        if not isinstance(target_jid_str, str):
            raise ValueError(
                "`target_jid_str' must be str"
                )

        if node is not None and not isinstance(node, str):
            raise ValueError(
                "`node' must be None or str"
                )

        self._target_jid_str = target_jid_str
        self._node = node

        q, stanza = wayround_org.xmpp.disco.get_info(
            to_jid=self._target_jid_str,
            from_jid=self._own_jid.full(),
            node=self._node,
            stanza_processor=self._client.stanza_processor
            )

        self._commands_mi.set_sensitive(False)
        self._error_mi.set_sensitive(False)
        self._muc_mi.set_sensitive(False)

#        self._registration_mi.set_sensitive(False)
#        privacy_mi.set_sensitive(False)

        if isinstance(stanza, wayround_org.xmpp.core.Stanza):
            if stanza.is_error():
                self._error_mi.set_label(stanza.gen_error().gen_text().strip())
            else:
                self._error_mi.set_label("No errors")

            t = self._target_jid_str
            if node:
                t += '\{}'.format(node)

            self._addr_mi.set_label(t)

            if q != None:
                self._commands_mi.set_sensitive(
                    q.has_feature('http://jabber.org/protocol/commands')
                    )

                self._muc_mi.set_sensitive(
                    q.has_feature('http://jabber.org/protocol/muc')
                    )

                #            self._registration_mi.set_sensitive(
                #                q.has_feature('jabber:iq:register')
                #                )

                #            self._privacy_mi.set_sensitive(
                #                q.has_feature('jabber:iq:privacy')
                #                )

            self._mucmenu.set(target_jid_str)

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

    def destroy(self):
        self._mucmenu.destroy()
        self._menu.destroy()

    def _on_commands_mi_activated(self, menuitem):

        wayround_org.pyabber.adhoc.adhoc_window_for_jid_and_node(
            self._target_jid_str,
            self._controller
            )

    def _on_addr_open_activated(self, menuitem):
        self._controller.show_disco_window(self._target_jid_str, self._node)

    def _on_privacy_mi_activated(self, menuitem):

        w = wayround_org.pyabber.privacy.PrivacyEditor(
            to_jid=self._target_jid_str,
            from_jid=self._own_jid,
            stanza_processor=self._client.stanza_processor
            )

        w.show()

        return

    def _on_registration_mi_activated(self, menuitem):

        self._controller.show_registration_window(
            target_jid_obj=wayround_org.xmpp.core.JID.new_from_str(
                self._target_jid_str
                ),
            from_jid_obj=self._controller.jid,
            get_reg_form=True,
            predefined_form=None,
            pred_username=None,
            pred_password=None
            )

        return

    def _on_jid_copy_to_clipboard_mi(self, mi):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(
            str(self._target_jid_str),
            - 1
            )
        return


class Disco:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._menu = DiscoMenu(controller)

        self._client = self._controller.client
        self._own_jid = self._controller.jid

        window = Gtk.Window()
        window.set_default_size(500, 500)

        self._on_destroy_idle = \
            wayround_org.utils.gtk.to_idle(self._on_destroy)

        window.connect('destroy', self._on_destroy_idle)

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_margin_top(5)
        main_box.set_margin_bottom(5)
        main_box.set_margin_start(5)
        main_box.set_margin_end(5)
        main_box.set_spacing(5)

        jid_entry = Gtk.Entry()
        jid_entry.set_hexpand(True)
        node_entry = Gtk.Entry()
        node_entry.set_hexpand(True)

        addr_control_grid = Gtk.Grid()

        go_button = Gtk.Button("Go!")
        self._go_button = go_button
        self._on_go_button_pressed_idle = \
            wayround_org.utils.gtk.to_idle(self._on_go_button_pressed)
        go_button.connect('clicked', self._on_go_button_pressed_idle)
        clear_node_button = Gtk.Button("Clear")
        server_menu_button = Gtk.Button("This Entity Menu")
        self._server_menu_button = server_menu_button

        server_menu_button.connect(
            'clicked', self._on_server_menu_button_clicked
            )

        addr_control_grid.attach(Gtk.Label("JID"), 0, 0, 1, 1)
        addr_control_grid.attach(jid_entry, 1, 0, 2, 1)
        addr_control_grid.attach(Gtk.Label("Node"), 0, 1, 1, 1)
        addr_control_grid.attach(node_entry, 1, 1, 1, 1)
        addr_control_grid.attach(clear_node_button, 2, 1, 1, 1)
        addr_control_grid.attach(go_button, 3, 0, 1, 2)
        addr_control_grid.attach(server_menu_button, 0, 3, 4, 1)
        addr_control_grid.set_row_homogeneous(True)
        addr_control_grid.set_row_spacing(5)
        addr_control_grid.set_column_spacing(5)

        self._on_jid_or_node_entry_activate_idle = \
            wayround_org.utils.gtk.to_idle(self._on_jid_or_node_entry_activate)

        jid_entry.connect('activate', self._on_jid_or_node_entry_activate_idle)

        self._on_jid_or_node_entry_activate_idle = \
            wayround_org.utils.gtk.to_idle(self._on_jid_or_node_entry_activate)

        node_entry.connect(
            'activate',
            self._on_jid_or_node_entry_activate_idle
            )

        view_frame = Gtk.Frame()
        view_sw = Gtk.ScrolledWindow()
        view_tw = Gtk.TreeView()

        view_tw.set_rules_hint(True)

        self._view_tw = view_tw

        view_sw.add(view_tw)
        view_frame.add(view_sw)

        self._spinner = Gtk.Spinner()
        self._progress_bar = Gtk.ProgressBar()
        self._stat_bar = Gtk.Statusbar()

        p_box = Gtk.Box()
        p_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        p_box.set_spacing(5)

        p_box.pack_start(self._progress_bar, True, True, 0)
        p_box.pack_start(self._spinner, False, False, 0)

        main_box.pack_start(addr_control_grid, False, False, 0)
        main_box.pack_start(view_frame, True, True, 0)
        main_box.pack_start(p_box, False, False, 0)
        main_box.pack_start(self._stat_bar, False, False, 0)

        window.add(main_box)

        # markup, disco, tag, category, type, name, var, jid, node
        # disco in ['info', 'items']
        # info : markup, tag, category, type, name, var,
        # items: markup, tag, jid, node

        view_model = Gtk.TreeStore(
            str,  # 0. display markup
            GdkPixbuf.Pixbuf,  # 1. icon
            str,  # 2. disco
            str,  # 3. tag
            str,  # 4. category
            str,  # 5. type
            str,  # 6. name
            str,  # 7. var
            str,  # 8. jid
            str  # 9. node
            )

        view_tw.set_model(view_model)

#        font_desc = Pango.FontDescription()
#        font_desc.set_family('Fixed')
#        font_desc.set_size(12)
#        font_desc.set_weight(Pango.Weight.NORMAL)

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
#        _r.set_property('font-desc', font_desc)
        _r.set_property('family', 'Fixed')
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        _c.set_title('Bla Bla Bla')
        view_tw.append_column(_c)
        view_tw.set_headers_visible(False)

#        self._on_row_activated_idle = \
#            wayround_org.utils.gtk.to_idle(self._on_row_activated)
        view_tw.connect('row-activated', self._on_row_activated)

#        self._on_treeview_buttonpress_idle = \
#            wayround_org.utils.gtk.to_idle(self._on_treeview_buttonpress)
        view_tw.connect(
            'button-release-event',
            self._on_treeview_buttonpress
            )

#        self._fill2_idle = wayround_org.utils.gtk.to_idle(self._fill2)

        self._lock = threading.Lock()

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        self._node = None
        self._target_jid_str = None
        self._view_model = view_model
        self._window = window

        self._jid_entry = jid_entry
        self._node_entry = node_entry
        self._work_jid = None
        self._work_node = None

        return

    def run(self, target_jid_str=None, node=None):

        if not isinstance(target_jid_str, str):
            raise ValueError(
                "`target_jid_str' must be str"
                )

        if node is not None and not isinstance(node, str):
            raise ValueError(
                "`node' must be None or str"
                )

        self._node = node
        self._target_jid_str = target_jid_str

        if (self._target_jid_str != None
            or (self._target_jid_str != None and self._node != None)):

            self.set_addr(self._target_jid_str, self._node)

        self._stat_bar.push(0, "Ready")

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._menu.destroy()
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _fill2(self, path, jid, node=None):

        self._lock.acquire()

        self._spinner.start()
        self._progress_bar.set_fraction(0.0)
        self._go_button.set_sensitive(False)
        self._view_tw.set_sensitive(False)

        try:

            self._stat_bar.push(0, "Clearing tree")

            itera = None
            if path != None:
                itera = self._view_model.get_iter(
                    path.get_path()
                    )

            child = self._view_model.iter_children(itera)
            res = True

            ii = 0
            while child != None and res != False:
                res = self._view_model.remove(child)
                ii += 1

            self._stat_bar.push(0, "Getting information from server")

            get_res = {'data': None}

            t = threading.Thread(
                target=_t_proc,
                args=(get_res, {
                    'to_jid': jid,
                    'from_jid': self._own_jid.full(),
                    'node': node,
                    'stanza_processor': self._client.stanza_processor
                    }),
                kwargs={}
                )
            t.start()

            wayround_org.utils.gtk.Waiter.wait_thread(t)

            res = get_res['data']

            if res['info'][0] != None:
                x = res['info'][0].get_xdata()

                for i in x:

                    itera = None
                    if path != None:
                        itera = self._view_model.get_iter(
                            path.get_path()
                            )

                    self._view_model.append(
                        itera,
                        [
                         "[jabber:x:data]\n    {}".format(
                            '\n    '.join(i.gen_info_text().splitlines())
                            ),
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None
                         ]
                        )

            identities = []
            features = []
            items = []

            self._stat_bar.push(0, "Parsing identities")
            q = res['info'][0]
            if q != None:
                identities = q.get_identity()

            self._stat_bar.push(0, "Parsing features")
            q = res['info'][0]
            if q != None:
                features = q.get_feature()

            self._stat_bar.push(0, "Parsing items")
            q = res['items'][0]
            if q != None:
                items = q.get_item()

            total_num = len(identities) + len(features) + len(items)

            current_num = 0

            self._stat_bar.push(
                0,
                "Adding result to tree ({} records to add)".format(total_num)
                )

            self._stat_bar.push(
                0, "Adding idents ({} records to add)".format(len(identities))
                )

            if res['info'][1] == False:
                self._view_model.append(
                    itera,
                    [
                     "[info error] request timeout",
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None
                     ]
                    )
            else:
                if res['info'][1].is_error():
                    itera = None
                    if path != None:
                        itera = self._view_model.get_iter(
                            path.get_path()
                            )

                    err_dict = res['info'][1].gen_error()

                    self._view_model.append(
                        itera,
                        [
                         "[info error] error type: {},"
                         " condition: {}, code: {}, text: {}".format(
                            err_dict.get_error_type(),
                            err_dict.get_condition(),
                            err_dict.get_code(),
                            err_dict.get_text()
                            ),
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None
                         ]
                        )

            for i in identities:

                itera = None
                if path != None:
                    itera = self._view_model.get_iter(
                        path.get_path()
                        )

                self._view_model.append(
                    itera,
                    [
                     "[identity] category: {}, type: {}, name: {}".format(
                        i.get_category(), i.get_typ(), i.get_name()
                        ),
                     None,
                     'info',
                     'identity',
                     i.get_category(),
                     i.get_typ(),
                     i.get_name(),
                     None,
                     None,
                     None
                     ]
                    )

                current_num += 1
                self._progress_bar.set_fraction(
                    1. / (float(total_num) / current_num)
                    )

            self._stat_bar.push(
                0, "Adding features ({} records to add)".format(len(features))
                )

            for i in features:

                itera = None
                if path != None:
                    itera = self._view_model.get_iter(
                        path.get_path()
                        )

                self._view_model.append(
                    itera,
                    [
                     "[feature] var: {}".format(i),
                     None,
                     'info',
                     'feature',
                     None,
                     None,
                     None,
                     i,
                     None,
                     None
                     ]
                    )

                current_num += 1
                self._progress_bar.set_fraction(
                    1. / (float(total_num) / current_num)
                    )

            self._stat_bar.push(
                0, "Adding items ({} records to add)".format(len(items))
                )

            if res['items'][1] == False:
                self._view_model.append(
                    itera,
                    [
                     "[items error] request timeout",
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None
                     ]
                    )
            else:
                if res['items'][1].is_error():
                    itera = None
                    if path != None:
                        itera = self._view_model.get_iter(
                            path.get_path()
                            )

                    err_dict = res['items'][1].gen_error()

                    self._view_model.append(
                        itera,
                        [
                         "[items error] error type: {}, condition:"
                         " {}, code: {}, text: {}".format(
                            err_dict.get_error_type(),
                            err_dict.get_condition(),
                            err_dict.get_code(),
                            err_dict.get_text()
                            ),
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None,
                         None
                         ]
                        )

            for i in items:

                itera = None
                if path != None:
                    itera = self._view_model.get_iter(
                        path.get_path()
                        )

                self._view_model.append(
                    itera,
                    [
                     "{}\n[item] jid: {}, node: {}".format(
                        i.get_name(), i.get_jid(), i.get_node()
                        ),
                     None,
                     'items',
                     'item',
                     None,
                     None,
                     i.get_name(),
                     None,
                     i.get_jid(),
                     i.get_node()
                     ]
                    )

                current_num += 1
                self._progress_bar.set_fraction(
                    1. / (float(total_num) / current_num)
                    )

            self._stat_bar.push(0, "Job finished")

        except:
            self._view_tw.set_sensitive(True)
            self._go_button.set_sensitive(True)
            self._spinner.stop()

            self._lock.release()

            raise

        self._view_tw.set_sensitive(True)
        self._go_button.set_sensitive(True)
        self._spinner.stop()

        self._lock.release()

        return

    def _fill(self, path, jid, node=None):

#        t = threading.Thread(
#            target=self._fill2_idle,
#            args=(path, jid),
#            kwargs={
#                'node': node
#                }
#            )
#        t.start()
#
#        w = wayround_org.utils.gtk.Waiter(t.join, None, t.is_alive)
#        w.wait()

        self._fill2(path, jid, node=node)

        return

    def set_addr(self, jid, node=None):

        if jid == None:
            jid = ''

        jid = jid.strip()

        if isinstance(node, str):
            node = node.strip()
        else:
            node = None

        self._work_jid = jid
        self._work_node = node

        self._jid_entry.set_text(self._work_jid)

        nt = ''
        if self._work_node != None and isinstance(self._work_node, str):
            nt = self._work_node

        t = jid
        if node:
            t += '\{}'.format(node)

        self._node_entry.set_text(nt)
        self._server_menu_button.set_label(
            "`{}' menu".format(t)
            )

        self._window.set_title(
            "Discovering `{}' as `{}'".format(
                "{}".format(t),
                self._own_jid.full()
                )
            )

        self._fill(
            None, self._work_jid, node=self._work_node
            )

        return

    def _on_go_button_pressed(self, button):
        node = None
        nt = self._node_entry.get_text()
        nt = nt.strip()
        if nt != '':
            node = nt
        self.set_addr(self._jid_entry.get_text().strip(), node=node)

    def _on_server_menu_button_clicked(self, button):

        if self._work_jid:
            self._menu.set(
                target_jid_str=self._work_jid,
                node=self._work_node
                )
            self._menu.show()

    def _on_row_activated(self, view, path, column):

        m = view.get_model()
        ref = Gtk.TreeRowReference.new(m, path)
        values = m[m.get_iter(ref.get_path())]

        if values[3] == 'item':

            node = None
            if values[9] != None:
                node = values[9]

            self._fill(ref, values[8], node=node)

            self._view_tw.expand_row(ref.get_path(), False)
            self._view_tw.scroll_to_cell(ref.get_path(), None, True, 0.1, 0.0)

#        if values[3] == 'feature':
#
#            par = m.iter_parent(m.get_iter(ref.get_path()))
#
#            jid = None
#            if par == None:
#                jid = self._work_jid
#            else:
#                jid = m[par][8]
#
#            self._fill(ref, jid, node=values[7])
#            self._view_tw.expand_row(ref.get_path(), False)
#            self._view_tw.scroll_to_cell(ref.get_path(), None, True, 0.1, 0.0)

        elif (values[3] == 'feature'
              and values[7] == 'http://jabber.org/protocol/commands'):

            par = m.iter_parent(m.get_iter(ref.get_path()))

            jid = None
            if par == None:
                jid = self._work_jid
            else:
                jid = m[par][8]

            self._fill(ref, jid, node='http://jabber.org/protocol/commands')
            self._view_tw.expand_row(ref.get_path(), False)
            self._view_tw.scroll_to_cell(ref.get_path(), None, True, 0.1, 0.0)

        else:
            pass

        return

    def _on_treeview_buttonpress(self, widget, event):

        if event.button == Gdk.BUTTON_SECONDARY:
            bw = widget.get_bin_window()
            if event.window == bw:

                res = widget.get_path_at_pos(event.x, event.y)

                if res != None:
                    path = res[0]

                    m = widget.get_model()
                    ref = Gtk.TreeRowReference.new(m, path)
                    values = m[m.get_iter(ref.get_path())]

                    if values[3] == 'item':

                        node = None
                        if values[9] != None:
                            node = values[9]

                        self._menu.set(
                            target_jid_str=values[8],
                            node=node
                            )
                        self._menu.show()

        return

    def _on_jid_or_node_entry_activate(self, entry):
        self._go_button.emit('clicked')


def _t_proc(x, y):
    x['data'] = wayround_org.xmpp.disco.get(**y)
