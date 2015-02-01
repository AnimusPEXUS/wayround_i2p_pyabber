
"""
widget and window for displaying and editing both new vcard and old vcard-temp
"""

import logging
import sys
import threading

from gi.repository import Gtk
import lxml.etree
import wayround_org.utils.error

import wayround_org.pyabber.xcard_temp_widgets
import wayround_org.utils.gtk
import wayround_org.xmpp.core
import wayround_org.xmpp.xcard_4
import wayround_org.xmpp.xcard_temp


OPERATION_MODES = Gtk.ListStore(str)
for i in ['vcard-temp', 'vcard-4.0']:
    OPERATION_MODES.append([i])

del i


class BasicFieldWidget:

    def __init__(
        self,
        controller,
        parent_xcard_widget,
        editable,
        child_widget, child_parameters_widget
        ):

        self._child = child_widget
        self._parameters = child_parameters_widget
        self._parent = parent_xcard_widget
        self._parent_box = parent_xcard_widget.get_box()

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.VERTICAL)
        self._b.set_spacing(5)
        self._b.set_margin_top(5)
        self._b.set_margin_start(5)
        self._b.set_margin_end(5)
        self._b.set_margin_bottom(5)

        controls_box = Gtk.Box()
        self._controls_box = controls_box
        controls_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        controls_box.set_spacing(5)
        controls_box.set_no_show_all(True)
        controls_box.hide()

        up_button = Gtk.Button('\uffea')
        up_button.show()
        up_button.connect('clicked', self._on_up_button_clicked)

        down_button = Gtk.Button('\uffec')
        down_button.show()
        down_button.connect('clicked', self._on_down_button_clicked)

        remove_button = Gtk.Button('x')
        remove_button.show()
        remove_button.connect('clicked', self._on_remove_button_clicked)

        controls_box.pack_start(up_button, False, False, 0)
        controls_box.pack_start(down_button, False, False, 0)
        controls_box.pack_start(remove_button, False, False, 0)

        c = self._child.get_widget()

        self._b.pack_start(controls_box, False, False, 0)
        if self._parameters:
            self._b.pack_start(self._parameters.get_widget(), False, False, 0)
        self._b.pack_start(c, True, True, 0)

        self._frame = Gtk.Frame()
        self._frame.add(self._b)

        self._frame.show_all()

        self.set_editable(editable)

        return

    def destroy(self):
        if self._parameters != None:
            self._parameters.destroy()
        self._child.destroy()
        self.get_widget().destroy()
        return

    def set_editable(self, value):
        self._child.set_editable(value)
        if self._parameters != None:
            self._parameters.set_editable(value)
        self._controls_box.set_visible(value)
        return

    def get_widget(self):
        return self._frame

    def get_child(self):
        return self._child

    def get_parameters(self):
        return self._parameters

    def gen_data(self):

        data = self._child.gen_data()

        if hasattr(data, 'set_parameters') and self._parameters != None:
            set_parameters = getattr(data, 'set_parameters')

            params = self._parameters.get_data()

            set_parameters(params)

        ret = data

        return ret

    def _on_up_button_clicked(self, button):
        box = self._parent.get_box()
        chi = box.get_children()

        for i in chi:
            if i == self.get_widget():
                ind = chi.index(i)
                box.reorder_child(i, ind - 1)
                break

    def _on_down_button_clicked(self, button):
        box = self._parent.get_box()
        chi = box.get_children()

        for i in chi:
            if i == self.get_widget():
                ind = chi.index(i)
                box.reorder_child(i, ind + 1)
                break

    def _on_remove_button_clicked(self, button):
        self._parent.remove_element(self.get_widget())
        return


class XCardWidget:

    def __init__(self, controller):

        self._controller = controller

        self._mode = 'vcard-temp'

        self._editable = False
        self._data = None

        self._element_objects = []

        self._vcard_temp_menu_items = []
        self._vcard_4_menu_items = []

        add_menu = Gtk.Menu()
        add_menu.connect('show', self._on_add_menu_show)
        add_menu.set_halign(Gtk.Align.END)

        mode_label = Gtk.Label(
            "Mode not selected. Create new vcard or open existing"
            )
        self._mode_label = mode_label

        add_button = Gtk.MenuButton()
        add_button.set_no_show_all(True)
        add_button.hide()
        add_button.set_popup(add_menu)
        self._add_button = add_button

        self._b = Gtk.Box()
        self._b.set_spacing(5)
        self._b.set_orientation(Gtk.Orientation.VERTICAL)

        sw = Gtk.ScrolledWindow()

        self._element_box = Gtk.Box()
        self._element_box.set_orientation(Gtk.Orientation.VERTICAL)
        self._element_box.set_spacing(5)

        sw.add(self._element_box)

        self._b.pack_start(mode_label, False, False, 0)
        self._b.pack_start(add_button, False, False, 0)
        self._b.pack_start(sw, True, True, 0)

        self._widget = self._b

        for i in wayround_org.xmpp.xcard_temp.VCARD_ELEMENTS:
            mi = Gtk.MenuItem(i[0].split('}')[1])
            mi.set_no_show_all(True)
            mi.connect('activate', self._on_add_mi_activate, i[0])
            self._vcard_temp_menu_items.append(mi)
            add_menu.append(mi)

#        for i in wayround_org.xmpp.xcard_4.VCARD_ELEMENTS:
#            mi = Gtk.MenuItem(i[0].split('}')[1])
#            mi.set_no_show_all(True)
#            mi.connect('activate', self._on_add_mi_activate, i[0])
#            self._vcard_temp_menu_items.append(mi)
#            add_menu.append(mi)

        return

    def destroy(self):
        for i in self._element_objects[:]:
            i.destroy()
            self._element_objects.remove(i)
        self.get_widget().destroy()
        return

    def get_box(self):
        return self._element_box

    def get_widget(self):
        return self._widget

    def set_xcard(self, obj):

        self._clear_elements()

        self._data = obj

        if isinstance(obj, wayround_org.xmpp.xcard_temp.XCardTemp):
            self._mode_label.set_text("xcard-temp mode")
        elif isinstance(obj, wayround_org.xmpp.xcard_4.XCard):
            self._mode_label.set_text("urn:ietf:params:xml:ns:vcard-4.0 mode")
        else:
            self._mode_label.set_text("unsupported mode")

        order = obj.get_order()

        for i in order:

            elem_obj = i[1]
            elem_obj_typ = type(elem_obj)

            error = False
            cw = None

            if elem_obj_typ.__module__ == 'wayround_org.xmpp.xcard_temp':
                try:
                    cls = getattr(
                        wayround_org.pyabber.xcard_temp_widgets,
                        elem_obj.corresponding_tag()
                        )
                    cw = cls(
                        self._controller,
                        elem_obj,
                        self.get_editable()
                        )
                except:
                    error = (
                        "Can't find class for "
                        "xcard-temp"
                        " element `{}'\n{}".format(
                            i,
                            wayround_org.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        )
                    logging.exception(error)

            elif elem_obj_typ.__module__ == 'wayround_org.xmpp.xcard_4':
                try:
                    cls = getattr(
                        wayround_org.pyabber.xcard_4_widgets,
                        elem_obj.corresponding_tag()
                        )
                    cw = cls(
                        self._controller,
                        elem_obj,
                        self.get_editable()
                        )
                except:
                    error = (
                        "Can't find class for "
                        "urn:ietf:params:xml:ns:vcard-4.0"
                        " element `{}'\n{}".format(
                            i,
                            wayround_org.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        )
                    logging.exception(error)
            else:
                pass

            if not error and cw != None:
                basic_elem = BasicFieldWidget(
                    self._controller,
                    self,
                    self.get_editable(),
                    cw,
                    None
                    )

                self._add_element(basic_elem)

            if error:
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't add element. (Programming Error):\n{}".format(error)
                    )
                d.run()
                d.destroy()

        self.get_widget().show_all()

        return

    def _add_element(self, widget):
        logging.debug("Adding widget {}".format(widget))
        self._element_objects.append(widget)
        w = widget.get_widget()
        self._element_box.pack_start(w, False, False, 0)
        w.set_hexpand(True)
        w.set_halign(Gtk.Align.FILL)
        return

    def _clear_elements(self):
        for i in self._element_objects[:]:
            i.destroy()
            self._element_objects.remove(i)
        return

    def remove_element(self, widget):
        for i in self._element_objects[:]:
            if widget == i.get_widget():
                i.destroy()
                self._element_objects.remove(i)
        return

    def set_editable(self, value):
        self._editable = value == True
        self._add_button.set_visible(value)
        for i in self._element_objects:
            i.set_editable(self._editable)
        return

    def get_editable(self):
        return self._editable

    def get_xcard(self):
        return self._data

    def gen_xcard(self):

        error = False
        count_error = None

        elems = []
        if isinstance(self._data, wayround_org.xmpp.xcard_temp.XCardTemp):
            elems = wayround_org.xmpp.xcard_temp.VCARD_ELEMENTS
        elif isinstance(self._data, wayround_org.xmpp.xcard_4.XCard):
            elems = wayround_org.xmpp.xcard_4.VCARD_ELEMENTS
        else:
            raise Exception("Programming error")

        for i in elems:

            already_count = self._get_number_of_named_objects_in_box(
                lxml.etree.QName(i[0]).localname
                )

            if i[3] == '' and already_count != 1:
                count_error = "element {} must be one".format(i[0])
            if i[3] == '?' and already_count > 1:
                count_error = \
                    "element {} can't be more when one".format(i[0])

        if count_error:
            error = True

            d = wayround_org.utils.gtk.MessageDialog(
                wayround_org.utils.gtk.get_root_gtk_window(
                    self.get_widget()
                    ),
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                count_error
                )
            d.run()
            d.destroy()

        ret = None

        if not error:
            ret = self._gen_xcard_part_two(self._data)

        return ret

    def _gen_xcard_part_two(self, data):

        children = self._element_box.get_children()

        ret = None

        new_order = []
        cancel = False

        for i in range(len(children)):
            obj = self._get_object_for_graphical_widget(children[i])
            if obj == None:
                raise Exception(
                    "Did not found object for widget "
                    "({}). Programming error".format(children[i])
                    )
            else:

                order_element = None
                obj_data = obj.gen_data()
                obj_data_type = type(obj_data)

                if obj_data == None:
                    cancel = True
                else:

                    logging.debug("Looking for {} solution".format(obj_data))

                    if (obj_data_type.__module__
                        == 'wayround_org.xmpp.xcard_temp'):

                        for j in  wayround_org.xmpp.xcard_temp.VCARD_ELEMENTS:
                            if (lxml.etree.QName(j[0]).localname
                                == obj_data.corresponding_tag()):

                                order_element = (j[0], obj_data, j[2])

                    elif (obj_data_type.__module__
                        == 'wayround_org.xmpp.xcard_4'):

                        for j in  wayround_org.xmpp.xcard_4.VCARD_ELEMENTS:
                            if (lxml.etree.QName(j[0]).localname
                                == obj_data.corresponding_tag()):

                                order_element = (j[0], obj_data, j[2])

                    else:
                        raise Exception("Programming error")

                    if order_element == None:
                        logging.error(
                            "Has no solution for order element {}".format(
                                obj_data
                                )
                            )
                    else:
                        new_order.append(order_element)

        if not cancel:
            xcard = wayround_org.xmpp.xcard_temp.XCardTemp()
            xcard.set_order(new_order)
            ret = xcard

        return ret

    def _get_object_for_graphical_widget(self, widg):
        ret = None
        for i in self._element_objects:
            if i.get_widget() == widg:
                ret = i
                break
        return ret

    def _get_number_of_named_objects_in_box(self, name):

        count = 0

        for i in self._element_objects:
            if type(i.get_child()).corresponding_tag() == name:
                count += 1

        return count

    def _on_add_mi_activate(self, mi, name):
        tag, ns = wayround_org.utils.lxml.parse_tag(name, None, None)

        error = False
        cw = None

        if ns == wayround_org.xmpp.xcard_temp.NAMESPACE:
            try:
                cls = getattr(
                    wayround_org.pyabber.xcard_temp_widgets,
                    tag.replace('-', '')
                    )

                cls2 = None
                for i in wayround_org.xmpp.xcard_temp.VCARD_ELEMENTS:
                    if i[0] == name:
                        cls2 = i[1]
                        break

                if cls2 == wayround_org.xmpp.xcard_temp.PCData:
                    cw = cls(
                        self._controller,
                        cls2(tag, ''),
                        self.get_editable()
                        )
                else:
                    cw = cls(
                        self._controller,
                        cls2.new_empty(),
                        self.get_editable()
                        )
            except:
                error = (
                    "Can't find class for "
                    "xcard-temp"
                    " element `{}'.\n{}".format(
                        name,
                        wayround_org.utils.error.return_exception_info(
                            sys.exc_info()
                            )
                        )
                    )
                logging.exception(error)

        elif ns == wayround_org.xmpp.xcard_4.NAMESPACE:
            try:
                cls = getattr(
                    wayround_org.pyabber.xcard_4_widgets,
                    tag.replace('-', '')
                    )

                cls2 = None
                for i in wayround_org.xmpp.xcard_4.VCARD_ELEMENTS:
                    if i[0] == name:
                        cls2 = i[1]
                        break

                cw = cls(
                    self._controller,
                    cls2(),
                    self.get_editable()
                    )
            except:
                error = (
                    "Can't find class for "
                    "urn:ietf:params:xml:ns:vcard-4.0"
                    " element `{}'.\n{}".format(
                        name,
                        wayround_org.utils.error.return_exception_info(
                            sys.exc_info()
                            )
                        )
                    )
                logging.exception(error)
        else:
            pass

        if not error and cw != None:
            basic_elem = BasicFieldWidget(
                self._controller,
                self,
                self.get_editable(),
                cw,
                None
                )

            self._add_element(basic_elem)

        if error:
            d = wayround_org.utils.gtk.MessageDialog(
                wayround_org.utils.gtk.get_root_gtk_window(
                    self.get_widget()
                    ),
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't add element. (Programming Error):\n{}".format(error)
                )
            d.run()
            d.destroy()

        self.get_widget().show_all()

        return

    def _on_add_menu_show(self, menu):

        m_show = []
        m_hide = []

        if isinstance(self._data, wayround_org.xmpp.xcard_temp.XCardTemp):
            m_show = self._vcard_temp_menu_items
            m_hide = self._vcard_4_menu_items
        elif isinstance(self._data, wayround_org.xmpp.xcard_4.XCard):
            m_show = self._vcard_4_menu_items
            m_hide = self._vcard_temp_menu_items
        else:
            m_hide = self._vcard_4_menu_items + self._vcard_temp_menu_items

        for i in m_show:
            i.show()

        for i in m_hide:
            i.hide()

        return


class XCardWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        window.add(b)

        self._xcard_widget = XCardWidget(controller)

        xcard_gui_widget = self._xcard_widget.get_widget()

        top_box = Gtk.Box()
        top_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        top_box.set_spacing(5)

        operation_mode_combobox = Gtk.ComboBox()
        self._operation_mode_combobox = operation_mode_combobox
        operation_mode_combobox.set_model(OPERATION_MODES)
        renderer_text = Gtk.CellRendererText()
        operation_mode_combobox.pack_start(renderer_text, True)
        operation_mode_combobox.add_attribute(renderer_text, "text", 0)
        operation_mode_combobox.set_active(0)

        target_entry = Gtk.Entry()
        self._target_entry = target_entry

        edit_button = Gtk.ToggleButton("Edit")
        edit_button.connect('toggled', self._on_edit_button_toggled)
        self._edit_button = edit_button

        reload_button = Gtk.Button("(re)Load")
        self._reload_button = reload_button
        reload_button.connect('clicked', self._on_reload_button_clicked)

        new_button = Gtk.Button("Create New")
        self._new_button = new_button
        new_button.connect('clicked', self._on_new_button_clicked)

        bottom_buttons = Gtk.ButtonBox()
        bottom_buttons.set_orientation(Gtk.Orientation.HORIZONTAL)

        submit_button = Gtk.Button("Submit")
        self._submit_button = submit_button
        submit_button.set_no_show_all(True)
        submit_button.hide()
        submit_button.connect('clicked', self._on_submit_button_clicked)

        close_button = Gtk.Button("Close")
        close_button.connect('clicked', self._on_close_button_clicked)

        top_box.pack_start(operation_mode_combobox, False, False, 0)
        top_box.pack_start(target_entry, True, True, 0)
        top_box.pack_start(reload_button, False, False, 0)
        top_box.pack_start(new_button, False, False, 0)

        bottom_buttons.pack_start(submit_button, False, False, 0)
        bottom_buttons.pack_start(close_button, False, False, 0)

        b.pack_start(top_box, False, False, 0)
        b.pack_start(edit_button, False, False, 0)
        b.pack_start(xcard_gui_widget, True, True, 0)
        b.pack_start(bottom_buttons, False, False, 0)

        self._edit_button.set_active(False)

        self._window = window

        return

    def run(self, target_jid_str=None):

        self._target_entry.set_text(target_jid_str)

        self.show()

        return

    def show(self):
        self._window.show_all()
        return

    def destroy(self):
        self._xcard_widget.destroy()
        self._window.hide()
        self._window.destroy()
        return

    def _on_destroy(self, window):
        self.destroy()
        return

    def _on_reload_button_clicked(self, button):

        mode = OPERATION_MODES[self._operation_mode_combobox.get_active()][0]

        to_jid = None
        t = self._target_entry.get_text()
        if not t in [None, '']:
            to_jid = t

        objects = []

        if mode == 'vcard-temp':
            objects.append(wayround_org.xmpp.xcard_temp.XCardTemp())
        elif mode == 'vcard-4.0':
            objects.append(wayround_org.xmpp.xcard_4.XCard())

        stanza = wayround_org.xmpp.core.Stanza(
            tag='iq',
            typ='get',
            from_jid=self._controller.jid.full(),
            to_jid=to_jid,
            objects=objects
            )

        proc_data = {
            'args': (stanza,),
            'kwargs': {'wait': True}
            }

        t = threading.Thread(
            target=self._t_proc,
            args=(proc_data,)
            )
        t.start()

        wayround_org.utils.gtk.Waiter.wait_thread(t)

        res = proc_data['res_data']

        if res == None:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Timeout"
                )
            d.run()
            d.destroy()
        else:

            if res.is_error():
                wayround_org.pyabber.misc.stanza_error_message(
                    self._window,
                    res,
                    "Failed to get vcard-temp"
                    )
            else:

                error = True

                if mode == 'vcard-temp':
                    obj = None
                    for i in res.get_element():
                        if wayround_org.utils.lxml.is_lxml_tag_element(i):
                            if wayround_org.xmpp.xcard_temp.is_xcard(i):
                                try:
                                    obj = \
                                        wayround_org.xmpp.xcard_temp.\
                                            XCardTemp.\
                                            new_from_element(i)
                                except:
                                    error = "Can't parse XCard:\n{}".format(
                                        wayround_org.utils.error.\
                                            return_exception_info(
                                                sys.exc_info()
                                                )
                                        )
                                    logging.exception(error)
                                    d = wayround_org.utils.gtk.MessageDialog(
                                        self._window,
                                        0,
                                        Gtk.MessageType.ERROR,
                                        Gtk.ButtonsType.OK,
                                        error
                                        )
                                    d.run()
                                    d.destroy()

                                break

                    if obj == None:
                        d = wayround_org.utils.gtk.MessageDialog(
                            self._window,
                            0,
                            Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            "Can't find vcard-temp in response stanza"
                            )
                        d.run()
                        d.destroy()
                    else:
                        error = False

                if not error:
                    self._xcard_widget.set_xcard(obj)
                    self._xcard_widget.set_editable(
                        self._edit_button.get_active()
                        )

        return

    def _on_close_button_clicked(self, button):
        self.destroy()

    def _on_edit_button_toggled(self, button):
        self._xcard_widget.set_editable(self._edit_button.get_active())

        act = self._edit_button.get_active()

        self._target_entry.set_sensitive(not act)
        self._reload_button.set_sensitive(not act)
        self._new_button.set_sensitive(not act)
        self._operation_mode_combobox.set_sensitive(not act)
        self._submit_button.set_visible(act)

        return

    def _on_submit_button_clicked(self, button):

        objects = []
        xcard = self._xcard_widget.gen_xcard()
        if xcard != None:
            objects.append(xcard)

            to_jid = None
            t = self._target_entry.get_text()
            if not t in [None, '']:
                to_jid = t

            stanza = wayround_org.xmpp.core.Stanza(
                tag='iq',
                typ='set',
                from_jid=self._controller.jid.full(),
                to_jid=to_jid,
                objects=objects
                )

            proc_data = {
                'args': (stanza,),
                'kwargs': {'wait': True}
                }

            t = threading.Thread(
                target=self._t_proc,
                args=(proc_data,)
                )
            t.start()

            wayround_org.utils.gtk.Waiter.wait_thread(t)

            res = proc_data['res_data']

            if isinstance(res, wayround_org.xmpp.core.Stanza):
                if res.is_error():
                    wayround_org.pyabber.misc.stanza_error_message(
                        self._window,
                        res,
                        "Failed to set vcard-temp"
                        )
                else:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.INFO,
                        Gtk.ButtonsType.OK,
                        "No error returned by server. "
                        "vcard-temp set successfully"
                        )
                    d.run()
                    d.destroy()
            else:

                if res == False:
                    d = wayround_org.utils.gtk.MessageDialog(
                        self._window,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Timeout"
                        )
                    d.run()
                    d.destroy()
                else:
                    raise Exception("This not should been happen")

        return

    def _on_new_button_clicked(self, button):

        self._target_entry.set_text('')

        mode = OPERATION_MODES[self._operation_mode_combobox.get_active()][0]

        if mode == 'vcard-temp':
            self._xcard_widget.set_xcard(
                wayround_org.xmpp.xcard_temp.XCardTemp()
                )
        elif mode == 'vcard-4.0':
            self._xcard_widget.set_xcard(wayround_org.xmpp.xcard_4.XCard())

        self._edit_button.set_active(True)

        return

    def _t_proc(self, x):
        x['res_data'] = \
            self._controller.client.stanza_processor.send(
                *x['args'],
                **x['kwargs']
                )
