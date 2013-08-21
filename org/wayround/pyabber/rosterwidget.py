
import logging

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import PangoCairo



class RosterCellRenderer(Gtk.CellRenderer):

    cell_type = GObject.property(type=str, default='contact')
    name_or_title = GObject.property(type=str, default='')
    bare_jid = GObject.property(type=str, default='')
    resource = GObject.property(type=str, default='')
    approved = GObject.property(type=str, default='')
    ask = GObject.property(type=str, default='')
    subscription = GObject.property(type=str, default='')
    nick = GObject.property(type=str, default='')
    userpic = GObject.property(type=GdkPixbuf.Pixbuf, default=None)
    available = GObject.property(type=bool, default=False)
    status = GObject.property(type=str, default='')
    status_text = GObject.property(type=str, default='')
    has_new_messages = GObject.property(type=bool, default=False)
    not_in_roster = GObject.property(type=bool, default=False)

    def __init__(self):

        super().__init__()

#    def do_get_request_mode(self):
#        logging.debug("get_request_mode")
#        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_width(self, widget):

        return (100, 100,)

    def do_get_preferred_height(self, widget):
        cell_type = self.get_property('cell_type')

        ret = (1, 1,)

        if cell_type == 'division':
            ret = (12, 12,)
        elif cell_type == 'group':
            ret = (10, 10,)
        elif cell_type == 'contact':
            ret = (75, 75,)
        elif cell_type == 'resource':
            ret = (10, 10,)
        else:
            raise Exception("Invalid cell_type")

        return ret

#    def do_get_preferred_height_for_width(self, width):
#        return self.get_preferred_height()
#
#    def do_get_preferred_width_for_height(self, height):
#        return self.get_preferred_width()
#
#    def gtk_cell_renderer_get_aligned_area(self, widget, flags, cell_area):
#        return cell_area
#
#    def get_size(self, widget, cell_area, x_offset, y_offset, width, height):
#        return cell_area

    def do_render(self, cr, widget, background_area, cell_area, flags):

        initial_ctm = cr.get_matrix()
#        resolution = widget.get_screen().get_resolution()

        cell_type = self.get_property('cell_type')

        if cell_type == 'division':

            cr.translate(
                cell_area.x,
                cell_area.y,
                )
            draw_division_cell(
                cr,
                cell_area.width,
                cell_area.height,
                title=self.get_property('name_or_title')
                )
            cr.set_matrix(initial_ctm)

        elif cell_type == 'group':

            cr.translate(
                cell_area.x,
                cell_area.y,
                )
            draw_group_cell(
                cr,
                cell_area.width,
                cell_area.height,
                title=self.get_property('name_or_title')
                )
            cr.set_matrix(initial_ctm)

        elif cell_type == 'contact':

            pass
            cr.translate(
                cell_area.x,
                cell_area.y,
                )
            draw_contact_cell(
                cr,
                width=cell_area.width,
                height=cell_area.height,
                approved=self.get_property('approved'),
                ask=self.get_property('ask'),
                bare_jid=self.get_property('bare_jid'),
                name=self.get_property('name_or_title'),
                subscription=self.get_property('subscription'),
                nick=self.get_property('nick'),
                userpic=self.get_property('userpic'),
                available=self.get_property('available'),
                status=self.get_property('status'),
                status_text=self.get_property('status_text'),
                has_new_messages=self.get_property('has_new_messages')
                )
            cr.set_matrix(initial_ctm)


        elif cell_type == 'resource':
            pass
        else:
            raise Exception("Invalid cell_type")

        return

def draw_division_cell(cr, width, height, title):
    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)
    l = Gtk.Label(title)
    ow.add(l)
    ow.show_all()
    l.draw(cr)
    ow.destroy()

def draw_group_cell(cr, width, height, title):
    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)
    l = Gtk.Label(title)
    ow.add(l)
    ow.show_all()
    l.draw(cr)
    ow.destroy()

def draw_contact_cell(
    cr, width, height,
    approved, ask, bare_jid, name, subscription,
    nick, userpic, available, status, status_text, has_new_messages
    ):

    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)

    b = Gtk.Box()
    b.set_orientation(Gtk.Orientation.VERTICAL)

    ow.add(b)

    bh = Gtk.Box()
    bh.set_orientation(Gtk.Orientation.HORIZONTAL)

    bb = Gtk.Box()
    bb.set_orientation(Gtk.Orientation.HORIZONTAL)


    jid_label = Gtk.Label(bare_jid)
    img = Gtk.Image()
    if not userpic:
        img.set_from_stock('gtk-missing-image', Gtk.IconSize.BUTTON)
    else:
        img.set_from_pixbuf(userpic)

    bh.pack_start(img, False, False, 0)

    b.pack_start(jid_label, False, False, 0)
    b.pack_start(bh, True, True, 0)
    b.pack_start(bb, True, True, 0)

    ow.show_all()
    b.draw(cr)
    ow.destroy()

class RosterWidgetItem:

    def __init__(self, cell_type, title, available, status_text, userpic):

        self.cell_type = cell_type
        self.title = title
        self.available = available
        self.status_text = status_text
        self.userpic = userpic


class RosterWidget:

    def __init__(self, treeview):

        self._treeview = treeview

        _c = Gtk.TreeViewColumn()
        _r = RosterCellRenderer()
        _c.pack_start(_r, False)
        _c.add_attribute(_r, 'cell_type', 0)
        _c.add_attribute(_r, 'name_or_title', 1)
        _c.add_attribute(_r, 'bare_jid', 2)
        _c.add_attribute(_r, 'resource', 3)
        _c.add_attribute(_r, 'approved', 4)
        _c.add_attribute(_r, 'ask', 5)
        _c.add_attribute(_r, 'subscription', 6)
        _c.add_attribute(_r, 'nick', 7)
        _c.add_attribute(_r, 'userpic', 8)
        _c.add_attribute(_r, 'available', 9)
        _c.add_attribute(_r, 'status', 10)
        _c.add_attribute(_r, 'status_text', 11)
        _c.add_attribute(_r, 'has_new_messages', 12)
        _c.set_title('Roster')
        self._treeview.append_column(_c)

        self._store = Gtk.TreeStore(
            str, str, str, str, bool, str, str, str,
            GdkPixbuf.Pixbuf, bool, str, str, bool
            )

        self._treeview.set_model(self._store)
        self._treeview.set_headers_visible(False)

        self._division_add('Grouped Contacts')
        self._division_add('Ungrouped Contacts')
        self._division_add('Not in roster(soft)')
        self._division_add('Not in roster(hard)')
        self._division_add('Transports')

    def _division_add(self, title):
        self._store.append(
            None,
            ['division',
             title,
             None,
             None,
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

    def _group_add(self, group):
        """
        Create group if not exists
        """
        if not self._group_get_iter(group):
            group_iter = self._division_get_iter('groups')

            self._store.append(
                group_iter,
                ['group',
                 group,
                 None,
                 None,
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

    def _contact_add(self, group, bare_jid):
        """
        Add contact to group if it isn't already there

        This function is only for adding contact, it's not for populating it -
        for populating all contacts of this bare_jid use :meth:`_contact_set`
        """
        if not self._group_get_iter(group):
            self._group_add(group)

        group_iter = self._group_get_iter(group)

        if not self._group_get_contact_iter(group, bare_jid):

            self._store.append(
                group_iter,
                ['contact',
                 None,
                 bare_jid,
                 None,
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

    def _contact_set(
        self,
        group,
        bare_jid,
        name_or_title,
        approved, ask, subscription,
        nick, userpic, available,
        status, status_text, has_new_messages
        ):

        if self._group_get_iter(group):

            group_iter = self._group_get_iter(group)

            child = self._store.iter_children(group_iter)

            while child:

                if self._store[child][2] == bare_jid:
                    self._store.set(
                        child,
                        0, 'contact',
                        1, name_or_title,
                        2, bare_jid,
                        3, None,
                        4, approved,
                        5, ask,
                        6, subscription,
                        7, nick,
                        8, userpic,
                        9, available,
                        10, status,
                        11, status_text,
                        12, has_new_messages
                        )
                    break

#                        ['contact',
#                         name_or_title,
#                         bare_jid,
#                         None,
#                         approved,
#                         ask,
#                         subscription,
#                         nick,
#                         userpic,
#                         available,
#                         status,
#                         status_text,
#                         has_new_messages
#                         ]

                child = self._store.iter_next(child)


    def _division_get_iter(self, name):

        """
        Returns iter or division
        """

        ret = None

        ifr = self._store.get_iter_first()

        if not ifr:
            ret = None
        else:

            lfo = None

            if name == 'groups':
                lfo = 'Grouped Contacts'
            elif name == 'ungrouped':
                lfo = 'Ungrouped Contacts'
            elif name == 'soft':
                lfo = 'Not in roster(soft)'
            elif name == 'hard':
                lfo = 'Not in roster(hard)'
            elif name == 'transports':
                lfo = 'Transports'

            while ifr != None:

                if self._store[ifr][1] == lfo:
                    ret = ifr
                    break

                ifr = self._store.iter_next(ifr)

        return ret

    def _groups_get(self):

        """
        Returns str list
        """

        ret = []

        group_iter = self._division_get_iter('groups')

        child = self._store.iter_children(group_iter)

        while child != None:
            ret.append(self._store[child][1])
            child = self._store.iter_next(child)

        return ret


    def _group_get_iter(self, name):
        """
        Returns TreeIter of the group

        If not found - None is returned
        """
        ret = None

        group_iter = self._division_get_iter('groups')

        child = self._store.iter_children(group_iter)

        while child != None:

            if self._store[child][1] == name:
                ret = child
                break

            child = self._store.iter_next(child)

        return ret

    def _group_get_contact_iter(self, group, bare_jid):
        """
        Gets contact TreeIter

        If not found - None is returned
        """
        ret = None
        git = self._group_get_iter(group)

        child = self._store.iter_children(git)

        while child:

            if self._store[child][2] == bare_jid:
                ret = child
                break

            child = self._store.iter_next(child)

        return ret

    def _group_remove_contact(self, group, bare_jid):
        """
        Remove contact from group

        Removing group if it's empty
        """

        res = self._group_get_contact_iter(group, bare_jid)
        if res:
            self._store.remove(res)

        group_iter = self._group_get_iter(group)
        count = self._store.n_children(group_iter)

        if count == 0:
            self._group_del(group_iter)

    def _groups_remove_contact(self, bare_jid, groups=None):
        """
        Remove contact from all groups or from named groups
        """

        if groups == None:
            groups = self._groups_get()

        for i in groups:
            self._group_remove_contact(i, bare_jid)

    def _group_del(self, group_or_iter):
        """
        Remove group

        group_or_iter can be group name (str) or TreeIter
        """

        if isinstance(group_or_iter, str):
            group_or_iter = self._group_get_iter(group_or_iter)

        self._store.remove(group_or_iter)

    def _groups_add_contact(self, groups, bare_jid):

        for i in groups:
            self._contact_add(i, bare_jid)

    def _groups_set_contact(
        self, groups, bare_jid,
        name_or_title,
        approved, ask, subscription,
        nick, userpic,
        available, status, status_text,
        has_new_messages
        ):

        if groups == None:
            groups = []

        groups = set(groups)
        a_groups = set(self._groups_get())
        m_groups = a_groups - groups
        p_groups = groups - a_groups

        self._groups_remove_contact(bare_jid, m_groups)
        self._groups_add_contact(p_groups, bare_jid)

        for i in groups:
            self._contact_set(
                i,
                bare_jid,
                name_or_title,
                approved, ask, subscription,
                nick, userpic,
                available, status, status_text,
                has_new_messages
                )

        return

    def set_contact(
        self,
        name_or_title,
        bare_jid, groups, resources,
        approved, ask, subscription,
        nick, userpic, available, status, status_text, has_new_messages,
        not_in_roster
        ):

        self._groups_set_contact(
            groups, bare_jid, name_or_title, approved, ask,
            subscription, nick, userpic, available, status,
            status_text, has_new_messages
            )
