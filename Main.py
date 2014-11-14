#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# An interface for Gnome Desktop
# author: Anderson Rodrigo de Almeida

# Quark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# Quark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk, GObject, GdkPixbuf, Gio, GdkX11
import Xlib.display

import time

import GnoMenu
import Network
import Sound
import Session

class Window(Gtk.Window):
    __gtype_name__ = "Quark"

    def __init__(self):
        super(Window, self).__init__()
        self.screen = self.get_screen()
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0, 0, 0, 1))

        self.overlay = Gtk.Overlay()
        self.image = Gtk.Image()
        self.overlay.add(self.image)
        self.add(self.overlay)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_valign(Gtk.Align.END)
        self.headerbar.set_halign(Gtk.Align.FILL)
        style = self.headerbar.get_style_context()
        style.add_class("frame")
        style.add_class("action-bar")

        self.headerbar.pack_start(GnoMenu.Button())
        self.headerbar.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL))
        self.headerbar.pack_end(Session.Button())
        self.headerbar.pack_end(Gtk.Separator.new(Gtk.Orientation.VERTICAL))
        self.headerbar.pack_end(Sound.Button())
        self.headerbar.pack_end(Network.Button())
        self.overlay.add_overlay(self.headerbar)

        self.move(0, 0)
        self.resize_to_geometry(self.screen.get_width(), self.screen.get_height())
        self.show_all()

        try:
            self.update_strut()
        except:
            pass

        try:
            self.update_background()
        except:
            pass

        GObject.timeout_add(100, self.update_clock)

    def update_strut(self):
        display = Xlib.display.Display()
        window = display.create_resource_object("window", self.get_window().get_xid())
        window.change_property(
            display.intern_atom("_NET_WM_STRUT"),
            display.intern_atom("CARDINAL"),
            32, [0, 0, 0, self.headerbar.get_allocated_height()])
        display.sync()

    def update_background(self):
        settings = Gio.Settings.new("org.gnome.desktop.background")
        picture = settings.get_string("picture-uri")
        picture = picture.replace("file://", "")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(picture)
        pixbuf = pixbuf.scale_simple(
            self.image.get_allocated_width(),
            self.image.get_allocated_height(),
            GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(pixbuf)

    def update_clock(self):
        self.headerbar.set_title((time.strftime("%H:%M", time.localtime())))
        self.headerbar.set_subtitle((time.strftime("%a, %d - %b", time.localtime())))
        return True

if __name__ == "__main__":
    Window()
    Gtk.main()
