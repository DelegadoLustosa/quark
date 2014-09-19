# author: Delegado Lustosa

from gi.repository import Gtk, GObject
import dbus

bus = dbus.SystemBus()

states = {
    0: "Unknown",
    10: "Unmanaged",
    20: "Unavailable",
    30: "Disconnected",
    40: "Prepare",
    50: "Config",
    60: "Need Auth",
    70: "IP Config",
    80: "IP Check",
    90: "Secondaries",
    100: "Activated",
    110: "Deactivating",
    120: "Failed"}

class Button(Gtk.Button):
    def __init__(self, handler):
        super(Button, self).__init__()
        self.network = NetworkManager()
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_image(Gtk.Image.new_from_icon_name("network-offline-symbolic", Gtk.IconSize.BUTTON))
        self.connect("event", self.event, handler)

        GObject.timeout_add(100, self.update)

    def update(self):
        device = self.network.get_current_device()
        if device.get_connected():
            icon = "network-transmit-receive-symbolic"
        else:
            icon = "network-offline-symbolic"
        self.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
        return True

    def event(self, button, event, handler):
        handler.emit("event-handler")

class NetworkManager():
    def __init__(self):
        super(NetworkManager, self).__init__()
        self.proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        self.manager = dbus.Interface(self.proxy, "org.freedesktop.NetworkManager")

    def get_current_device(self):
        return NetworkDevice(self.manager.GetDevices()[0])

class NetworkDevice():
    def __init__(self, device):
        super(NetworkDevice, self).__init__()
        self.device = device

    def get_props(self):
        dev_proxy = bus.get_object("org.freedesktop.NetworkManager", self.device)
        prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")
        return prop_iface.GetAll("org.freedesktop.NetworkManager.Device")

    def get_connected(self):
        props = self.get_props()
        if states[props["State"]] == "Activated":
            return True
        else:
            return False
