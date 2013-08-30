
import threading

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import PangoCairo
from django.conf.locale import ro

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
    subscription_label = Gtk.Label("subscription: " + str(subscription))
    available_l = Gtk.Label("available: " + str(available))
    show_l = Gtk.Label("show: " + str(show))

    status_box.pack_start(ask_label, False, False, 3)
    status_box.pack_start(approved_label, False, False, 3)
    status_box.pack_start(subscription_label, False, False, 3)
    status_box.pack_start(available_l, False, False, 3)
    status_box.pack_start(show_l, False, False, 3)

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

    resource_l = Gtk.Label("resource: " + str(resource))
    available_l = Gtk.Label("available: " + str(available))
    show_l = Gtk.Label("show: " + str(show))
    status_l = Gtk.Label("status: " + str(status))

    main_box.pack_start(resource_l, False, False, 3)
    main_box.pack_start(available_l, False, False, 3)
    main_box.pack_start(show_l, False, False, 3)
    main_box.pack_start(status_l, False, False, 3)

    ow.add(main_box)
    ow.show_all()
    main_box.draw(cr)
    ow.destroy()

class RosterWidget:

    def __init__(self, treeview):

        self._lock = threading.Lock()

        self._treeview = treeview

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

        # TODO: check what self is sane and works where it need's to work
        self._division_add('Self', 'self')
        self._division_add('Grouped Contacts', 'groups')
        self._division_add('Ungrouped Contacts', 'ungrouped')
        self._division_add('Transports', 'transport')
        self._division_add('Ask', 'ask')
        self._division_add('To', 'to')
        self._division_add('From', 'from')
        self._division_add('None', 'none')
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
                "pointed node type is invalid for adding {}".format(mode)
                )

        fill_list = [
            ROW_CELL_NAME_OR_TITLE,
            ROW_CELL_APPROVED,
            ROW_CELL_ASK,
            ROW_CELL_SUBSCRIPTION,
            ROW_CELL_NICK,
            ROW_CELL_USERPIC,
            ROW_CELL_AVAILABLE,
            ROW_CELL_SHOW,
            ROW_CELL_STATUS,
            ROW_CELL_HAS_NEW_MESSAGES,
            ]

        values = [
            ROW_CELL_CELL_TYPE, mode
            ]

        if mode == 'contact':
#            values += [ROW_CELL_RESOURCE, None]
            values += [ROW_CELL_BARE_JID, value]
        else:
            values += [ROW_CELL_RESOURCE, value]
#            values += [ROW_CELL_BARE_JID, None]

        for i in fill_list:

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


    def _division_get_iter(self, nick):
        """
        Returns division iter
        """
        ret = None

        ifr = self._store.get_iter_first()

        if not ifr:
            ret = None
        else:

            while ifr != None:

                if self._store[ifr][ROW_CELL_NICK] == nick:
                    ret = ifr
                    break

                ifr = self._store.iter_next(ifr)

        return ret

    def _group_contact_set(
        self,
        group,
        bare_jid,
        name_or_title,
        approved, ask, subscription,
        nick, userpic, available,
        show, status, has_new_messages
        ):

        if self._group_get_iter(group):

            group_iter = self._group_get_iter(group)

            self._level_contact_set(
                group_iter,
                bare_jid, name_or_title, approved, ask,
                subscription, nick, userpic, available, show,
                status, has_new_messages
                )


        return

    def _group_contact_add(self, group, bare_jid):

        """
        Add contact to group if it isn't already there

        This function is only for adding contact, it's not for populating it -
        for populating all contacts of this bare_jid use
        :meth:`_group_contact_set`
        """

        if not self._group_get_iter(group):
            self._group_add(group)

        group_iter = self._group_get_iter(group)

        self._level_contact_add(group_iter, bare_jid)


    def _group_contact_get(self, bare_jid):
        """
        Get contact data from one of the groups or from ungrouped div
        """

        ret = None

        groups = self._get_contact_groups(bare_jid)

        if len(groups) == 0:
            div_iter = self._division_get_iter('ungrouped')
            ret = self._level_contact_get(div_iter, bare_jid)
        else:
            group_iter = self._group_get_iter(groups[0])
            ret = self._level_contact_get(group_iter, bare_jid)

        return ret

    def _group_contact_get_iter(self, group, bare_jid):
        """
        Gets contact TreeIter

        If not found - None is returned
        """
        git = self._group_get_iter(group)

        ret = self._level_contact_get_iter(git, bare_jid)

        return ret

    def _group_contact_remove(self, group, bare_jid):
        """
        Remove contact from group

        Removing group if it's empty
        """

        itera = self._group_get_iter(group)
        self._level_contact_remove(itera, bare_jid)

        group_iter = self._group_get_iter(group)
        count = self._store.iter_n_children(group_iter)

        if count == 0:
            self._group_del(group_iter)

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
            self._group_contact_add(i, bare_jid)

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


    def _groups_remove_contact(self, bare_jid, groups=None):
        """
        Remove contact from all groups or from named groups
        """

        if groups == None:
            groups = self._groups_list()

        for i in groups:
            self._group_contact_remove(i, bare_jid)


    def _groups_set_contact(
        self, groups, bare_jid,
        name_or_title,
        approved, ask, subscription,
        nick, userpic,
        available, show, status,
        has_new_messages
        ):

        if groups == None:
            groups = self._get_contact_groups(bare_jid)

        groups = set(groups)
        a_groups = set(self._groups_list())
        m_groups = a_groups - groups
        p_groups = set(groups)

        self._groups_remove_contact(bare_jid, m_groups)
        self._groups_add_contact(p_groups, bare_jid)

        for i in groups:
            self._group_contact_set(
                i,
                bare_jid,
                name_or_title,
                approved, ask, subscription,
                nick, userpic,
                available, show, status,
                has_new_messages
                )

        return

    def _get_contact_groups(self, bare_jid):

        groups = self._groups_list()

        found_in = []

        for i in groups:

            it = self._group_contact_get_iter(i, bare_jid)

            if it:
                found_in.append(i)

        return found_in

    def _get_contact_list(self):

        ret = set()

        for i in self._groups_list():
            ret |= self._level_contacts_get_list(self._group_get_iter(i))

        for i in ['ungrouped', 'transport', 'to', 'from', 'none' , 'hard']:
            ret |= self._level_contacts_get_list(self._division_get_iter(i))

        return ret


    def set_contact_resource(
        self,
        bare_jid,
        resource,
        available=None,
        show=None,
        status=None,
        not_in_roster=None,
        is_self=False
        ):

        print('set_contact_resource')

        self.set_contact(
            bare_jid=bare_jid,
            available=available,
            show=show, status=status,
            is_self=is_self
            )

        self._lock.acquire()


        if is_self:

            self_div = self._division_get_iter('self')

            c_iter = self._level_contact_get_iter(self_div, bare_jid)

            self._level_resource_add(c_iter, resource)

            self._level_resource_set(
                c_iter, resource,
                available=available,
                show=show,
                status=status,
                )

        else:

            all_contact_resources_with_data = {}

            all_contact_iterators = self._get_contact_iterators(bare_jid)

            for i in all_contact_iterators:
                cc_res_list = self._level_resources_get_list(i)

                for j in cc_res_list:

                    if not j in all_contact_resources_with_data:

                        res_iter = self._level_resource_get_iter(i, j)

                        res = self._level_resource_get(
                            res_iter,
                            j
                            )

                        if res:
                            all_contact_resources_with_data[j] = res

            if resource:
                if not resource in all_contact_resources_with_data:
                    all_contact_resources_with_data[resource] = {}

                if available:
                    all_contact_resources_with_data[resource]['available'] = available

                if show:
                    all_contact_resources_with_data[resource]['show'] = show

                if status:
                    all_contact_resources_with_data[resource]['status'] = status

            for key in all_contact_resources_with_data.keys():

                for i in all_contact_iterators:

                    self._level_resource_add(i, key)

                    self._level_resource_set(
                        i, key,
                        name_or_title=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_NAME_OR_TITLE], None),
                        approved=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_APPROVED], None),
                        ask=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_ASK], None),
                        subscription=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_SUBSCRIPTION], None),
                        nick=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_NICK], None),
                        userpic=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_USERPIC], None),
                        available=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_AVAILABLE], None),
                        show=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_SHOW], None),
                        status=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_STATUS], None),
                        has_new_messages=all_contact_resources_with_data[key].get(ROW_CELL_NAMES[ROW_CELL_HAS_NEW_MESSAGES], None),
                        )

        self._lock.release()

        return

    def set_contact(
        self,
        bare_jid,
        name_or_title=None, groups=None,
        approved=None, ask=None, subscription=None,
        nick=None, userpic=None, available=None, show=None, status=None,
        has_new_messages=None,
        not_in_roster=None, is_transport=None, is_self=False
        ):

        print('set_contact')


        """
        Change indication parameters

        For all parameters (except bare_jid off course) None value means - do no
        change current indication.

        threadsafe using Lock()
        """

        # TODO: I think I'm too paranoic with iterators lifetime here. research
        # and optimizations are requiredw

        adding_new_contact = False

        if is_self:

            self._lock.acquire()

            itera = self._division_get_iter('self')

            contacts = self._level_contacts_get_list(itera)

            for i in contacts:
                if i != bare_jid:
                    itera = self._division_get_iter('self')
                    self._level_contact_remove(itera, i)


            itera = self._division_get_iter('self')

            self._level_contact_add(
                itera,
                bare_jid
                )

            itera = self._division_get_iter('self')

            self._level_contact_set(
                itera, bare_jid, name_or_title, approved, ask,
                subscription, nick, userpic, available, show,
                status, has_new_messages
                )

            self._lock.release()

        else:

            self._lock.acquire()

            adding_new_contact = self._get_contact(bare_jid) == None

            if groups == None:
                groups = self._get_contact_groups(bare_jid)

            if not_in_roster or is_transport:
                groups = []

            self._groups_set_contact(
                groups, bare_jid, name_or_title, approved, ask,
                subscription, nick, userpic, available, show,
                status, has_new_messages
                )

            itera = self._division_get_iter('hard')

            if not_in_roster:

                self._level_contact_add(
                    itera,
                    bare_jid
                    )

                self._level_contact_set(
                    itera, bare_jid, name_or_title, approved, ask,
                    subscription, nick, userpic, available, show,
                    status, has_new_messages
                    )
            else:

                self._level_contact_remove(
                    itera,
                    bare_jid
                    )

            itera = self._division_get_iter('transport')

            if is_transport and not not_in_roster:

                self._level_contact_add(
                    itera,
                    bare_jid
                    )

                self._level_contact_set(
                    itera, bare_jid, name_or_title, approved, ask,
                    subscription, nick, userpic, available, show,
                    status, has_new_messages
                    )
            else:

                self._level_contact_remove(
                    itera,
                    bare_jid
                    )


            itera = self._division_get_iter('ungrouped')

            if len(groups) == 0 and not is_transport and not not_in_roster:

                self._level_contact_add(
                    itera,
                    bare_jid
                    )

                self._level_contact_set(
                    itera, bare_jid, name_or_title, approved, ask,
                    subscription, nick, userpic, available, show,
                    status, has_new_messages
                    )
            else:

                self._level_contact_remove(
                    itera,
                    bare_jid
                    )

            for i in ['to', 'from', 'none']:

                itera = self._division_get_iter(i)

                if subscription == i and not not_in_roster:

                    self._level_contact_add(
                        itera,
                        bare_jid
                        )

                    self._level_contact_set(
                        itera, bare_jid, name_or_title, approved, ask,
                        subscription, nick, userpic, available, show,
                        status, has_new_messages
                        )
                else:

                    self._level_contact_remove(
                        itera,
                        bare_jid
                        )

            itera = self._division_get_iter('ask')

            if ask != None:

                self._level_contact_add(
                    itera,
                    bare_jid
                    )

                self._level_contact_set(
                    itera, bare_jid, name_or_title, approved, ask,
                    subscription, nick, userpic, available, show,
                    status, has_new_messages
                    )
            else:

                self._level_contact_remove(
                    itera,
                    bare_jid
                    )

            self._lock.release()

        if adding_new_contact:
            self._sync_resources(bare_jid)

        return

    def _sync_resources(self, bare_jid):
        self.set_contact_resource(
            bare_jid, resource=None, available=None,
            show=None, status=None, is_self=False
            )

    def get_contact(self, bare_jid):
        """
        Get contact data

        threadsafe using Lock()
        """

        self._lock.acquire()
        ret = self._get_contact(bare_jid)
        self._lock.release()

        return ret

    def _get_contact_iterators(self, bare_jid):

        ret = []

        groups = self._get_contact_groups(bare_jid)

        for i in groups:
            group_iter = self._group_get_iter(i)
            itera = self._level_contact_get_iter(group_iter, bare_jid)

            if itera:
                ret.append(itera)

        for i in [
            'ungrouped', 'none', 'hard', 'transport', 'to', 'from', 'ask'
            ]:

            itera = self._level_contact_get_iter(
                self._division_get_iter(i),
                bare_jid
                )

            if itera:
                ret.append(itera)

        return ret

    def _get_contact(self, bare_jid):

        ret = None

        cont_data = self._group_contact_get(bare_jid)

        if cont_data != None:
            cont_data['is_transport'] = False
            cont_data['not_in_roster'] = False

        if cont_data == None:

            for i in ['to', 'from', 'ask']:

                cont_data = self._level_contact_get(
                    self._division_get_iter(i),
                    bare_jid
                    )

                if cont_data != None:
                    cont_data['is_transport'] = None
                    cont_data['not_in_roster'] = False

                    break


        if cont_data == None:

            cont_data = self._level_contact_get(
                self._division_get_iter('hard'),
                bare_jid
                )

            if cont_data != None:
                cont_data['is_transport'] = False
                cont_data['not_in_roster'] = True

        if cont_data == None:
            cont_data = self._level_contact_get(
                self._division_get_iter('transport'),
                bare_jid
                )

            if cont_data != None:
                cont_data['is_transport'] = True
                cont_data['not_in_roster'] = False

        if cont_data:
            cont_data['groups'] = list(self._get_contact_groups(bare_jid))
            ret = cont_data

        return ret

    def get_contacts(self):

        self._lock.acquire()

        ret = {}

        lst = list(self._get_contact_list())

        for i in lst:
            ret[i] = self._get_contact(i)

        self._lock.release()

        return ret

