
import threading

from gi.repository import Gtk

import wayround_org.pyabber.misc
import wayround_org.pyabber.xdata
import wayround_org.utils.gtk
import wayround_org.xmpp.captcha
import wayround_org.xmpp.core


class CAPTCHAWidget:

    def __init__(
        self,
        controller,
        captcha_element_object,
        origin_stanza,
        editable=True
        ):

        self._controller = controller
        self._captcha_element_object = captcha_element_object
        self._editable = editable
        self._origin_stanza = origin_stanza

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        self._xdata = captcha_element_object.get_x()

        self._xdata_widget = wayround_org.pyabber.xdata.XDataFormWidget(
            controller,
            self._xdata,
            origin_stanza,
            editable
            )

        b.pack_start(self._xdata_widget.get_widget(), True, True, 0)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        b.pack_start(bb, False, False, 0)

        send_button = Gtk.Button("Submit CAPTCHA")
        send_button.connect('clicked', self._on_send_button_clicked)

        bb.pack_start(send_button, False, False, 0)

        self._b = b
        self._b.show_all()

        return

    def destroy(self):
        self._xdata_widget.destroy()
        self.get_widget().destroy()

    def get_widget(self):
        return self._b

    def gen_stanza_subobject(self):

        c = wayround_org.xmpp.captcha.Captcha(
            self._xdata_widget.gen_stanza_subobject()
            )

        return c

    def _t_proc(self, x):
        x['res_data'] = \
            self._controller.client.stanza_processor.send(
                *x['args'],
                **x['kwargs']
                )

    def _on_send_button_clicked(self, button):

        stanza = wayround_org.xmpp.core.Stanza(tag='iq')
        stanza.set_typ('set')
        stanza.set_to_jid(self._origin_stanza.get_from_jid())
        stanza.set_objects(
            [self.gen_stanza_subobject()]
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
                    None,
                    res,
                    "CAPTCHA challenge failed"
                    )
            else:
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    "Processed. No Error Returned From Server."
                    )
                d.run()
                d.destroy()
        else:
            if res == False:
                d = wayround_org.utils.gtk.MessageDialog(
                    wayround_org.utils.gtk.get_root_gtk_window(
                        self.get_widget()
                        ),
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Timeout"
                    )
                d.run()
                d.destroy()

        return
