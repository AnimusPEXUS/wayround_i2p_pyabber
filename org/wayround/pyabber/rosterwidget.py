
import threading
import copy

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import PangoCairo

import org.wayround.xmpp.core

import org.wayround.pyabber.contact_popup_menu
import org.wayround.pyabber.icondb


ROW_CELL_NAMES = [
    'cell_type',
    'name_or_title',
    'bare_jid',
    'resource',
    'approved',
    'ask',
    'subscription',
    'nick',
    'userpic',
    'available',
    'show',
    'status',
    'has_new_messages'
    ]

ROW_CELL_NAMES_COUNT = len(ROW_CELL_NAMES)
ROW_CELL_CELL_TYPE = 0
ROW_CELL_NAME_OR_TITLE = 1
ROW_CELL_BARE_JID = 2
ROW_CELL_RESOURCE = 3
ROW_CELL_APPROVED = 4
ROW_CELL_ASK = 5
ROW_CELL_SUBSCRIPTION = 6
ROW_CELL_NICK = 7
ROW_CELL_USERPIC = 8
ROW_CELL_AVAILABLE = 9
ROW_CELL_SHOW = 10
ROW_CELL_STATUS = 11
ROW_CELL_HAS_NEW_MESSAGES = 12

LEVEL_CONTACT_SET_FILL_LIST = [
    ROW_CELL_NAME_OR_TITLE,
    ROW_CELL_APPROVED,
    ROW_CELL_ASK,
    ROW_CELL_SUBSCRIPTION,
    ROW_CELL_NICK,
    ROW_CELL_USERPIC,
    ROW_CELL_AVAILABLE,
    ROW_CELL_SHOW,
    ROW_CELL_STATUS,
    ROW_CELL_HAS_NEW_MESSAGES
    ]


#for i in ROW_CELL_NAMES:
#    exec("""\
#ROW_CELL_{upper} = {normal}
#""".formay(upper=i.upper(), normal=i))
#
#del(i)

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
    show = GObject.property(type=str, default='')
    status = GObject.property(type=str, default='')
    has_new_messages = GObject.property(type=bool, default=False)
    not_in_roster = GObject.property(type=bool, default=False)

    def __init__(self):

        super().__init__()

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
            ret = (60, 60,)
        elif cell_type == 'resource':
            ret = (16, 16,)
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
                show=self.get_property('show'),
                status=self.get_property('status'),
                has_new_messages=self.get_property('has_new_messages')
                )
            cr.set_matrix(initial_ctm)


        elif cell_type == 'resource':

            cr.translate(
                cell_area.x,
                cell_area.y,
                )
            draw_resource_cell(
                cr,
                width=cell_area.width,
                height=cell_area.height,
                resource=self.get_property('resource'),
                available=self.get_property('available'),
                show=self.get_property('show'),
                status=self.get_property('status'),
                has_new_messages=self.get_property('has_new_messages')
                )
            cr.set_matrix(initial_ctm)

        else:
            raise Exception("Invalid cell_type")

        return

def draw_division_cell(cr, width, height, title):
    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)
    l = Gtk.Label(title)
    l.set_alignment(0, 0.5)
    ow.add(l)
    ow.show_all()
    l.draw(cr)
    ow.destroy()

def draw_group_cell(cr, width, height, title):
    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)
    l = Gtk.Label(title)
    l.set_alignment(0, 0.5)
    ow.add(l)
    ow.show_all()
    l.draw(cr)
    ow.destroy()

def draw_contact_cell(
    cr, width, height,
    approved, ask, bare_jid, name, subscription,
    nick, userpic, available, show, status, has_new_messages
    ):

    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)

    main_box = Gtk.Box()
    main_box.set_orientation(Gtk.Orientation.VERTICAL)

    main_horizontal_box = Gtk.Box()
    main_horizontal_box.set_orientation(Gtk.Orientation.HORIZONTAL)

    text_info_box = Gtk.Box()
    text_info_box.set_orientation(Gtk.Orientation.VERTICAL)

    status_box = Gtk.Box()
    status_box.set_orientation(Gtk.Orientation.HORIZONTAL)

    ask_label = Gtk.Label("ask: " + str(ask))
    approved_label = Gtk.Label("approved: " + str(approved))

    subscription_i = Gtk.Image()
    if subscription == None:
        subscription = 'none'

    subscription_i.set_from_pixbuf(
        org.wayround.pyabber.icondb.get('subscription_{}'.format(subscription))
        )

    available_i = Gtk.Image()
    if available:
        available_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('contact_available'))
    else:
        available_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('contact_unavailable'))

    show_i = Gtk.Image()

    if not show in ['available', 'unavailable', 'dnd', 'away', 'xa', 'chat']:
        show = 'unknown'
    show_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('show_{}'.format(show)))

    status_box.pack_start(available_i, False, False, 0)
    status_box.pack_start(show_i, False, False, 0)
    status_box.pack_start(subscription_i, False, False, 0)
    status_box.pack_start(ask_label, False, False, 3)
    status_box.pack_start(approved_label, False, False, 3)

    title_label_text = ''
    if isinstance(name, str) and name != '' and not name.isspace():
        title_label_text = name
    elif isinstance(nick, str) and nick != '' and  not nick.isspace():
        title_label_text = nick
    else:
        title_label_text = bare_jid

    title_label = Gtk.Label(title_label_text)
    title_label.set_alignment(0, 0.5)

    jid_label = Gtk.Label(bare_jid)
    jid_label.set_alignment(0, 0.5)

    status_text_label = Gtk.Label(status)
    status_text_label.set_alignment(0, 0)

    img = Gtk.Image()
    img.set_alignment(0.5, 0)
    img.set_margin_right(5)
    if not userpic:
        img.set_from_stock('gtk-missing-image', Gtk.IconSize.BUTTON)
    else:
        img.set_from_pixbuf(userpic)

    text_info_box.pack_start(title_label, False, False, 0)
    text_info_box.pack_start(jid_label, False, False, 0)
    text_info_box.pack_start(status_text_label, True, True, 0)
    text_info_box.pack_start(status_box, False, False, 0)


    main_horizontal_box.pack_start(img, False, False, 0)
    main_horizontal_box.pack_start(text_info_box, True, True, 0)

    main_box.pack_start(main_horizontal_box, True, True, 0)

    ow.add(main_box)
    ow.show_all()
    main_box.draw(cr)
    ow.destroy()

def draw_resource_cell(
    cr, width, height,
    resource, available, show, status, has_new_messages
    ):

    ow = Gtk.OffscreenWindow()
    ow.set_default_size(width, height)

    main_box = Gtk.Box()
    main_box.set_orientation(Gtk.Orientation.HORIZONTAL)

    resource_l = Gtk.Label(str(resource))
    available_i = Gtk.Image()
    if available:
        available_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('contact_available'))
    else:
        available_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('contact_unavailable'))

    show_i = Gtk.Image()

    if not show in ['available', 'unavailable', 'dnd', 'away', 'xa', 'chat']:
        show = 'unknown'
    show_i.set_from_pixbuf(org.wayround.pyabber.icondb.get('show_{}'.format(show)))

    status_l = Gtk.Label(str(status))

    main_box.pack_start(available_i, False, False, 0)
    main_box.pack_start(show_i, False, False, 0)
    main_box.pack_start(resource_l, False, False, 3)
    main_box.pack_start(status_l, False, False, 3)

    # FIXME: crap! : Pango Attributes are not introspectable... :( need to do
    # with this something

#    attr_list = Pango.AttrList()
##    attr_list.insert(Pango.Weight.BOLD)
#    font_desc = Pango.FontDescription()
#    font_desc.set_weight(Pango.Weight.BOLD)
#
#    attr_font_desc = Pango.AttrFontDesc()
#    attr_font_desc.
#    resource_l.set_attributes(attr_list)

    ow.add(main_box)
    ow.show_all()
    main_box.draw(cr)
    ow.destroy()

class RosterWidget:

    def __init__(self, treeview, main_window):

        self._self_bare_jid = None

        self._lock = threading.Lock()

        self._data = {}

        self._treeview = treeview
        self._main_window = main_window

        self._treeview.connect('button-release-event', self._on_treeview_buttonpress)
#        self._treeview.connect('key-press-event', self._on_treeview_keypress)

        _c = Gtk.TreeViewColumn()
        _r = RosterCellRenderer()
        _c.pack_start(_r, False)

        for i in range(len(ROW_CELL_NAMES)):
            _c.add_attribute(_r, ROW_CELL_NAMES[i], i)

        _c.set_title('Roster')
        self._treeview.append_column(_c)

        self._store = Gtk.TreeStore(
            str, str, str, str, bool, str, str, str,
            GdkPixbuf.Pixbuf, bool, str, str, bool
            )

        self._treeview.set_model(self._store)
        self._treeview.set_headers_visible(False)

        self._division_add('Self', 'self')
        self._division_add('Grouped Contacts', 'groups')
        self._division_add('Ungrouped Contacts', 'ungrouped')
        self._division_add('Ask', 'ask')
        self._division_add('To', 'to')
        self._division_add('From', 'from')
        self._division_add('None', 'none')
        self._division_add('Transports', 'transport')
        self._division_add('Not in roster', 'hard')

    def _division_add(self, title, nick):
        values = [None] * ROW_CELL_NAMES_COUNT

        values[ROW_CELL_CELL_TYPE] = 'division'
        values[ROW_CELL_NAME_OR_TITLE] = title
        values[ROW_CELL_NICK] = nick

        self._store.append(
            None,
            values
            )

    def _division_get_iter(self, nick):
        """
        Returns division iter
        """
        ret = None

        ifr = self._store.get_iter_first()

        while ifr:

            if self._store[ifr][ROW_CELL_NICK] == nick:
                ret = ifr
                break

            ifr = self._store.iter_next(ifr)

        return ret

    def _group_add(self, group):
        """
        Create group if not exists
        """
        if not self._group_get_iter(group):
            division_iter = self._division_get_iter('groups')

            values = [None] * ROW_CELL_NAMES_COUNT
            values[ROW_CELL_CELL_TYPE] = 'group'
            values[ROW_CELL_NAME_OR_TITLE] = group

            self._store.append(
                division_iter,
                values
                )

    def _group_get_iter(self, name):
        """
        Returns TreeIter of the group

        If not found - None is returned
        """
        ret = None

        group_iter = self._division_get_iter('groups')

        child = self._store.iter_children(group_iter)

        while child != None:

            if self._store[child][ROW_CELL_NAME_OR_TITLE] == name:
                ret = child
                break

            child = self._store.iter_next(child)

        return ret


    def _groups_list(self):

        """
        Returns str list
        """

        ret = []

        group_iter = self._division_get_iter('groups')

        child = self._store.iter_children(group_iter)

        while child != None:
            ret.append(self._store[child][ROW_CELL_NAME_OR_TITLE])
            child = self._store.iter_next(child)

        return ret

    def _mode_check(self, mode):
        if not mode in ['contact', 'resource']:
            raise ValueError("Invalid contact/resource mode")

    def _level_contact_add(self, itera, value, mode='contact'):

        self._mode_check(mode)

        itera_type = self._store[itera][ROW_CELL_CELL_TYPE]

        if ((mode == 'contact' and not itera_type in ['division', 'group'])
            or (mode == 'resource' and itera_type != 'contact')):
            raise Exception(
                "pointed node type is invalid for adding {}".format(mode)
                )

        sr = None
        if mode == 'contact':
            sr = self._level_contact_get_iter(itera, value)
        else:
            sr = self._level_resource_get_iter(itera, value)

        if not sr:

            values = [None] * ROW_CELL_NAMES_COUNT

            values[ROW_CELL_CELL_TYPE] = mode

            if mode == 'contact':
                values[ROW_CELL_BARE_JID] = value
            else:
                values[ROW_CELL_RESOURCE] = value

            self._store.append(
                itera,
                values
                )

        return


    def _level_resource_add(self, itera, resource):
        return self._level_contact_add(itera, value=resource, mode='resource')

    def _level_contact_get_iter(self, itera, bare_jid, mode='contact'):
        """
        Gets contact TreeIter

        If not found - None is returned
        """

        self._mode_check(mode)

        ret = None

        child = self._store.iter_children(itera)

        looking_for_cell = None

        if mode == 'contact':
            looking_for_cell = ROW_CELL_BARE_JID
        else:
            looking_for_cell = ROW_CELL_RESOURCE

        while child:

            if (self._store[child][ROW_CELL_CELL_TYPE] == mode
                and self._store[child][looking_for_cell] == bare_jid):
                ret = child
                break

            child = self._store.iter_next(child)

        return ret

    def _level_resource_get_iter(self, itera, resource):
        return self._level_contact_get_iter(itera, bare_jid=resource, mode='resource')

    def _level_contact_remove(self, itera, bare_jid, mode='contact'):

        self._mode_check(mode)

        res = None
        if mode == 'contact':
            res = self._level_contact_get_iter(itera, bare_jid)
        else:
            res = self._level_resource_get_iter(itera, bare_jid)

        if res:
            self._store.remove(res)

        return

    def _level_resource_remove(self, itera, resource):
        return self._level_contact_remove(itera, bare_jid=resource, mode='resource')

    def _level_contact_get(self, itera, bare_jid, mode='contact'):

        self._mode_check(mode)

        ret = None

        it = None
        if mode == 'contact':
            it = self._level_contact_get_iter(itera, bare_jid)
        else:
            it = self._level_resource_get_iter(itera, bare_jid)

        if it:
            _ts = self._store[it]
            ret = {
#                'cell_type': _ts[ROW_CELL_CELL_TYPE],
                'name_or_title': _ts[ROW_CELL_NAME_OR_TITLE],
                'bare_jid': _ts[ROW_CELL_BARE_JID],
                'resource': _ts[ROW_CELL_RESOURCE],
                'approved': _ts[ROW_CELL_APPROVED],
                'ask': _ts[ROW_CELL_ASK],
                'subscription': _ts[ROW_CELL_SUBSCRIPTION],
                'nick': _ts[ROW_CELL_NICK],
                'userpic': _ts[ROW_CELL_USERPIC],
                'available': _ts[ROW_CELL_AVAILABLE],
                'show': _ts[ROW_CELL_SHOW],
                'status': _ts[ROW_CELL_STATUS],
                'has_new_messages': _ts[ROW_CELL_HAS_NEW_MESSAGES]
                }

        return ret

    def _level_resource_get(self, itera, resource):
        return self._level_contact_get(itera, bare_jid=resource, mode='resource')

    def _level_contacts_get_list(self, itera, mode='contact'):

        self._mode_check(mode)

        values = set()

        looking_for_cell = None

        if mode == 'contact':
            looking_for_cell = ROW_CELL_BARE_JID
        else:
            looking_for_cell = ROW_CELL_RESOURCE

        child = self._store.iter_children(itera)

        while child:

            if self._store[child][ROW_CELL_CELL_TYPE] == mode:
                values.add(self._store[child][looking_for_cell])

            child = self._store.iter_next(child)

        ret = values

        return ret

    def _level_resources_get_list(self, itera):
        return self._level_contacts_get_list(itera, mode='resource')



    def _level_contact_set(
        self,
        itera,
        value,
        name_or_title=None,
        approved=None,
        ask=None,
        subscription=None,
        nick=None,
        userpic=None,
        available=None,
        show=None,
        status=None,
        has_new_messages=None,
        mode='contact'
        ):
        """
        Set contact parameters in selected groups's or division's child level
        """

        self._mode_check(mode)

        itera_type = self._store[itera][ROW_CELL_CELL_TYPE]

        if ((mode == 'contact' and not itera_type in ['division', 'group'])
            or (mode == 'resource' and itera_type != 'contact')):
            raise Exception(
                "pointed node type is invalid for setting {}".format(mode)
                )

        values = [
            ROW_CELL_CELL_TYPE, mode
            ]

        if mode == 'contact':
            values += [ROW_CELL_BARE_JID, value]
        else:
            values += [ROW_CELL_RESOURCE, value]

        for i in LEVEL_CONTACT_SET_FILL_LIST:

            er = eval(ROW_CELL_NAMES[i])

            if er != None:
                values += [i, er]

        ti = ROW_CELL_RESOURCE
        if mode == 'contact':
            ti = ROW_CELL_BARE_JID

        child = self._store.iter_children(itera)

        while child:

            if self._store[child][ti] == value:
                self._store.set(
                    child,
                    *values
                    )
                break

            child = self._store.iter_next(child)

        return

    def _level_resource_set(
            self,
            itera, resource,
            name_or_title=None,
            approved=None,
            ask=None,
            subscription=None,
            nick=None,
            userpic=None,
            available=None,
            show=None,
            status=None,
            has_new_messages=None
            ):
        """
        Set resource parameters in selected contact's child level
        """
        return self._level_contact_set(
            itera, resource, name_or_title, approved, ask,
            subscription, nick, userpic, available, show,
            status, has_new_messages, mode='resource'
            )

    def _get_contact_row_refs(self, bare_jid):

        ret = []

        groups = self._groups_list()

        for i in groups:
            group_iter = self._group_get_iter(i)
            itera = self._level_contact_get_iter(group_iter, bare_jid)

            if itera:
                ret.append(Gtk.TreeRowReference.new(self._store, self._store.get_path(itera)))

        for i in [
            'ungrouped', 'none', 'hard', 'transport', 'to', 'from', 'ask',
            'self'
            ]:

            it = self._division_get_iter(i)
            if it:
                itera = self._level_contact_get_iter(
                    it,
                    bare_jid
                    )

                if itera:
                    ret.append(Gtk.TreeRowReference.new(self._store, self._store.get_path(itera)))

        return ret

    def _sync_treeview_with_data_contacts_resources(self):

        for bare_jid in self._data.keys():

            all_contact_row_refs = self._get_contact_row_refs(bare_jid)

            for resource in self._data[bare_jid]['full'].keys():

                data = self._data[bare_jid]['full'][resource]

                for i in all_contact_row_refs:
                    pat = i.get_path()
                    if pat:
                        it = self._store.get_iter(pat)
                        if it:
                            self._level_resource_add(
                                it,
                                resource
                                )
                    pat = i.get_path()
                    if pat:
                        it = self._store.get_iter(pat)
                        if it:
                            self._level_resource_set(
                                it,
                                resource,
                                **data
                                )

                # TODO: is it a memory leak?
                #                for i in all_contact_row_refs:
                #                    if i.valid():
                #                        i.free()

        return

    def _sync_treeview_with_data_contacts(self):

        group_names = self._groups_list()

        for i in group_names:
            for j in self._data.keys():
                if not i in self._data[j]['bare']['groups'] or j == self._self_bare_jid:
                    g_iter = self._group_get_iter(i)
                    self._level_contact_remove(g_iter, j)

        for i in self._data.keys():
            for j in self._data[i]['bare']['groups']:

                self._group_add(j)

                g_iter = self._group_get_iter(j)
                self._level_contact_add(g_iter, i)

                g_iter = self._group_get_iter(j)
                self._level_contact_set(
                    g_iter, i, **self._data[i]['bare']
                    )

        for i in [
            'ungrouped', 'none', 'hard', 'transport', 'to', 'from', 'ask',
            'self'
            ]:

            div_iter = self._division_get_iter(i)
            lst = self._level_contacts_get_list(div_iter)

            for j in lst:
                if not j in self._data:
                    div_iter = self._division_get_iter(i)
                    self._level_contact_remove(div_iter, j)

        for i in self._data.keys():

            data = copy.deepcopy(self._data[i]['bare'])

            is_transport = False
            not_in_roster = False
            groups = set()

            if 'is_transport' in data:
                is_transport = data['is_transport']
                del(data['is_transport'])

            if 'not_in_roster' in data:
                not_in_roster = data['not_in_roster']
                del(data['not_in_roster'])

            if 'groups' in data:
                groups = data['groups']
                del(data['groups'])

            itera = self._division_get_iter('hard')

            if not_in_roster and i != self._self_bare_jid:
                self._level_contact_add(itera, i)
                itera = self._division_get_iter('hard')
                self._level_contact_set(itera, i, **data)

            else:
                self._level_contact_remove(itera, i)

            itera = self._division_get_iter('transport')

            if (is_transport
                and not not_in_roster
                and i != self._self_bare_jid):

                self._level_contact_add(itera, i)
                itera = self._division_get_iter('transport')
                self._level_contact_set(itera, i, **data)

            else:
                self._level_contact_remove(itera, i)

            itera = self._division_get_iter('ungrouped')

            if (len(groups) == 0
                and not is_transport
                and not not_in_roster
                and i != self._self_bare_jid):

                self._level_contact_add(itera, i)
                itera = self._division_get_iter('ungrouped')
                self._level_contact_set(itera, i, **data)

            else:
                self._level_contact_remove(itera, i)

            for j in ['to', 'from', 'none']:

                itera = self._division_get_iter(j)

                if (data['subscription'] == j
                    and not not_in_roster
                    and i != self._self_bare_jid):

                    self._level_contact_add(itera, i)
                    itera = self._division_get_iter(j)
                    self._level_contact_set(itera, i, **data)

                else:
                    self._level_contact_remove(itera, i)

            itera = self._division_get_iter('ask')

            if data['ask'] != None and i != self._self_bare_jid:
                self._level_contact_add(itera, i)
                itera = self._division_get_iter('ask')
                self._level_contact_set(itera, i, **data)

            else:
                self._level_contact_remove(itera, i)

            itera = self._division_get_iter('self')

            if i == self._self_bare_jid:
                self._level_contact_add(itera, i)
                itera = self._division_get_iter('self')
                self._level_contact_set(itera, i, **data)

            else:
                self._level_contact_remove(itera, i)

        return


    def _sync_treeview_with_data(self):
        self._sync_treeview_with_data_contacts()
        self._sync_treeview_with_data_contacts_resources()


    def set_self(self, self_bare_jid):
        self._self_bare_jid = self_bare_jid

    def set_contact_resource(
        self,
        bare_jid,
        resource,
        available=None,
        show=None,
        status=None,
        not_in_roster=None
        ):

        self.set_contact(
            bare_jid=bare_jid,
            available=available,
            show=show,
            status=status,
            sync=False
            )

        self._lock.acquire()

        if not resource in self._data[bare_jid]['full']:
            self._data[bare_jid]['full'][resource] = {}

        for i in [
            'available',
            'show',
            'status'
            ]:

            ev = eval(i)
            if ev != None:
                self._data[bare_jid]['full'][resource][i] = ev

            if not i in self._data[bare_jid]['full'][resource]:
                self._data[bare_jid]['full'][resource][i] = None

        self._sync_treeview_with_data()

        self._lock.release()

        return

    def set_contact(
        self,
        bare_jid,
        name_or_title=None, groups=None,
        approved=None, ask=None, subscription=None,
        nick=None, userpic=None, available=None, show=None, status=None,
        has_new_messages=None,
        not_in_roster=None, is_transport=None, sync=True
        ):

        """
        Change indication parameters

        For all parameters (except bare_jid off course) None value means - do no
        change current indication.

        threadsafe using Lock()
        """

        self._lock.acquire()

        if not bare_jid in self._data:
            self._data[bare_jid] = {
                'bare':{},
                'full':{}
                }

        for i in [
            'name_or_title', 'groups',
            'approved', 'ask', 'subscription',
            'nick', 'userpic', 'available', 'show', 'status',
            'has_new_messages',
            'not_in_roster', 'is_transport'
            ]:

            ev = eval(i)
            if ev != None:
                self._data[bare_jid]['bare'][i] = ev

            if not i in self._data[bare_jid]['bare']:
                self._data[bare_jid]['bare'][i] = None

        if ask == None:
            self._data[bare_jid]['bare']['ask'] = None

        if self._data[bare_jid]['bare']['groups'] == None:
            self._data[bare_jid]['bare']['groups'] = set()

        if sync:
            self._sync_treeview_with_data()

        self._lock.release()

        return

    def get_contacts(self):

        self._lock.acquire()

        ret = list(self._data.keys())

        self._lock.release()

        return ret

    def get_data(self):

        self._lock.acquire()

        ret = copy.deepcopy(self._data)

        self._lock.release()

        return ret

    def get_groups(self):

        self._lock.acquire()

        ret = self._groups_list()

        self._lock.release()

        return ret

    def forget(self, bare_jid):

        self._lock.acquire()

        if bare_jid in self._data:
            del self._data[bare_jid]

        self._sync_treeview_with_data()

        self._lock.release()

#    def _on_treeview_keypress(self, widget, event):
#        print("keypress")

    def _on_treeview_buttonpress(self, widget, event):

        if event.button == Gdk.BUTTON_SECONDARY:

            self._lock.acquire()

            sel = widget.get_selection()

            selec = sel.get_selected_rows()

            model = selec[0]
            rows = selec[1]

            if len(rows) != 0:

                pat = Gtk.TreeRowReference.new(model, rows[0])

                row = model[rows[0]]
                row_t = row[ROW_CELL_CELL_TYPE]
                bj = row[ROW_CELL_BARE_JID]
                res = row[ROW_CELL_RESOURCE]

                if row_t in ['contact', 'resource']:

                    if row_t == 'contact':
                        bare_jid = bj
                        resource = ''

                        jid = org.wayround.xmpp.core.jid_from_str(bare_jid)

                        org.wayround.pyabber.contact_popup_menu.contact_popup_menu(
                            self._main_window.controller,
                            jid.bare()
                            )


                    if row_t == 'resource':
                        resource = res
                        itrap = pat.get_path()
                        if itrap:
                            path_iter = model.get_iter(itrap)

                            if path_iter != None:
                                parent = model.iter_parent(
                                    path_iter
                                    )
                                if parent:
                                    parent_row = model[parent]
                                    bare_jid = parent_row[ROW_CELL_BARE_JID]

                                    jid = org.wayround.xmpp.core.jid_from_str(
                                        bare_jid + '/' + resource
                                        )

                                    org.wayround.pyabber.contact_popup_menu.contact_popup_menu(
                                        self._main_window.controller,
                                        jid.full()
                                        )


            self._lock.release()
