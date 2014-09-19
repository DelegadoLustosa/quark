# author: Delegado Lustosa

from gi.repository import Gtk, GObject
import subprocess
import collections
import re

class Button(Gtk.Box):
    def __init__(self, handler):
        super(Button, self).__init__()
        self.sound = SoundManager()
        style = self.get_style_context()
        style.add_class(Gtk.STYLE_CLASS_LINKED)

        self.toggle = Gtk.ToggleButton()
        self.toggle.set_active(self.sound.get_mute())
        self.toggle.set_image(Gtk.Image.new_from_icon_name("audio-volume-muted-symbolic", Gtk.IconSize.BUTTON))
        self.toggle.connect("toggled", self.toggle_mute)
        self.toggle.connect("event", self.event, handler)
        self.add(self.toggle)

        button = Gtk.Button()
        button.set_image(Gtk.Image.new_from_icon_name("list-remove-symbolic", Gtk.IconSize.BUTTON))
        button.connect("clicked", self.minus)
        button.connect("event", self.event, handler)
        self.add(button)

        button = Gtk.Button()
        button.set_image(Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON))
        button.connect("clicked", self.plus)
        button.connect("event", self.event, handler)
        self.add(button)

        GObject.timeout_add(100, self.update)

    def update(self):
        volume = self.sound.get_volume()
        if volume == 0 or self.sound.get_mute():
            icon = "audio-volume-muted-symbolic"
        elif volume <= 33:
            icon = "audio-volume-low-symbolic"
        elif volume <= 66:
            icon = "audio-volume-medium-symbolic"
        else:
            icon = "audio-volume-high-symbolic"
        self.toggle.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
        return True

    def toggle_mute(self, button):
        self.sound.set_mute(button.get_active())

    def minus(self, button):
        volume = self.sound.get_volume()
        volume -= 10
        if volume <= 0:
            volume = 0
        volume = self.sound.set_volume(volume)

    def plus(self, button):
        volume = self.sound.get_volume()
        volume += 10
        if volume >= 100:
            volume = 100
        volume = self.sound.set_volume(volume)

    def event(self, button, event, handler):
        handler.emit("event-handler")

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
