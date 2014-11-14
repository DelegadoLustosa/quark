#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
import subprocess

class Button(Gtk.Button):
    def __init__(self):
        super(Button, self).__init__()
        self.set_image(Gtk.Image.new_from_icon_name("system-shutdown-symbolic", Gtk.IconSize.BUTTON))
        self.connect("clicked", self.clicked)

    def clicked(self, row):
        Window()

class ListBoxRow(Gtk.ListBoxRow):
    def __init__(self, text, data):
        super(ListBoxRow, self).__init__()
        self.data = data
        label = Gtk.Label(text)
        label.set_margin_left(10)
        label.set_margin_right(10)
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        label.set_halign(Gtk.Align.START)
        self.add(label)
        self.show_all()

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()
        self.set_size_request(350, -1)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.connect("focus-out-event", self.focus_out_event)
        self.connect("key-press-event", self.key_press_event)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_title(GLib.get_real_name())
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_decoration_layout(":close")
        self.set_titlebar(self.headerbar)

        listbox = Gtk.ListBox()
        listbox.add(ListBoxRow("Hibernate"  , "systemctl hibernate"))
        listbox.add(ListBoxRow("Restart"    , "systemctl reboot"))
        listbox.add(ListBoxRow("Shutdown"   , "systemctl poweroff"))
        listbox.add(ListBoxRow("Preferences", "gnome-control-center --overview"))
        listbox.connect("row-activated", self.row_activated)

        self.add(listbox)
        self.show_all()
        self.present()

    def row_activated(self, listbox, row):
        subprocess.Popen(row.data, shell = True)

    def focus_out_event(self, window, event):
        self.close()

    def key_press_event(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

if __name__ == "__main__":
    window = Window()
    window.connect("delete-event", Gtk.main_quit)
    Gtk.main()
