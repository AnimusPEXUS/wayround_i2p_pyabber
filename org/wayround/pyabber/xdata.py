
import logging
import lxml.etree
import copy
import json

import org.wayround.utils.list
import org.wayround.xmpp.core

from gi.repository import Gtk

EXPENDABLE_WIDGETS = ['list-multi', 'list-single', 'jid-multi', 'text-multi']

class XDataFormWidgetController:

    def __init__(self, x_data):

        """
        Forms a Gtk+3 widget, which can be added to Container or packed to Box

        x_data is deepcopied internally
        """

        if not isinstance(x_data, dict):
            raise TypeError("`element' must be lxml.etree.Element")

        x_data = copy.deepcopy(x_data)
        self._x_data = x_data

        self._fields = {}

        main_frame = Gtk.Frame()
        self._main_frame = main_frame

        b = Gtk.Box()
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_spacing(5)
        sw = Gtk.ScrolledWindow()
        sw.add(b)
        main_frame.add(sw)
        b.set_orientation(Gtk.Orientation.VERTICAL)
        self._main_box = b

        title_label = Gtk.Label(x_data['title'])
        main_frame.set_label_widget(title_label)

        if x_data['instructions']:
            instructions_frame = Gtk.Frame()
            instructions_frame.set_label("Instructions")

            instructions_box = Gtk.Box()
            instructions_box.set_spacing(5)
            instructions_frame.add(instructions_box)
            instructions_box.set_orientation(Gtk.Orientation.VERTICAL)

            for i in x_data['instructions']:
                label = Gtk.Label(i)
                instructions_box.pack_start(label, False, False, 0)

            b.pack_start(instructions_frame, False, False, 0)

        for i in x_data['fields']:
            if i['var'] != None:
                w = _field_widget(i)
                self._fields[i['var']] = w['controller']

                widg = w['widget']
                exp = False
                if i['type'] in EXPENDABLE_WIDGETS:
                    exp = True
                b.pack_start(widg, exp, exp, 0)

        if len(x_data['reported_fields']) != 0:
            widg = ReportWidget(x_data)
            w = widg.get_widget()
            b.pack_start(w, True, True, 0)

        b.show_all()

        return

    def get_widget(self):
        return self._main_frame

    def gen_x_data(self):
        """
        Applies form changes to internal x_data copy and returns the result

        Only field values are touched, so You may need to strip unneeded data
        and change form type value to use it as submit data. There are some
        functions to help You with this.
        """

        ret = None

        error = False

        for i in self._x_data['fields']:
            var = i['var']

            if not i['type'] in ['hidden', 'fixed']:
                field = self._fields[var]

                if field.has_errors():
                    d = org.wayround.utils.gtk.MessageDialog(
                        None,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Error in field {} ({})".format(i['label'], i['var'])
                        )
                    d.run()
                    d.destroy()
                    error = True

                i['values'] = field.get_values()

        if error:
            ret = None
        else:
            ret = self._x_data

        return ret

def _field_widget(field_data):

    f = Gtk.Frame()

    r = ' '
    if field_data['required']:
        r = ' (*)'

    f.set_label(
        "{label} {{{typ}}}{req}".format(
            label=field_data['label'],
            typ=field_data['type'],
            req=r
            )
        )


    b = Gtk.Box()
    f.add(b)
    b.set_spacing(5)
    b.set_orientation(Gtk.Orientation.VERTICAL)

    if field_data['desc']:
        desc_label = Gtk.Label(field_data['desc'])
        b.pack_start(desc_label, False, False, 0)

    specific_field_widget_controller = None
    ft = field_data['type']
    if ft == 'boolean':
        specific_field_widget_controller = FieldBoolean(field_data)

    elif ft == 'hidden':
        specific_field_widget_controller = FieldHidden(field_data)

    elif ft == 'list-multi':
        specific_field_widget_controller = FieldList(field_data, True)

    elif ft == 'list-single':
        specific_field_widget_controller = FieldList(field_data, False)

    elif ft == 'fixed':
        specific_field_widget_controller = FieldTextArea(field_data, False, True)

    elif ft == 'jid-multi':
        specific_field_widget_controller = FieldTextArea(field_data, True, False)

    elif ft == 'text-multi':
        specific_field_widget_controller = FieldTextArea(field_data, False, False)

    elif ft == 'jid-single':
        specific_field_widget_controller = FieldText(field_data, True, False)

    elif ft == 'text-single':
        specific_field_widget_controller = FieldText(field_data, False, False)

    elif ft == 'text-private':
        specific_field_widget_controller = FieldText(field_data, False, True)

    else:
        raise ValueError("invalid field type: {}".format(field_data['type']))

    widg = specific_field_widget_controller.get_widget()
    widg.set_margin_top(5)
    widg.set_margin_bottom(5)
    widg.set_margin_left(5)
    widg.set_margin_right(5)
    exp = False
    if ft in EXPENDABLE_WIDGETS:
        exp = True
    b.pack_start(widg, exp, exp, 0)

    return {'controller':specific_field_widget_controller, 'widget':f}

class FieldBoolean:

    def __init__(self, field_data):

        value = False
        if len(field_data['values']) != 0:
            value = field_data['values'][0]
            value = value == 'true' or value == '1'

        text = field_data['label']

        widget = Gtk.CheckBox()
        widget.set_label(text)
        widget.set_active(value)

        self._widget = widget

    def get_values(self):
        return self._widget.get_active()

    def get_widget(self):
        return self._widget

    def has_errors(self):
        return False

class FieldHidden:

    def __init__(self, field_data):
        self._values = copy.copy(field_data['values'])
        self._w = Gtk.Label(json.dumps(self._values))

    def get_values(self):
        return self._values

    def get_widget(self):
        return self._w

    def has_errors(self):
        return False

class FieldList:

    def __init__(self, field_data, multi=False):

        v = Gtk.TreeView()
        self._view = v
        f = Gtk.Frame()
        sw = Gtk.ScrolledWindow()
        sw.add(v)
        f.add(sw)
        self._widget = f

        c1 = Gtk.TreeViewColumn()
        cr1 = Gtk.CellRendererText()
        c1.pack_start(cr1, False)
        c1.add_attribute(cr1, 'text', 1)
        v.append_column(c1)
        v.set_headers_visible(False)

        s = v.get_selection()

        if multi:
            s.set_mode(Gtk.SelectionMode.MULTIPLE)

        model = Gtk.ListStore(str, str)

        if field_data['options']:
            for i in field_data['options']:
                l = i['value']
                if i['label'] != None:
                    l = '{} ({})'.format(i['label'], i['value'])

                model.append([i['value'], l])

        v.set_model(model)

        selected = False
        for i in range(len(model)):
            val = model[i][1]
            if val in field_data['values'] and (not multi and not selected):
                s.select_path(Gtk.TreePath([i]))
                selected = True
            else:
                s.unselect_path(Gtk.TreePath([i]))


    def get_values(self):

        s = self._view.get_selection()
        sele = s.get_selection()
        model, rows = sele.get_selected_rows()
        ret = []

        for i in rows:
            ne = model[i][1]
            ret.append(ne)

        return ret

    def get_widget(self):
        return self._widget

    def has_errors(self):
        return False

class FieldTextArea:

    def __init__(self, field_data, jid_mode=False, fixed=False):

        value = field_data['values']

        if not isinstance(value, list):
            raise TypeError("`value' must be list")

        self._is_jid_mode = jid_mode

        view = Gtk.TextView()
        sw = Gtk.ScrolledWindow()
        sw.add(view)
        frame = Gtk.Frame()
        frame.add(sw)

        self._widget = frame
        self._view = view

        text = '\n'.join(value)

        view.get_buffer().set_text(text)

        view.set_editable(not fixed)


    def get_values(self):

        b = self._view.get_buffer()

        res = b.get_text(
            b.get_start_iter(),
            b.get_end_iter(),
            False
            )

        lines = res.splitlines()

        if self._is_jid_mode:

            lines = org.wayround.utils.list.list_lower(lines)
            lines = org.wayround.utils.list.list_strip_remove_empty_remove_duplicated_lines(lines)

            lines2 = []

            for i in lines:
                if not i in lines2:
                    lines2.append(i)

            lines = lines2

        return lines

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
                    res = org.wayround.xmpp.core.jid_from_str(i)
                except:
                    logging.exception("Exception")
                    err = True

                if not isinstance(res, org.wayround.xmpp.core.JID) or err:
                    ret = True

        return ret

class FieldText:

    def __init__(self, field_data, jid_mode=False, private=False):

        value = ''
        if field_data['values']:
            value = field_data['values'][0]

        if not isinstance(value, str):
            raise TypeError("`value' must be str")

        self._is_jid_mode = jid_mode

        entry = Gtk.Entry()

        self._widget = entry
        self._entry = entry

        text = '\n'.join(value)

        entry.set_text(text)
        entry.set_visibility(not private)


    def get_values(self):

        ret = self._entry.get_text()
        if self._is_jid_mode:
            ret = ret.lower().strip()

        return [ret]

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
                res = org.wayround.xmpp.core.jid_from_str(val)
            except:
                logging.exception("Exception")
                err = True

            if not isinstance(res, org.wayround.xmpp.core.JID) or err:
                ret = True

        return ret


class ReportWidget:

    def __init__(self, x_data):

        if not isinstance(x_data, dict):
            raise TypeError("`element' must be lxml.etree.Element")

        frame = Gtk.Frame()
        self._widget = frame
        sw = Gtk.ScrolledWindow()
        view = Gtk.TreeView()
        sw.add(view)
        frame.add(sw)

        store = eval(
            'Gtk.ListStore({})'.format(
                ', '.join(['str'] * len(x_data['reported_fields']))
                )
            )

        view.set_model(store)

        fields = []
        fields_count = len(x_data['reported_fields'])
        for i in range(fields_count):

            field = x_data['reported_fields'][0]

            c1 = Gtk.TreeViewColumn()
            c1.set_title(field['label'])
            cr1 = Gtk.CellRendererText()
            c1.pack_start(cr1, False)
            c1.add_attribute(cr1, 'text', i)
            view.append_column(c1)

            fields.append(field['var'])

        for i in x_data['reported_items']:

            vares = [None] * len()

            for j in i:

                if j['values']:
                    vares[fields.index(j['var'])] = j['values'][0]

            store.append(vares)

        return

    def get_widget(self):
        return self._widget






