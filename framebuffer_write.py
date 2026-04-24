from FBpyGIF import fb
from argparse import ArgumentParser
import os

parser = ArgumentParser()
parser.add_argument("-img", action="store", required=True, dest="image_name", help="name of splash image")
parser.add_argument("-halt", action="store_true", required=False, dest="halt_process", help="halt process")

args = parser.parse_args()

BIT_DEPTH = 32
FRAME_BUFFER = 0
fb.ready_fb(BIT_DEPTH, FRAME_BUFFER)
fb.show_img(fb.ready_img(args.image_name))

if args.halt_process:
    do_manual_shutdown = '/opt/rgbpi/ui/temp/do_manual_shutdown'
    if os.path.isfile(do_manual_shutdown):
        os.system('rm /opt/rgbpi/ui/temp/do_manual_shutdown > /dev/null 2>&1')
        while True:
            pass