"""Lakka-port: soft-fail optional native dependencies.

Upstream hard-imports several Pi-specific native libs (smbus, RPi.GPIO, dbus,
alsaaudio, paramiko, evdev, pyudev, psutil, requests) at module top.  On a
stock Lakka install many are absent and Python aborts before `rtk` can run.

This module injects dummy stubs for anything missing so the frontend at least
*loads*. Features that actually need the real lib either no-op silently or
raise a caught exception at call-site (upstream code already wraps them).
"""

import sys
import types


class _EmptyContext:
    def list_devices(self, *args, **kwargs):
        return []


class _EmptyDevices:
    @staticmethod
    def from_name(*args, **kwargs):
        return {}


class _Mem:
    percent = 0
    total = 1
    used = 0
    free = 1


class _CpuFreq:
    max = 0
    min = 0
    current = 0


class _Temp:
    current = 0


class _Partition:
    mountpoint = '/'

def _stub(name, attrs=None):
    if name in sys.modules:
        return sys.modules[name]
    m = types.ModuleType(name)
    for a in (attrs or []):
        setattr(m, a, lambda *a, **k: None)
    sys.modules[name] = m
    return m

def _stub_dbus():
    dbus = _stub('dbus', ['SystemBus', 'Interface'])
    mainloop = _stub('dbus.mainloop')
    glib = _stub('dbus.mainloop.glib', ['DBusGMainLoop'])
    dbus.mainloop = mainloop
    mainloop.glib = glib

def _stub_pyudev():
    pyudev = _stub('pyudev')
    pyudev.Context = _EmptyContext
    pyudev.Monitor = lambda *args, **kwargs: None
    pyudev.Devices = _EmptyDevices

def _stub_psutil():
    psutil = _stub('psutil')
    psutil.cpu_percent = lambda *args, **kwargs: 0
    psutil.cpu_freq = lambda *args, **kwargs: _CpuFreq()
    psutil.virtual_memory = lambda *args, **kwargs: _Mem()
    psutil.disk_usage = lambda *args, **kwargs: _Mem()
    psutil.disk_partitions = lambda *args, **kwargs: [_Partition()]
    psutil.sensors_temperatures = lambda *args, **kwargs: {'cpu_thermal': [_Temp()]}
    psutil.net_if_addrs = lambda *args, **kwargs: {}
    psutil.net_if_stats = lambda *args, **kwargs: {}

def install_stubs():
    # Try real imports; stub only what fails
    mapping = [
        ('smbus',      ['SMBus']),
        ('RPi',        []),
        ('RPi.GPIO',   ['setwarnings', 'setmode', 'setup', 'input', 'output', 'BCM', 'IN', 'OUT', 'PUD_DOWN', 'PUD_UP']),
        ('alsaaudio',  ['Mixer', 'cards', 'mixers']),
        ('dbus',       []),
        ('evdev',      ['InputDevice', 'list_devices', 'categorize', 'ecodes']),
        ('paramiko',   ['SSHClient', 'AutoAddPolicy']),
        ('psutil',     ['cpu_percent', 'virtual_memory', 'disk_usage', 'sensors_temperatures']),
        ('pyudev',     ['Context', 'Monitor']),
        ('requests',   ['get', 'post']),
    ]
    for name, attrs in mapping:
        try:
            __import__(name)
        except Exception:
            if name == 'dbus':
                _stub_dbus()
            elif name == 'pyudev':
                _stub_pyudev()
            elif name == 'psutil':
                _stub_psutil()
            else:
                _stub(name, attrs)
    try:
        __import__('dbus.mainloop.glib')
    except Exception:
        _stub_dbus()
    try:
        __import__('pyudev')
    except Exception:
        _stub_pyudev()
    try:
        import psutil
        if not hasattr(psutil, 'net_if_addrs'):
            _stub_psutil()
    except Exception:
        _stub_psutil()

# Auto-install on import so simple `import lakka_optional_deps` early in
# rgbpiui.py covers downstream imports.
install_stubs()
