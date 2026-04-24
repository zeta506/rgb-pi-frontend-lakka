"""Lakka-port: FBpyGIF-free framebuffer image writer.

Replaces `from FBpyGIF import fb` with a pure PIL + /dev/fb0 implementation.
Writes an image to /dev/fb0 at 32bpp (BGRX order, matching Pi5 RP1 DPI fb layout).

Usage identical to upstream:
    python3 framebuffer_write.py -img /path/to/splash.png [-halt]
"""

from argparse import ArgumentParser
from PIL import Image
import os
import struct
import fcntl

FBIOGET_VSCREENINFO = 0x4600

def fb_info(fb_path='/dev/fb0'):
    """Returns (xres, yres, bits_per_pixel)."""
    with open(fb_path, 'rb') as f:
        buf = bytearray(160)
        fcntl.ioctl(f.fileno(), FBIOGET_VSCREENINFO, buf, True)
        xres, yres, _xv, _yv, _xo, _yo, bpp = struct.unpack_from('7I', buf, 0)
    return xres, yres, bpp

def write_image(img_path, fb_path='/dev/fb0'):
    xres, yres, bpp = fb_info(fb_path)
    img = Image.open(img_path).convert('RGBA').resize((xres, yres), Image.NEAREST)
    r, g, b, a = img.split()
    # Pi5 RP1 DPI fb pixel order: BGRX (byte0=B byte1=G byte2=R byte3=pad)
    bgra = Image.merge('RGBA', (b, g, r, a))
    raw = bgra.tobytes()
    if bpp == 32:
        with open(fb_path, 'wb') as f:
            f.write(raw)
    elif bpp == 16:
        packed = bytearray(xres * yres * 2)
        src = img.tobytes()
        for i in range(xres * yres):
            r, g, b, _ = src[i*4], src[i*4+1], src[i*4+2], src[i*4+3]
            v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            struct.pack_into('<H', packed, i*2, v)
        with open(fb_path, 'wb') as f:
            f.write(bytes(packed))
    else:
        raise RuntimeError('Unsupported fb bpp=%d' % bpp)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-img', action='store', required=True, dest='image_name',
                        help='path to splash image')
    parser.add_argument('-halt', action='store_true', required=False, dest='halt_process',
                        help='loop forever until shutdown flag removed')
    args = parser.parse_args()

    write_image(args.image_name)

    if args.halt_process:
        shutdown_flag = '/storage/rgbpi/temp/do_manual_shutdown'
        if os.path.isfile(shutdown_flag):
            try:
                os.remove(shutdown_flag)
            except OSError:
                pass
            while True:
                pass
