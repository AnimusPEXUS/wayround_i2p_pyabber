
import base64

from gi.repository import Gtk, Pango, GLib, Gio, GdkPixbuf

import lxml.etree

import wayround_org.utils.factory
import wayround_org.xmpp.xcard_temp


class ValuePCDataWidgetGroup:

    def __init__(
        self,
        element_obj,
        mode='*',
        value=None, title='', description='', editable=True
        ):

        """
        mode - must be in ['+', '*']
        """

        if value == None:
            value = []

        self._mode = mode

        self._editable = editable

        self._element_obj = element_obj

        self._subwidgets = []

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.VERTICAL)
        self._b.set_spacing(5)
        self._b.set_margin_top(5)
        self._b.set_margin_start(5)
        self._b.set_margin_end(5)
        self._b.set_margin_bottom(5)

        add_button = Gtk.Button('Add')
        self._add_button = add_button
        add_button.connect('clicked', self._on_add_button_clicked)

        self._description = Gtk.Label()

        self._b.pack_start(self._description, False, False, 0)
        self._b.pack_start(add_button, False, False, 0)

        self._subwidgets_box = Gtk.Box()
        self._subwidgets_box.set_orientation(Gtk.Orientation.VERTICAL)
        self._subwidgets_box.set_spacing(5)

        self._b.pack_start(self._subwidgets_box, False, False, 0)

        self._frame = Gtk.Frame()
        self._frame.add(self._b)

        self._frame.show_all()

        self.set_title(title)
        self.set_description(description)
        self.set_value(value)
        self.set_editable(editable)

        return

    def set_editable(self, value):
        self._editable = value
        for i in self._subwidgets:
            i.set_editable(value)

        self._add_button.set_visible(value)
        self._description.set_visible(
            value
            and
            self._description.get_text() != ''
            )

        return

    def get_editable(self):
        return self._editable

    def get_widget(self):
        return self._frame

    def check_value(self, value):
        if not wayround_org.utils.types.struct_check(
            value,
            {'t': list, '.':
             {'t': str}
             }
            ):
            raise TypeError(
                "`value' must be list of str"
                )
        return

    def set_value(self, value):
        self.check_value(value)
        for i in value:
            self._add_subelement(
                ValuePCDataWidget(
                    self._element_obj,
                    i, '', '',
                    True, False, False,
                    momentarily_deletable=self._remove_subelement
                    )
                )
        return

    def get_value(self):

        ret = None

        if self._mode == '+':
            if len(self._subwidgets) == 0:
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Widget group `{}' requires at least one value".format(
                        self.get_title()
                        )
                    )
                d.run()
                d.destroy()
        else:

            ret = []
            for i in self._subwidgets:
                ret.append(i.get_value())

        return ret

    def set_title(self, value):
        self._frame.set_label(value)
        return

    def get_title(self):
        return self._frame.get_label()

    def set_description(self, value):
        self._description.set_text(value)
        return

    def get_description(self):
        return self._description.get_text()

    def _add_subelement(self, element):

        self._subwidgets.append(element)
        e = element.get_widget()
        self._subwidgets_box.pack_start(e, False, False, 0)
        e.show_all()

        return

    def _remove_subelement(self, element):
        self._subwidgets.remove(element)
        element.destroy()
        return

    def destroy(self):

        for i in self._subwidgets[:]:
            i.destroy()
            self._subwidgets.remove(i)

        return

    def _on_add_button_clicked(self, button):
        self._add_subelement(
            ValuePCDataWidget(
                self._element_obj,
                '', '', '',
                True, False, False,
                momentarily_deletable=self._remove_subelement
                )
            )
        return


class ValuePCDataWidget:

    def __init__(
        self, element_obj, value='', title='', description='',
        editable=True, deletable=False, deleted=False,
        momentarily_deletable=None
        ):

        """
        momentarily_deletable must be None or callable with one parameter,
        which receives instance of object to remove (self)
        """

        self._element_obj = element_obj
        self._momentarily_deletable = momentarily_deletable

        self._deletable = True

        self._widget = Gtk.Box()
        self._widget.set_orientation(Gtk.Orientation.VERTICAL)
        self._widget.set_margin_top(5)
        self._widget.set_margin_start(5)
        self._widget.set_margin_end(5)
        self._widget.set_margin_bottom(5)
        self._widget.set_spacing(5)

        self._value_widget = Gtk.Label()

        self._title_widget_box = Gtk.Box()
        self._title_widget_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._title_widget_box.show_all()

        present_button = Gtk.CheckButton()
        self._present_button = present_button
        present_button.set_no_show_all(True)
        present_button.hide()

        self._title = Gtk.Label()
        self._title.set_alignment(0, 0.5)
        self._title.set_no_show_all(True)
        self._title.hide()

        self._description = Gtk.Label()
        self._description.set_alignment(0, 0.5)
        self._description.set_no_show_all(True)
        self._description.hide()

        self._title_widget_box.pack_start(present_button, False, False, 0)
        self._title_widget_box.pack_start(self._title, True, True, 0)

        delete_button = Gtk.Button('x')
        delete_button.set_no_show_all(True)
        delete_button.hide()
        self._delete_button = delete_button
        delete_button.connect('clicked', self._on_delete_button_clicked)
        self._title_widget_box.pack_start(delete_button, False, False, 0)

        self._widget.pack_start(self._value_widget, False, False, 0)
        self._widget.pack_start(self._description, False, False, 0)

        self._frame = Gtk.Frame()
        self._frame.set_no_show_all(True)
        self._frame.hide()
        self._frame.add(self._widget)
        self._frame.set_label_widget(self._title_widget_box)

        self._widget.show_all()

        self.set_value(value)
        self.set_title(title)
        self.set_description(description)
        self.set_deletable(deletable)
        self.set_deleted(deleted)
        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    def destroy(self):
        self._value_widget.destroy()
        self.get_widget().destroy()
        return

    def set_deleted(self, value):
        self._present_button.set_active(value != True)
        return

    def get_deleted(self):
        return not self._present_button.get_active()

    def check_editable(self, value):
        if not isinstance(value, bool):
            raise TypeError("`editable' value must be bool")
        return

    def set_editable(self, value):

        val = ''
        if self._value_widget != None:
            val = self._value_widget.get_text()
            self._value_widget.destroy()

        if value == True:
            self._value_widget = Gtk.Entry()
        else:
            self._value_widget = Gtk.Label()
            self._value_widget.set_selectable(True)
            self._value_widget.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self._value_widget.set_text(val)

        self._frame.set_visible(
            value == True
            or not self.get_deleted()
            )

        self._description.set_visible(
            value and self._description.get_text() != ''
            )

        self._present_button.set_visible(
            value == True and self.get_deletable()
            )

        self._delete_button.set_visible(
            self._momentarily_deletable != None
            and
            value
            )

        self._widget.pack_start(self._value_widget, False, False, 0)
        self._widget.reorder_child(self._value_widget, 0)

        self._widget.show_all()

        return

    def get_editable(self):
        return type(self._value_widget) == Gtk.Entry

    def set_value(self, value):
        self.check_value(value)
        self._value_widget.set_text(value)
        return

    def get_value(self):
        ret = ''
        if self._value_widget:
            ret = self._value_widget.get_text()
        return ret

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("`value' must be str")
        return

    def check_title(self, value):
        if not isinstance(value, str):
            raise ValueError("`title' must be str")
        return

    def set_title(self, value):
        self.check_title(value)
        self._title.set_text(value)
        self._title.set_visible(value != '')
        return

    def get_title(self, value):
        return self._title.get_text()

    def check_description(self, value):
        if not isinstance(value, str):
            raise ValueError("`description' must be str")
        return

    def set_description(self, value):
        self.check_description(value)
        self._description.set_text(value)
        self._description.set_visible(value != '')
        return

    def get_description(self, value):
        return self._description.get_text()

    def check_deletable(self, value):
        if not isinstance(value, bool):
            raise TypeError("`deletable' value must be bool")
        return

    def set_deletable(self, value):
        self.check_deletable(value)
        self._deletable = value
        self._present_button.set_visible(value == True and self.get_editable())
        return

    def get_deletable(self):
        return self._deletable

    def _on_delete_button_clicked(self, button):
        self._momentarily_deletable(self)


class ValueEmptyWidget:

    def __init__(
        self,
        element_obj,
        value=False, title='', description='', editable=True
        ):

        self._element_obj = element_obj

        self._value_widget = Gtk.CheckButton()

        self._value_widget.show_all()
        self._value_widget.set_no_show_all(True)
        self._value_widget.hide()

        self.set_value(value)
        self.set_title(title)
        self.set_description(description)
        self.set_editable(editable)

        return

    def get_widget(self):
        return self._value_widget

    def destroy(self):
        self.get_widget().destroy()
        return

    def get_group(self):
        ret = None
        if type(self._value_widget) == Gtk.RadioButton:
            ret = self._value_widget.get_group()
        return ret

    def check_editable(self, value):
        if not isinstance(value, bool):
            raise TypeError("`editable' value must be bool")
        return

    def set_editable(self, value):

        if value:
            self._value_widget.set_visible(True)
        else:
            self._value_widget.set_visible(self.get_value())

        self._value_widget.set_sensitive(value)

        return

    def get_editable(self):
        return self._value_widget.get_sensitive()

    def set_value(self, value):
        self.check_value(value)
        self._value_widget.set_active(value)
        return

    def get_value(self):
        ret = False
        if self._value_widget:
            ret = self._value_widget.get_active()
        return ret

    def check_value(self, value):
        if not isinstance(value, bool):
            raise ValueError("`value' must be bool")
        return

    def check_title(self, value):
        if not isinstance(value, str):
            raise ValueError("`title' must be str")
        return

    def set_title(self, value):
        self.check_title(value)
        txt = ''
        if value != '':
            txt = value
        self._value_widget.set_label(txt)
        return

    def get_title(self, value):
        return self._value_widget.get_label()

    def check_description(self, value):
        if not isinstance(value, str):
            raise ValueError("`description' must be str")
        return

    def set_description(self, value):
        self.check_description(value)
        txt = None
        if value != '':
            txt = value
        self._value_widget.set_tooltip_text(txt)
        return

    def get_description(self, value):
        return self._value_widget.get_tooltip_text()


class ValueImageBinvalWidget:

    def __init__(
        self, element_obj, value='', title='', description='',
        editable=True, deletable=False, deleted=False
        ):

        self._element_obj = element_obj

        self._deletable = True

        self._widget = Gtk.Box()
        self._widget.set_orientation(Gtk.Orientation.VERTICAL)
        self._widget.set_margin_top(5)
        self._widget.set_margin_start(5)
        self._widget.set_margin_end(5)
        self._widget.set_margin_bottom(5)
        self._widget.set_spacing(5)

        self._value_widget = Gtk.Image()
        self._value_widget_sw = Gtk.ScrolledWindow()
        self._value_widget_sw.set_size_request(200, 200)
        self._value_widget_sw.add(self._value_widget)

        self._image_buttons = Gtk.ButtonBox()
        self._image_buttons.set_orientation(Gtk.Orientation.HORIZONTAL)

        open_img_button = Gtk.Button("Open..")
        open_img_button.set_no_show_all(True)
        self._open_img_button = open_img_button
        open_img_button.connect('clicked', self._on_open_img_button_clicked)

        save_img_button = Gtk.Button("Save..")

        self._image_buttons.pack_start(open_img_button, False, False, 0)
        self._image_buttons.pack_start(save_img_button, False, False, 0)

        self._title_widget_box = Gtk.Box()
        self._title_widget_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._title_widget_box.show_all()

        present_button = Gtk.CheckButton()
        self._present_button = present_button
        present_button.set_no_show_all(True)
        present_button.hide()

        self._title = Gtk.Label()
        self._title.set_alignment(0, 0.5)
        self._title.set_no_show_all(True)
        self._title.hide()

        self._description = Gtk.Label()
        self._description.set_alignment(0, 0.5)
        self._description.set_no_show_all(True)
        self._description.hide()

        self._title_widget_box.pack_start(present_button, False, False, 0)
        self._title_widget_box.pack_start(self._title, True, True, 0)

        self._widget.pack_start(self._value_widget_sw, False, False, 0)
        self._widget.pack_start(self._image_buttons, False, False, 0)
        self._widget.pack_start(self._description, False, False, 0)

        self._frame = Gtk.Frame()
        self._frame.set_no_show_all(True)
        self._frame.hide()
        self._frame.add(self._widget)
        self._frame.set_label_widget(self._title_widget_box)

        self._widget.show_all()

        self.set_value(value)
        self.set_title(title)
        self.set_description(description)
        self.set_deletable(deletable)
        self.set_deleted(deleted)
        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    def destroy(self):
        self._value_widget.destroy()
        self.get_widget().destroy()
        return

    def set_deleted(self, value):
        self._present_button.set_active(value != True)
        return

    def get_deleted(self):
        return not self._present_button.get_active()

    def check_editable(self, value):
        if not isinstance(value, bool):
            raise TypeError("`editable' value must be bool")
        return

    def set_editable(self, value):

        self._open_img_button.set_visible(value)

        self._frame.set_visible(
            value == True
            or not self.get_deleted()
            )

        self._present_button.set_visible(
            value == True and self.get_deletable()
            )

        self._description.set_visible(
            value and self._description.get_text() != ''
            )

        self._widget.show_all()

        return

    def get_editable(self):
        return self._open_img_button.get_visible()

    def set_value(self, value):
        self.check_value(value)
        if value != '':
            data = base64.b64decode(value)
            stream = Gio.MemoryInputStream.new_from_data(data, None)
            pb = GdkPixbuf.Pixbuf.new_from_stream(stream, None)
            self._value_widget.set_from_pixbuf(pb)
            stream.close(None)
        else:
            self._value_widget.set_from_stock(
                Gtk.STOCK_MISSING_IMAGE,
                Gtk.IconSize.DIALOG
                )
        return

    def get_value(self):
        ret = None
        if self._value_widget:
            pb = self._value_widget.get_pixbuf()
            if not pb:
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't get pixel buffer. Is image loaded?"
                    )
                d.run()
                d.destroy()
            else:
                code, data = pb.save_to_bufferv('png', [], [])
                if code == True:
                    ret = str(base64.b64encode(data), 'utf-8')
        return ret

    def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("`value' must be str")
        return

    def check_title(self, value):
        if not isinstance(value, str):
            raise ValueError("`title' must be str")
        return

    def set_title(self, value):
        self.check_title(value)
        self._title.set_text(value)
        self._title.set_visible(value != '')
        return

    def get_title(self, value):
        return self._title.get_text()

    def check_description(self, value):
        if not isinstance(value, str):
            raise ValueError("`description' must be str")
        return

    def set_description(self, value):
        self.check_description(value)
        self._description.set_text(value)
        self._description.set_visible(value != '')
        return

    def get_description(self, value):
        return self._description.get_text()

    def check_deletable(self, value):
        if not isinstance(value, bool):
            raise TypeError("`deletable' value must be bool")
        return

    def set_deletable(self, value):
        self.check_deletable(value)
        self._deletable = value
        self._present_button.set_visible(value == True and self.get_editable())
        return

    def get_deletable(self):
        return self._deletable

    def _on_open_img_button_clicked(self, button):
        d = Gtk.FileChooserDialog(
            "Select Image",
            None,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            )
        img = Gtk.Image()
        self._preview_img = img
        d.set_preview_widget(img)
        d.connect('update-preview', self._on_d_update_preview)
        res = d.run()
        if res == Gtk.ResponseType.OK:
            fn = d.get_filename()
            if not fn.endswith('.png'):
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Only PNG images are supported"
                    )
                d.run()
                d.destroy()
            else:
                self._value_widget.set_from_file(fn)
                self._element_obj._type_.set_value('image/png')
                self._element_obj._type_.set_deleted(False)
                self._element_obj._binval.set_deleted(False)
                self._element_obj._extval.set_deleted(True)

        d.destroy()
        return

    def _on_d_update_preview(self, widget):

        filename = widget.get_preview_filename()
        try:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 150, 150)
            self._preview_img.set_from_pixbuf(pb)
        except:
            pass
        return


for i in wayround_org.xmpp.xcard_temp.VCARD_ELEMENTS:

    if i[1] == wayround_org.xmpp.xcard_temp.PCData:

        tag = i[0].split('}')[1]
        name = tag.replace('-', '')
        title = i[4]

        exec("""
class {name}:

    def __init__(self, controller, data, editable):

        self._controller = controller
        self._data = data

        self._value_field = ValuePCDataWidget(
            self, data.get_text(), '', '', editable, False, False
            )

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._b.set_margin_top(5)
        self._b.set_margin_start(5)
        self._b.set_margin_end(5)
        self._b.set_margin_bottom(5)
        self._b.set_spacing(5)

        self._b.pack_start(self._value_field.get_widget(), True, True, 0)

        self._frame = Gtk.Frame()
        self._frame.set_label("{title}")
        self._frame.add(self._b)

        if hasattr(self, 'additional_init'):
            self.additional_init()

        self._frame.show_all()

        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    @classmethod
    def corresponding_tag(cls):
        return '{tag}'

    def set_editable(self, value):
        self._value_field.set_editable(value)
        if value:
            self._b.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self._b.set_orientation(Gtk.Orientation.HORIZONTAL)
        return

    def destroy(self):
        self._value_field.destroy()
        return

    def get_data(self):
        return self._data

    def gen_data(self):
        ret = None

        error = False
        if hasattr(self, 'is_values_error'):
            if self.is_values_error():
                error = True

        if error:
            ret = None
        else:
            ret = wayround_org.xmpp.xcard_temp.PCData(
                self.corresponding_tag(),
                self._value_field.get_value()
                )
        return ret
""".format(name=name, tag=tag, title=title)
    )

    else:

        tag = i[0].split('}')[1]
        name = tag.replace('-', '')
        title = i[4]
        prot_class_name = i[1].__name__

        single_box = 'False'
        if tag in ['PHOTO', 'LOGO']:
            single_box = 'True'

        exec("""
class {name}:

    def __init__(self, controller, data, editable):

        self._controller = controller
        self._data = data

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.VERTICAL)
        self._b.set_margin_top(5)
        self._b.set_margin_start(5)
        self._b.set_margin_end(5)
        self._b.set_margin_bottom(5)
        self._b.set_spacing(5)

        self._b1 = Gtk.Box()
        self._b1.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._b1.set_spacing(5)

        self._b2 = Gtk.Box()
        self._b2.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._b2.set_spacing(5)

        _init_fields(
            self,
            wayround_org.xmpp.xcard_temp.{name}_ELEMENTS,
            data,
            editable,
            {single_box}
            )

        self._frame = Gtk.Frame()
        self._frame.set_label("{title}")
        self._frame.add(self._b)

        self._b.pack_start(self._b1, False, False, 0)
        self._b.pack_start(self._b2, False, False, 0)

        if hasattr(self, 'additional_init'):
            self.additional_init()

        self._frame.show_all()

        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    @classmethod
    def corresponding_tag(cls):
        return '{tag}'

    def set_editable(self, value):

        _set_editable_fields(
            self,
            wayround_org.xmpp.xcard_temp.{name}_ELEMENTS,
            value
            )

        if value:
            self._b1.set_orientation(Gtk.Orientation.VERTICAL)
            self._b2.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self._b1.set_orientation(Gtk.Orientation.HORIZONTAL)
            self._b2.set_orientation(Gtk.Orientation.HORIZONTAL)
        return

    def destroy(self):
        _destroy_fields(
            self,
            wayround_org.xmpp.xcard_temp.{name}_ELEMENTS
            )
        return

    def get_data(self):
        return self._data

    def gen_data(self):

        ret = None

        error = False
        if hasattr(self, 'is_values_error'):
            if self.is_values_error():
                error = True

        if error:
            ret = None
        else:

            data = wayround_org.xmpp.xcard_temp.{prot_class_name}.new_empty()

            _gen_data_fields(
                self,
                wayround_org.xmpp.xcard_temp.{name}_ELEMENTS,
                data
                )

            ret = data

        return ret

""".format(
           prot_class_name=prot_class_name,
           name=name,
           tag=tag,
           title=title,
           single_box=single_box
           )
            )

        del prot_class_name


del i
del tag
del name
del title


def _init_fields(inst, elements_struct, data, editable, single_box):

    for i in elements_struct:

        b1 = inst._b1
        b2 = inst._b2
        if single_box:
            b1 = inst._b
            b2 = inst._b

        if i[1] == wayround_org.xmpp.xcard_temp.Empty:
            value = getattr(data, 'get_{}'.format(i[2]))() != None
            field = ValueEmptyWidget(inst, value, i[4], i[5], editable)
            setattr(inst, '_{}'.format(i[2]), field)
            b1.pack_start(field.get_widget(), True, True, 0)

        elif i[1] == wayround_org.xmpp.xcard_temp.PCData:

            class_name = 'ValuePCDataWidget'

            if (i[0]
                == wayround_org.xmpp.xcard_temp.LXML_NAMESPACE + 'BINVAL'):

                if type(inst) in [PHOTO, LOGO]:
                    class_name = 'ValueImageBinvalWidget'

            if i[3] in ['', '?']:
                deleted = getattr(data, 'get_{}'.format(i[2]))() == None
                value = ''
                if not deleted:
                    value = getattr(data, 'get_{}'.format(i[2]))().get_text()
                field = eval(class_name)(
                    inst,
                    value, i[4], i[5], editable, i[3] != '', deleted
                    )
                setattr(inst, '_{}'.format(i[2]), field)
                b2.pack_start(field.get_widget(), True, True, 0)
            elif i[3] in ['*', '+']:
                attr = getattr(data, 'get_{}'.format(i[2]))
                field = ValuePCDataWidgetGroup(
                    inst,
                    i[3],
                    [x.get_text() for x in attr()],
                    i[4],
                    i[5],
                    editable
                    )
                setattr(inst, '_{}'.format(i[2]), field)
                b2.pack_start(field.get_widget(), True, True, 0)

        else:
            d = wayround_org.utils.gtk.MessageDialog(
                wayround_org.utils.gtk.get_root_gtk_window(
                    inst.get_widget()
                    ),
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Not supported field type: {}".format(i[1])
                )
            d.run()
            d.destroy()

    return


def _gen_data_fields(inst, elements_struct, data):

    for i in elements_struct:

        if i[1] == wayround_org.xmpp.xcard_temp.Empty:
            field = getattr(inst, '_{}'.format(i[2]))
            value = field.get_value()
            if value:
                getattr(data, 'set_{}'.format(i[2]))(
                    wayround_org.xmpp.xcard_temp.Empty(
                        lxml.etree.QName(i[0]).localname
                        )
                    )
            else:
                getattr(data, 'set_{}'.format(i[2]))(None)

        elif i[1] == wayround_org.xmpp.xcard_temp.PCData:
            if i[3] in ['', '?']:
                attr = getattr(data, 'set_{}'.format(i[2]))
                field = getattr(inst, '_{}'.format(i[2]))
                if not field.get_deleted():
                    attr(
                        wayround_org.xmpp.xcard_temp.PCData(
                            lxml.etree.QName(i[0]).localname,
                            field.get_value()
                            )
                        )
                else:
                    attr(None)
            elif i[3] in ['*', '+']:
                attr = getattr(data, 'set_{}'.format(i[2]))
                field = getattr(inst, '_{}'.format(i[2]))
                attr(
                    [wayround_org.xmpp.xcard_temp.PCData(
                        lxml.etree.QName(i[0]).localname,
                        x
                        ) for x in field.get_value()]
                    )

        else:
            d = wayround_org.utils.gtk.MessageDialog(
                wayround_org.utils.gtk.get_root_gtk_window(
                    inst.get_widget()
                    ),
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Not supported field type: {}".format(i[1])
                )
            d.run()
            d.destroy()

    return


def _set_editable_fields(inst, elements_struct, value):

    for i in elements_struct:
        field = getattr(inst, '_{}'.format(i[2]))
        field.set_editable(value)

    return


def _destroy_fields(inst, elements_struct):
    for i in elements_struct:
        field = getattr(inst, '_{}'.format(i[2]))
        field.destroy()

    return


def is_EMAIL_values_error(self):

    ret = False

    if self._userid.get_deleted():
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "UserID is required in EMAIL property"
            )
        d.run()
        d.destroy()
        ret = True

    return ret

EMAIL.is_values_error = is_EMAIL_values_error
del is_EMAIL_values_error


def is_TEL_values_error(self):

    ret = False

    if self._number.get_deleted():
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Number is required in TEL property"
            )
        d.run()
        d.destroy()
        ret = True

    return ret

TEL.is_values_error = is_TEL_values_error
del is_TEL_values_error


def is_image_binval_error(self):

    ret = False

    if not self._binval.get_deleted() and not self._extval.get_deleted():
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Binval and Extval can not be present both. Disable one of them"
            )
        d.run()
        d.destroy()
        ret = True

    if self._binval.get_deleted() and self._extval.get_deleted():
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Binval and Extval can not be disabled both. Enable one of them"
            )
        d.run()
        d.destroy()
        ret = True

    if not self._binval.get_deleted() and self._type_.get_deleted():
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "If binval enabled, type must be enabled too"
            )
        d.run()
        d.destroy()
        ret = True

    return ret


PHOTO.is_values_error = is_image_binval_error
LOGO.is_values_error = is_image_binval_error
del is_image_binval_error


def is_GEO_values_error(self):

    ret = False

    try:
        float(self._lat.get_value())
        float(self._lon.get_value())
    except:
        ret = True

    if ret:
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Both values of GEO must be float"
            )
        d.run()
        d.destroy()
        ret = True

    return ret

GEO.is_values_error = is_GEO_values_error
del is_GEO_values_error


def is_CLASS_values_error(self):

    ret = False

    c = 0

    if self._public.get_value():
        c += 1

    if self._private.get_value():
        c += 1

    if self._confidential.get_value():
        c += 1

    if c:
        d = wayround_org.utils.gtk.MessageDialog(
            wayround_org.utils.gtk.get_root_gtk_window(
                self.get_widget()
                ),
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "There must be one and only one selection in CLASS property"
            )
        d.run()
        d.destroy()
        ret = True

    return ret

CLASS.is_values_error = is_CLASS_values_error
del is_CLASS_values_error
