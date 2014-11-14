#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GObject
import subprocess
import collections
import re

class Button(Gtk.Button):
    def __init__(self):
        super(Button, self).__init__()
        self.soundmanager = SoundManager()
        self.set_image(Gtk.Image.new_from_icon_name("audio-volume-muted-symbolic", Gtk.IconSize.BUTTON))
        self.connect("clicked", self.clicked)

        GObject.timeout_add(100, self.update)

    def update(self):
        volume = self.soundmanager.get_volume()
        if volume == 0 or self.soundmanager.get_mute():
            icon = "audio-volume-muted-symbolic"
        elif volume <= 33:
            icon = "audio-volume-low-symbolic"
        elif volume <= 66:
            icon = "audio-volume-medium-symbolic"
        else:
            icon = "audio-volume-high-symbolic"
        self.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
        return True

    def clicked(self, button):
        Window()

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()
        self.soundmanager = SoundManager()
        self.set_size_request(400, 200)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.connect("focus-out-event", self.focus_out_event)
        self.connect("key-press-event", self.key_press_event)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_decoration_layout(":close")
        self.set_titlebar(self.headerbar)

        button = Gtk.ToggleButton()
        button.set_active(self.soundmanager.get_mute())
        button.set_image(Gtk.Image.new_from_icon_name("audio-volume-muted-symbolic", Gtk.IconSize.BUTTON))
        button.connect("toggled", self.toggled)
        self.headerbar.pack_start(button)

        self.scale = Gtk.Scale()
        self.scale.set_adjustment(Gtk.Adjustment.new(self.soundmanager.get_volume(), 0, 100, 10, 10, 0))
        self.scale.set_digits(0)
        self.scale.grab_focus()
        self.scale.connect("value_changed", self.value_changed)
        self.add(self.scale)

        self.show_all()
        self.present()

    def toggled(self, button):
        self.soundmanager.set_mute(button.get_active())

    def value_changed(self, scale):
        self.soundmanager.set_volume(scale.get_value())

    def focus_out_event(self, window, event):
        self.close()

    def key_press_event(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

class SoundManager():
    def __init__(self):
        super(SoundManager, self).__init__()
        self.volume_re = re.compile(b'^set-sink-volume ([^ ]+) (.*)')
        self.mute_re = re.compile(b'^set-sink-mute ([^ ]+) ((?:yes)|(?:no))')
        self._mute = collections.OrderedDict()
        self._volume = collections.OrderedDict()

    def update(self):
        proc = subprocess.Popen(["pacmd", "dump"], stdout = subprocess.PIPE)
        for line in proc.stdout:
            volume_match = self.volume_re.match(line)
            mute_match = self.mute_re.match(line)
            if volume_match:
                self._volume[volume_match.group(1)] = int(volume_match.group(2), 16)
            elif mute_match:
                self._mute[mute_match.group(1)] = mute_match.group(2).lower() == b"yes"

    def set_mute(self, mute):
        self.update()
        sink = list(self._mute.keys())[0]
        subprocess.Popen(["pacmd", "set-sink-mute", sink, "yes" if mute else "no"], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        self._mute[sink] = mute

    def get_mute(self):
        self.update()
        sink = list(self._mute.keys())[0]
        return self._mute[sink]

    def set_volume(self, volume):
        self.update()
        sink = list(self._volume.keys())[0]
        subprocess.Popen(["pacmd", "set-sink-volume", sink, str(int(volume * 655.36))], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        self._volume[sink] = int(volume * 655.36)

    def get_volume(self):
        self.update()
        sink = list(self._volume.keys())[0]
        return int(self._volume[sink] / 655.36)

if __name__ == "__main__":
    window = Window()
    window.connect("delete-event", Gtk.main_quit)
    Gtk.main()
