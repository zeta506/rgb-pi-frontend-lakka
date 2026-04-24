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

def _stub(name, attrs=None):
    if name in sys.modules:
        return
    m = types.ModuleType(name)
    for a in (attrs or []):
        setattr(m, a, lambda *a, **k: None)
    sys.modules[name] = m

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
            _stub(name, attrs)

# Auto-install on import so simple `import lakka_optional_deps` early in
# rgbpiui.py covers downstream imports.
install_stubs()
