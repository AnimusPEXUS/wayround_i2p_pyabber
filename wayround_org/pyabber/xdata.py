
import copy
import json
import logging

from gi.repository import Gtk, Pango

import wayround_org.pyabber.ccc
import wayround_org.pyabber.xdata_media_element
import wayround_org.utils.list
import wayround_org.xmpp.core
import wayround_org.xmpp.xdata


EXPENDABLE_WIDGETS = ['list-multi', 'list-single', 'jid-multi', 'text-multi']


class XDataFormWidget:

    def __init__(self, controller, x_data, origin_stanza, editable=True):

        """
        Forms a Gtk+3 widget, which can be added to Container or packed to Box

        x_data is deepcopied internally
        """

        if not isinstance(x_data, wayround_org.xmpp.xdata.XData):
            raise TypeError("`x_data' must be wayround_org.xmpp.xdata.XData")

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise TypeError(
    "`controller' must be wayround_org.pyabber.ccc.ClientConnectionController"
                )

        if (origin_stanza != None
            and not isinstance(origin_stanza, wayround_org.xmpp.core.Stanza)):
            raise ValueError(
                "`origin_stanza' must be None or wayround_org.xmpp.core.Stanza"
                )

        self._controller = controller
        self._origin_stanza = origin_stanza
        self._editable = editable

        x_data = copy.deepcopy(x_data)
        self._x_data = x_data

        self._fields = {}
        self._fieldswgs = []
        self._media_fields = []

        main_frame = Gtk.Frame()
        self._main_frame = main_frame

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_spacing(5)
        sw = Gtk.ScrolledWindow()
        sw.add(b)
        main_frame.add(sw)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        self._main_box = b

        title_label = Gtk.Label(x_data.get_title() or 'No title')
        main_frame.set_label_widget(title_label)

        instructions = x_data.get_instructions()
        if len(instructions) != 0:
            instructions_frame = Gtk.Frame()
            instructions_frame.set_label("Instructions")

            instructions_box = Gtk.Box()
            instructions_box.set_spacing(5)
            instructions_frame.add(instructions_box)
            instructions_box.set_orientation(Gtk.Orientation.VERTICAL)

            for i in instructions:
                label = Gtk.Label(i)
                instructions_box.pack_start(label, False, False, 0)

            b.pack_start(instructions_frame, False, False, 0)

        fields = x_data.get_fields()
        for i in fields:
            i_var = i.get_var()
            if i_var != None:
                w = self.field_widget(i)
                self._fields[i_var] = w['controller']

                widg = w['widget']
                exp = False
                if i.get_type() in EXPENDABLE_WIDGETS:
                    exp = True
                b.pack_start(widg, exp, exp, 0)

        if len(x_data.get_reported_fields()) != 0:
            widg = ReportWidget(x_data)
            w = widg.get_widget()
            b.pack_start(w, True, True, 0)

        self.get_widget().show_all()

        return

    def get_widget(self):
        return self._main_frame

    def destroy(self):
        # TODO: check everything is destroyed
        for i in self._fieldswgs[:]:
            i.destroy()
            self._fieldswgs.remove(i)

        for i in self._media_fields[:]:
            i.destroy()
            self._media_fields.remove(i)

        self.get_widget().destroy()

    def gen_stanza_subobject(self):
        """
        Applies form changes to internal x_data copy and returns the result

        Only field values are touched, so You may need to strip unneeded data
        and change form type value to use it as submit data. There are some
        functions to help You with this.
        """

        ret = None

        error = False

        for i in self._x_data.get_fields():
            var = i.get_var()

            if not i.get_type() in ['hidden', 'fixed']:
                field = self._fields[var]

                if field.has_errors():
                    d = wayround_org.utils.gtk.MessageDialog(
                        wayround_org.utils.gtk.get_root_gtk_window(
                            self.get_widget()
                            ),
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Error in field {} ({})".format(i.get_label(), var)
                        )
                    d.run()
                    d.destroy()
                    error = True

                i.set_values(field.get_values())

        if error:
            ret = None
        else:
            ret = self._x_data

        return ret

    def field_widget(self, field_data):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        b = Gtk.Box()
        b.set_spacing(5)
        b.set_orientation(Gtk.Orientation.VERTICAL)

        desc = field_data.get_desc()
        if desc:
            desc_label = Gtk.Label(desc)
            b.pack_start(desc_label, False, False, 0)

        media = field_data.get_media()
        if media != None:
            media_widget = \
                wayround_org.pyabber.xdata_media_element.MediaElementWidget(
                    self._controller,
                    media,
                    self._origin_stanza
                    )
            self._media_fields.append(media_widget)
            b.pack_start(media_widget.get_widget(), False, False, 0)

        specific_field_widget_controller = None
        ft = field_data.get_type()
        if ft == 'boolean':
            specific_field_widget_controller = \
                FieldBoolean(field_data, editable=self._editable)

        elif ft == 'hidden':
            specific_field_widget_controller = \
                FieldHidden(field_data, editable=self._editable)

        elif ft == 'list-multi':
            specific_field_widget_controller = \
                FieldList(field_data, True, editable=self._editable)

        elif ft == 'list-single':
            specific_field_widget_controller = \
                FieldList(field_data, False, editable=self._editable)

        elif ft == 'fixed':
            specific_field_widget_controller = \
                FieldTextArea(field_data, False, True, editable=self._editable)

        elif ft == 'jid-multi':
            specific_field_widget_controller = \
                FieldTextArea(field_data, True, False, editable=self._editable)

        elif ft == 'text-multi':
            specific_field_widget_controller = \
                FieldTextArea(
                    field_data, False, False, editable=self._editable
                    )

        elif ft == 'jid-single':
            specific_field_widget_controller = \
                FieldText(field_data, True, False, editable=self._editable)

        elif ft == 'text-single':
            specific_field_widget_controller = \
                FieldTextArea(
                    field_data, False, False, True, editable=self._editable
                    )

        elif ft == 'text-private':
            specific_field_widget_controller = \
                FieldText(field_data, False, True, editable=self._editable)

        else:
            raise ValueError("invalid field type: {}".format(ft))

        widg = specific_field_widget_controller.get_widget()
        self._fieldswgs.append(widg)
        widg.set_margin_start(5)
        widg.set_margin_end(5)
        exp = False
        if ft in EXPENDABLE_WIDGETS:
            exp = True
        b.pack_start(widg, exp, exp, 0)

        ret_widg = b
        if ft not in ['boolean']:
            widg.set_margin_top(5)
            widg.set_margin_bottom(5)
            f = Gtk.Frame()

            r = ''
            if field_data.get_required():
                r = ' (required)'

            f.set_label(
                "{label} {{{typ}}}{req}".format(
                    label=field_data.get_label(),
                    typ=field_data.get_type(),
                    req=r
                    )
                )
            f.add(b)
            ret_widg = f

        return {
            'controller': specific_field_widget_controller,
            'widget': ret_widg
            }


class FieldBoolean:

    def __init__(self, field_data, editable=True):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        value = False
        values = field_data.get_values()
        if len(values) != 0:
            value = values[0].get_value()
            value = value == 'true' or value == '1'

        text = field_data.get_label()

        widget = Gtk.CheckButton()
        widget.set_sensitive(editable)
        widget.set_label(text)
        widget.set_active(value)

        self._widget = widget

    def get_values(self):
        val = self._widget.get_active()
        ret = '0'
        if val:
            ret = '1'

        ret = wayround_org.xmpp.xdata.XDataValue(ret)
        return [ret]

    def get_widget(self):
        return self._widget

    def has_errors(self):
        return False

    def destroy(self):
        self.get_widget().destroy()


class FieldHidden:

    def __init__(self, field_data, editable=True):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        self._values = copy.copy(field_data.get_values())
        vals = []
        for i in self._values:
            vals.append(i.get_value())
        self._w = Gtk.Label(json.dumps(vals))
        self._w.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self._w.set_selectable(True)

    def get_values(self):
        return self._values

    def get_widget(self):
        return self._w

    def has_errors(self):
        return False

    def destroy(self):
        self.get_widget().destroy()


class FieldList:

    def __init__(self, field_data, multi=False, editable=True):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        view = Gtk.TreeView()
        view.set_sensitive(editable)
        self._view = view
        frame = Gtk.Frame()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add(view)
        frame.add(scrolledwindow)
        self._widget = frame

        c1 = Gtk.TreeViewColumn()
        cr1 = Gtk.CellRendererText()
        c1.pack_start(cr1, False)
        c1.add_attribute(cr1, 'text', 1)
        view.append_column(c1)
        view.set_headers_visible(False)

        selection = view.get_selection()

        if multi:
            selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        # there may be no default value, so SINGLE mode is not acceptable
        #        else:
        #            selection.set_mode(Gtk.SelectionMode.SINGLE)

        model = Gtk.ListStore(str, str)

        options = field_data.get_options()
        if options:
            for i in options:
                value = i.get_value().get_value()
                label = i.get_label()
                l = value
                if label != None:
                    l = '{} (value: {})'.format(label, value)

                model.append([value, l])

        view.set_model(model)

        values = field_data.get_values()
        values2 = []
        for i in values:
            values2.append(i.get_value())

        values = values2

        selected = False
        scroll_to = None
        for i in range(len(model)):

            val = model[i][0]

            if val in values and (not multi and not selected):
                path = Gtk.TreePath([i])
                selection.select_path(path)
                scroll_to = path
                selected = True
            else:
                selection.unselect_path(Gtk.TreePath([i]))

        if scroll_to:
            view.scroll_to_cell(scroll_to, None, True, 0.1, 0.0)

        return

    def get_values(self):

        sele = self._view.get_selection()
        model, rows = sele.get_selected_rows()
        ret = []

        for i in rows:
            ne = model[i][0]
            ret.append(wayround_org.xmpp.xdata.XDataValue(ne))

        return ret

    def get_widget(self):
        return self._widget

    def has_errors(self):
        return False

    def destroy(self):
        self.get_widget().destroy()


class FieldTextArea:

    def __init__(
        self, field_data, jid_mode=False, fixed=False, single_mode=False,
        editable=True
        ):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        self._is_jid_mode = jid_mode
        self._is_single_mode = single_mode

        view = Gtk.TextView()
        sw = Gtk.ScrolledWindow()
        sw.add(view)
        frame = Gtk.Frame()
        frame.add(sw)

        self._widget = frame
        self._view = view

        values = []

        for i in field_data.get_values():
            for j in i.get_value().splitlines():
                values.append(j)

        text = '\n'.join(values)

        view.get_buffer().set_text(text)

        view.set_editable(not fixed and editable)

        return

    def get_values(self):

        b = self._view.get_buffer()

        res = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        lines = res.splitlines()

        if self._is_jid_mode:

            lines = wayround_org.utils.list.list_lower(lines)
            lines = wayround_org.utils.list.\
                list_strip_remove_empty_remove_duplicated_lines(lines)

            lines2 = []

            for i in lines:
                if not i in lines2:
                    lines2.append(i)

            lines = lines2

        if self._is_single_mode:
            lines = ['\n'.join(lines)]

        ret = []
        for i in lines:
            ret.append(wayround_org.xmpp.xdata.XDataValue(i))

        return ret

    def get_widget(self):
        return self._widget

    def has_errors(self):
        ret = False

        if not self._is_jid_mode:
            ret = False
        else:
            val = self.get_values()
            for i in val:
                res = None
                err = False
                try:
                    res = wayround_org.xmpp.core.JID.new_from_str(
                        i.get_value()
                        )
                except:
                    logging.exception("Can't convert string to JID")
                    err = True

                if not isinstance(res, wayround_org.xmpp.core.JID) or err:
                    ret = True

        return ret

    def destroy(self):
        self.get_widget().destroy()


class FieldText:

    def __init__(
        self, field_data, jid_mode=False, private=False,
        editable=True
        ):

        if not isinstance(field_data, wayround_org.xmpp.xdata.XDataField):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XDataField"
                )

        value = ''
        values = field_data.get_values()
        if values:
            value = values[0].get_value()

        self._is_jid_mode = jid_mode

        entry = Gtk.Entry()
        entry.set_editable(editable)

        self._widget = entry
        self._entry = entry

        entry.set_text(value)
        entry.set_visibility(not private)

    def get_values(self):

        ret = self._entry.get_text()
        if self._is_jid_mode:
            ret = ret.lower().strip()

        return [wayround_org.xmpp.xdata.XDataValue(ret)]

    def get_widget(self):
        return self._widget

    def has_errors(self):

        ret = False

        if not self._is_jid_mode:
            ret = False
        else:
            val = self.get_values()[0]

            res = None
            err = False
            try:
                res = wayround_org.xmpp.core.JID.new_from_str(val.get_value())
            except:
                logging.exception("Can't convert string to JID")
                err = True

            if not isinstance(res, wayround_org.xmpp.core.JID) or err:
                ret = True

        return ret

    def destroy(self):
        self.get_widget().destroy()


class ReportWidget:

    def __init__(self, x_data):

        if not isinstance(x_data, wayround_org.xmpp.xdata.XData):
            raise TypeError(
                "`field_data' must be wayround_org.xmpp.xdata.XData"
                )

        frame = Gtk.Frame()
        self._widget = frame
        sw = Gtk.ScrolledWindow()
        view = Gtk.TreeView()
        sw.add(view)
        frame.add(sw)

        reported_fields = x_data.get_reported_fields()
        reported_items = x_data.get_reported_items()

        store = eval(
            'Gtk.ListStore({})'.format(
                ', '.join(['str'] * len(reported_fields))
                )
            )

        view.set_model(store)

        fields = []
        fields_count = len(reported_fields)
        for i in range(fields_count):

            field = reported_fields[0]

            c1 = Gtk.TreeViewColumn()
            c1.set_title(field.get_label())
            cr1 = Gtk.CellRendererText()
            c1.pack_start(cr1, False)
            c1.add_attribute(cr1, 'text', i)
            view.append_column(c1)

            fields.append(field.get_var())

        for i in reported_items:

            vares = [None] * len()

            for j in i:
                values = j.get_values()
                if values:
                    vares[fields.index(j.get_var())] = values[0]

            store.append(vares)

        return

    def get_widget(self):
        return self._widget

    def destroy(self):
        self.get_widget().destroy()
