
import sys
import collections
import json

from gi.repository import Gtk

import wayround_org.utils.gtk
import wayround_org.utils.types

import wayround_org.xmpp.core
import wayround_org.xmpp.privacy


class PrivacyEditor:

    def __init__(self, to_jid, from_jid, stanza_processor):

        if not isinstance(to_jid, str):
            raise ValueError("`to_jid' must be str")

        if not isinstance(from_jid, wayround_org.xmpp.core.JID):
            raise ValueError("`from_jid' must be wayround_org.xmpp.core.JID")

        if not isinstance(
            stanza_processor,
            wayround_org.xmpp.core.StanzaProcessor
            ):
            raise ValueError(
        "`stanza_processor' must be wayround_org.xmpp.core.StanzaProcessor"
                )

        self._to_jid = to_jid
        self._from_jid = from_jid
        self._stanza_processor = stanza_processor

        l_frame = Gtk.Frame()
        l_frame.set_label("List Lists")

        l_box = Gtk.Box()
        l_box.set_margin_top(5)
        l_box.set_margin_start(5)
        l_box.set_margin_end(5)
        l_box.set_margin_bottom(5)
        l_box.set_spacing(5)
        l_frame.add(l_box)
        l_box.set_orientation(Gtk.Orientation.VERTICAL)

        l_grid = Gtk.Grid()
        l_grid.set_column_spacing(5)
        l_grid.set_row_spacing(5)

        active_combobox = Gtk.ComboBox()
        self._active_combobox = active_combobox
        active_combobox.set_hexpand(True)

        default_combobox = Gtk.ComboBox()
        self._default_combobox = default_combobox
        default_combobox.set_hexpand(True)

        active_combobox.set_id_column(0)
        default_combobox.set_id_column(0)

        renderer_text = Gtk.CellRendererText()
        active_combobox.pack_start(renderer_text, True)
        active_combobox.add_attribute(renderer_text, "text", 0)

        default_combobox.pack_start(renderer_text, True)
        default_combobox.add_attribute(renderer_text, "text", 0)

        list_model = Gtk.ListStore(str)

        active_combobox.set_model(list_model)
        default_combobox.set_model(list_model)

        active_save_button = Gtk.Button("Save")
        default_save_button = Gtk.Button("Save")

        active_save_button.connect(
            'clicked',
            self._on_active_save_button_clicked
            )

        default_save_button.connect(
            'clicked',
            self._on_default_save_button_clicked
            )

        active_checkbutton = Gtk.CheckButton.new_with_label("Active")
        default_checkbutton = Gtk.CheckButton.new_with_label("Default")

        active_checkbutton.connect(
            "toggled",
            self._on_active_checkbutton_toggled
            )

        default_checkbutton.connect(
            "toggled",
            self._on_default_checkbutton_toggled
            )

        self._active_checkbutton = active_checkbutton
        self._default_checkbutton = default_checkbutton

        l_grid.attach(active_checkbutton, 0, 0, 1, 1)
        l_grid.attach(default_checkbutton, 0, 1, 1, 1)

        l_grid.attach(active_combobox, 1, 0, 1, 1)
        l_grid.attach(default_combobox, 1, 1, 1, 1)

        l_grid.attach(active_save_button, 2, 0, 1, 1)
        l_grid.attach(default_save_button, 2, 1, 1, 1)
        l_box.pack_start(l_grid, False, False, 0)

        l_list_frame = Gtk.Frame()
        l_list_frame.set_label("Lists Already on Server")

        l_list_box = Gtk.Box()
        l_list_box.set_spacing(5)
        l_list_box.set_orientation(Gtk.Orientation.VERTICAL)

        l_list_view = Gtk.TreeView()
        l_list_view_sw = Gtk.ScrolledWindow()
        l_list_view_sw.add(l_list_view)
        l_list_view_sw_frame = Gtk.Frame()
        l_list_view_sw_frame.add(l_list_view_sw)
        self._l_list_view = l_list_view

        c1 = Gtk.TreeViewColumn()
        cr1 = Gtk.CellRendererText()
        c1.pack_start(cr1, False)
        c1.add_attribute(cr1, 'text', 0)
        l_list_view.append_column(c1)
        l_list_view.set_headers_visible(False)

        l_list_view.set_model(list_model)
        l_list_bb = Gtk.ButtonBox()
        l_list_bb.set_spacing(5)

        l_list_box.pack_start(l_list_view_sw_frame, True, True, 0)
        l_list_box.pack_start(l_list_bb, False, False, 0)

        l_box.pack_start(l_list_box, True, True, 0)

        new_list_button = Gtk.Button("New")
        new_list_button.connect('clicked', self._on_new_list_button_clicked)

        delete_list_button = Gtk.Button("Delete")
        delete_list_button.connect(
            'clicked', self._on_delete_list_button_clicked
            )

        edit_list_button = Gtk.Button("Open (Edit)")
        edit_list_button.connect('clicked', self._on_edit_list_button_clicked)

        l_list_bb.pack_start(new_list_button, False, False, 0)
        l_list_bb.pack_start(delete_list_button, False, False, 0)
        l_list_bb.pack_start(edit_list_button, False, False, 0)

        r_frame = Gtk.Frame()
        r_frame.set_label("List Editing")

        r_box = Gtk.Box()
        r_box.set_margin_top(5)
        r_box.set_margin_start(5)
        r_box.set_margin_end(5)
        r_box.set_margin_bottom(5)
        r_box.set_spacing(5)
        r_frame.add(r_box)
        r_box.set_orientation(Gtk.Orientation.VERTICAL)

        r_name_box = Gtk.Box()
        r_name_box.set_spacing(5)
        r_name_box.set_orientation(Gtk.Orientation.HORIZONTAL)

        r_name_entry = Gtk.Entry()
        self._r_name_entry = r_name_entry
        r_open_button = Gtk.Button("(Re)Open")
        r_save_button = Gtk.Button("Save")

        r_open_button.connect('clicked', self._on_r_open_button_clicked)
        r_save_button.connect('clicked', self._on_r_save_button_clicked)

        r_name_box.pack_start(r_name_entry, True, True, 0)
        r_name_box.pack_start(r_open_button, False, False, 0)
        r_name_box.pack_start(r_save_button, False, False, 0)

        r_box.pack_start(r_name_box, False, False, 0)

        r_editor_text = Gtk.TextView()
        self._r_editor_text = r_editor_text
        r_editor_text_sw = Gtk.ScrolledWindow()
        r_editor_text_sw_frame = Gtk.Frame()
        r_editor_text_sw_frame.add(r_editor_text_sw)
        r_editor_text_sw.add(r_editor_text)

        r_box.pack_start(r_editor_text_sw_frame, True, True, 0)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        jid_box = Gtk.Box()
        jid_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        jid_box.set_margin_top(5)
        jid_box.set_margin_bottom(5)
        jid_box.set_margin_start(5)
        jid_box.set_margin_end(5)
        jid_box.set_spacing(5)

        jid_reload_button = Gtk.Button("(Re)Load")
        jid_reload_button.connect(
            'clicked', self._on_jid_reload_button_clicked
            )

        jid_entry = Gtk.Entry()
        self._jid_entry = jid_entry
        jid_box.pack_start(jid_entry, True, True, 0)
        jid_box.pack_start(jid_reload_button, False, False, 0)

        jid_frame = Gtk.Frame()
        jid_frame.set_label("Target JID")
        jid_frame.add(jid_box)

        paned = Gtk.Paned()
        paned.set_orientation(Gtk.Orientation.HORIZONTAL)
        paned.add1(l_frame)
        paned.add2(r_frame)

        b.pack_start(jid_frame, False, False, 0)
        b.pack_start(paned, True, True, 0)

        window = Gtk.Window()
        window.add(b)

        self._window = window

        self.set_jid(to_jid)

    def show(self):
        self._window.show_all()

    def set_jid(self, jid):

        self._to_jid = jid

        try:
            jid = wayround_org.xmpp.core.JID.new_from_string(jid)
        except:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't parse string `{}' as JID".format(jid)
                )
            d.run()
            d.destroy()

        else:

            jid = str(jid)

            self._jid_entry.set_text(jid)

            res = wayround_org.xmpp.privacy.get_privacy_lists(
                to_jid=jid,
                from_jid=str(self._from_jid),
                stanza_processor=self._stanza_processor
                )

            if isinstance(res, wayround_org.xmpp.core.StanzaError):
                wayround_org.pyabber.misc.stanza_error_error_message(
                    self._window,
                    res,
                    "Can't get privacy lists from server"
                    )
            else:

                model = self._l_list_view.get_model()
                while len(model) != 0:
                    del(model[0])

                if len(res) != 1:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "This program supports one Query result per stanza"
                        "but this stanza result has {} Query results".format(
                            len(res)
                            )
                        )
                    d.run()
                    d.destroy()
                else:
                    res = res[0]

                    for i in res.get_lst():
                        model.append([i.get_name()])

                    active = res.get_active()
                    self._active_checkbutton.set_active(
                        active != None
                        )

                    default = res.get_default()
                    self._default_checkbutton.set_active(
                        default != None
                        )

                    if active:
                        index = 0
                        name = active.get_name()
                        if name is not None:
                            for i in model:
                                if i[0] == name:
                                    self._active_combobox.set_active(index)
                                    break
                                index += 1

                    if default:
                        index = 0
                        name = default.get_name()
                        if name is not None:
                            for i in model:
                                if i[0] == name:
                                    self._default_combobox.set_active(index)
                                    break
                                index += 1

                    self._on_active_checkbutton_toggled(None)
                    self._on_default_checkbutton_toggled(None)

        return

    def _on_jid_reload_button_clicked(self, button):
        self.set_jid(self._jid_entry.get_text())

    def _on_active_checkbutton_toggled(self, checkbutton):
        self._active_combobox.set_sensitive(
            self._active_checkbutton.get_active()
            )

    def _on_default_checkbutton_toggled(self, checkbutton):
        self._default_combobox.set_sensitive(
            self._default_checkbutton.get_active()
            )

    def _on_active_save_button_clicked(self, button):

        value = None

        if self._active_checkbutton.get_active() != False:

            model = self._active_combobox.get_model()
            index = self._active_combobox.get_active()
            value = model[index][0]

        res = wayround_org.xmpp.privacy.set_active_list(
            value, self._to_jid, str(self._from_jid), self._stanza_processor
            )

        if isinstance(res, wayround_org.xmpp.core.StanzaError):
            wayround_org.pyabber.misc.stanza_error_error_message(
                self._window,
                res,
                "Can't set active list"
                )
        else:
            self.set_jid(self._to_jid)

        return

    def _on_default_save_button_clicked(self, button):

        value = None

        if self._default_checkbutton.get_active() != False:

            model = self._default_combobox.get_model()
            index = self._default_combobox.get_active()
            value = model[index][0]

        res = wayround_org.xmpp.privacy.set_default_list(
            value, self._to_jid, str(self._from_jid), self._stanza_processor
            )

        if isinstance(res, wayround_org.xmpp.core.StanzaError):
            wayround_org.pyabber.misc.stanza_error_error_message(
                self._window,
                res,
                "Can't set default list"
                )
        else:
            self.set_jid(self._to_jid)

        return

    def _on_r_save_button_clicked(self, button):

        name = self._r_name_entry.get_text()

        b = self._r_editor_text.get_buffer()
        text = b.get_text(b.get_start_iter(), b.get_end_iter(), False)
        try:
            data = json.loads(text)
        except:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Error Parsing JSON Text:\n\n{}".format(
                    wayround_org.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                )
            d.run()
            d.destroy()
        else:
            b.set_text(
                json.dumps(data, sort_keys=True,
                           indent=4, separators=(',', ': '))
                )
            if not wayround_org.utils.types.struct_check(
                data,
                {'t': list, '.': {'t': dict}}
                ):
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "JSON data must be list of dicts"
                    )
                d.run()
                d.destroy()
            else:

                numbers = []
                numbers_err = []

                for i in data:
                    o = i['order']
                    if o in numbers or o < 0 or o > 255:
                        if not o in numbers_err:
                            numbers_err.append(o)
                    else:
                        numbers.append(o)

                numbers_err.sort()

                data2 = []
                for i in data:
                    data2.append(collections.OrderedDict(i))

                data = data2

                for i in data:
                    _order_ordered_dict(i)

                data.sort(key=_data_key)

                b = self._r_editor_text.get_buffer()
                b.set_text(
                    json.dumps(data, indent=4, separators=(',', ': '))
                    )

                if numbers_err:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Duplicated or invalid order numbers:\n{}".format(
                            numbers_err
                            )
                        )
                    d.run()
                    d.destroy()

                else:

                    items = []

                    for i in data:

                        item = wayround_org.xmpp.privacy.Item(
                            i['action'], i['order']
                            )

                        item.set_typ(i['type'])
                        item.set_iq(i['iq'])
                        item.set_message(i['message'])
                        item.set_presence_in(i['presence-in'])
                        item.set_presence_out(i['presence-out'])
                        item.set_value(i['value'])

                        items.append(item)

                    res = wayround_org.xmpp.privacy.set_list(
                        name,
                        items, self._to_jid, str(self._from_jid),
                        self._stanza_processor
                        )

                    if isinstance(res, wayround_org.xmpp.core.StanzaError):
                        wayround_org.pyabber.misc.\
                            stanza_error_error_message(
                                self._window,
                                res,
                                "Can't save list `{}'".format(name)
                                )

        return

    def _open_edit_list(self, name):

        res = wayround_org.xmpp.privacy.get_list(
            name, self._to_jid, str(self._from_jid), self._stanza_processor
            )

        if isinstance(res, wayround_org.xmpp.core.StanzaError):
            wayround_org.pyabber.misc.stanza_error_error_message(
                self._window,
                res,
                "Can't get list `{}'".format(name)
                )
        else:

            if len(res) != 1:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "This program supports one Query result per stanza"
                    "but this stanza result has {} Query results".format(
                        len(res)
                        )
                    )
                d.run()
                d.destroy()
            else:
                res = res[0]

                data = []

                lst = res.get_lst()

                if len(lst) != 1:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Query returned {} lists, but it's a standard"
                        " violation".format(
                            len(lst)
                            )
                        )
                    d.run()
                    d.destroy()
                else:
                    lst = lst[0]

                    for i in lst.get_item():
                        dic = collections.OrderedDict()

                        dic['order'] = i.get_order()
                        dic['action'] = i.get_action()
                        dic['type'] = i.get_typ()
                        dic['iq'] = i.get_iq()
                        dic['message'] = i.get_message()
                        dic['presence-in'] = i.get_presence_in()
                        dic['presence-out'] = i.get_presence_out()
                        dic['value'] = i.get_value()

                        _order_ordered_dict(dic)

                        data.append(dic)

                    data.sort(key=_data_key)

                    b = self._r_editor_text.get_buffer()
                    b.set_text(
                        json.dumps(data, indent=4, separators=(',', ': '))
                        )

                    self._r_name_entry.set_text(name)

        return

    def _on_edit_list_button_clicked(self, button):

        name = None

        sel = self._l_list_view.get_selection()

        model, iter = sel.get_selected()

        if iter is None:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "List Item Not Selected"
                )
            d.run()
            d.destroy()

        else:

            name = model[iter][0]

            self._open_edit_list(name)

        return

    def _on_new_list_button_clicked(self, button):

        self._r_name_entry.set_text('')
        self._r_editor_text.get_buffer().set_text('')
        self._r_name_entry.grab_focus()

    def _on_delete_list_button_clicked(self, button):

        name = None

        sel = self._l_list_view.get_selection()

        model, iter = sel.get_selected()

        if iter is None:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "List Item Not Selected"
                )
            d.run()
            d.destroy()

        else:

            name = model[iter][0]

            res = wayround_org.xmpp.privacy.delete_list(
                name, self._to_jid, str(self._from_jid), self._stanza_processor
                )

            if isinstance(res, wayround_org.xmpp.core.StanzaError):
                wayround_org.pyabber.misc.stanza_error_error_message(
                    self._window,
                    res,
                    "Can't delete list `{}'".format(name)
                    )

            self.set_jid(self._to_jid)

        return

    def _on_r_open_button_clicked(self, button):

        name = self._r_name_entry.get_text()
        self._open_edit_list(name)


def _data_key(x):
    return x['order']


def _order_ordered_dict(dic):

    for i in ['order', 'action', 'type', 'iq', 'message',
              'presence-in', 'presence-out', 'value']:
        dic.move_to_end(i)
