"""Framebuffer presenter for Lakka's pygame dummy backend.

The aarch64 pygame wheel available on Lakka does not include SDL's kmsdrm or
fbcon video drivers. RGB-Pi can still render into a normal pygame Surface using
the dummy driver; this module mirrors that Surface to /dev/fb0.
"""

import fcntl
import os
import struct
import time

FBIOGET_VSCREENINFO = 0x4600
FBIOPUT_VSCREENINFO = 0x4601


def fb_info(fb_path='/dev/fb0'):
    with open(fb_path, 'rb') as fb:
        buf = bytearray(160)
        fcntl.ioctl(fb.fileno(), FBIOGET_VSCREENINFO, buf, True)
    xres, yres, _xv, _yv, _xo, _yo, bpp = struct.unpack_from('7I', buf, 0)
    return xres, yres, bpp


def fb_try_set_mode(width, height, fb_path='/dev/fb0'):
    with open(fb_path, 'r+b') as fb:
        buf = bytearray(160)
        fcntl.ioctl(fb.fileno(), FBIOGET_VSCREENINFO, buf, True)
        fields = list(struct.unpack_from('7I', buf, 0))
        fields[0] = width
        fields[1] = height
        fields[2] = width
        fields[3] = height
        fields[4] = 0
        fields[5] = 0
        struct.pack_into('7I', buf, 0, *fields)
        fcntl.ioctl(fb.fileno(), FBIOPUT_VSCREENINFO, buf, True)


class FbPresenter:
    def __init__(self, pygame, source, fb_path='/dev/fb0'):
        self.pygame = pygame
        self.source = source
        self.fb_path = fb_path
        target_x = int(os.environ.get('RGBPI_FB_WIDTH', '3840'))
        target_y = int(os.environ.get('RGBPI_FB_HEIGHT', '240'))
        try:
            fb_try_set_mode(target_x, target_y, fb_path)
        except OSError:
            pass
        fb_xres, fb_yres, self.bpp = fb_info(fb_path)
        # On Lakka/Pi5 super resolutions, fbdev can expose the logical
        # 320x240 surface even while DRM scans out 3840x240. Force the CRT
        # target size by default so the 320-wide RGB-Pi UI fills the screen.
        self.xres = target_x or fb_xres
        self.yres = target_y or fb_yres
        self.ui_width = int(os.environ.get('RGBPI_UI_WIDTH', '1280'))
        self.ui_height = int(os.environ.get('RGBPI_UI_HEIGHT', str(self.yres)))
        self.ui_x = int(os.environ.get('RGBPI_UI_X', str(max(0, (self.xres - self.ui_width) // 2))))
        self.ui_y = int(os.environ.get('RGBPI_UI_Y', '0'))
        self.min_interval = float(os.environ.get('RGBPI_FB_MAX_FPS', '30'))
        self.min_interval = 1.0 / self.min_interval if self.min_interval > 0 else 0
        self.last_present = 0.0
        if self.bpp not in (16, 32):
            raise RuntimeError('Unsupported framebuffer bpp=%d' % self.bpp)

    def present(self):
        now = time.monotonic()
        if self.min_interval and now - self.last_present < self.min_interval:
            return
        self.last_present = now
        frame = self.pygame.Surface((self.xres, self.yres))
        frame.fill((0, 0, 0))
        ui = self.pygame.transform.scale(self.source, (self.ui_width, self.ui_height))
        frame.blit(ui, (self.ui_x, self.ui_y))
        if self.bpp == 32:
            # Pi5 RP1 DPI framebuffer is BGRX byte order.
            raw = self.pygame.image.tostring(frame, 'BGRA')
        else:
            raw32 = self.pygame.image.tostring(frame, 'RGBX')
            packed = bytearray(self.xres * self.yres * 2)
            for i in range(self.xres * self.yres):
                r = raw32[i * 4]
                g = raw32[i * 4 + 1]
                b = raw32[i * 4 + 2]
                v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                struct.pack_into('<H', packed, i * 2, v)
            raw = bytes(packed)
        with open(self.fb_path, 'wb', buffering=0) as fb:
            fb.write(raw)


def install(pygame, source, fb_path='/dev/fb0'):
    if not os.path.exists(fb_path):
        return None
    presenter = FbPresenter(pygame, source, fb_path)
    return presenter
