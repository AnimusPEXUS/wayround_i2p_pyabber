

from gi.repository import Gtk, Pango

import wayround_org.utils.gtk
import wayround_org.pyabber.l10n


class AddModeLang:

    def __init__(self, mode='message'):

        if not mode in ['message', 'subject']:
            raise ValueError("`mode' must be in ['message', 'subject']")

        self._mode = mode

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        ok_button = Gtk.Button("Ok")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self._on_cancel_button_clicked)

        mode_switch_combo = Gtk.ComboBox()
        self._mode_lang_switch_combo = mode_switch_combo
        renderer_text = Gtk.CellRendererText()
        mode_switch_combo.pack_start(renderer_text, True)
        mode_switch_combo.add_attribute(renderer_text, "text", 0)
        mode_switch_combo.set_model(wayround_org.pyabber.l10n.MODE_LIST)
        mode_switch_combo.set_active(0)

        bb.pack_start(ok_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        b2 = Gtk.Box()
        b2.set_orientation(Gtk.Orientation.HORIZONTAL)
        b2.set_spacing(5)

        self._entry = Gtk.Entry()

        b2.pack_start(Gtk.Label("Mode:"), False, False, 0)
        b2.pack_start(mode_switch_combo, False, False, 0)
        b2.pack_start(
            Gtk.Label("Language Code (en, ru, jp etc..):"),
            False, False, 0
            )
        b2.pack_start(self._entry, True, True, 0)

        b.pack_start(b2, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._window = window

        self._result = None, None

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self):

        self.show()

        self._iterated_loop.wait()

        return self._result

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_ok_button_clicked(self, button):
        lang = self._entry.get_text()
        if lang.isspace():
            lang = None
        self._result = self._combo_get_active(), lang
        self.destroy()
        return

    def _on_cancel_button_clicked(self, button):
        self.destroy()

    def _combo_get_active(self):
        ret = 'plain'

        res = self._mode_lang_switch_combo.get_active()
        if res != -1:
            ret = wayround_org.pyabber.l10n.MODE_LIST[res][0]

        return ret


class MessageEdit:

    def __init__(self, controller, mode='message'):

        if not mode in ['message', 'subject']:
            raise ValueError("`mode' must be in ['message', 'subject']")

        self._controller = controller

        self._mode = mode

        self._plain = {}
        self._xhtml = {}

        b = Gtk.Box()
        self._b = b
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)

        frame = Gtk.Frame()
        text_view_sw = Gtk.ScrolledWindow()
        frame.add(text_view_sw)

        font_desc = Pango.FontDescription.from_string("Clean 9")

        text_view = Gtk.TextView()
        self._text_view = text_view
        text_view.override_font(font_desc)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)

        text_view_sw.add(text_view)

        mode_language_tool_box = Gtk.Box()
        mode_language_tool_box = mode_language_tool_box
        mode_language_tool_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        mode_language_tool_box.set_spacing(5)

        add_button = Gtk.Button("Add")
        self._add_button = add_button
        add_button.connect('clicked', self._on_add_button_clicked)

        remove_button = Gtk.Button("Remove")
        self._remove_button = remove_button
        remove_button.connect('clicked', self._on_remove_button_clicked)

        mode_lang_switch_combo = Gtk.ComboBox()
        self._mode_lang_switch_combo = mode_lang_switch_combo

        mode_language_tool_box.pack_start(add_button, False, False, 0)
        mode_language_tool_box.pack_start(remove_button, False, False, 0)
        mode_language_tool_box.pack_start(
            mode_lang_switch_combo, False, False, 0
            )

        renderer_text = Gtk.CellRendererText()
        mode_lang_switch_combo.pack_start(renderer_text, True)
        mode_lang_switch_combo.add_attribute(renderer_text, "text", 0)

        self._modes_langs = Gtk.ListStore(str)

        mode_lang_switch_combo.set_model(self._modes_langs)
        mode_lang_switch_combo.connect(
            'changed',
            self._on_mode_lang_switch_combo_changed
            )

        b.pack_start(mode_language_tool_box, False, False, 0)
        b.pack_start(frame, True, True, 0)
        b.show_all()

#        self._update_mode_combobox()
        self.clear()
        self.set_mode_lang_switch_status('', 'plain')

        return

    def get_widget(self):
        return self._b

    def destroy(self):
        self.get_widget().destroy()

    def _update_mode_combobox(self):
        lang, mode = self.get_mode_lang_switch_status()

        modes = ['plain']
        if self._mode == 'message':
            modes.append('xhtml')

        while len(self._modes_langs) != 0:
            del self._modes_langs[0]

        for i in modes:

            lng_lst = self._plain
            if i == 'xhtml':
                lng_lst = self._xhtml

            lng_lst_names = list(lng_lst.keys())
            lng_lst_names.sort()

            for j in lng_lst_names:
                mod_lang = self._format_mode_lang_name(i, j)
                self._modes_langs.append([mod_lang])

        self._text_view.set_sensitive(len(self._modes_langs) != 0)
        self._mode_lang_switch_combo.set_sensitive(len(self._modes_langs) != 0)

        self.set_mode_lang_switch_status(lang, mode)

        return

    def get_mode_lang_switch_status(self):

        ret = '', 'plain'

        active = self._mode_lang_switch_combo.get_active()

        if active != -1:

            active_text = self._modes_langs[active][0]

            res = None

            if self._mode == 'message':
                res = wayround_org.pyabber.l10n.LANG_MODE_RE.match(active_text)
                if res != None:
                    lang = res.group('lang')
                    if lang == None:
                        lang = ''
                    ret = lang, res.group('mode')
            else:
                res = wayround_org.pyabber.l10n.LANG_RE.match(active_text)
                if res != None:
                    lang = res.group('lang')
                    if lang == None:
                        lang = ''
                    ret = lang, 'plain'

        return ret

    def find_mode_lang_index(self, lang, mode):
        mod_lang = self._format_mode_lang_name(mode, lang)
        ret = -1
        for i in range(len(self._modes_langs)):
            if self._modes_langs[i][0] == mod_lang:
                ret = i
                break

        return ret

    def set_mode_lang_switch_status(self, lang, mode):

        if lang == None:
            lang = ''

        if mode == None:
            mode = 'plain'

        if not isinstance(lang, str):
            raise TypeError("`lang' must be str")

        if not isinstance(mode, str):
            raise TypeError("`mode' must be str")

        if self._mode == 'message' and not isinstance(mode, str):
            raise TypeError("`mode' must be str")

        if self._mode == 'subject' and mode != 'plain':
            raise ValueError(
                "`mode' must be 'plain' if self._mode is 'status'"
                )

        active = self.find_mode_lang_index(lang, mode)

        if active == -1:
            active = self.find_mode_lang_index('', 'plain')

        self._mode_lang_switch_combo.set_active(active)

        return

    def _format_mode_lang_name(self, mode, lang):

        if lang == None:
            lang = ''

        if mode == None:
            mode = 'plain'

        ret = None
        if self._mode == 'message':
            minus = ''
            if lang != '':
                minus = '-'
            ret = '{}{}{}'.format(mode, minus, lang)
        else:
            ret = lang
        return ret

    def clear(self):
        self.set_data({'': ''}, {})

    def set_data(self, plain, xhtml):

        if plain != None and not isinstance(plain, dict):
            raise TypeError("`plain' must be None or dict")

        if xhtml != None and not isinstance(xhtml, dict):
            raise TypeError("`xhtml' must be None or dict")

        if plain != None:

            for i in list(self._plain.keys()):
                if not i in plain:
                    del self._plain[i]

            for i in list(plain.keys()):
                if not i in self._plain:
                    self._plain[i] = Gtk.TextBuffer()
                self._plain[i].set_text(plain[i])

        if xhtml != None:

            for i in list(self._xhtml.keys()):
                if not i in xhtml:
                    del self._xhtml[i]

            for i in list(xhtml.keys()):
                if not i in self._xhtml:
                    self._xhtml[i] = Gtk.TextBuffer()
                self._xhtml[i].set_text(xhtml[i])

        self._update_mode_combobox()

        return

    def get_data(self):

        plain = {}
        xhtml = {}

        for i in list(self._plain.keys()):
            b = self._plain[i]
            plain[i] = b.get_text(
                b.get_start_iter(),
                b.get_end_iter(),
                False
                )

        for i in list(self._xhtml.keys()):
            b = self._xhtml[i]
            xhtml[i] = b.get_text(
                b.get_start_iter(),
                b.get_end_iter(),
                False
                )

        return plain, xhtml

    def set_editable(self, val):
        self._text_view.set_editable(val)
        self._add_button.set_sensitive(val)
        self._remove_button.set_sensitive(val)

    def get_editable(self):
        return self._text_view.get_editable()

    def set_cursor_to_end(self):
        b = self._text_view.get_buffer()
        b.place_cursor(b.get_end_iter())

    def grab_focus(self):
        self._text_view.grab_focus()

    def connect(self, signal, cb, *args):
        return self._text_view.connect(signal, cb, *args)

    def add_mode_lang(self, mode, lang):

        if lang == None:
            lang = ''

        if mode == None:
            mode = 'plain'

        m = self._plain
        if mode == 'xhtml':
            m = self._xhtml

        if not lang in m:

            m[lang] = Gtk.TextBuffer()

            self._update_mode_combobox()

        self.set_mode_lang_switch_status(lang, mode)

        return

    def remove_mode_lang(self, mode, lang):

        m = self._plain
        if mode == 'xhtml':
            m = self._xhtml

        if lang in m:
            del m[lang]

        self._update_mode_combobox()

        return

    def _on_add_button_clicked(self, button):
        res = self._controller.show_add_mode_language_window()
        self.add_mode_lang(res[0], res[1])

    def _on_remove_button_clicked(self, button):
        lang, mode = self.get_mode_lang_switch_status()
        self.remove_mode_lang(mode, lang)

    def _on_mode_lang_switch_combo_changed(self, combo):
        lang, mode = self.get_mode_lang_switch_status()

        m = self._plain
        if mode == 'xhtml':
            m = self._xhtml

        if lang in m:
            self._text_view.set_buffer(m[lang])
        else:
            self._text_view.set_buffer(None)

        return
