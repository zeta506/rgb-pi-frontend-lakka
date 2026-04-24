import time
import utils
import rtk
import dbus
import dbus.mainloop.glib
import threading

class Bluetooth_Manager:
    # https://github.com/emlid/bluetool
    def __init__(self):
        try:
            self.bluetooth = Bluetooth()
            self.bt_active = True
        except:
            self.bt_active = False
        self.reset_devices()

    def reset_devices(self):
        self.bt_device_names = ['-','-','-','-','-','-','-','-']
        self.bt_mac_addrs = ['','','','','','','','']

    def convert(self, data):
        if isinstance(data, bytes):  return data.decode('utf-8')
        if isinstance(data, dict):   return dict(map(self.convert, data.items()))
        if isinstance(data, tuple):  return map(self.convert, data)
        return data

    def get_available_devices(self):
        if self.bt_active:
            self.reset_devices()
            valid_dev_types = [1288,1344,9480,1412,9476,9484,9536,9600,9620,66816,525568]
            valid_dev_names = ['SteamController',
                            'PLAYSTATION(R)3 Controller',
                            'PLAYSTATION(R)3Conteroller',
                            'PLAYSTATION(R)3Conteroller-PANHAI',
                            'PS(R) Gamepad',
                            'PS3 GamePad',
                            'Sony Interactive Entertainment Wireless Controller',
                            'Sony PLAYSTATION(R)3 Controller',
                            'Sony Computer Entertainment Wireless Controller',
                            'Microsoft X-Box 360 pad',
                            'Xbox 360 Wireless Receiver']
            block_list = ["[\x1b[0;", "removed", "unknown"]
            try:
                self.bluetooth.scan()
                nearby_devices = self.bluetooth.get_devices_to_pair()
                i=0
                for device in nearby_devices:
                    dev = self.convert(data=device)
                    dev_name = dev['name']
                    dev_mac = dev['mac_address']
                    string_valid = not any(keyword in dev_name for keyword in block_list)
                    # BT Info Class: 0x002508 -> input-gaming (9480 DEC)
                    if dev_name in valid_dev_names:
                        dev_type = 9480
                        try: self.bluetooth.set_device_property(dev_mac, 'Class', dev_type)
                        except: pass
                    else:
                        try: dev_type = self.bluetooth.get_device_property(dev_mac, 'Class')
                        except: dev_type = 'null'
                    # Fix Retrobit
                    if dev_name == '<unknown>' and dev_type == 9480:
                        dev_name == 'Unknown Controller'
                        string_valid = True
                    rtk.logging.info('Checking BT device: %s %s %s', dev_name, dev_type, dev_mac)
                    if string_valid and dev_type in valid_dev_types:
                        if not utils.is_tate() and len(dev_name) > 29:
                            dev_name = dev_name[:15] + '~' + dev_name[-14:]
                        elif utils.is_tate() and len(dev_name) > 17:
                            dev_name = dev_name[:7] + '~' + dev_name[-10:]
                        self.bt_device_names[i] = dev_name
                        self.bt_mac_addrs[i] = dev_mac
                        i += 1
                        rtk.logging.info('Found valid BT joy: %s %s %s', dev_name, dev_type, dev_mac)
                return self.bt_device_names
            except:
                pass

    def quick_connect(self, device_number):
        mac_address = self.bt_mac_addrs[int(device_number)]
        rtk.logging.info('mac_address %s', mac_address)
        is_paired = False
        is_connected = False
        is_trusted = False
        try:
            tries = 3
            while not is_paired and tries > 0:
                is_paired = self.bluetooth.pair(mac_address)
                tries -=1
                time.sleep(1)
            if is_paired:
                tries = 3
                while not is_trusted and tries > 0:
                    is_trusted = self.bluetooth.trust(mac_address)
                    tries -=1
                    time.sleep(1)
                tries = 3
                while not is_connected and tries > 0:
                    is_connected = self.bluetooth.connect(mac_address)
                    tries -=1
                    time.sleep(1)
            else:
                rtk.logging.info('Unable to pair device %s',mac_address)
        except self.bluetooth.btcommon.BluetoothError as err:
            rtk.logging.error('Error in BT quick_connect: %s', err)

    def remove_pairings(self):
        paired_devices = self.bluetooth.get_available_devices()
        for device in paired_devices:
            dev = self.convert(data=device)
            self.bluetooth.remove(dev['mac_address'])

class Bluetooth(object):

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SystemBus()

    def scan(self, timeout=10):
        try:
            adapter = find_adapter()
            adapter.StartDiscovery()
            time.sleep(timeout)
            adapter.StopDiscovery()
        except Exception as error:
            rtk.logging.error('BT scan error: %s', error)

    def get_devices_to_pair(self):
        devices = self.get_available_devices()
        for key in self.get_paired_devices():
            devices.remove(key)
        return devices

    def get_available_devices(self):
        available_devices = self._get_devices("Available")
        rtk.logging.info("Available devices: {}".format(available_devices))
        return available_devices

    def get_paired_devices(self):
        paired_devices = self._get_devices("Paired")
        rtk.logging.info("Paired devices: {}".format(paired_devices))
        return paired_devices

    def get_connected_devices(self):
        connected_devices = self._get_devices("Connected")
        rtk.logging.info("Connected devices: {}".format(connected_devices))
        return connected_devices

    def _get_devices(self, condition):
        devices = []
        conditions = ("Available", "Paired", "Connected")

        if condition not in conditions:
            rtk.logging.error("_get_devices: unknown condition - {}\n".format(
                condition))
            return devices

        try:
            man = dbus.Interface(
                self._bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager")
            objects = man.GetManagedObjects()

            for path, interfaces in objects.items():
                if "org.bluez.Device1" in interfaces:
                    dev = interfaces["org.bluez.Device1"]

                    if condition == "Available":
                        if "Address" not in dev:
                            continue

                        if "Name" not in dev:
                            dev["Name"] = "<unknown>"

                        device = {
                            "mac_address": dev["Address"].encode("utf-8"),
                            "name": dev["Name"].encode("utf-8")
                        }

                        devices.append(device)
                    else:
                        props = dbus.Interface(
                            self._bus.get_object("org.bluez", path),
                            "org.freedesktop.DBus.Properties")

                        if props.Get("org.bluez.Device1", condition):
                            if "Address" not in dev:
                                continue

                            if "Name" not in dev:
                                dev["Name"] = "<unknown>"

                            device = {
                                "mac_address": dev["Address"].encode("utf-8"),
                                "name": dev["Name"].encode("utf-8")
                            }

                            devices.append(device)
        except dbus.exceptions.DBusException as error:
            rtk.logging.error(str(error) + "\n")

        return devices

    def start_pairing(self, address, callback=None, args=()):
        pair_thread = threading.Thread(
            target=self._pair_trust_and_notify,
            args=(address, callback, args))
        pair_thread.daemon = True
        pair_thread.start()

    def _pair_trust_and_notify(self, address, callback=None, args=()):
        result = self.pair(address)

        if callback is not None:
            if result:
                result = self.trust(address)
            callback(result, *args)

    def pair(self, address):
        try:
            device = find_device(address)
            rtk.logging.info('Pairing...')
            device.Pair()
            rtk.logging.info("Successfully paired to {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT pair error: %s', error)
            return False

    def connect(self, address):
        try:
            device = find_device(address)
            rtk.logging.info('Connecting...')
            device.Connect()
            rtk.logging.info("Successfully connected to {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT connect error: %s', error)
            return False

    def disconnect(self, address):
        try:
            device = find_device(address)
            rtk.logging.info('Disconnecting...')
            device.Disconnect()
            rtk.logging.info("Successfully disconnected from {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT disconnect error: %s', error)
            return False

    def trust(self, address):
        try:
            device = find_device(address)
            props = dbus.Interface(
                self._bus.get_object("org.bluez", device.object_path),
                "org.freedesktop.DBus.Properties")
            rtk.logging.info('Trusting...')
            props.Set("org.bluez.Device1", "Trusted", dbus.Boolean(1))
            rtk.logging.info("Successfully trusted to {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT trust error: %s', error)
            return False

    def remove(self, address):
        try:
            adapter = find_adapter()
            dev = find_device(address)
            adapter.RemoveDevice(dev.object_path)
            rtk.logging.info("Successfully removed: {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT remove error: %s', error)
            return False

    def set_device_property(self, address, prop, value):
        try:
            device = find_device(address)
            props = dbus.Interface(
                self._bus.get_object("org.bluez", device.object_path),
                "org.freedesktop.DBus.Properties")
            if props.Get("org.bluez.Device1", prop) != value:
                props.Set("org.bluez.Device1", prop, value)
            rtk.logging.info("Successfully set device property: {}".format(address))
            return True
        except Exception as error:
            rtk.logging.error('BT set device property error: %s', error)
            return False

    def get_device_property(self, address, prop):
        try:
            device = find_device(address)
            props = dbus.Interface(
                self._bus.get_object("org.bluez", device.object_path),
                "org.freedesktop.DBus.Properties")
            rtk.logging.info("Successfully get device property: {}".format(address))
            return props.Get("org.bluez.Device1", prop)
        except Exception as error:
            rtk.logging.error('BT get device property error: %s', error)
            return False

# Utility Functions

def get_managed_objects():
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object("org.bluez", "/"),
        "org.freedesktop.DBus.ObjectManager")
    return manager.GetManagedObjects()

def find_adapter(pattern=None):
    return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_in_objects(objects, pattern=None):
    bus = dbus.SystemBus()

    for path, ifaces in objects.items():
        adapter = ifaces.get("org.bluez.Adapter1")

        if adapter is None:
            continue

        if not pattern or pattern == adapter["Address"] or path.endswith(
                pattern):
            obj = bus.get_object("org.bluez", path)
            return dbus.Interface(obj, "org.bluez.Adapter1")

    rtk.logging.error('Bluetooth adapter not found')

def find_device(device_address, adapter_pattern=None):
    return find_device_in_objects(
        get_managed_objects(), device_address, adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
    bus = dbus.SystemBus()
    path_prefix = ""

    if adapter_pattern:
        adapter = find_adapter_in_objects(objects, adapter_pattern)
        path_prefix = adapter.object_path

    for path, ifaces in objects.items():
        device = ifaces.get("org.bluez.Device1")

        if device is None:
            continue

        if (device["Address"] == device_address and path.startswith(
                path_prefix)):
            obj = bus.get_object("org.bluez", path)
            return dbus.Interface(obj, "org.bluez.Device1")

    rtk.logging.error('Bluetooth adapter not found')