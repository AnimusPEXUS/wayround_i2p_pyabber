
from gi.repository import Gtk

import org.wayround.pyabber.ccc
import org.wayround.pyabber.oob
import org.wayround.pyabber.xdata
import org.wayround.utils.gtk
import org.wayround.xmpp.core
import org.wayround.xmpp.registration


class RegistrationWidgetField:

    def __init__(self, name, label='noname', value=''):

        self.name = name

        self.frame = Gtk.Frame()
        self.frame.set_label(label)

        self.entry = Gtk.Entry()
        self.entry.set_margin_top(5)
        self.entry.set_margin_left(5)
        self.entry.set_margin_right(5)
        self.entry.set_margin_bottom(5)
        self.entry.set_text(value)

        self.frame.add(self.entry)

    def get_widget(self):
        return self.frame

    def get_value(self):
        return self.entry.get_text()

    def destroy(self):
        self.get_widget().destroy()


class RegistrationWidget:

    def __init__(self):

        self._fields = []
        self._oob = None
        self._xdata = None

        self._registered_label = Gtk.Label()
        self._insructions_label = Gtk.Label()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        b.pack_start(self._registered_label, False, False, 0)
        b.pack_start(self._insructions_label, False, False, 0)

        self._b = b

        return

    def set_form(self, form):

        while len(self._fields) != 0:
            self._fields[0].destroy()
            del self._fields[0]

        if self._oob != None:
            self._oob.destroy()
            self._oob = None

        if self._xdata != None:
            self._xdata.destroy()
            self._xdata = None

        if form.get_registered():
            self._registered_label.set_text("ALREADY REGISTERED")
        else:
            self._registered_label.set_text("NOT registered")

        instructions = form.get_instructions()

        if instructions != None:
            self._insructions_label.set_text(instructions)
        else:
            self._insructions_label.set_text("(instructions not provided)")

        fields = form.get_input_fields()

        for i in list(fields.keys()):

            v = ''
            if isinstance(fields[i], str):
                v = fields[i]

            _t = RegistrationWidgetField(i, label=i, value=v)

            self._fields.append(_t)
            self._b.pack_start(_t.get_widget(), False, False, 0)

        oob = form.get_oob()
        if oob != None:
            self._oob = org.wayround.pyabber.oob.OOBField(oob)
            _f = Gtk.Frame()
            _f.set_label("Out of Band Data")

            _w = self._oob.get_widget()
            _f.add(_w)
            self._b.pack_start(_f, False, False, 0)

        xdata = form.get_xdata()
        if xdata != None:
            self._xdata = org.wayround.pyabber.xdata.XDataFormWidgetController(
                xdata
                )
            _f = Gtk.Frame()
            _f.set_label("Additional Form Supplied")

            _w = self._xdata.get_widget()
            _f.add(_w)
            _w.set_margin_top(5)
            _w.set_margin_left(5)
            _w.set_margin_right(5)
            _w.set_margin_bottom(5)
            self._b.pack_start(_f, True, True, 0)

        self._b.show_all()

        return

    def get_form(self):

        form = org.wayround.xmpp.registration.Query()

        for i in self._fields:

            key = i.name

            func = getattr(form, 'set_{}'.format(key))

            func(i.get_value())

        if self._xdata != None:
            xdata = self._xdata.gen_x_data()
            form.set_xdata(xdata)

        return form

    def set_pred_username(self, value):
        for i in self._fields:
            if i.name == 'username':
                i.entry.set_text(value)
                i.set_sensitive(False)
        return

    def set_pred_password(self, value):
        for i in self._fields:
            if i.name == 'password':
                i.entry.set_text(value)
                i.set_sensitive(False)
        return

    def get_widget(self):
        return self._b


class RegistrationWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.above.client.XMPPC2SClient"
                )

        self._controller = controller
        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._pred_username = None
        self._pred_password = None

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_bottom(5)
        b.set_margin_right(5)

        target_cb = Gtk.CheckButton()
        self._target_cb = target_cb
        target_cb.set_label("Target JID (check to use it)")
        target_frame = Gtk.Frame()
        target_frame.set_label_widget(target_cb)
        target_entry = Gtk.Entry()
        target_entry.set_margin_top(5)
        target_entry.set_margin_left(5)
        target_entry.set_margin_bottom(5)
        target_entry.set_margin_right(5)
        self._target_entry = target_entry
        target_frame.add(target_entry)

        from_cb = Gtk.CheckButton()
        self._from_cb = from_cb
        from_cb.set_label("From JID (check to use it)")
        from_frame = Gtk.Frame()
        from_frame.set_label_widget(from_cb)
        from_entry = Gtk.Entry()
        from_entry.set_margin_top(5)
        from_entry.set_margin_left(5)
        from_entry.set_margin_bottom(5)
        from_entry.set_margin_right(5)
        self._from_entry = from_entry
        from_frame.add(from_entry)

        self._reg_widget_ins = RegistrationWidget()
        _reg_widget_ins_widg = self._reg_widget_ins.get_widget()
        #        _reg_widget_ins_widg.set_margin_top(5)
        #        _reg_widget_ins_widg.set_margin_left(5)
        #        _reg_widget_ins_widg.set_margin_right(5)
        #        _reg_widget_ins_widg.set_margin_bottom(5)

        self._resolution_label = Gtk.Label('waiting for Your actions')
        self._resolution_label.set_tooltip_text(
            """\
This text will be returned to caller.
'REGISTERED' is valid value for registration sequences.
'UNREGISTERED' is valid value for unreg sequences."""
            )

        bb2 = Gtk.ButtonBox()
        bb2.set_orientation(Gtk.Orientation.HORIZONTAL)

        get_data_button = Gtk.Button("Get Registration Form")
        get_data_button.connect('clicked', self._on_get_form_button_clicked)

        send_button = Gtk.Button("Send this Form")
        send_button.connect('clicked', self._on_send_button_clicked)

        remove_button = Gtk.Button("Remove Registration")
        remove_button.connect('clicked', self._on_remove_button_clicked)

        bb2.pack_start(get_data_button, False, False, 0)
        bb2.pack_start(send_button, False, False, 0)
        bb2.pack_start(
            Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 0
            )
        bb2.pack_start(remove_button, False, False, 0)

        close_button = Gtk.Button("Close")
        close_button.connect('clicked', self._on_close_button_clicked)
        close_button.set_tooltip_text(
            "Close this window and return resulting message to caller"
            )

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        bb.pack_start(close_button, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.add(_reg_widget_ins_widg)

        b.pack_start(target_frame, False, False, 0)
        b.pack_start(from_frame, False, False, 0)
        b.pack_start(bb2, False, False, 0)
        b.pack_start(sw, True, True, 0)
        b.pack_start(
            Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), False, False, 0
            )
        b.pack_start(self._resolution_label, False, False, 0)
        b.pack_start(
            Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), False, False, 0
            )
        b.pack_start(bb, False, False, 0)

        self._resolution_text = 'error'

        window.add(b)

        self._window = window

        return

    def run(
        self,
        target_jid_obj=None, from_jid_obj=None, get_reg_form=False,
        predefined_form=None,
        pred_username=None, pred_password=None
        ):

        if isinstance(pred_username, str):
            self._pred_username = pred_username

        if isinstance(pred_password, str):
            self._pred_password = pred_password

        if target_jid_obj != None:
            self._target_entry.set_text(str(target_jid_obj))
            self._target_cb.set_active(True)
        else:
            self._target_entry.set_text('')
            self._target_cb.set_active(False)

        if from_jid_obj != None:
            self._from_entry.set_text(str(from_jid_obj))
            self._from_cb.set_active(True)
        else:
            self._from_entry.set_text('')
            self._from_cb.set_active(False)

        if predefined_form != None:
            self._reg_widget_ins.set_form(predefined_form)
        else:
            if get_reg_form == True:
                self.get_registration_form()

        self.show()
        self._iterated_loop.wait()
        return self._resolution_text

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._resolution_text = self._resolution_label.get_text()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def get_to_and_from(self):

        to = None
        from_ = None

        if self._target_cb.get_active():
            to = self._target_entry.get_text()

        if self._from_cb.get_active():
            from_ = self._from_entry.get_text()

        return to, from_

    def get_registration_form(self):

        t, f = self.get_to_and_from()

        res = org.wayround.xmpp.registration.get_form(
            f,
            t,
            self._controller.client.stanza_processor,
            True
            )

        if res == None:
            self._resolution_label.set_text("Unknown Error")
        else:
            if res.is_error():
                self._resolution_label.set_text(
                    res.gen_error().gen_text()
                    )
            else:
                self._reg_widget_ins.set_form(res)

        return

    def _on_close_button_clicked(self, widget):
        self._window.destroy()

    def _on_send_button_clicked(self, widget):
        t, f = self.get_to_and_from()
        form = self._reg_widget_ins.get_form()
        res = org.wayround.xmpp.registration.set_form(
            t,
            f,
            form,
            self._controller.client.stanza_processor,
            True
            )
        if res == None:
            self._resolution_label.set_text("Unknown Error")
        else:
            if res.is_error():
                self._resolution_label.set_text(
                    res.gen_error().gen_text()
                    )
            else:
                self._resolution_label.set_text("REGISTERED")
        return

    def _on_remove_button_clicked(self, widget):
        t, f = self.get_to_and_from()
        res = org.wayround.xmpp.registration.unregister(
            t,
            f,
            self._controller.client.stanza_processor,
            True
            )
        if res == None:
            self._resolution_label.set_text("Unknown Error")
        else:
            if res.is_error():
                self._resolution_label.set_text(
                    res.gen_error().gen_text()
                    )
            else:
                self._resolution_label.set_text("UNREGISTERED")
        return

    def _on_get_form_button_clicked(self, widget):
        self.get_registration_form()
        return
