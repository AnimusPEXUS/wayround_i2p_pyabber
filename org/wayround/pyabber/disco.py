
import threading

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

import org.wayround.xmpp.disco
import org.wayround.pyabber.adhoc
import org.wayround.utils.gtk

_disco_menu = None

class DiscoMenu:

    def __init__(self):

        self._jid = None
        self._node = None

        self._menu = Gtk.Menu()

        addr_mi = Gtk.MenuItem("jid and node")

        commands_mi = Gtk.MenuItem("Commands")
        commands_mi.connect('activate', self._on_commands_mi_activated)

        self.addr_mi = addr_mi
        self.commands_mi = commands_mi

        self._menu.append(addr_mi)
        self._menu.append(Gtk.SeparatorMenuItem())
        self._menu.append(commands_mi)

    def show(self, controller, jid, node=None):

        self._jid = jid
        self._node = node

        self.controller = controller

        q = org.wayround.xmpp.disco.get_info(
            jid_to=jid,
            jid_from=self.controller.jid.full(),
            node=node,
            stanza_processor=self.controller.client.stanza_processor
            )

        t = jid
        if node:
            t += '\n{}'.format(node)

        self.addr_mi.set_label(t)

        if q != None:
            r = q.find(
                "{http://jabber.org/protocol/disco#info}feature[@var='http://jabber.org/protocol/commands']"
                )

            self.commands_mi.set_sensitive(r != None)

            self._menu.show_all()
            self._menu.popup(
                None,
                None,
                None,
                None,
                0,
                Gtk.get_current_event_time()
                )

        return

    def _on_commands_mi_activated(self, menuitem):

        org.wayround.pyabber.adhoc.adhoc_window_for_jid_and_node(
            controller=self.controller,
            jid_to=self._jid,
            jid_from=self.controller.jid.full()
            )

def disco_menu(controller, jid, node=None):
    global _disco_menu

    if _disco_menu == None:
        _disco_menu = DiscoMenu()

    _disco_menu.show(controller, jid, node)

class Disco:

    def __init__(self, controller):

        self._controller = controller

        window = Gtk.Window()

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_margin_top(5)
        main_box.set_margin_bottom(5)
        main_box.set_margin_left(5)
        main_box.set_margin_right(5)
        main_box.set_spacing(5)

        jid_entry = Gtk.Entry()
        jid_entry.set_hexpand(True)
        node_entry = Gtk.Entry()
        node_entry.set_hexpand(True)

        addr_control_grid = Gtk.Grid()

        go_button = Gtk.Button("Go!")
        self._go_button = go_button
        go_button.connect('clicked', self._on_go_button_pressed)
        clear_node_button = Gtk.Button("Clear")
        server_menu_button = Gtk.Button("This Entity Menu")
        self._server_menu_button = server_menu_button
        server_menu_button.connect('clicked', self._on_server_menu_button_clicked)

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


        view_frame = Gtk.Frame()
        view_sw = Gtk.ScrolledWindow()
        view_tw = Gtk.TreeView()
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

        self.window = window
        self.jid_entry = jid_entry
        self.node_entry = node_entry

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

        self._view_model = view_model

        _c = Gtk.TreeViewColumn()
        _r = Gtk.CellRendererText()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'text', 0)
        _c.set_title('Bla Bla Bla')
        view_tw.append_column(_c)
        view_tw.set_headers_visible(False)

        view_tw.connect('row-activated', self._on_row_activated)
        view_tw.connect('button-release-event', self._on_treeview_buttonpress)

        self._work_jid = None
        self._work_node = None

        self._lock = threading.Lock()

        return

    def show(self):

        self.window.show_all()

        self._stat_bar.push(0, "Ready")

    def _fill2(self, path, jid, node=None):

        self._lock.acquire()

        self._spinner.start()
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

            res = org.wayround.xmpp.disco.get(
                jid_to=jid,
                jid_from=self._controller.jid.full(),
                node=node,
                stanza_processor=self._controller.client.stanza_processor
                )

            if res['info'] == None or res['items'] == None:
                pass
            else:

                self._stat_bar.push(0, "Parsing identities")


                identities = []
                q = res['info']
                if q != None:
                    identities = q.findall('{http://jabber.org/protocol/disco#info}identity')

                self._stat_bar.push(0, "Parsing features")


                features = []
                q = res['info']
                if q != None:
                    features = q.findall('{http://jabber.org/protocol/disco#info}feature')

                self._stat_bar.push(0, "Parsing items")

                items = []
                q = res['items']
                if q != None:
                    items = q.findall('{http://jabber.org/protocol/disco#items}item')

                total_num = len(identities) + len(features) + len(items)
                current_num = 0

                self._stat_bar.push(0, "Adding result to tree ({} records to add)".format(total_num))

                self._stat_bar.push(0, "Adding idents ({} records to add)".format(len(identities)))


                for i in identities:

                    itera = None
                    if path != None:
                        itera = self._view_model.get_iter(
                            path.get_path()
                            )

                    self._view_model.append(
                        itera,
                        [
                         "[ident] category: {}, type: {}, name: {}".format(
                            i.get('category'), i.get('type'), i.get('name')
                            ),
                         None,
                         'info',
                         'identity',
                         i.get('category'),
                         i.get('type'),
                         i.get('name'),
                         None,
                         None,
                         None
                         ]
                        )

                    current_num += 1
                    self._progress_bar.set_fraction(1. / (float(total_num) / current_num))


                self._stat_bar.push(0, "Adding features ({} records to add)".format(len(features)))

                for i in features:

                    itera = None
                    if path != None:
                        itera = self._view_model.get_iter(
                            path.get_path()
                            )

                    self._view_model.append(
                        itera,
                        [
                         "[feature] var: {}".format(i.get('var')),
                         None,
                         'info',
                         'feature',
                         None,
                         None,
                         None,
                         i.get('var'),
                         None,
                         None
                         ]
                        )

                    current_num += 1
                    self._progress_bar.set_fraction(1. / (float(total_num) / current_num))

                self._stat_bar.push(0, "Adding items ({} records to add)".format(len(items)))

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
                            i.get('name'), i.get('jid'), i.get('node')
                            ),
                         None,
                         'items',
                         'item',
                         None,
                         None,
                         i.get('name'),
                         None,
                         i.get('jid'),
                         i.get('node')
                         ]
                        )


                    current_num += 1
                    self._progress_bar.set_fraction(1. / (float(total_num) / current_num))


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

        t = threading.Thread(
            target=self._fill2,
            args=(path, jid),
            kwargs={
                'node':node
                }
            )
        t.start()

        w = org.wayround.utils.gtk.Waiter(t.join, None, t.is_alive)
        w.wait()

        return

    def set_addr(self, jid, node=None):

        jid = jid.strip()

        if isinstance(node, str):
            node = node.strip()
        else:
            node = None

        self._work_jid = jid
        self._work_node = node

        self.jid_entry.set_text(self._work_jid)

        nt = ''
        if self._work_node != None:
            nt = self._work_node

        self.node_entry.set_text(nt)

        self._fill(
            None, self._work_jid, node=self._work_node
            )

        return

    def _on_go_button_pressed(self, button):
        node = None
        nt = self.node_entry.get_text()
        nt = nt.strip()
        if nt != '':
            node = nt
        self.set_addr(self.jid_entry.get_text().strip(), node=node)

    def _on_server_menu_button_clicked(self, button):

        if self._work_jid:
            disco_menu(
                self._controller,
                self._work_jid,
                self._work_node
                )



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

        elif values[3] == 'feature' and values[7] == 'http://jabber.org/protocol/commands':

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
                    path, column, cell_x, cell_y = res

                    m = widget.get_model()
                    ref = Gtk.TreeRowReference.new(m, path)
                    values = m[m.get_iter(ref.get_path())]

                    if values[3] == 'item':

                        node = None
                        if values[9] != None:
                            node = values[9]

                        disco_menu(
                            self._controller,
                            values[8],
                            node
                            )

        return

def disco(controller, jid, node=None):
    a = Disco(controller)
    a.show()
