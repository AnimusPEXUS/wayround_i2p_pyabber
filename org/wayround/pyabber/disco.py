
from gi.repository import Gtk
from gi.repository import GdkPixbuf

import org.wayround.xmpp.disco

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
        go_button.connect('clicked', self._on_go_button_pressed)
        clear_node_button = Gtk.Button("Clear")

        addr_control_grid.attach(Gtk.Label("JID"), 0, 0, 1, 1)
        addr_control_grid.attach(jid_entry, 1, 0, 2, 1)
        addr_control_grid.attach(Gtk.Label("Node"), 0, 1, 1, 1)
        addr_control_grid.attach(node_entry, 1, 1, 1, 1)
        addr_control_grid.attach(clear_node_button, 2, 1, 1, 1)
        addr_control_grid.attach(go_button, 3, 0, 1, 2)
        addr_control_grid.set_row_homogeneous(True)
        addr_control_grid.set_row_spacing(5)
        addr_control_grid.set_column_spacing(5)


        view_frame = Gtk.Frame()
        view_sw = Gtk.ScrolledWindow()
        view_tw = Gtk.TreeView()
        self._view_tw = view_tw

        view_sw.add(view_tw)
        view_frame.add(view_sw)

        main_box.pack_start(addr_control_grid, False, False, 0)
        main_box.pack_start(view_frame, True, True, 0)

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

        self._work_jid = None
        self._work_node = None

        return

    def show(self):

        self.window.show_all()

    def _fill(self, path, jid, node=None):

        itera = None
        if path != None:
            itera = self._view_model.get_iter(
                path.get_path()
                )

        child = self._view_model.iter_children(itera)
        res = True

        while child != None and res != False:
            res = self._view_model.remove(child)

            # I don't like this part but...
#            itera = None
#            if path != None:
#                itera = self._view_model.get_iter(
#                    path.get_path()
#                    )
#
#            child = self._view_model.iter_children(itera)

        res = org.wayround.xmpp.disco.get(
            jid_to=jid,
            jid_from=None,
            node=node,
            stanza_processor=self._controller.client.stanza_processor
            )

        identities = []
        q = res['info'].body.find('{http://jabber.org/protocol/disco#info}query')
        if q != None:
            identities = q.findall('{http://jabber.org/protocol/disco#info}identity')

        features = []
        q = res['info'].body.find('{http://jabber.org/protocol/disco#info}query')
        if q != None:

            features = q.findall('{http://jabber.org/protocol/disco#info}feature')

        items = []
        q = res['items'].body.find('{http://jabber.org/protocol/disco#items}query')
        if q != None:
            items = q.findall('{http://jabber.org/protocol/disco#items}item')

        for i in identities:

            itera = None
            if path != None:
                itera = self._view_model.get_iter(
                    path.get_path()
                    )

            self._view_model.append(
                itera,
                [
                 "[ident] category: {}, type: {}, name: {}".format(i.get('category'), i.get('type'), i.get('name')),
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

        for i in items:

            itera = None
            if path != None:
                itera = self._view_model.get_iter(
                    path.get_path()
                    )

            self._view_model.append(
                itera,
                [
                 "[item] jid: {}, node: {}".format(i.get('jid'), i.get('node')),
                 None,
                 'items',
                 'item',
                 None,
                 None,
                 None,
                 None,
                 i.get('jid'),
                 i.get('node')
                 ]
                )

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

        if values[3] == 'feature' and values[7] == 'http://jabber.org/protocol/commands':

            par = m.iter_parent(m.get_iter(ref.get_path()))

            jid = None
            if par == None:
                jid = self._work_jid
            else:
                jid = m[par][8]

            self._fill(ref, jid, node='http://jabber.org/protocol/commands')
            self._view_tw.expand_row(ref.get_path(), False)
            self._view_tw.scroll_to_cell(ref.get_path(), None, True, 0.1, 0.0)




def disco(controller, jid, node=None):
    a = Disco(controller)
    a.show()
