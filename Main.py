#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# An interface for Gnome Desktop
# author: Delegado Lustosa

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

from gi.repository import Gtk, Gdk, GObject

import time

import GnoMenu
import Network
import Sound

class EventHandler(GObject.GObject):
    __gsignals__ = {"event-handler": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),}

    def __init__(self):
        super(EventHandler, self).__init__()
        GObject.threads_init()

class GnomeButton(Gtk.Button):
    def __init__(self, handler):
        super(GnomeButton, self).__init__()
        self.set_image(Gtk.Image.new_from_icon_name("view-list-symbolic", Gtk.IconSize.BUTTON))
        self.connect("clicked", self.clicked)
        self.connect("event", self.event, handler)

    def clicked(self, button):
        GnoMenu.Window()

    def event(self, button, event, handler):
        handler.emit("event-handler")

class Dock(Gtk.Window):
    __gtype_name__ = "Dock"

    def __init__(self):
        super(Dock, self).__init__()
        self.size = 46
        self.border = 3
        self.speed = 10
        self.state = "Hide"
        self.focused = False
        self.count = 0
        self.thread = None
        self.thread_smooth = None

        self.screen = self.get_screen()
        self.screen.connect("size-changed", self.screen_size_changed)

        visual = self.screen.get_rgba_visual()
        if visual == None:
            visual = self.screen.get_system_visual()
        self.set_visual(visual)
        self.set_app_paintable(True)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("event", self.event)

        self.handler = EventHandler()
        self.handler.connect("event-handler", self.event_handler)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.pack_start(GnomeButton(self.handler))
        self.headerbar.pack_end(Sound.Button(self.handler))
        self.headerbar.pack_end(Network.Button(self.handler))
        self.add(self.headerbar)

        self.reposition()

        GObject.timeout_add(100, self.update_clock)

    def reposition(self):
        self.set_size_request(self.screen.get_width(), self.size)
        self.move(0, self.screen.get_height() - self.border)
        self.show_all()
        self.present()
        self.toggle_hidden()

    def toggle_hidden(self):
        self.reset_smooth()
        if self.state == "Hide" and self.focused == True:
            self.thread = GObject.timeout_add(self.speed, self.scroll_show)
        if self.state == "Show" and self.focused == False:
            self.thread_smooth = GObject.timeout_add(self.speed, self.count_smooth)

    def reset_smooth(self):
        if self.thread_smooth is not None:
            GObject.source_remove(self.thread_smooth)
            self.thread_smooth = None
        self.count = 0

    def count_smooth(self):
        self.count += 1
        if self.count >= (1 * 1000) / self.speed:
            self.reset_smooth()
            self.thread = GObject.timeout_add(self.speed, self.scroll_hide)
        return True

    def scroll_show(self):
        self.state = "Scroll"
        x, y = self.get_position()
        y -= (self.size - self.border) / 4
        if y <= self.screen.get_height() - self.size:
            GObject.source_remove(self.thread)
            self.thread = None
            y = self.screen.get_height() - self.size
            self.state = "Show"
        self.move(x, y)
        self.present()
        return True

    def scroll_hide(self):
        self.state = "Scroll"
        x, y = self.get_position()
        y += (self.size - self.border) / 4
        if y >= self.screen.get_height() - self.border:
            GObject.source_remove(self.thread)
            self.thread = None
            y = self.screen.get_height() - self.border
            self.state = "Hide"
        self.move(x, y)
        self.present()
        return True

    def update_clock(self):
        self.headerbar.set_title((time.strftime("%H:%M", time.localtime())))
        self.headerbar.set_subtitle((time.strftime("%a, %d - %b", time.localtime())))
        return True

    def screen_size_changed(self, screen):
        self.reposition()

    def event(self, window, event):
        if event.type == Gdk.EventType.ENTER_NOTIFY:
            self.focused = True
        if event.type == Gdk.EventType.LEAVE_NOTIFY:
            self.focused = False
        self.toggle_hidden()

    def event_handler(self, handler):
        self.reset_smooth()

if __name__ == "__main__":
    Dock()
    Gtk.main()
