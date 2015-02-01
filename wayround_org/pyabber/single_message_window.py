
import copy

from gi.repository import Gtk

import wayround_org.pyabber.captcha
import wayround_org.pyabber.message_edit_widget
import wayround_org.pyabber.subject_widget
import wayround_org.pyabber.thread_widget
import wayround_org.utils.gtk
import wayround_org.xmpp.captcha


class SingleMessageWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller
        self._original_stanza = None

        self._window = Gtk.Window()

        date_label = Gtk.Label()
        date_label.set_no_show_all(True)
        date_label.set_alignment(0.0, 0.5)
        date_label.set_selectable(True)
        self._date_label = date_label

        b0 = Gtk.Box()
        b0.set_orientation(Gtk.Orientation.VERTICAL)
        b0.set_spacing(5)
        b0.set_margin_top(5)
        b0.set_margin_bottom(5)
        b0.set_margin_start(5)
        b0.set_margin_end(5)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.HORIZONTAL)
        b.set_spacing(5)

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_spacing(5)
        main_box.set_size_request(300, -1)

        from_frame = Gtk.Frame()
        from_frame.set_no_show_all(True)
        from_frame.set_label("From Jabber ID")
        self._from_frame = from_frame

        from_entry = Gtk.Entry()
        self._from_entry = from_entry
        from_entry.set_margin_top(5)
        from_entry.set_margin_bottom(5)
        from_entry.set_margin_start(5)
        from_entry.set_margin_end(5)
        from_entry.show()

        from_frame.add(from_entry)

        to_frame = Gtk.Frame()
        to_frame.set_no_show_all(True)
        to_frame.set_label("To Jabber ID")
        self._to_frame = to_frame

        to_entry = Gtk.Entry()
        self._to_entry = to_entry
        to_entry.set_margin_top(5)
        to_entry.set_margin_bottom(5)
        to_entry.set_margin_start(5)
        to_entry.set_margin_end(5)
        to_entry.show()

        to_frame.add(to_entry)

        subject_frame = Gtk.Frame()
        self._subject_frame = subject_frame
        subject_frame_cb = Gtk.CheckButton()
        self._subject_frame_cb = subject_frame_cb

        subject_frame_cb.set_label("Include Subject")
        subject_frame_cb.set_active(True)

        subject_frame.set_label_widget(subject_frame_cb)

        self._subject_widget = \
            wayround_org.pyabber.subject_widget.SubjectWidget(
                controller,
                contact_bare_jid=self._controller.jid.bare(),
                contact_resource=self._controller.jid.resource,
                operation_mode='normal'
                )

        subject_entry = self._subject_widget.get_widget()
        self._subject_entry = subject_entry
        subject_entry.set_margin_top(5)
        subject_entry.set_margin_bottom(5)
        subject_entry.set_margin_start(5)
        subject_entry.set_margin_end(5)

        subject_frame.add(subject_entry)

        thread_frame = Gtk.Frame()
        self._thread_frame = thread_frame
        thread_frame_cb = Gtk.CheckButton()
        self._thread_frame_cb = thread_frame_cb

        thread_frame_cb.set_label("Include Unique Thread Identifier")
        thread_frame_cb.set_active(True)

        thread_frame.set_label_widget(thread_frame_cb)

        thread_box = Gtk.Box()
        thread_box.set_margin_top(5)
        thread_box.set_margin_bottom(5)
        thread_box.set_margin_start(5)
        thread_box.set_margin_end(5)
        thread_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        thread_box.set_spacing(5)

        self._thread_widget = wayround_org.pyabber.thread_widget.ThreadWidget(
            controller,
            contact_bare_jid=self._controller.jid.bare(),
            contact_resource=self._controller.jid.resource,
            operation_mode='normal'
            )

        thread_entry = self._thread_widget.get_widget()
        self._thread_entry = thread_entry
        thread_entry.set_tooltip_text(
            "You not really need to edit it manually!"
            )

        thread_box.pack_start(thread_entry, True, True, 0)

        thread_frame.add(thread_box)

        msg_edit_widget = \
            wayround_org.pyabber.message_edit_widget.MessageEdit(
                self._controller
                )
        self._msg_edit_widget = msg_edit_widget

        self._body_message_editor = msg_edit_widget.get_widget()

        buttons_bb = Gtk.ButtonBox()
        buttons_bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        reply_button = Gtk.Button("Reply..")
        reply_button.set_no_show_all(True)
        reply_button.connect('clicked', self._on_reply_button_clicked)

        send_button = Gtk.Button("Send")
        send_button.connect('clicked', self._on_send_button_clicked)
        send_button.set_no_show_all(True)

        self._reply_button = reply_button
        self._send_button = send_button

        buttons_bb.pack_start(reply_button, False, False, 0)
        buttons_bb.pack_start(send_button, False, False, 0)

        self._additional_box = Gtk.Box()
        self._additional_box.set_spacing(5)
        self._additional_box.set_orientation(Gtk.Orientation.VERTICAL)
        self._additional_box.set_no_show_all(True)

        main_box.pack_start(date_label, False, False, 0)
        main_box.pack_start(from_frame, False, False, 0)
        main_box.pack_start(to_frame, False, False, 0)
        main_box.pack_start(subject_frame, False, False, 0)
        main_box.pack_start(thread_frame, False, False, 0)
        main_box.pack_start(self._body_message_editor, True, True, 0)

        b.pack_start(main_box, True, True, 0)
        b.pack_start(self._additional_box, True, True, 0)

        b0.pack_start(b, True, True, 0)
        b0.pack_start(buttons_bb, False, False, 0)

        self._window.add(b0)
        self._window.connect('destroy', self._on_destroy)

        self._additional_widgets = []

        return

    def __del__(self):
        print("deleting {}".format(self))
        return

    def run(
        self,
        mode='new',
        stanza=None,
        date=None
        ):

        if not mode in ['new', 'view']:
            raise ValueError("Wrong mode")

        if mode == 'view':
            self._date_label.set_text(str(date))

        self._date_label.set_visible(mode == 'view')

        self._original_stanza = stanza

        to_jid = stanza.get_to_jid()
        from_jid = stanza.get_from_jid()
        subject = stanza.get_subject_dict()
        thread = stanza.get_thread()
        body = stanza.get_body_dict()

        if mode == 'new' and thread == None:
            self._thread_widget.generate_new_thread_entry()

        self._reply_button.set_visible(mode == 'view')
        self._send_button.set_visible(mode == 'new')
        self._from_frame.set_visible(mode == 'view')
        self._to_frame.set_visible(mode == 'new')

        if mode == 'view':
            self._subject_frame.set_label("Subject")
            self._thread_frame.set_label("Unique Thread Identifier")

        self._thread_widget.set_editable(mode == 'new')
        self._subject_widget.set_editable(mode == 'new')
        self._from_entry.set_editable(mode == 'new')
        self._to_entry.set_editable(mode == 'new')

        self._msg_edit_widget.set_editable(mode == 'new')

        if to_jid != None:
            self._to_entry.set_text(str(to_jid))

        if from_jid != None:
            self._from_entry.set_text(str(from_jid))

        if subject != None:
            self._subject_widget.set_data(subject)

        if thread != None:
            self._thread_widget.set_data(thread.get_thread())

        if body != None:
            self._msg_edit_widget.set_data(body, None)

        if mode == 'new':
            self._msg_edit_widget.set_cursor_to_end()
            self._msg_edit_widget.grab_focus()

        e = self._original_stanza.get_element()
        if e != None:

            if self._original_stanza.is_error():
                err = self._original_stanza.gen_error()
                txt = err.gen_text()
                l = Gtk.Label(txt)
                l.show()
                self._additional_box.pack_start(l, False, False, 0)

            for i in e:
                if i.tag == '{urn:xmpp:captcha}captcha':

                    captcha_data = \
                        wayround_org.xmpp.captcha.Captcha.new_from_element(i)

                    captcha_widget = \
                        wayround_org.pyabber.captcha.CAPTCHAWidget(
                            self._controller,
                            captcha_element_object=captcha_data,
                            origin_stanza=self._original_stanza,
                            editable=True
                            )

                    self._additional_widgets.append(captcha_widget)
                    self._additional_box.pack_start(
                        captcha_widget.get_widget(),
                        False,
                        False,
                        0
                        )
                    w = captcha_widget.get_widget()
                    w.set_size_request(300, 400)

                if i.tag == '{jabber:x:data}x':

                    xdata = wayround_org.xmpp.xdata.XData.new_from_element(i)

                    xform = wayround_org.pyabber.xdata.XDataFormWidget(
                        self._controller,
                        x_data=xdata,
                        origin_stanza=self._original_stanza,
                        editable=mode == 'new'
                        )

                    self._additional_widgets.append(xform)
                    self._additional_box.pack_start(
                        xform.get_widget(),
                        False,
                        False,
                        0
                        )
                    w = xform.get_widget()
                    w.set_size_request(300, 400)

            self._additional_box.show()
        else:
            self._additional_box.hide()

        self.show()

        return

    def show(self):
        self._window.show_all()
        return

    def destroy(self):
        self._window.destroy()
        return

    def _on_destroy(self, window):
        for i in self._additional_widgets[:]:
            i.destroy()
            self._additional_widgets.remove(i)
        self._thread_widget.destroy()
        self._subject_widget.destroy()
        self._msg_edit_widget.destroy()
        return

    def _on_send_button_clicked(self, button):

        thread = None
        if self._thread_frame_cb.get_active() == True:
            t = self._thread_widget.get_data()
            if t != None:
                thread = wayround_org.xmpp.core.MessageThread(
                    t
                    )

        subject = None
        if self._subject_frame_cb.get_active() == True:
            subject = self._subject_widget.get_data()

        objects = []
        for i in self._additional_widgets:
            objects.append(i.gen_stanza_subobject())

        for i in objects:
            if type(i) == wayround_org.xmpp.xdata.XData:
                i.set_typ('submit')

        plain, xhtml = self._msg_edit_widget.get_data()

        stanza = wayround_org.xmpp.core.Stanza(tag='message')
        stanza.set_typ('normal')
        stanza.set_to_jid(self._to_entry.get_text())
        stanza.set_objects(objects)
        stanza.set_body_dict(plain)
        stanza.set_subject_dict(subject)
        stanza.set_thread(thread)

        self._controller.client.stanza_processor.send(stanza, wait=False)

        self.destroy()

        return

    def _on_reply_button_clicked(self, button):

        cp = copy.copy(self._msg_edit_widget.get_data()[0])
        for i in list(cp.keys()):
            cp[i] = '>{}\n'.format(cp[i].replace('\n', '\n>'))

        stanza = wayround_org.xmpp.core.Stanza(tag='message')
        stanza.set_to_jid(self._from_entry.get_text())
        stanza.set_from_jid(str(self._controller.jid))
        stanza.set_subject_dict(self._subject_widget.get_data())
        stanza.set_body_dict(cp)
        stanza.set_element(self._original_stanza.get_element())

        # TODO: add XHTML processing

        self._controller.show_single_message_window(
            mode='new',
            stanza=stanza
            )

        self.destroy()

        return
