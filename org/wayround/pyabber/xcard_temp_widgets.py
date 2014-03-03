
from gi.repository import Gtk, Pango

import org.wayround.utils.factory
import org.wayround.xmpp.xcard_temp


class ValuePCDataWidget:

    def __init__(
        self, value='', title='', description='',
        editable=True, deletable=False, deleted=False
        ):

        self._deletable = True

        self._widget = Gtk.Box()
        self._widget.set_orientation(Gtk.Orientation.VERTICAL)
        self._widget.set_margin_top(5)
        self._widget.set_margin_left(5)
        self._widget.set_margin_right(5)
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

        self._present_button.set_visible(
            value == True and self.get_deletable()
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
        self._title.get_text()
        return

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
        self._description.get_text()
        return

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


class N:

    def __init__(self, controller, data, editable):

        self._controller = controller
        self._data = data

        deleted = data.get_family() == None
        value = ''
        if not deleted:
            value = data.get_family().get_text()
        self._value_field = ValuePCDataWidget(
            value, 'Family', '', editable, True, deleted
            )

        deleted = data.get_given() == None
        value = ''
        if not deleted:
            value = data.get_given().get_text()
        self._given = ValuePCDataWidget(
            value, 'Given', '', editable, True, deleted
            )

        deleted = data.get_middle() == None
        value = ''
        if not deleted:
            value = data.get_middle().get_text()
        self._middle = ValuePCDataWidget(
            value, 'Middle', '', editable, True, deleted
            )

        deleted = data.get_prefix() == None
        value = ''
        if not deleted:
            value = data.get_prefix().get_text()
        self._prefix = ValuePCDataWidget(
            value, 'Prefix', '', editable, True, deleted
            )

        deleted = data.get_suffix() == None
        value = ''
        if not deleted:
            value = data.get_suffix().get_text()
        self._suffix = ValuePCDataWidget(
            value, 'Suffix', '', editable, True, deleted
            )

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._b.set_margin_top(5)
        self._b.set_margin_left(5)
        self._b.set_margin_right(5)
        self._b.set_margin_bottom(5)
        self._b.set_spacing(5)

        self._b.pack_start(self._prefix.get_widget(), True, True, 0)
        self._b.pack_start(self._given.get_widget(), True, True, 0)
        self._b.pack_start(self._middle.get_widget(), True, True, 0)
        self._b.pack_start(self._value_field.get_widget(), True, True, 0)
        self._b.pack_start(self._suffix.get_widget(), True, True, 0)

        self._frame = Gtk.Frame()
        self._frame.set_label("N (Name)")
        self._frame.add(self._b)

        self._frame.show_all()

        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    @classmethod
    def corresponding_tag(cls):
        return 'N'

    def set_editable(self, value):
        self._value_field.set_editable(value)
        self._given.set_editable(value)
        self._middle.set_editable(value)
        self._prefix.set_editable(value)
        self._suffix.set_editable(value)
        if value:
            self._b.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self._b.set_orientation(Gtk.Orientation.HORIZONTAL)
        return

    def destroy(self):
        self._value_field.destroy()
        self._given.destroy()
        self._middle.destroy()
        self._prefix.destroy()
        self._suffix.destroy()
        return

    def get_data(self):
        return self._data

    def gen_data(self):
        ret = org.wayround.xmpp.xcard_temp.N()

        ret.set_family(None)
        if not self._value_field.get_deleted():
            ret.set_family(
                org.wayround.xmpp.xcard_temp.PCData(
                    'FAMILY',
                    self._value_field.get_value()
                    )
                )

        ret.set_given(None)
        if not self._given.get_deleted():
            ret.set_given(
                org.wayround.xmpp.xcard_temp.PCData(
                    'GIVEN',
                    self._given.get_value()
                    )
                )

        ret.set_middle(None)
        if not self._middle.get_deleted():
            ret.set_middle(
                org.wayround.xmpp.xcard_temp.PCData(
                    'MIDDLE',
                    self._middle.get_value()
                    )
                )

        ret.set_prefix(None)
        if not self._prefix.get_deleted():
            ret.set_prefix(
                org.wayround.xmpp.xcard_temp.PCData(
                    'PREFIX',
                    self._prefix.get_value()
                    )
                )

        ret.set_suffix(None)
        if not self._suffix.get_deleted():
            ret.set_suffix(
                org.wayround.xmpp.xcard_temp.PCData(
                    'SUFFIX',
                    self._suffix.get_value()
                    )
                )

        return ret


class FN:

    def __init__(self, controller, data, editable):

        self._controller = controller
        self._data = data

        self._value_field = ValuePCDataWidget(
            data.get_text(), '', '', editable, False, False
            )

        self._b = Gtk.Box()
        self._b.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._b.set_margin_top(5)
        self._b.set_margin_left(5)
        self._b.set_margin_right(5)
        self._b.set_margin_bottom(5)
        self._b.set_spacing(5)

        self._b.pack_start(self._value_field.get_widget(), True, True, 0)

        self._frame = Gtk.Frame()
        self._frame.set_label("FN (Full Name)")
        self._frame.add(self._b)

        self._frame.show_all()

        self.set_editable(editable)

        return

    def get_widget(self):
        return self._frame

    @classmethod
    def corresponding_tag(cls):
        return 'FN'

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
        ret = org.wayround.xmpp.xcard_temp.PCData(
            'FN',
            self._value_field.get_value()
            )
        return ret
