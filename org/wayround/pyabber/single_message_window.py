
import uuid

from gi.repository import Gtk

import org.wayround.pyabber.message_edit_widget
import org.wayround.utils.gtk


class SingleMessageWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            org.wayround.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be org.wayround.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._window = Gtk.Window()

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_spacing(5)
        main_box.set_margin_top(5)
        main_box.set_margin_bottom(5)
        main_box.set_margin_left(5)
        main_box.set_margin_right(5)

        from_frame = Gtk.Frame()
        from_frame.set_no_show_all(True)
        from_frame.set_label("From Jabber ID")
        self.from_frame = from_frame

        from_entry = Gtk.Entry()
        self.from_entry = from_entry
        from_entry.set_margin_top(5)
        from_entry.set_margin_bottom(5)
        from_entry.set_margin_left(5)
        from_entry.set_margin_right(5)

        from_frame.add(from_entry)

        to_frame = Gtk.Frame()
        to_frame.set_no_show_all(True)
        to_frame.set_label("To Jabber ID")
        self.to_frame = to_frame

        to_entry = Gtk.Entry()
        self.to_entry = to_entry
        to_entry.set_margin_top(5)
        to_entry.set_margin_bottom(5)
        to_entry.set_margin_left(5)
        to_entry.set_margin_right(5)

        to_frame.add(to_entry)

        subject_frame = Gtk.Frame()
        self.subject_frame = subject_frame
        subject_frame_cb = Gtk.CheckButton()
        self.subject_frame_cb = subject_frame_cb

        subject_frame_cb.set_label("Include Subject")
        subject_frame_cb.set_active(True)

        subject_frame.set_label_widget(subject_frame_cb)

        subject_entry = Gtk.Entry()
        self.subject_entry = subject_entry
        subject_entry.set_margin_top(5)
        subject_entry.set_margin_bottom(5)
        subject_entry.set_margin_left(5)
        subject_entry.set_margin_right(5)

        subject_frame.add(subject_entry)

        thread_frame = Gtk.Frame()
        self.thread_frame = thread_frame
        thread_frame_cb = Gtk.CheckButton()
        self.thread_frame_cb = thread_frame_cb

        thread_frame_cb.set_label("Include Unique Thread Identifier")
        thread_frame_cb.set_active(True)

        thread_frame.set_label_widget(thread_frame_cb)

        thread_box = Gtk.Box()
        thread_box.set_margin_top(5)
        thread_box.set_margin_bottom(5)
        thread_box.set_margin_left(5)
        thread_box.set_margin_right(5)
        thread_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        thread_box.set_spacing(5)

        thread_generate_button = Gtk.Button("Generate New UUID")
        thread_generate_button.set_no_show_all(True)
        thread_generate_button.connect(
            'clicked',
            self._on_thread_generate_button_clicked
            )
        self.thread_generate_button = thread_generate_button

        thread_edit_button = Gtk.Button("Edit Thread")
        thread_edit_button.set_no_show_all(True)
        self.thread_edit_button = thread_edit_button
        thread_edit_button.connect(
            'clicked',
            self._on_thread_edit_button_clicked
            )

        thread_entry = Gtk.Entry()
        self.thread_entry = thread_entry
        thread_entry.set_tooltip_text(
            "You not really need to edit it manually!"
            )
        thread_entry.set_editable(False)

        thread_box.pack_start(thread_entry, True, True, 0)
        thread_box.pack_start(thread_edit_button, False, False, 0)
        thread_box.pack_start(thread_generate_button, False, False, 0)

        thread_frame.add(thread_box)

        msg_edit_widget = \
            org.wayround.pyabber.message_edit_widget.MessageEdit(
                self._controller
                )
        self.msg_edit_widget = msg_edit_widget

        body_message_editor = msg_edit_widget.get_widget()
        self.body_message_editor = body_message_editor
        body_message_editor.set_margin_top(5)
        body_message_editor.set_margin_bottom(5)
        body_message_editor.set_margin_left(5)
        body_message_editor.set_margin_right(5)

        buttons_bb = Gtk.ButtonBox()
        buttons_bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        reply_button = Gtk.Button("Reply")
        reply_button.set_no_show_all(True)
        reply_button.connect('clicked', self._on_reply_button_clicked)

        send_button = Gtk.Button("Send")
        send_button.connect('clicked', self._on_send_button_clicked)
        send_button.set_no_show_all(True)

        self.reply_button = reply_button
        self.send_button = send_button

        buttons_bb.pack_start(reply_button, False, False, 0)
        buttons_bb.pack_start(send_button, False, False, 0)

        main_box.pack_start(from_frame, False, False, 0)
        main_box.pack_start(to_frame, False, False, 0)
        main_box.pack_start(subject_frame, False, False, 0)
        main_box.pack_start(thread_frame, False, False, 0)
        main_box.pack_start(body_message_editor, True, True, 0)
        main_box.pack_start(buttons_bb, False, False, 0)

        self._window.add(main_box)
        self._window.connect('destroy', self._on_destroy)
        self._window.show_all()

    def run(
        self,
        mode='new',
        to_jid=None, from_jid=None, subject=None, thread=None, body=None
        ):

        if not mode in ['new', 'view']:
            raise ValueError("Wrong mode")

        if mode == 'new' and thread == None:
            self.generate_new_thread_entry()

        self.reply_button.set_visible(mode == 'view')
        self.send_button.set_visible(mode == 'new')
        self.from_frame.set_visible(mode == 'view')
        self.to_frame.set_visible(mode == 'new')

        self.thread_generate_button.set_visible(mode == 'new')
        self.thread_edit_button.set_visible(mode == 'new')

        if mode == 'view':
            self.subject_frame.set_label("Subject")
            self.thread_frame.set_label("Unique Thread Identifier")

        self.subject_entry.set_editable(mode == 'new')
        self.from_entry.set_editable(mode == 'new')
        self.to_entry.set_editable(mode == 'new')

        self.msg_edit_widget.set_editable(mode == 'new')

        if to_jid != None:
            self.to_entry.set_text(str(to_jid))

        if from_jid != None:
            self.from_entry.set_text(str(from_jid))

        if subject != None:
            self.subject_entry.set_text(str(subject))

        if thread != None:
            self.thread_entry.set_text(repr(thread)[1:-1])

        if body != None:
            self.msg_edit_widget.set_data({'': body}, None)

        if mode == 'new':
            self.msg_edit_widget.set_cursor_to_end()
            self.msg_edit_widget.grab_focus()

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_thread_generate_button_clicked(self, button):
        self.generate_new_thread_entry()

    def _on_send_button_clicked(self, button):

        thread = None
        if self.thread_frame_cb.get_active() == True:
            thread = self.thread_entry.get_text()

        subject = None
        if self.subject_frame_cb.get_active() == True:
            subject = self.subject_entry.get_text()

        plain, xhtml = self.msg_edit_widget.get_data()

        self._controller.message_client.message(
            to_jid=self.to_entry.get_text(),
            from_jid=False,
            typ='normal',
            thread=thread,
            subject=subject,
            body=plain,
            xhtml=xhtml,
            wait=False
            )

        self._window.destroy()

    def _on_reply_button_clicked(self, button):
        initial_text = self.msg_edit_widget.get_data()[0]['']

        body = ''
        if len(initial_text) != 0 and not initial_text.isspace():
            body = ">{}\n\n".format(initial_text)

        self._controller.show_single_message_window(
            mode='new',
            to_jid=self.from_entry.get_text(),
            subject="Re: {}".format(self.subject_entry.get_text()),
            thread=self.thread_entry.get_text(),
            body=body
            )

    def _on_thread_edit_button_clicked(self, button):
        self.thread_entry.set_editable(not self.thread_entry.get_editable())

    def generate_new_thread_entry(self):

        self.thread_entry.set_text(uuid.uuid4().hex)
