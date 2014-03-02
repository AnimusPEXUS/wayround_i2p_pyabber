
"""
widget and window for displaying and editing both new vcard and old vcard-temp
"""

import logging

from gi.repository import Gtk

import org.wayround.pyabber.xcard_temp_widgets
import org.wayround.xmpp.core
import org.wayround.xmpp.xcard
import org.wayround.xmpp.xcard_temp
import org.wayround.utils.gtk

OPERATION_MODES = Gtk.ListStore(str)
for i in ['vcard-temp', 'vcard-4']:
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
        self._b.set_orientation(Gtk.Orientation.HORIZONTAL)

        c = self._child.get_widget()

        if self._parameters:
            self._b.pack_start(self._parameters.get_widget(), False, False, 0)
        self._b.pack_start(c, True, True, 0)

        self._b.show_all()

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
        return

    def get_widget(self):
        return self._b

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

        add_button = Gtk.MenuButton()
        add_button.set_no_show_all(True)
        add_button.hide()
        add_button.set_popup(add_menu)
        self._add_button = add_button

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.VERTICAL)

        sw = Gtk.ScrolledWindow()

        self._element_box = Gtk.Box()
        self._element_box.set_orientation(Gtk.Orientation.VERTICAL)

        sw.add(self._element_box)

        self._b.pack_start(add_button, False, False, 0)
        self._b.pack_start(sw, True, True, 0)

        self._widget = self._b

        for i in org.wayround.xmpp.xcard_temp.VCARD_ELEMENTS:
            mi = Gtk.MenuItem(i[0].split('}')[1])
            mi.set_no_show_all(True)
            mi.connect('activate', self._on_add_mi_activate, i[0])
            self._vcard_temp_menu_items.append(mi)
            add_menu.append(mi)

#        for i in org.wayround.xmpp.xcard.VCARD_ELEMENTS:
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

        ret = None

        if isinstance(self._data, org.wayround.xmpp.xcard_temp.XCardTemp):
            ret = self._set_xcard_temp(self._data)
        elif isinstance(self._data, org.wayround.xmpp.xcard.XCard):
            ret = self._set_xcard(self._data)

        return ret

    def _set_xcard_temp(self, obj):

        order = obj.get_order()

        for i in order:

            elem_obj = i[1]
            elem_obj_typ = type(elem_obj)

            error = False
            cw = None

            if elem_obj_typ == org.wayround.xmpp.xcard_temp.N:
                cw = org.wayround.pyabber.xcard_temp_widgets.N(
                    self._controller,
                    elem_obj,
                    self.get_editable()
                    )
            else:
                # TODO: enable this error when tis module is done
                # error = True
                logging.error(
                    "Can't find class for xcard-temp element `{}'".format(i)
                    )

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
                self._clear_elements()
                break

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

        ret = None

        if self._data != None:
            if isinstance(self._data, org.wayround.xmpp.xcard_temp.XCardTemp):
                ret = self._gen_xcard_temp(self._data)
            elif isinstance(self._data, org.wayround.xmpp.xcard.XCard):
                ret = self._gen_xcard(self._data)

        return ret

    def _gen_xcard_temp(self, data):

        children = self._element_box.get_children()

        new_order = []

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
                obj_data_type = type(obj)

                if obj_data_type == org.wayround.pyabber.xcard_temp_widgets.N:
                    order_element = ('N', obj_data, 'n')

                if order_element == None:
                    logging.error(
                        "Has no solution for order element {}".format(obj)
                        )
                else:
                    new_order.append(order_element)

        xcard = org.wayround.xmpp.xcard_temp.XCardTemp()
        xcard.set_order(new_order)

        return xcard

    def _get_object_for_graphical_widget(self, widg):
        ret = None
        for i in self._element_objects:
            if i.get_widget() == widg:
                ret = i
                break
        return ret

    def _on_add_mi_activate(self, mi, name):
        tag, ns = org.wayround.utils.lxml.parse_tag(name, None, None)

        if ns == 'vcard-temp':
            pass

        return

    def _on_add_menu_show(self, menu):

#        print("Menu show")

        m_show = []
        m_hide = []

        if isinstance(self._data, org.wayround.xmpp.xcard_temp.XCardTemp):
            m_show = self._vcard_temp_menu_items
            m_hide = self._vcard_4_menu_items
        elif isinstance(self._data, org.wayround.xmpp.xcard.XCard):
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
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_margin_bottom(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        window.add(b)

        self._xcard_widget = XCardWidget(controller)

        xcard_gui_widget = self._xcard_widget.get_widget()
        xcard_gui_widget.set_margin_top(5)
        xcard_gui_widget.set_margin_left(5)
        xcard_gui_widget.set_margin_right(5)
        xcard_gui_widget.set_margin_bottom(5)

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

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()
        return

    def destroy(self):
        self._xcard_widget.destroy()
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()
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
            objects.append(org.wayround.xmpp.xcard_temp.XCardTemp())

        stanza = org.wayround.xmpp.core.Stanza(
            tag='iq',
            typ='get',
            from_jid=self._controller.jid.full(),
            to_jid=to_jid,
            objects=objects
            )

        res = self._controller.client.stanza_processor.send(
            stanza, wait=True
            )

        if res == None:
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Timeout"
                )
            d.run()
            d.destroy()
        else:

            if res.is_error():
                org.wayround.pyabber.misc.stanza_error_message(
                    None,
                    res,
                    "Failed to get vcard-temo"
                    )
            else:

                error = True

                if mode == 'vcard-temp':
                    obj = None
                    for i in res.get_element():
                        if org.wayround.xmpp.xcard_temp.is_xcard(i):
                            obj = org.wayround.xmpp.xcard_temp.XCardTemp.\
                                new_from_element(i)
                            break

                    if obj == None:
                        d = org.wayround.utils.gtk.MessageDialog(
                            None,
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

        return

    def _on_submit_button_clicked(self, button):

        to_jid = None
        t = self._target_entry.get_text()
        if not t in [None, '']:
            to_jid = t

        objects = [self._xcard_widget.gen_xcard()]

        stanza = org.wayround.xmpp.core.Stanza(
            tag='iq',
            typ='set',
            from_jid=self._controller.jid.full(),
            to_jid=to_jid,
            objects=objects
            )

        res = self._controller.client.stanza_processor.send(
            stanza, wait=True
            )

        if res == None:
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Timeout"
                )
            d.run()
            d.destroy()
        else:

            if res.is_error():
                org.wayround.pyabber.misc.stanza_error_message(
                    None,
                    res,
                    "Failed to set vcard-temo"
                    )
            else:
                d = org.wayround.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    "No error returned by server. vcard-temp set successfully"
                    )
                d.run()
                d.destroy()

        return

    def _on_new_button_clicked(self, button):

        self._target_entry.set_text('')

        mode = OPERATION_MODES[self._operation_mode_combobox.get_active()][0]

        if mode == 'vcard-temp':
            self._xcard_widget.set_xcard(
                org.wayround.xmpp.xcard_temp.XCardTemp()
                )
        elif mode == 'vcard-4':
            self._xcard_widget.set_xcard(org.wayround.xmpp.xcard.XCard())

        self._edit_button.set_active(True)

        return
