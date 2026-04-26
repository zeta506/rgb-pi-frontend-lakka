import os
import sys
import pygame
import binascii
import subprocess
import rtk
import cglobals
import csv
import time
import glob
import socket
import requests
import smbus
import RPi.GPIO as GPIO
import configparser
import random
import gc
import zipfile
import shutil
import psutil
import datetime
import paramiko
import re
import platform
import json
from PIL import Image
from collections import namedtuple
from games_view import Games_View
from lgun_view import Lgun_View
from favs_view import Favs_View

''' Sections '''

# System
# Disk
# Network
# Hardware
# Data
# Sound
# Input
# Retroarch
# Webservices

''' System '''

def fix_permissions(fix_all=False):
    '''
    # a+rwX,+t
    https://www.thegeekstuff.com/2013/02/sticky-bit/
    If the sticky bit is set on a directory, files inside the directory may be renamed or removed only by the owner of the file,
    the owner of the directory, or the superuser (even if the modes of the directory would otherwise allow such an operation)
    '''
    themes_path         = rtk.path_rgbpi + '/themes'
    cfg_file            = rtk.path_rgbpi + '/config.ini'
    auto_play_file      = rtk.path_rgbpi_data + '/autoplay.dat'
    games_file          = cglobals.mount_point + '/dats/games.dat'
    fav_file            = cglobals.mount_point + '/dats/favorites.dat'
    fav_tate_file       = cglobals.mount_point + '/dats/favorites_tate.dat'
    cmd('chmod a+rwX ' + cfg_file)
    cmd('chmod a+rwX ' + auto_play_file)
    cmd('chmod a+rwX ' + games_file)
    cmd('chmod a+rwX ' + fav_file)
    cmd('chmod a+rwX ' + fav_tate_file)
    cmd('chmod -R a+rwX ' + rtk.path_autoconfig)
    if fix_all:
        cmd('chmod -R a+rwX ' + cglobals.mount_point)
        cmd('chmod -R a+rwX ' + themes_path)
        # Make default theme RO to avoid users deleting system files
        default_theme = themes_path + '/' + rtk.cfg_default_theme
        cmd('chmod a-w "' + default_theme + '"')

def gen_screenshot(game_id, system, game_path):
    '''def convert(file_path,new_path_png,new_path_bmp):
        shutil.move(file_path, new_path_png)
        img = Image.open(new_path_png)
        img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        img.save(new_path_bmp)
        os.remove(new_path_png)'''
    def crop_sms(img_file):
        image = Image.open(img_file)
        width, height = image.size
        top = (height - 192)/2
        bottom = (height + 192)/2
        if width == 256: # native
            x = 8
        else: # superx
            x = 80
        cropped = image.crop((x, top, width, bottom))
        cropped.save(img_file)
        return cropped
    def crop_zx(img_file):
        image = Image.open(img_file) # 320x240 / 2624x240
        width, height = image.size
        if width > 320: # SuperX
            image = image.resize((320,240),resample=Image.NEAREST)
            width, height = image.size
        left = (width - 256)/2
        top = (height - 192)/2
        right = (width + 256)/2
        bottom = (height + 192)/2
        cropped = image.crop((left, top, right, bottom))
        cropped.save(img_file)
        return cropped
    def rotate(image_path):
        image = Image.open(image_path)
        image = image.rotate(90,expand = 1)
        image.save(image_path)
    def resize(system, original_img, new_img):
        if system in ('sg1000','mastersystem'):
            image = crop_sms(original_img)
        elif system == 'zxspectrum':
            image = crop_zx(original_img)
        else:
            image = Image.open(original_img)
        if is_tate():
            resized = image.resize((192,256),resample=Image.LANCZOS)
        else:
            resized = image.resize((256,192),resample=Image.LANCZOS)
        resized.save(new_img)
    def send(original_img):
        hostname = rtk.cfg_scr_hostname
        port = 1022
        username = rtk.cfg_scr_username
        password = rtk.cfg_scr_password
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
            ssh_client.connect(hostname=hostname,port=port,username=username,password=password)
            rtk.logging.info('SSH Connected')
            ftp_client=ssh_client.open_sftp()
            rtk.logging.info('SFTP Connected')
            if is_tate():
                ftp_client.put(original_img,'/images/original/tate/' + original_img.split('/')[-1])
            else:
                ftp_client.put(original_img,'/images/original/yoko/' + original_img.split('/')[-1])
            ftp_client.close()
        except Exception as error:
            rtk.logging.error('Error sending images: %s', error)
    if 'fbneo' in game_path:
        system = system + "/fbneo"
    elif 'mame' in game_path:
        system = system + "/mame"
    elif 'naomi' in game_path:
        system = system + "/naomi"
    ori_path = os.path.join(cglobals.mount_point + '/screenshots', system)
    cpy_path = os.path.join(cglobals.mount_point + '/screenshots', 'scraper')
    end_path = os.path.join(rtk.path_rgbpi_scraper, 'images')
    try: os.mkdir(cpy_path)
    except: pass
    for i, entry in enumerate(sorted(os.scandir(ori_path), key=lambda e: e.name)):
        if entry.is_file():
            ori_file = os.path.join(ori_path, entry.name)
            if i == 0:
                cpy_file = os.path.join(cpy_path, game_id + '_title_' + rtk.cfg_scrap_region + '.png')
                end_file = os.path.join(end_path, game_id + '_title_' + rtk.cfg_scrap_region + '.png')
                shutil.move(ori_file, cpy_file)
                if is_tate():
                    rotate(cpy_file)
                resize(system, cpy_file, end_file)
                if rtk.cfg_scr_hostname != 'notset':
                    send(cpy_file)
            elif i == 1:
                cpy_file = os.path.join(cpy_path, game_id + '_ingame_' + rtk.cfg_scrap_region + '.png')
                end_file = os.path.join(end_path, game_id + '_ingame_' + rtk.cfg_scrap_region + '.png')
                shutil.move(ori_file, cpy_file)
                if is_tate():
                    rotate(cpy_file)
                resize(system, cpy_file, end_file)
                if rtk.cfg_scr_hostname != 'notset':
                    send(cpy_file)
            else:
                os.remove(ori_file)

def clean_screenshot(system):
    img_path = os.path.join(cglobals.mount_point + '/screenshots', system)
    for i, entry in enumerate(sorted(os.scandir(img_path), key=lambda e: e.name)):
        if entry.is_file():
            file_path = os.path.join(img_path, entry.name)
            os.remove(file_path)

def scantree(path, _seen=None):
    """Recursive scandir that also descends into symlinked directories.
    Lakka's USB auto-mounts and our /storage/roms/<system>/<sub> symlinks
    require this — without it every symlinked dir is treated as a file
    and skipped by the format check."""
    if _seen is None:
        _seen = set()
    try:
        real = os.path.realpath(path)
    except OSError:
        return
    if real in _seen:
        return
    _seen.add(real)
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=True):
                        yield from scantree(entry.path, _seen)
                    elif entry.is_file(follow_symlinks=True):
                        yield entry
                except OSError:
                    continue
    except OSError:
        return

def cmd(command, verbose=False):
    if verbose:
        return os.system(command)
    else:
        return os.system(command + ' > /dev/null 2>&1')

def set_scroll_led():
    if rtk.cfg_keyb_mouse == 'on':
        cmd('setleds -L +scroll')
    else:
        cmd('setleds -L -scroll')

def reset_key_pressed():
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    for joy_id in range(num_joysticks):
        joystick = pygame.joystick.Joystick(joy_id)
        joystick.init()

def check_rom_path(path):
    if os.path.isfile(path) or '/media/' in path:
        return True
    else:
        return False

def reset_launcher():
    cglobals.launcher['arcade_mode'] = None
    cglobals.launcher['neogeo_mode'] = None
    cglobals.launcher['lgun_mode'] = None
    cglobals.launcher['system'] = None
    cglobals.launcher['game_path'] = None
    cglobals.launcher['game_id'] = None
    cglobals.launcher['return_view'] = None

def get_crc(filename):
    try:
        file_size = os.path.getsize(filename)
        # CRC limited to files with max 200 Mb for performance reassons
        if file_size < 209715200:
            buf = open(filename,'rb').read()
            buf = (binascii.crc32(buf) & 0xFFFFFFFF)
            crc = "%08X" % buf
            return crc.lower()
        else:
            return '00000000'
    except:
        return '00000000'

def has_cheats():
    cheat_files = [entry.path for entry in os.scandir(cglobals.mount_point + '/cheats') if entry.name.endswith('.cfg')]
    if cheat_files:
        return True
    else:
        return False

def rotate_boot_images():
    if is_tate():
        if rtk.cfg_ui_rotation == 'rotate_ccw':
            rotation = 90
        elif rtk.cfg_ui_rotation == 'rotate_cw':
            rotation = 270
        boot_img_1          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_1_tate.bmp').convert(), rotation)
        boot_img_2          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_2_tate.bmp').convert(), rotation)
        boot_img_3          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_3_tate.bmp').convert(), rotation)
        boot_img_4          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_4_tate.bmp').convert(), rotation)
        boot_img_5          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_5_tate.bmp').convert(), rotation)
        powerdown_init_img  = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/powerdown_init_tate.bmp').convert(), rotation)
        powerdown_img       = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/powerdown_tate.bmp').convert(), rotation)
        unplug_img          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/unplug_tate.bmp').convert(), rotation)
        pygame.image.save(boot_img_1, rtk.path_rgbpi_images + '/boot_1.bmp')
        pygame.image.save(boot_img_2, rtk.path_rgbpi_images + '/boot_2.bmp')
        pygame.image.save(boot_img_3, rtk.path_rgbpi_images + '/boot_3.bmp')
        pygame.image.save(boot_img_4, rtk.path_rgbpi_images + '/boot_4.bmp')
        pygame.image.save(boot_img_5, rtk.path_rgbpi_images + '/boot_5.bmp')
        pygame.image.save(powerdown_init_img, rtk.path_rgbpi_images + '/powerdown_init.bmp')
        pygame.image.save(powerdown_img, rtk.path_rgbpi_images + '/powerdown.bmp')
        pygame.image.save(unplug_img, rtk.path_rgbpi_images + '/unplug.bmp')
    else:
        if rtk.cfg_ui_rotation == 'rotate_full':
            rotation = 180
            boot_img_1          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_1.bmp').convert(), rotation)
            boot_img_2          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_2.bmp').convert(), rotation)
            boot_img_3          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_3.bmp').convert(), rotation)
            boot_img_4          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_4.bmp').convert(), rotation)
            boot_img_5          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/boot_5.bmp').convert(), rotation)
            powerdown_init_img  = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/powerdown_init.bmp').convert(), rotation)
            powerdown_img       = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/powerdown.bmp').convert(), rotation)
            unplug_img          = pygame.transform.rotate(pygame.image.load(rtk.path_rgbpi_images + '/src/unplug.bmp').convert(), rotation)
            pygame.image.save(boot_img_1, rtk.path_rgbpi_images + '/boot_1.bmp')
            pygame.image.save(boot_img_2, rtk.path_rgbpi_images + '/boot_2.bmp')
            pygame.image.save(boot_img_3, rtk.path_rgbpi_images + '/boot_3.bmp')
            pygame.image.save(boot_img_4, rtk.path_rgbpi_images + '/boot_4.bmp')
            pygame.image.save(boot_img_5, rtk.path_rgbpi_images + '/boot_5.bmp')
            pygame.image.save(powerdown_init_img, rtk.path_rgbpi_images + '/powerdown_init.bmp')
            pygame.image.save(powerdown_img, rtk.path_rgbpi_images + '/powerdown.bmp')
            pygame.image.save(unplug_img, rtk.path_rgbpi_images + '/unplug.bmp')
        else:
            cmd('cp ' + rtk.path_rgbpi_images + '/src/boot_1.bmp ' + rtk.path_rgbpi_images + '/boot_1.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/boot_2.bmp ' + rtk.path_rgbpi_images + '/boot_2.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/boot_3.bmp ' + rtk.path_rgbpi_images + '/boot_3.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/boot_4.bmp ' + rtk.path_rgbpi_images + '/boot_4.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/boot_5.bmp ' + rtk.path_rgbpi_images + '/boot_5.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/powerdown_init.bmp ' + rtk.path_rgbpi_images + '/powerdown_init.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/powerdown.bmp ' + rtk.path_rgbpi_images + '/powerdown.bmp')
            cmd('cp ' + rtk.path_rgbpi_images + '/src/unplug.bmp ' + rtk.path_rgbpi_images + '/unplug.bmp')

def shutdown(reboot=False, save_cfg=False, manual_shutdown=False):
    # Print image in screen
    cmd('python3 /storage/rgbpi/framebuffer_write.py -img /storage/rgbpi/images/powerdown_init.bmp')
    # Save dat files bck
    bck_dat_files()
    # Save current configuration
    if save_cfg:
        rtk.save_cfg_file()
    # Manual shutdown
    #if manual_shutdown:
    #    cmd('touch ' + rtk.path_rgbpi_temp + '/do_manual_shutdown')
    # Sync disk
    #cmd('sync')
    # Clear screen
    cmd('clear')
    # Manual shutdown
    if manual_shutdown:
        cglobals.sound_mgr.stop_music()
        cmd('python3 /storage/rgbpi/framebuffer_write.py -img /storage/rgbpi/images/unplug.bmp')
        cmd('sync')
        cmd('umount -a')
        while True:
            pass
    else:
        cmd('sync')
    # Quit Pygame
    pygame.quit()
    # Shutdown or reboot
    if reboot:
        cmd('shutdown -r now')
    else:
        cmd('shutdown -h now')
    sys.exit(0)

def return_to_lakka():
    rtk.save_cfg_file()
    cmd('systemctl start rgbpi-switch-to-lakka.service --no-block')
    pygame.quit()
    sys.exit(0)

def is_game_480i(game_path):
    """Heuristic: known MAME hi-res arcade titles run at 480i and need the
    superx480 font. Anything else falls to 240p."""
    name = os.path.basename(game_path).lower()
    hi_res_prefixes = (
        'tekken', 'sf3', 'sfiii', 'jojo', 'redearth', 'wzard', 'wofch',
        'mk4', 'killinst', 'killer', 'soulclbr', 'ehrgeiz', 'fgtlayer',
        'tekkentt', 'gauntdl', 'rushgun', 'crisscross', 'twrldwar',
        'cps3', 'naomi', 'atomiswv', 'awbios', 'segasp', 'segabill'
    )
    return any(name.startswith(p) for p in hi_res_prefixes)

def is_tate():
    if rtk.cfg_ui_rotation == 'rotate_ccw' or rtk.cfg_ui_rotation == 'rotate_cw':
        return True
    else:
        return False

def fit_text(text, mode):
    if mode == 'full_elipsis':
        if not is_tate() and len(text) > 28:
            return text[:28] + '<elipsis>'
        elif is_tate() and len(text) > 20:
            return text[:20] + '<elipsis>'
        else:
            return text
    elif mode == 'short_multiline':
        if is_tate():
            max_chars = 20
        else:
            max_chars = 28
        new_txt = [j.ljust(max_chars,' ') for j in (text[i:i+max_chars] for i in  range(0,len(text),max_chars))]
        new_txt = '|'.join(new_txt)
        return new_txt
    elif mode == 'short_truncated':
        if not is_tate() and len(text) > 23:
            return text[:13] + '~' + text[-12:]
        elif is_tate() and len(text) > 15:
            return text[:7] + '~' + text[-8:]
        else:
            return text

def get_max_item_sizes(val_sizes):
    max_sizes = []
    if is_tate():
        #max_chr = 22
        max_chr = (rtk.opt_value_list_x_tate - rtk.opt_list_x) / 8
    else:
        #max_chr = 32
        max_chr = (rtk.opt_value_list_x - rtk.opt_list_x) / 8
    for val_size in val_sizes:
        val_chrs = int(val_size / 8)
        max_item_chr = max_chr - val_chrs
        max_sizes.append(max_item_chr)
    return max_sizes

def clear_navigation(up_to_view):
    rtk.logging.debug('Clear up to %s, Navigation %s',up_to_view, cglobals.nav_history)
    for view in reversed(cglobals.nav_history):
        if view != up_to_view:
            rtk.logging.debug('Removing %s',view)
            eval('cglobals.' + view).deactivate()
            cglobals.nav_history.remove(view)
        elif view == up_to_view:
            cglobals.nav_history.remove(view) # Avoind duplicated by goto_view
            break
    rtk.logging.debug('Navigation %s',cglobals.nav_history)

def goto_view(name):
    cglobals.scr_wait_time = 0
    if name == 'same_view':
        rtk.logging.debug('Goto same view %s',name)
        rtk.popup_msg.hide()
        if rtk.notif_msg.allow_hide:
            rtk.notif_msg.hide()
        rtk.transition.rewind()
        rtk.transition_tate.rewind()
    elif name == 'last_view':
        from_view = eval('cglobals.' + cglobals.nav_history[-1])
        to_view = eval('cglobals.' + cglobals.nav_history[-2])
        rtk.logging.debug('Goto last view %s --> %s',cglobals.nav_history[-1],cglobals.nav_history[-2])
        from_view.deactivate()
        to_view.activate()
        cglobals.nav_history.pop(-1)
        rtk.popup_msg.hide()
        if rtk.notif_msg.allow_hide:
            rtk.notif_msg.hide()
        rtk.transition.rewind()
        rtk.transition_tate.rewind()
    else:
        from_view = eval('cglobals.' + cglobals.nav_history[-1])
        to_view = eval('cglobals.' + name)
        rtk.logging.debug('Goto view %s --> %s',cglobals.nav_history[-1],name)
        from_view.deactivate()
        to_view.activate()
        cglobals.nav_history.append(name)
        rtk.popup_msg.hide()
        if rtk.notif_msg.allow_hide:
            rtk.notif_msg.hide()
        rtk.transition.rewind()
        rtk.transition_tate.rewind()

def get_hash(text):
    return hex(binascii.crc32(bytes(text.upper(),'utf-8')) & 0xFFFFFFFF)

def get_view_name():
    return cglobals.nav_history[-1]

def garbage_stats():
    refs = gc.get_objects()
    strs = 0
    ints = 0
    floats = 0
    tuples = 0
    lists = 0
    dicts = 0
    rtk_images = 0
    rtk_sprites = 0
    rtk_rects = 0
    rtk_boxsprites = 0
    rtk_anisprites = 0
    rtk_selectors = 0
    rtk_anigifs = 0
    rtk_texts = 0
    rtk_scrollbgs = 0
    rtk_parallaxbgs = 0
    rtk_containermgrs = 0
    rtk_containers = 0
    rtk_textlists = 0
    rtk_pageindicators = 0
    rtk_txtmsgs = 0
    rtk_events = 0
    rtk_steptimers = 0
    for ref in refs:
        if isinstance(ref, str): strs += 1
        if isinstance(ref, int): ints += 1
        if isinstance(ref, float): floats += 1
        if isinstance(ref, tuple): tuples += 1
        if isinstance(ref, list): lists += 1
        if isinstance(ref, dict): dicts += 1
        if isinstance(ref, rtk.RtkImage): rtk_images += 1
        if isinstance(ref, rtk.RtkSprite): rtk_sprites += 1
        if isinstance(ref, rtk.RtkRect): rtk_rects += 1
        if isinstance(ref, rtk.RtkBoxSprite): rtk_boxsprites += 1
        if isinstance(ref, rtk.RtkAniSprite): rtk_anisprites += 1
        if isinstance(ref, rtk.RtkSelector): rtk_selectors += 1
        if isinstance(ref, rtk.RtkAniGif): rtk_anigifs += 1
        if isinstance(ref, rtk.RtkText): rtk_texts += 1
        if isinstance(ref, rtk.RtkScrollBg): rtk_scrollbgs += 1
        if isinstance(ref, rtk.RtkParallaxBg): rtk_parallaxbgs += 1
        if isinstance(ref, rtk.RtkContainerMgr): rtk_containermgrs += 1
        if isinstance(ref, rtk.RtkContainer):
            rtk_containers += 1
            if ref.name in cglobals.debug01:
                rtk.logging.debug('Memory leak! Container: %s', ref.name)
            else:
                cglobals.debug01.append(ref.name)
        if isinstance(ref, rtk.RtkTextList): rtk_textlists += 1
        if isinstance(ref, rtk.RtkPageIndicator): rtk_pageindicators += 1
        if isinstance(ref, rtk.RtkTxtMsg): rtk_txtmsgs += 1
        if isinstance(ref, rtk.RtkEvent): rtk_events += 1
        if isinstance(ref, rtk.RtkStepTimer): rtk_steptimers += 1
    rtk.logging.debug(
        'References:\tstr=%s\tints=%s\tfloats=%s\ttuples=%s\tlists=%s\tdicts=%s\trtk_images=%s\trtk_sprites=%s\t \
        rtk_rects=%s\trtk_boxsprites=%s\trtk_anisprites=%s\trtk_selectors=%s\trtk_anigifs=%s\trtk_texts=%s\t \
        rtk_scrollbgs=%s\trtk_parallaxbgs=%s\trtk_containermgrs=%s\trtk_containers=%s\trtk_textlists=%s\t \
        rtk_pageindicators=%s\trtk_txtmsgs=%s\trtk_events=%s\trtk_steptimers=%s\t',
        strs,ints,floats,tuples,lists,dicts,rtk_images,rtk_sprites,
        rtk_rects,rtk_boxsprites,rtk_anisprites,rtk_selectors,rtk_anigifs,rtk_texts,
        rtk_scrollbgs,rtk_parallaxbgs,rtk_containermgrs,rtk_containers,rtk_textlists,
        rtk_pageindicators,rtk_txtmsgs,rtk_events,rtk_steptimers
        )
    cglobals.debug01 = []

def get_obj_size(input_obj):
    memory_size = 0
    ids = set()
    objects = [input_obj]
    while objects:
        new = []
        for obj in objects:
            if id(obj) not in ids:
                ids.add(id(obj))
                memory_size += sys.getsizeof(obj)
                new.append(obj)
        objects = gc.get_referents(*new)
    return memory_size

def write_stats(start=0,end=0):
    try: # Bug '\x00' null values written
        stats_file = cglobals.mount_point + '/dats/stats.dat'
        user       = rtk.cfg_nick
        system     = cglobals.launcher['system']
        game       = cglobals.launcher['game_path'].split('/')[-1]
        time       = str(float(end)-float(start))
        log_entry  = user + '|' + system + '|' + game + '|' + time + '\n'
        with open(stats_file, 'a', encoding='utf-8') as file:
            file.writelines(log_entry)
        url1 = 'https://' + rtk.url_webservices + '/stats.php'
        url2 = 'http://'  + rtk.url_webservices + '/stats.php'
        ws_send_stats(url1,system,game,time) or ws_send_stats(url2,system,game,time)
    except:
        pass

def get_stats():
    Stats = namedtuple('stats', 'num_games num_game_plays time_game_plays top_system')
    stats_file = cglobals.mount_point + '/dats/stats.dat'
    num_game_plays = 0
    time_game_plays = 0
    top_system = '-'
    top_number = 0
    num_games = 0
    systems_counter = {}
    # Get info from stats file
    if os.path.isfile(stats_file):
        with open(stats_file, encoding='utf-8') as file:
            for line in file:
                try:
                    line   = line.replace('\n','')
                    line   = line.split('|')
                    system = line[1]
                    time   = float(line[3])
                    num_game_plays  += 1
                    time_game_plays += time
                    if system in systems_counter:
                        systems_counter[system] += 1
                    else:
                        systems_counter[system] = 1
                except Exception as error:
                    rtk.logging.error('Error in get_stats: %s', error)
    # Get top system
    for key, value in systems_counter.items():
        if value > top_number:
            top_system = key.upper()
            top_number = value
    # Get stats numbers
    num_game_plays = str(num_game_plays)
    time = str(round(time_game_plays/3600.0,2)).split(".")
    h = str(time[0])
    m = str(int((float(time[1])/100.0)*60))
    time_game_plays = h+'h '+m+'m'
    # Get total num games
    if is_tate():
        num_games = len(cglobals.games_tate)
    else:
        for system in cglobals.system_names:
            if system != 'favorites' and system != 'kodi':
                if system == 'none':
                    break
                system_index = get_system_index(system=system)
                num_games += len(cglobals.games[system_index])
    # Return data
    stats = Stats(num_games,num_game_plays,time_game_plays,top_system)
    return stats

def get_wait_time():
    if rtk.cfg_screensaver == 'disabled': wait_time = 0
    elif rtk.cfg_screensaver_time == '1_min': wait_time = 1
    elif rtk.cfg_screensaver_time == '3_min': wait_time = 3
    elif rtk.cfg_screensaver_time == '5_min': wait_time = 5
    elif rtk.cfg_screensaver_time == '10_min': wait_time = 10
    return wait_time * 60 * rtk.fps

def check_scrsvr_wait_time():
    if not cglobals.is_in_task:
        cglobals.scr_wait_time += 1
        wait_time = get_wait_time()
        if cglobals.scr_wait_time >= wait_time and wait_time != 0:
            current_view = get_view_name()
            if current_view != 'joy_cfg_view' and current_view != 'sys_opt_grid_view' and current_view != 'lgun_cfg_view':
                goto_view('scr_saver_view')

def refresh_lang():
    if rtk.cfg_lang_selected == 'configuring':
        rtk.cfg_lang_selected = 'true'
    refresh_views(reload=False)
    rtk.save_cfg_file()
    set_core_dosbox_kb()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    if rtk.cfg_lang_selected == 'true':
        goto_view('systems_view')

def refresh_views(reload):
    gen_sys_kodi()
    update_sys_favs()
    update_sys_recents()
    cglobals.systems_view.refresh_view()
    cglobals.joy_cfg_view.refresh_view()
    cglobals.lgun_cfg_view.refresh_view()
    cglobals.games_opt_view.refresh_view()
    cglobals.favs_opt_view.refresh_view()
    cglobals.sys_opt_main_view.refresh_view()
    cglobals.sys_opt_display_view.refresh_view()
    cglobals.sys_opt_grid_view.refresh_view()
    cglobals.sys_opt_sound_view.refresh_view()
    cglobals.sys_opt_eq_view.refresh_view()
    cglobals.sys_opt_control_view.refresh_view()
    cglobals.sys_opt_bt_view.refresh_view()
    cglobals.sys_opt_network_view.refresh_view()
    cglobals.sys_opt_wifi_view.refresh_view()
    cglobals.sys_opt_netplay_view.refresh_view()
    cglobals.sys_opt_system_view.refresh_view()
    cglobals.sys_opt_lang_view.refresh_view()
    cglobals.sys_opt_theme_view.refresh_view()
    cglobals.sys_opt_playlist_view.refresh_view()
    cglobals.sys_opt_storage_view.refresh_view()
    cglobals.sys_opt_emulation_view.refresh_view()
    cglobals.sys_opt_info_view.refresh_view()
    cglobals.vkeyb_view.refresh_view()
    cglobals.scr_saver_view.refresh_view()
    cglobals.sel_ng_mode_view.refresh_view()
    cglobals.sel_handheld_mode_view.refresh_view()
    cglobals.sel_shutdown_view.refresh_view()
    cglobals.sel_scan_view.refresh_view()
    cglobals.sel_nfs_view.refresh_view()
    cglobals.info_key_view.refresh_view()
    refresh_all_game_views(reload)

def refresh_list_mode():
    refresh_all_game_views(reload_game_data=False)
    refresh_all_game_view_helpers()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def refresh_all_game_views(reload_game_data=False):
    # Create or refresh Favorites game view
    if has_favs():
        rtk.logging.info('Refreshing favs view...')
        if 'favorites_view' not in cglobals.__dict__.keys():
            cglobals.__dict__['favorites_view'] = Favs_View('favorites')
        else:
            cglobals.favorites_view.item_index = 0
            cglobals.favorites_view.get_items()
            cglobals.favorites_view.sort_items()
            cglobals.favorites_view.get_game_names()
            cglobals.favorites_view.game_list.set_txt_list(text=cglobals.favorites_view.game_names)
            cglobals.favorites_view.game_list.index = cglobals.favorites_view.item_index
            cglobals.favorites_view.game_list.refresh(force_refresh=True)
            cglobals.favorites_view.refresh_view()
            cglobals.favorites_view.deactivate()
    # Refresh all other Game views
    rtk.logging.info('Refreshing game views (reload = %s)...',reload_game_data)
    for sys_name in get_system_short_names():
        if sys_name != 'none':
            rtk.logging.info('Refreshing %s view...', sys_name)
            if sys_name != 'favorites' and sys_name != 'kodi':
                view_name = sys_name + '_view'
                if view_name not in cglobals.__dict__.keys():
                    if sys_name == 'lightgun':
                        rtk.logging.info('Creating LGun view...')
                        cglobals.__dict__[sys_name + '_view'] = Lgun_View(sys_name)
                    else:
                        rtk.logging.info('Creating Game view...')
                        cglobals.__dict__[sys_name + '_view'] = Games_View(sys_name)
                else:
                    rtk.logging.info('Getting view...')
                    game_view = cglobals.__dict__[sys_name + '_view']
                    rtk.logging.info('Resetting game view folder params...')
                    game_view.reset_folder_params(system=sys_name)
                    if reload_game_data:
                        rtk.logging.info('Getting items and reloading view...')
                        game_view.get_items(reload=True)
                    rtk.logging.info('Getting items and reloading view...')
                    game_view.get_game_names()
                    rtk.logging.info('Updating game list...')
                    game_view.game_list.set_txt_list(text=game_view.game_names)
                    rtk.logging.info('Updating game list index...')
                    game_view.game_list.index = game_view.item_index
                    rtk.logging.info('Refreshing game list...')
                    game_view.game_list.refresh(force_refresh=True)
                    rtk.logging.info('Refreshing view...')
                    game_view.refresh_view()
                    game_view.deactivate()

def refresh_recents_view():
    if rtk.cfg_show_recents != 'on':
        return
    load_recent_history()
    if 'recents' not in cglobals.system_names:
        update_sys_recents()
        cglobals.systems_view.refresh_view()
    if 'recents_view' in cglobals.__dict__.keys():
        game_view = cglobals.recents_view
        game_view.item_index = 0
        game_view.get_items(reload=True)
        game_view.get_game_names()
        game_view.game_list.set_txt_list(text=game_view.game_names)
        game_view.game_list.index = game_view.item_index
        game_view.game_list.refresh(force_refresh=True)
        game_view.refresh_view()

def refresh_helpers(): 
    cglobals.systems_view.gen_helper(is_active=False)
    cglobals.games_opt_view.gen_helper(is_active=False)
    cglobals.favs_opt_view.gen_helper(is_active=False)
    cglobals.sys_opt_main_view.gen_helper(is_active=False)
    cglobals.sys_opt_display_view.gen_helper(is_active=False)
    cglobals.sys_opt_grid_view.gen_helper(is_active=False)
    cglobals.sys_opt_sound_view.gen_helper(is_active=False)
    cglobals.sys_opt_eq_view.gen_helper(is_active=False)
    cglobals.sys_opt_control_view.gen_helper(is_active=False)
    cglobals.sys_opt_bt_view.gen_helper(is_active=False)
    cglobals.sys_opt_network_view.gen_helper(is_active=False)
    cglobals.sys_opt_wifi_view.gen_helper(is_active=False)
    cglobals.sys_opt_netplay_view.gen_helper(is_active=False)
    cglobals.sys_opt_system_view.gen_helper(is_active=False)
    cglobals.sys_opt_lang_view.gen_helper(is_active=False)
    cglobals.sys_opt_theme_view.gen_helper(is_active=False)
    cglobals.sys_opt_playlist_view.gen_helper(is_active=False)
    cglobals.sys_opt_storage_view.gen_helper(is_active=False)
    cglobals.sys_opt_emulation_view.gen_helper(is_active=False)
    cglobals.sys_opt_info_view.gen_helper(is_active=False)
    cglobals.vkeyb_view.gen_helper(is_active=False)
    cglobals.sel_ng_mode_view.gen_helper(is_active=False)
    cglobals.sel_handheld_mode_view.gen_helper(is_active=False)
    cglobals.sel_shutdown_view.gen_helper(is_active=False)
    cglobals.sel_scan_view.gen_helper(is_active=False)
    cglobals.sel_nfs_view.gen_helper(is_active=False)
    cglobals.info_key_view.gen_helper(is_active=False)
    refresh_all_game_view_helpers()

def refresh_all_game_view_helpers():
    # Create or refresh Favorites game view
    if has_favs():
        cglobals.favorites_view.gen_helper(is_active=False, force_refresh=True)
    # Refresh all other Game views
    for sys_name in get_system_short_names():
        if sys_name != 'none':
            if sys_name != 'favorites' and sys_name != 'kodi':
                view_name = sys_name + '_view'
                if view_name in cglobals.__dict__.keys():
                    eval('cglobals.'+view_name).gen_helper(is_active=False, force_refresh=True)

def refresh_theme():
    cglobals.sound_mgr.load_sound_fx()
    load_music()
    rtk.load_theme(name=rtk.cfg_theme, is_tate=is_tate())
    cglobals.systems_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.joy_cfg_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.lgun_cfg_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.games_opt_view.gen_menu(is_fav=False,is_active=False,is_refresh=True)
    cglobals.favs_opt_view.gen_menu(is_fav=True,is_active=False,is_refresh=True)
    cglobals.sys_opt_main_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_display_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_grid_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_sound_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_eq_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_control_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_bt_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_network_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_wifi_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_netplay_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_system_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_lang_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_theme_view.gen_menu(is_active=True,is_refresh=True)
    cglobals.sys_opt_playlist_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_emulation_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_storage_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sys_opt_info_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.vkeyb_view.gen_keyboard(is_active=False,is_refresh=True)
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    cglobals.sel_ng_mode_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sel_handheld_mode_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sel_shutdown_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sel_scan_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.sel_nfs_view.gen_menu(is_active=False,is_refresh=True)
    cglobals.info_key_view.gen_menu(is_active=False,is_refresh=True)
    for sys_name in get_system_short_names():
        if sys_name == 'kodi':
            continue
        elif sys_name != 'none':
            cglobals.__dict__[sys_name + '_view'].gen_menu(system=sys_name,is_active=False,is_refresh=True)
    cglobals.sys_opt_playlist_view.set_playlist(name=rtk.cfg_playlist)
    rtk.step_timer.start()
    cglobals.time_step = rtk.step_timer.get_ticks()

def replace_text_line(file_path,search_string,replace_string):
    with open(file_path, 'r', encoding='utf-8') as fp:
        file_content = fp.read()
        new_content = file_content.replace(search_string, replace_string)
    with open(file_path, 'w', encoding='utf-8') as fp:
        fp.write(new_content)

def chg_boot_param(old,new):
    cmd('cp /boot/config.txt ' + rtk.path_rgbpi_temp)
    replace_text_line(file_path=rtk.path_rgbpi_temp + '/config.txt',search_string=old,replace_string=new)
    cmd('cp -f ' + rtk.path_rgbpi_temp + '/config.txt /boot')

def copytree(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    lst = os.listdir(src)
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d)
        else:
            shutil.copyfile(s, d)

def sys_update():
    # Lakka-port: OTA server is RGB-Pi proprietary; disabled until
    # a Lakka-specific update endpoint is wired up.
    try:
        rtk.logging.info('sys_update: disabled on Lakka port')
        rtk.notif_msg.display(text='no_update_server', l_icon='forbidden')
        return
        url1 = 'https://' + rtk.url_webservices + '/sys_update.php'
        url2 = 'http://'  + rtk.url_webservices + '/sys_update.php'
        upd_info = ws_get_osversion(url1) or ws_get_osversion(url2)
        if upd_info:
            upd_os_ver      = int(upd_info[0])
            upd_os_int_ver  = int(upd_info[1])
            upd_os_date_ver = int(upd_info[2])
            cur_os_ver      = int(rtk.cfg_os_ver)
            cur_os_int_ver  = int(rtk.cfg_os_int_ver)
            cur_os_date_ver = int(rtk.cfg_os_date_ver)
            if upd_os_ver == cur_os_ver and upd_os_int_ver > cur_os_int_ver and upd_os_date_ver > cur_os_date_ver:
                rtk.logging.info('upd_os_ver %s, upd_os_int_ver %s, upd_os_date_ver %s', upd_os_ver, upd_os_int_ver, upd_os_date_ver)
                rtk.logging.info('cur_os_ver %s, cur_os_int_ver %s, cur_os_date_ver %s', cur_os_ver, cur_os_int_ver, cur_os_date_ver)
                full_ver = str(upd_os_ver) + '_' + str(upd_os_int_ver) + '_' + str(upd_os_date_ver)
                rtk.popup_msg.display(text='installing_update', l_icon='download')
                # Download update file
                file_name = full_ver + '.zip'
                local_file = ws_download_file('sys_update', file_name)
                rtk.logging.info('file_name %s, local_file %s',file_name, local_file)
                # Extract files
                extract_dir = rtk.path_rgbpi_temp + '/' + full_ver
                rtk.logging.info('extract_dir %s',extract_dir)
                zip_ref = zipfile.ZipFile(local_file, 'r')
                zip_ref.extractall(extract_dir)
                zip_ref.close()
                # Pre-update tasks
                update_script = extract_dir + '/pre-update.py'
                rtk.logging.info('update_script %s',update_script)
                if os.path.isfile(update_script):
                    cmd('python3 ' + update_script)
                # Update system files
                # Data
                system_dir = rtk.path_rgbpi_data
                update_dir = extract_dir + '/data/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                copytree(src=update_dir, dst=system_dir)
                # RA Fonts
                system_dir = rtk.path_retroarch_fonts
                update_dir = extract_dir + '/fonts/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                copytree(src=update_dir, dst=system_dir)
                # Images
                system_dir = rtk.path_rgbpi_images
                update_dir = extract_dir + '/images/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                copytree(src=update_dir, dst=system_dir)
                # Sounds
                system_dir = rtk.path_rgbpi_sounds
                update_dir = extract_dir + '/sounds/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                copytree(src=update_dir, dst=system_dir)
                # Themes
                system_dir = rtk.path_rgbpi_themes
                update_dir = extract_dir + '/themes/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                copytree(src=update_dir, dst=system_dir)
                # System
                system_dir = rtk.path_rgbpi
                update_dir = extract_dir + '/system/'
                rtk.logging.info('system_dir %s, update_dir %s',system_dir, update_dir)
                #cmd('mv ' + update_dir + 'rgbpiui ' + rtk.path_rgbpi_temp) # Move binary
                copytree(src=update_dir, dst=system_dir)
                # Post-update tasks
                update_script = extract_dir + '/post-update.py'
                rtk.logging.info('update_script %s',update_script)
                if os.path.isfile(update_script):
                    cmd('python3 ' + update_script)
                # Update system version info
                rtk.cfg_os_ver      = upd_os_ver
                rtk.cfg_os_int_ver  = upd_os_int_ver
                rtk.cfg_os_date_ver = upd_os_date_ver
                rtk.logging.info('cfg_os_ver %s, cfg_os_int_ver %s, cfg_os_date_ver %s', rtk.cfg_os_ver, rtk.cfg_os_int_ver, rtk.cfg_os_date_ver)
                # Delete instalation files from temp directory
                os.remove(local_file)
                shutil.rmtree(extract_dir, ignore_errors=True)
                # Do safe reboot
                rtk.popup_msg.hide()
                rtk.notif_msg.display(text='update_complete', l_icon='download')
                cmd('clear')
                shutdown(reboot=True, save_cfg=True)
            else:
                rtk.notif_msg.display(text='update_not_found', l_icon='download')
            rtk.popup_msg.hide()
            cglobals.is_in_task = False
        else:
            rtk.popup_msg.hide()
            cglobals.is_in_task = False
            rtk.notif_msg.display(text='update_error', l_icon='download')
    except Exception as error:
        rtk.popup_msg.hide()
        cglobals.is_in_task = False
        rtk.notif_msg.display(text='update_error', l_icon='download')
        rtk.logging.error('Error updating system %s', error)

def scr_update():
    try:
        url1 = 'https://' + rtk.url_webservices + '/scr_update.php'
        url2 = 'http://'  + rtk.url_webservices + '/scr_update.php'
        upd_info = ws_get_scrversion(url1) or ws_get_scrversion(url2)
        if upd_info:
            upd_scr_date_ver = int(upd_info)
            cur_scr_date_ver = int(rtk.cfg_scr_date_ver)
            if upd_scr_date_ver > cur_scr_date_ver:
                rtk.logging.info('upd_scr_date_ver %s', upd_scr_date_ver)
                rtk.logging.info('cur_scr_date_ver %s', cur_scr_date_ver)
                full_ver = str(upd_scr_date_ver)
                rtk.popup_msg.display(text='installing_update', l_icon='download')
                # Download update file
                file_name = full_ver + '.zip'
                local_file = ws_download_file('scr_update', file_name)
                rtk.logging.info('file_name %s, local_file %s',file_name, local_file)
                # Extract files
                extract_dir = os.path.join(rtk.path_rgbpi_scraper, 'images')
                rtk.logging.info('extract_dir %s',extract_dir)
                zip_ref = zipfile.ZipFile(local_file, 'r')
                zip_ref.extractall(extract_dir)
                zip_ref.close()
                # Copy scraper.dat
                cmd('mv -f ' + rtk.path_rgbpi_scraper + '/images/scraper.dat ' + rtk.path_rgbpi_scraper)
                # Update scraper version info
                rtk.cfg_scr_date_ver = upd_scr_date_ver
                rtk.logging.info('cfg_scr_date_ver %s', rtk.cfg_scr_date_ver)
                cglobals.event_mgr.submit_event('save_config')
                # Delete instalation files from temp directory
                os.remove(local_file)
                # Do safe reboot
                rtk.popup_msg.hide()
                rtk.notif_msg.display(text='update_complete', l_icon='download')
                cmd('clear')
                rtk.save_cfg_file()
                #shutdown(reboot=True, save_cfg=False)
            else:
                rtk.notif_msg.display(text='update_not_found', l_icon='download')
            rtk.popup_msg.hide()
            cglobals.is_in_task = False
        else:
            rtk.popup_msg.hide()
            cglobals.is_in_task = False
            rtk.notif_msg.display(text='update_error', l_icon='download')
    except Exception as error:
        rtk.popup_msg.hide()
        cglobals.is_in_task = False
        rtk.notif_msg.display(text='update_error', l_icon='download')
        rtk.logging.error('Error updating scraper %s', error)

def restore_config():
    # Units
    umount_all()
    # Sound
    cglobals.sound_mgr.set_volume('80')
    cglobals.sound_mgr.set_preset(preset='Flat')
    disable_audio_jack()
    # Controls
    unpair_bt_joys()
    # Network
    rtk.cfg_wifi_pwd = '-'
    rtk.cfg_wifi_ssid = '-'
    rtk.cfg_wifi_country = 'GB'
    set_wifi_config()
    wifi_disconnect()
    # Emulation
    rtk.cfg_keyb_mouse = 'off'
    set_scroll_led()
    # Overclock
    if rtk.cfg_overclock == 'on':
        disable_overclock()
    # Remove autoconfig files
    cmd('rm -f ' + rtk.path_autoconfig + '/*')
    # Remove all per game configuration
    cmd('rm -f ' + cglobals.mount_point + '/gameconfig/*')
    # Remove log files
    cmd('rm -f ' + rtk.path_rgbpi_logs + '/*')
    # Remove dat files
    cmd('rm -f ' + cglobals.mount_point + '/dats/games.dat')
    cmd('rm -f ' + cglobals.mount_point + '/dats/favorites.dat')
    cmd('rm -f ' + cglobals.mount_point + '/dats/favorites_tate.dat')
    cmd('rm -f ' + cglobals.mount_point + '/dats/games.bck')
    cmd('rm -f ' + cglobals.mount_point + '/dats/favorites.bck')
    cmd('rm -f ' + cglobals.mount_point + '/dats/favorites_tate.bck')
    cmd('rm -f ' + cglobals.mount_point + '/dats/stats.dat')
    # Remove temp files
    cmd('rm -rf ' + rtk.path_rgbpi_temp + '/*')
    # Remove RA custom config
    cmd('rm -f ' + rtk.path_rgbpi_data + '/retroarch.cfg')
    # Remove remaps
    cmd('rm -rf ' + cglobals.mount_point + '/remaps/*')
    # Restore backup files
    cmd('cp -fp ' + rtk.path_rgbpi_backup + '/joyconfig/* ' + rtk.path_autoconfig)
    cmd('cp -fp ' + rtk.path_rgbpi_backup + '/config.ini ' + rtk.path_rgbpi)
    cmd('cp -fp ' + rtk.path_rgbpi_backup + '/cores.cfg ' + rtk.path_rgbpi_data)
    # Fix file and folder permissions (SD)
    fix_permissions(fix_all=True)
    # Clear command line history    
    cmd('cat /dev/null 2>&1 > ~/.bash_history && history -c')
    # Set current version
    set_ver()
    # Do safe reboot
    cmd('clear')
    shutdown()

def set_ver():
    cur_os_ver       = str(rtk.cfg_os_ver)
    cur_os_int_ver   = str(rtk.cfg_os_int_ver)
    cur_os_date_ver  = str(rtk.cfg_os_date_ver)
    cur_scr_date_ver = str(rtk.cfg_scr_date_ver)
    cfg_file = rtk.path_rgbpi + '/config.ini'
    # Open config file
    configr = configparser.RawConfigParser()
    configr.read(cfg_file)
    # Create new configuration
    configw = configparser.RawConfigParser()
    # Set configuration values
    for section in configr.sections():
        configw.add_section(section)
        for (option, value) in configr.items(section):
            if option == 'os_ver':
                configw.set(section, option, cur_os_ver)
            elif option == 'os_int_ver':
                configw.set(section, option, cur_os_int_ver)
            elif option == 'os_date_ver':
                configw.set(section, option, cur_os_date_ver)
            elif option == 'scr_date_ver':
                configw.set(section, option, cur_scr_date_ver)
            else:
                configw.set(section, option, value)
    # Write configuration to file
    with open(cfg_file, 'w', encoding='utf-8') as configfile:
        configw.write(configfile)

def get_cpu_info():
    CPU = namedtuple('cpu', 'max_freq min_freq current_freq revision')
    cpufreq = psutil.cpu_freq()
    max_freq = f'{cpufreq.max:.0f}Mhz'
    min_freq = f'{cpufreq.min:.0f}Mhz'
    current_freq = f'{cpufreq.current:.0f}Mhz'
    revision = get_cpu_rev()
    cpu_info = CPU(max_freq,min_freq,current_freq,revision)
    return cpu_info

def get_cpu_rev():
    p = subprocess.Popen('cat /proc/cpuinfo | grep Revision', stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p.wait()
    revision = output.decode('utf-8').replace('\n','').split(':')[1].strip()
    return revision

def get_sensor_info():
    Sensor = namedtuple('sensor', 'temp')
    sensors = psutil.sensors_temperatures()
    temp = f'{sensors["cpu_thermal"][0].current:.1f}ºC'
    sensor_info = Sensor(temp)
    return sensor_info

def get_ram_info():
    Mem = namedtuple('memory', 'total')
    mem = psutil.virtual_memory()
    total = get_size(mem.total)
    ram_info = Mem(total)
    return ram_info

''' Disk '''
    
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.1f}{unit}{suffix}"
        bytes /= factor

def get_disk_info():
    Disk = namedtuple('disk', 'total used free')
    partitions = psutil.disk_partitions()
    for partition in partitions:
        mount_point = partition.mountpoint
        try: partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError: continue
        total = get_size(partition_usage.total)
        used = get_size(partition_usage.used)
        free = get_size(partition_usage.free)
        if mount_point == '/':
            disk_info = Disk(total,used,free)
        elif mount_point == cglobals.mount_point:
            disk_info = Disk(total,used,free)
    return disk_info

def _read_first_line(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.readline().replace('\x00', '').strip()
    except Exception:
        return ''

def _read_os_release():
    data = {}
    for path in ('/etc/os-release', '/usr/lib/os-release'):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                for line in file:
                    if '=' not in line:
                        continue
                    key, value = line.strip().split('=', 1)
                    data[key] = value.strip().strip('"')
            if data:
                return data
        except Exception:
            pass
    return data

def get_lakka_system_version():
    os_release = _read_os_release()
    name = os_release.get('NAME') or 'Lakka'
    version_id = os_release.get('VERSION_ID')
    if version_id:
        return name + ' ' + version_id
    return os_release.get('PRETTY_NAME') or _read_first_line('/etc/release') or name

def get_lakka_build_version():
    os_release = _read_os_release()
    return (
        os_release.get('VERSION') or
        os_release.get('BUILD_ID') or
        _read_first_line('/etc/release') or
        platform.release()
    )

def get_cpu_info():
    CPU = namedtuple('cpu', 'max_freq min_freq current_freq revision')
    try:
        cpufreq = psutil.cpu_freq()
        max_freq = f'{cpufreq.max:.0f}MHz' if cpufreq and cpufreq.max else 'N/A'
        min_freq = f'{cpufreq.min:.0f}MHz' if cpufreq and cpufreq.min else 'N/A'
        current_freq = f'{cpufreq.current:.0f}MHz' if cpufreq and cpufreq.current else 'N/A'
    except Exception:
        max_freq = 'N/A'
        min_freq = 'N/A'
        current_freq = 'N/A'
    if current_freq == 'N/A':
        khz = _read_first_line('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq')
        if khz.isdigit():
            current_freq = f'{int(khz) / 1000:.0f}MHz'
    revision = get_cpu_rev()
    return CPU(max_freq,min_freq,current_freq,revision)

def get_cpu_rev():
    model = _read_first_line('/proc/device-tree/model')
    if model:
        return model.replace('Raspberry Pi ', 'RPi ')
    try:
        with open('/proc/cpuinfo', 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('Revision'):
                    return line.split(':', 1)[1].strip()
                if line.startswith('Model'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return platform.machine()

def get_sensor_info():
    Sensor = namedtuple('sensor', 'temp')
    temp = None
    try:
        sensors = psutil.sensors_temperatures()
        for key in ('cpu_thermal', 'soc_thermal', 'thermal_zone0'):
            if key in sensors and sensors[key]:
                temp = sensors[key][0].current
                break
    except Exception:
        pass
    if temp is None:
        raw_temp = _read_first_line('/sys/class/thermal/thermal_zone0/temp')
        if raw_temp.isdigit():
            temp = int(raw_temp) / 1000
    temp = f'{temp:.1f}C' if temp is not None else 'N/A'
    return Sensor(temp)

def get_ram_info():
    Mem = namedtuple('memory', 'total')
    try:
        mem = psutil.virtual_memory()
        total = get_size(mem.total)
    except Exception:
        total = 'N/A'
    return Mem(total)

def get_disk_info():
    Disk = namedtuple('disk', 'total used free')
    for path in ('/storage', cglobals.mount_point, '/'):
        try:
            partition_usage = psutil.disk_usage(path)
            total = get_size(partition_usage.total)
            used = get_size(partition_usage.used)
            free = get_size(partition_usage.free)
            return Disk(total,used,free)
        except Exception:
            continue
    return Disk('N/A','N/A','N/A')

def check_boot_disk():
    if not cglobals.is_in_task:
        if rtk.cfg_data_source == 'sd':
            umount_all()
            cglobals.mount_point = rtk.path_media_sd
        elif 'usb' in rtk.cfg_data_source:
            umount_all()
            status = mount_usb(usb=rtk.cfg_data_source)
            if status != 'ok_mount':
                rtk.cfg_data_source = 'sd'
                cglobals.mount_point = rtk.path_media_sd
                cglobals.event_mgr.submit_event('save_config')
        elif 'nfs' in rtk.cfg_data_source:
            umount_all()
            # Check network status
            for i in range(15):
                ethernet_status = get_net_status(type='ethernet')
                wifi_status = get_net_status(type='wifi')
                if ethernet_status != 'disconnected_info' or wifi_status != 'disconnected_info':
                    rtk.logging.debug('NFS cable status: %s', ethernet_status)
                    rtk.logging.debug('NFS wifi status: %s', wifi_status)
                    break
                time.sleep(1)
            else:
                rtk.logging.debug('NFS network unavailable')
            status = mount_nfs(nfs=rtk.cfg_data_source)
            if 'ko' in status:
                rtk.cfg_data_source = 'sd'
                cglobals.mount_point = rtk.path_media_sd
                cglobals.event_mgr.submit_event('save_config')

def check_folders(path=None):
    if path:
        create_folder(path=path + '/dats')
        create_folder(path=path + '/roms')
        create_folder(path=path + '/roms/kodi')
        create_folder(path=path + '/bios')
        create_folder(path=path + '/saves')
        create_folder(path=path + '/screenshots')
        create_folder(path=rtk.path_autoconfig)
        create_folder(path=path + '/gameconfig')
        create_folder(path=path + '/remaps')
        create_folder(path=path + '/remaps/system')
        create_folder(path=path + '/remaps/user')
        create_folder(path=path + '/cheats')
        create_sys_folders(destination=path + '/roms')
        create_sys_folders(destination=path + '/saves')
        create_sys_folders(destination=path + '/screenshots')
    else:
        create_folder(path=cglobals.mount_point + '/dats')
        create_folder(path=cglobals.mount_point + '/roms')
        create_folder(path=cglobals.mount_point + '/roms/kodi')
        create_folder(path=cglobals.mount_point + '/bios')
        create_folder(path=cglobals.mount_point + '/saves')
        create_folder(path=cglobals.mount_point + '/screenshots')
        create_folder(path=rtk.path_autoconfig)
        create_folder(path=cglobals.mount_point + '/gameconfig')
        create_folder(path=cglobals.mount_point + '/remaps')
        create_folder(path=cglobals.mount_point + '/remaps/system')
        create_folder(path=cglobals.mount_point + '/remaps/user')
        create_folder(path=cglobals.mount_point + '/cheats')
        create_sys_folders(destination=cglobals.mount_point + '/roms')
        create_sys_folders(destination=cglobals.mount_point + '/saves')
        create_sys_folders(destination=cglobals.mount_point + '/screenshots')

def create_sys_folders(destination):
    try:
        with open(rtk.path_rgbpi_data + '/systems.dat', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in reader:
                system = row["System"]
                subsystems = row["Subsystems"].split('|')
                if subsystems == [""]:
                    subsystems = []
                path = destination + '/' + system
                # Create main system rom directory
                create_folder(path=path)
                # Create specific core rom subdirectory
                for subdir in subsystems:
                    path = destination + '/' + system + '/' + subdir
                    create_folder(path=path)
    except Exception as error:
        rtk.logging.error('Error checking folders: %s', error)

def physical_drives():
    drive_glob = '/sys/block/*/device'
    return [os.path.basename(os.path.dirname(d)) for d in glob.glob(drive_glob)]

def refresh_sys_info():
    cglobals.sys_opt_info_view.refresh_values()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def refresh_storage_names():
    cglobals.sys_opt_storage_view.set_labels()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def evt_mount_sd():
    umount_all()
    rtk.cfg_data_source = 'sd'
    cglobals.mount_point = rtk.path_media_sd
    cglobals.event_mgr.submit_event('save_config')
    scan_from_ui_common()
    goto_view('systems_view')
    cglobals.sys_opt_storage_view.refresh_options()
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text='ok_mount')

def evt_mount_usb1():
    status = mount_usb(usb='usb1')
    if status == 'ok_mount':
        rtk.cfg_data_source = 'usb1'
        cglobals.event_mgr.submit_event('save_config')
        scan_from_ui_common()
        goto_view('systems_view')
        cglobals.sys_opt_storage_view.refresh_options()
    else:
        cglobals.mount_point = rtk.path_media_sd
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def evt_mount_usb2():
    status = mount_usb(usb='usb2')
    if status == 'ok_mount':
        rtk.cfg_data_source = 'usb2'
        cglobals.event_mgr.submit_event('save_config')
        scan_from_ui_common()
        goto_view('systems_view')
        cglobals.sys_opt_storage_view.refresh_options()
    else:
        cglobals.mount_point = rtk.path_media_sd
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def evt_format_usb1():
    status = format_usb(usb='usb1')
    if status == 'ok_format':
        refresh_storage_names()
        goto_view('last_view')
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def evt_format_usb2():
    status = format_usb(usb='usb2')
    if status == 'ok_format':
        refresh_storage_names()
        goto_view('last_view')
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def evt_mount_nfsa():
    status = mount_nfs(nfs='nfsa')
    if status == 'ok_mount':
        rtk.cfg_data_source = 'nfsa'
        cglobals.event_mgr.submit_event('save_config')
        scan_from_ui_common()
        goto_view('systems_view')
        cglobals.sys_opt_storage_view.refresh_options()
    else:
        cglobals.mount_point = rtk.path_media_sd
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def evt_mount_nfsb():
    rtk.logging.info('Mounting NFS Global...')
    status = mount_nfs(nfs='nfsb')
    if status == 'ok_mount':
        rtk.logging.info('NFS mounted OK')
        rtk.cfg_data_source = 'nfsb'
        rtk.logging.info('Saving configuration...')
        cglobals.event_mgr.submit_event('save_config')
        rtk.logging.info('Scanning games...')
        scan_from_ui_common()
        rtk.logging.info('Navigating to system view...')
        goto_view('systems_view')
        rtk.logging.info('Refreshing storage view...')
        cglobals.sys_opt_storage_view.refresh_options()
    else:
        rtk.logging.info('NFS mounted KO')
        cglobals.mount_point = rtk.path_media_sd
    rtk.logging.info('Refreshing screen saver...')
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    rtk.logging.info('NFS mount completed')
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    rtk.notif_msg.display(text=status)

def get_storage_name(device):
        if device == 'sd':
            dev = 'mmcblk0p2'
        elif device == 'usb1':
            dev = 'sda1'
        elif device == 'usb2':
            dev = 'sdb1'
        else:
            dev = device
        p = subprocess.Popen('blkid -o value -s LABEL /dev/' + dev, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p.wait()
        name = output.decode('utf-8').replace('\n','')
        if not name:
            name = '-'
        return name

def umount_all():
    cmd('umount -l ' + rtk.path_media_sd)
    cmd('umount -l ' + rtk.path_media_usb1)
    cmd('umount -l ' + rtk.path_media_usb2)
    cmd('umount -l ' + rtk.path_media_nfsl)
    cmd('umount -l ' + rtk.path_media_nfsg)
    
def check_usb_drive():
    num_drives = len(physical_drives())
    if num_drives != cglobals.num_drives:
        cglobals.num_drives = num_drives
    try:
        if 'usb' in rtk.cfg_data_source:
            for d in physical_drives():
                if rtk.cfg_data_source == 'usb1' and d == 'sda':
                    return True
                elif rtk.cfg_data_source == 'usb2' and d == 'sdb':
                    return True                            
            else:
                rtk.popup_msg.display(text='mounting_unit')
                cglobals.is_in_task = True
                evt_mount_sd()
                refresh_storage_names()
    except Exception as error:
        rtk.logging.error('Error checking USB drives: %s', error)

def create_folder(path):
    if not os.path.exists(path):
        try: os.mkdir(path)
        except Exception as error: rtk.logging.debug('Error creating folder %s. %s',path,error)

def format_usb(usb):
    # Get disk info
    disk = None
    for d in physical_drives():
        if usb == 'usb1' and d == 'sda':
            disk = 'sda1'
            path = rtk.path_media_usb1
            break
        elif usb == 'usb2' and d == 'sdb':
            disk = 'sdb1'
            path = rtk.path_media_usb2
            break
    # Check disk
    if disk == None:
        return 'ko_unit_not_found'
    else:
        cmd('umount -l ' + path)
        # Delete all partitions
        cmd('wipefs -a -f /dev/' + disk[:-1])
        # Create new partition
        # https://www.systutorials.com/making-gpt-partition-table-and-creating-partitions-with-parted-on-linux/
        cmd('parted -s /dev/' + disk[:-1] + ' mklabel GPT')
        cmd('parted -s --align=opt /dev/' + disk[:-1] + ' mkpart primary 1 100%')
        cmd('mkfs.exfat -L RGB-PI /dev/' + disk)
        # Mount disk
        exit_code = cmd('mount -w -o dmask=000,fmask=000,noatime /dev/' + disk + ' ' + path)
        if exit_code == 0:
            # Create folder structure
            check_folders(path)
            # Check that game dat files exist
            is_ok = gen_game_files(dats_path=path + '/dats')
            if is_ok:
                # Force write all data to disk
                cmd('sync')
                # Umount
                cmd('umount -l ' + path)
                return 'ok_format'
            else:
                return 'ko_format'
        else:
            return 'ko_unit_not_found'

def mount_usb(usb):
    # Get disk info
    disk = None
    for d in physical_drives():
        if usb == 'usb1' and d == 'sda':
            disk = 'sda1'
            cglobals.mount_point = rtk.path_media_usb1
            break
        elif usb == 'usb2' and d == 'sdb':
            disk = 'sdb1'
            cglobals.mount_point = rtk.path_media_usb2
            break
    # Check disk
    if disk == None:
        return 'ko_unit_not_found'
    # Lakka-port: udisks auto-mounts USB sticks under
    # /storage/roms/<dev>-usb-<label>/. Reuse that mount instead of
    # forcing the disk into /var/media — saves us re-mounting and lets
    # Lakka own the device. We just point cglobals.mount_point at the
    # auto-mount and consider it ok.
    try:
        with open('/proc/mounts') as _mf:
            for line in _mf:
                parts = line.split()
                if parts and parts[0] == '/dev/' + disk:
                    auto_mp = parts[1]
                    # Only accept paths under /storage/roms or /var/media
                    if auto_mp.startswith('/storage/roms') or auto_mp.startswith('/var/media'):
                        cglobals.mount_point = auto_mp
                        rtk.logging.info('mount_usb: reusing existing mount %s', auto_mp)
                        is_ok = gen_game_files()
                        return 'ok_mount' if is_ok else 'ko_mnt_files'
    except Exception as _e:
        rtk.logging.debug('mount_usb auto-mount probe: %s', _e)
    # Fall through to original behaviour (remount at path_media_usbN)
    if True:
        # Umount units
        umount_all()
        # Mount and replace local gamefiles path
        exit_code = cmd('mount -w -o dmask=000,fmask=000,noatime /dev/' + disk + ' ' + cglobals.mount_point)
        if exit_code == 0:
            # Check folder structure
            check_folders()
            if not os.path.exists(cglobals.mount_point + '/roms') or not os.path.exists(cglobals.mount_point + '/bios'):
                umount_all()
                return 'ko_mnt_folders'
            # Check data game files
            is_ok = gen_game_files()
            if not is_ok:
                umount_all()
                return 'ko_mnt_files'
            return 'ok_mount'
        else:
            return 'ko_unit_not_found'

def mount_nfs(nfs):
    # Get nas info
    if nfs == 'nfsa':
        srv_share = rtk.cfg_nfsa
        cglobals.mount_point = rtk.path_media_nfsl
    elif nfs == 'nfsb':
        srv_share = rtk.cfg_nfsb
        cglobals.mount_point = rtk.path_media_nfsg
    if ':' not in srv_share and len(srv_share) < 12:
        has_nas_config = False
    else:
        has_nas_config = True
    # Check nas
    if not has_nas_config:
        return 'ko_nas_config'
    else:
        umount_all()
        # Mount and replace local gamefiles path
        # mount -t nfs -o rw,soft,timeo=3,retrans=1,retry=0,noatime nfs.rgb-pi.com:/hi /media/nfsg
        exit_code = cmd('mount -t nfs -o rw,soft,timeo=3,retrans=1,retry=0,noatime ' + srv_share + ' ' + cglobals.mount_point)
        rtk.logging.info('NFS mount status: %s', exit_code)
        if exit_code == 0:
            # Check folder structure
            rtk.logging.info('NFS checking folders...')
            check_folders()
            if not os.path.exists(cglobals.mount_point + '/roms') or not os.path.exists(cglobals.mount_point + '/bios'):
                rtk.logging.info('NFS checking folders error: ko_mnt_folders')
                umount_all()
                return 'ko_mnt_folders'
            # Check data game files
            rtk.logging.info('NFS generating dat files...')
            is_ok = gen_game_files()
            if not is_ok:
                rtk.logging.info('NFS checking folders error: ko_mnt_files')
                umount_all()
                return 'ko_mnt_files'
            rtk.logging.info('NFS mounted OK')
            return 'ok_mount'
        else:
            rtk.logging.info('NFS not found')
            return 'ko_unit_not_found'

def expand_sd():
    # Get max partition size in MB
    p = subprocess.Popen("parted -s /dev/mmcblk0 -m unit Mb print free | tail -1 | grep -E 'free' | cut -d: -f 3", stdout=subprocess.PIPE, shell=True)
    (newsize, err) = p.communicate()
    p.wait()
    # Resize partition
    cmd('parted -s /dev/mmcblk0 resizepart 2 ' + newsize.decode())
    # Resize filesystem
    cmd('resize2fs /dev/mmcblk0p2')
    cglobals.event_mgr.submit_event('sd_expanded')

''' Network '''

def is_global_nfs():
    return 'nfs' in rtk.cfg_data_source and not is_local_nfs()

def set_random_nick():
    # If no custom nick is set then generate a random one
    nick = rtk.cfg_nick
    if nick == 'PLAYER':
        number = random.randint(10000, 99999)
        nick = nick + '_' + str(number)
        rtk.cfg_nick = nick
        cglobals.sys_opt_netplay_view.set_nick_name(name=nick)
        cglobals.sys_opt_netplay_view.refresh_values()

def get_selected_server_name():
    return cglobals.netplay_server_name
    
def get_all_server_names():
    return ','.join(cglobals.server_names)

def get_ip_address(ifname):
    ip = '-'
    try:
        p = subprocess.Popen('ip -4 -o addr show dev ' + ifname, stdout=subprocess.PIPE, shell=True)
        (output, _err) = p.communicate(timeout=5)
        p.wait()
        parts = output.decode('utf-8', errors='ignore').split()
        if 'inet' in parts:
            ip = parts[parts.index('inet') + 1].split('/')[0]
            return ip
    except Exception:
        pass
    try:
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            if interface_name == ifname:
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        ip = address.address
    except Exception:
        pass
    return ip

def get_net_status(type):
    if type == 'ethernet':
        net = get_ip_address('eth0')
        if net == '-':
            return 'disconnected_info'
        else:
            return net
    elif type == 'wifi':
        net = get_ip_address('wlan0')
        if net == '-':
            if cglobals.is_connecting:
                return 'connecting_info'
            else:
                return 'disconnected_info'
        else:
            cglobals.is_connecting = False
            return net

def _connman_services():
    services = []
    try:
        p = subprocess.Popen('connmanctl services', stdout=subprocess.PIPE, shell=True)
        (output, _err) = p.communicate(timeout=10)
        p.wait()
        for raw_line in output.decode('utf-8', errors='ignore').splitlines():
            line = raw_line.strip()
            if not line or ' wifi_' not in line:
                continue
            flags = ''
            while line and line[0] in '*AROT ':
                if line[0] != ' ':
                    flags += line[0]
                line = line[1:].strip()
            parts = line.rsplit(None, 1)
            if len(parts) != 2 or not parts[1].startswith('wifi_'):
                continue
            services.append({'name': parts[0].strip(), 'service': parts[1].strip(), 'flags': flags})
    except Exception as e:
        rtk.logging.error('_connman_services: %s', e)
    return services

def get_active_wifi_ssid():
    for service in _connman_services():
        if 'A' in service.get('flags', '') or 'R' in service.get('flags', ''):
            return service.get('name') or '-'
    return '-'

def enable_netplay():
    if cglobals.netplay_mode == 'server':
        cglobals.netplay_server_name = '-'
        cglobals.server_names = []
        url1 = 'https://' + rtk.url_webservices + '/netplay.php'
        url2 = 'http://'  + rtk.url_webservices + '/netplay.php'
        ws_send_netplay_info(url1) or ws_send_netplay_info(url2)
    elif cglobals.netplay_mode == 'client':
        get_server_info()
    cglobals.sys_opt_netplay_view.set_server_names()
    cglobals.sys_opt_netplay_view.refresh_values()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def disable_netplay():
    # Restore default dummy values
    cglobals.netplay_server_name = '-'
    cglobals.network_server_ip = '192.168.9.9'
    cglobals.server_names = []
    cglobals.server_ips = []
    cglobals.sys_opt_netplay_view.set_server_names()
    cglobals.sys_opt_netplay_view.refresh_values()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False
    
def get_server_info():
    # Get info from server
    try:
        url1 = 'https://' + rtk.url_webservices + '/netplay.php'
        url2 = 'http://'  + rtk.url_webservices + '/netplay.php'
        output = ws_get_netplay_info(url1) or ws_get_netplay_info(url2)
        rtk.logging.info('Netplay server info %s',output)
        cglobals.server_names = []
        cglobals.server_ips = []
        if output == 'None':
            cglobals.netplay_server_name = '-'
            cglobals.network_server_ip = '192.168.9.9'
        else:
            servers = {}
            for s in output:
                info = s.split(",")
                servers[info[0]] = info[1]
            for s,i in servers.items():
                cglobals.server_names.append(s)
                cglobals.server_ips.append(i)
            cglobals.netplay_server_name = cglobals.server_names[0]
            cglobals.network_server_ip = cglobals.server_ips[0]
    except Exception as error:
        rtk.logging.error('Error getting server info: %s', error)
        cglobals.netplay_server_name = '-'
        cglobals.network_server_ip = '192.168.9.9'
    # Get local network info
    local_ip = '-'
    ip_cable = get_ip_address('eth0')
    ip_wifi = get_ip_address('wlan0')
    # Set cable IP by default
    if ip_cable != '-':
        local_ip = ip_cable
    elif ip_wifi != '-':
        local_ip = ip_wifi
    # Scan local network
    if local_ip != '-':
        # if not found or error happen via webserver, reset for local only
        if cglobals.netplay_server_name == '-':
            cglobals.server_names = []
            cglobals.server_ips = []
        ip = local_ip.split(".")
        address = 2
        end = 80
        ip_1 = ip[0]
        ip_2 = ip[1]
        ip_3 = ip[2]
        network = ip_1 + '.' + ip_2 + '.' + ip_3 + '.'
        try:
            while address < end:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                result = sock.connect_ex((network + str(address), 55439))
                if result == 0:
                    cglobals.server_names.append(network + str(address))
                    cglobals.server_ips.append(network + str(address))
                address += 1
                sock.close()
            if cglobals.server_names:
                cglobals.netplay_server_name = cglobals.server_names[0]
                cglobals.network_server_ip = cglobals.server_ips[0]
        except Exception as error:
            rtk.logging.error('Error scanning local network: %s', error)

def set_wifi_config():
    """Lakka-port: write ConnMan config; never run wpa_passphrase / wpa_cli /
    ifconfig — those break Lakka and kill SSH on wlan0."""
    ssid = str(rtk.cfg_wifi_ssid).strip()
    pwd = str(rtk.cfg_wifi_pwd or '').strip()
    if not ssid:
        rtk.logging.info('set_wifi_config: empty SSID, skipping')
        return
    cm_dir = '/storage/.cache/connman'
    os.makedirs(cm_dir, exist_ok=True)
    ssid_hex = ''.join('%02x' % b for b in ssid.encode('utf-8'))
    cfg = (
        '[global]\n'
        'Name = wifi\n'
        'Description = wifi seeded by rgbpi-lakka\n\n'
        '[service_wifi]\n'
        'Type = wifi\n'
        'Security = psk\n'
        'Name = ' + ssid + '\n'
        'SSID = ' + ssid_hex + '\n'
        'Passphrase = ' + pwd + '\n'
        'IPv4 = dhcp\n'
        'Nameservers = 1.1.1.1,8.8.8.8\n'
    )
    try:
        with open(cm_dir + '/wifi.config', 'w', encoding='utf-8') as f:
            f.write(cfg)
        os.chmod(cm_dir + '/wifi.config', 0o600)
        # Ask connman to re-read configs without bouncing wlan0 (keeps SSH alive)
        cmd('connmanctl scan wifi >/dev/null 2>&1; true')
    except Exception as e:
        rtk.logging.error('set_wifi_config (Lakka): %s', e)

def wifi_connect():
    """Lakka-port: ask ConnMan to connect using its existing service/config.
    Never touch ifconfig/wpa_cli; that would drop SSH on Lakka."""
    cglobals.is_connecting = True
    target = str(rtk.cfg_wifi_ssid).strip()
    try:
        service_id = ''
        for service in _connman_services():
            if service.get('name') == target:
                service_id = service.get('service')
                break
        if service_id:
            cmd('connmanctl connect ' + service_id + ' >/dev/null 2>&1; true')
        else:
            cmd('connmanctl scan wifi >/dev/null 2>&1; true')
    except Exception as e:
        rtk.logging.error('wifi_connect (ConnMan): %s', e)

def wifi_disconnect():
    """Do not disconnect wlan0 from the FE; SSH may depend on it."""
    cglobals.is_connecting = False
    rtk.logging.info('wifi_disconnect: skipped to preserve Lakka/SSH network')

def scan_wifi():
    """Lakka-port: query connmanctl instead of iw scan."""
    ssids = []
    try:
        cmd('connmanctl scan wifi >/dev/null 2>&1; true')
        ssids = [service.get('name') for service in _connman_services()]
    except Exception as e:
        rtk.logging.error('scan_wifi: %s', e)
    ssids = list(dict.fromkeys(s for s in ssids if s))
    if hasattr(cglobals, 'sys_opt_wifi_view') and cglobals.sys_opt_wifi_view:
        cglobals.sys_opt_wifi_view.set_wifi_names(ssids)
        cglobals.sys_opt_wifi_view.refresh_values()
    if hasattr(rtk, 'popup_msg'):
        rtk.popup_msg.hide()
    cglobals.is_in_task = False

def is_local_nfs():
    local_ip_ranges = ('10.','172.16.','172.17.','172.18.','172.19.','172.20.','172.21.','172.22.','172.23.',
                        '172.24.','172.25.','172.26.','172.27.','172.28.','172.29.','172.30.','172.31.','192.168.')
    server = None
    if rtk.cfg_data_source == 'nfsa':
        server = rtk.cfg_nfsa.split(':')[0]
    elif rtk.cfg_data_source == 'nfsb':
        server = rtk.cfg_nfsb.split(':')[0]
    if server:
        for local_range in local_ip_ranges:
            if server.startswith(local_range):
                return True
        return False
    else:
        return False

''' Hardware '''

def init_rgbpi():
    check_01 = False
    check_02 = True # For future use
    config_file = '/flash/config.txt' if os.path.isfile('/flash/config.txt') else '/boot/config.txt'
    config_overlay_01 = 'dtoverlay=vc4-vga666,mode6\n'
    lakka_dpi_overlay = 'dtoverlay=vc4-kms-dpi-generic'
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line == config_overlay_01 or line.strip() == lakka_dpi_overlay:
                    check_01 = True
    except OSError:
        check_01 = False
    if check_01 and check_02:
        cglobals.is_rgbpi = True
    # Lakka/RetroTINK uses vc4-kms-dpi-generic, not the RGB-Pi OS VGA666
    # overlay. Treat a valid DPI config as compatible and skip raspi-gpio if
    # the tool is not present.
    if not check_01 and os.path.isfile('/flash/config.txt'):
        with open('/flash/config.txt', 'r', encoding='utf-8') as file:
            if 'vc4-kms-dpi-generic' in file.read():
                check_01 = True
    if check_01 and check_02:
        cglobals.is_rgbpi = True
    if os.path.exists('/usr/bin/raspi-gpio') or os.path.exists('/bin/raspi-gpio'):
        # Restore 1 bit color lost when i2c is enabled via dtparam=i2c_*=on.
        cmd('raspi-gpio set 4 a2')

def init_jamma():
    # Disable driver manually > modprobe -r joypi
    # Enable driver manually  > modprobe joypi
    # Check available devices > i2cdetect -y 0
    # JAMMA is 32 0x20 and 33 0x21
    try:
        bus = smbus.SMBus(0) # 0 indicates /dev/i2c-0
        bus.read_byte(32)
        cmd('modprobe joypi')
        cglobals.is_jamma = True
        rtk.logging.info('Reading i2c-0... JAMMA device initialized!')
    except Exception as error:
        rtk.logging.info('Reading i2c-0... JAMMA device NOT found!')

def disable_jamma():
    try:
        if os.path.isfile('/dev/i2c-0'):
            cmd('modprobe -r joypi')
            cglobals.is_jamma = False
            rtk.logging.info('Freeing i2c-0... JAMMA device disabled!')
    except Exception as error:
        rtk.logging.info('Error releasing JAMMA in i2c-0!')

def check_native_csync_support():
    if not (os.path.exists('/usr/bin/raspi-gpio') or os.path.exists('/bin/raspi-gpio')):
        cglobals.has_native_csync_support = False
        return
    p = subprocess.Popen('raspi-gpio get 10', stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p.wait()
    cglobals.has_native_csync_support = 'level=1' in output.decode('utf-8')
    if cglobals.has_native_csync_support and rtk.cfg_native_csync != 'on':
        rtk.cfg_native_csync = 'on'
        cglobals.event_mgr.submit_event('save_config')
    elif not cglobals.has_native_csync_support and rtk.cfg_native_csync != 'off':
        rtk.cfg_native_csync = 'off'
        cglobals.event_mgr.submit_event('save_config')

def set_sync():
    # By switching all off, we fix some resynch issues when changing timings
    cmd('raspi-gpio set 1 a0')
    cmd('raspi-gpio set 2 a0')
    cmd('raspi-gpio set 3 a0')
    time.sleep(0.2)
    # Set CSYNC or H/VSYNC
    if rtk.cfg_native_csync == 'on':
        cmd('raspi-gpio set 1 a2')
    elif rtk.cfg_native_csync == 'off':
        cmd('raspi-gpio set 2 a2')
        cmd('raspi-gpio set 3 a2')

def fix_xbox_one_bt():
    # Fix XBOX ONE S BT Pair issue
    cmd("bash -c 'echo 1 > /sys/module/bluetooth/parameters/disable_ertm'")

def fix_kb_capslock():
    # Enables capslock key led functonality
    cmd('echo keycode 58 = Caps_Lock | loadkeys -')

def create_udev_rules_file():
    if not os.path.exists(rtk.path_udev_rules):
        # Create rules file
        cmd('touch ' + rtk.path_udev_rules)
        # Remove devices that are identified as joysticks but they are not
        # List of tuples ('idVendor', 'idProduct'), as four hexadecimal digits.
        dev_blacklist = [
            # Microsoft Microsoft Wireless Optical Desktop® 2.10
            # Microsoft Wireless Desktop - Comfort Edition
            ('045e', '009d'),
            # Microsoft Microsoft® Digital Media Pro Keyboard
            # Microsoft Corp. Digital Media Pro Keyboard
            ('045e', '00b0'),
            # Microsoft Microsoft® Digital Media Keyboard
            # Microsoft Corp. Digital Media Keyboard 1.0A
            ('045e', '00b4'),
            # Microsoft Microsoft® Digital Media Keyboard 3000
            ('045e', '0730'),
            # Microsoft Microsoft® 2.4GHz Transceiver v6.0
            # Microsoft Microsoft® 2.4GHz Transceiver v8.0
            # Microsoft Corp. Nano Transceiver v1.0 for Bluetooth
            # Microsoft Wireless Mobile Mouse 1000
            # Microsoft Wireless Desktop 3000
            ('045e', '0745'),
            # Microsoft® SideWinder(TM) 2.4GHz Transceiver
            ('045e', '0748'),
            # Microsoft Corp. Wired Keyboard 600
            ('045e', '0750'),
            # Microsoft Corp. Sidewinder X4 keyboard
            ('045e', '0768'),
            # Microsoft Corp. Arc Touch Mouse Transceiver
            ('045e', '0773'),
            # Microsoft® 2.4GHz Transceiver v9.0
            # Microsoft® Nano Transceiver v2.1
            # Microsoft Sculpt Ergonomic Keyboard (5KV-00001)
            ('045e', '07a5'),
            # Microsoft® Nano Transceiver v1.0
            # Microsoft Wireless Keyboard 800
            ('045e', '07b2'),
            # Microsoft® Nano Transceiver v2.0
            ('045e', '0800'),
            ('046d', 'c30a'),  # Logitech, Inc. iTouch Composite keboard
            ('04d9', 'a0df'),  # Tek Syndicate Mouse (E-Signal USB Gaming Mouse)
            # List of Wacom devices at: http://linuxwacom.sourceforge.net/wiki/index.php/Device_IDs
            ('056a', '0010'),  # Wacom ET-0405 Graphire
            ('056a', '0011'),  # Wacom ET-0405A Graphire2 (4x5)
            ('056a', '0012'),  # Wacom ET-0507A Graphire2 (5x7)
            ('056a', '0013'),  # Wacom CTE-430 Graphire3 (4x5)
            ('056a', '0014'),  # Wacom CTE-630 Graphire3 (6x8)
            ('056a', '0015'),  # Wacom CTE-440 Graphire4 (4x5)
            ('056a', '0016'),  # Wacom CTE-640 Graphire4 (6x8)
            ('056a', '0017'),  # Wacom CTE-450 Bamboo Fun (4x5)
            ('056a', '0018'),  # Wacom CTE-650 Bamboo Fun 6x8
            ('056a', '0019'),  # Wacom CTE-631 Bamboo One
            ('056a', '00d1'),  # Wacom Bamboo Pen and Touch CTH-460
            ('056a', '030e'),  # Wacom Intuos Pen (S) CTL-480
            ('09da', '054f'),  # A4 Tech Co., G7 750 mouse
            ('09da', '1410'),  # A4 Tech Co., Ltd Bloody AL9 mouse
            ('09da', '3043'),  # A4 Tech Co., Ltd Bloody R8A Gaming Mouse
            ('09da', '31b5'),  # A4 Tech Co., Ltd Bloody TL80 Terminator Laser Gaming Mouse
            ('09da', '3997'),  # A4 Tech Co., Ltd Bloody RT7 Terminator Wireless
            ('09da', '3f8b'),  # A4 Tech Co., Ltd Bloody V8 mouse
            ('09da', '51f4'),  # Modecom MC-5006 Keyboard
            ('09da', '5589'),  # A4 Tech Co., Ltd Terminator TL9 Laser Gaming Mouse
            ('09da', '7b22'),  # A4 Tech Co., Ltd Bloody V5
            ('09da', '7f2d'),  # A4 Tech Co., Ltd Bloody R3 mouse
            ('09da', '8090'),  # A4 Tech Co., Ltd X-718BK Oscar Optical Gaming Mouse
            ('09da', '9033'),  # A4 Tech Co., X7 X-705K
            ('09da', '9066'),  # A4 Tech Co., Sharkoon Fireglider Optical
            ('09da', '9090'),  # A4 Tech Co., Ltd XL-730K / XL-750BK / XL-755BK Laser Mouse
            ('09da', '90c0'),  # A4 Tech Co., Ltd X7 G800V keyboard
            ('09da', 'f012'),  # A4 Tech Co., Ltd Bloody V7 mouse
            ('09da', 'f32a'),  # A4 Tech Co., Ltd Bloody B540 keyboard
            ('09da', 'f613'),  # A4 Tech Co., Ltd Bloody V2 mouse
            ('09da', 'f624'),  # A4 Tech Co., Ltd Bloody B120 Keyboard
            ('1b1c', '1b3c'),  # Corsair Harpoon RGB gaming mouse
            ('1d57', 'ad03'),  # [T3] 2.4GHz and IR Air Mouse Remote Control
            ('1e7d', '2e4a'),  # Roccat Tyon Mouse
            ('20a0', '422d'),  # Winkeyless.kr Keyboards
            ('2516', '001f'),  # Cooler Master Storm Mizar Mouse
            ('2516', '0028'),  # Cooler Master Storm Alcor Mouse
            # Retroflag SNES Classic USB Gamepad
            ('057e', '2009')   # Nintendo Co., Ltd. Pro Controller
        ]
        # Add rules
        with open(rtk.path_udev_rules, 'w', encoding='utf-8') as file:
            file.write('# NVidia Shield Controller\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="NVIDIA Corporation NVIDIA Controller v01.03", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# IPEGA\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="ipega Bluetooth Gamepad", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="ipega Bluetooth Gamepad   ", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Gamepad", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="GamePad", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# Neo-Geo X Arcade Stick\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="TOMMO NEOGEOX Arcade Stick", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# Mad Catz C.T.R.L.R gamepad\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Mad Catz C.T.R.L.R", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# Wiimote\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Nintendo Wii Remote", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1", ENV{ID_INPUT_KEY}="0"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Nintendo Wii Remote Classic Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1", ENV{ID_INPUT_KEY}="0"\n')
            file.write('# iPEGA 9055\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="ipega media gamepad controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="PG-9055", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# OUYA gamepad\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="OUYA Game Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# Namco GunCon 2\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Namco GunCon 2", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1", ENV{ID_INPUT_MOUSE}="1"\n')
            file.write('# PS3 Gamepad\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="SHANWAN PS3 GamePad Motion Sensors", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Sony Interactive Entertainment Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Sony PLAYSTATION(R)3 Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*PLAYSTATION(R)3 Controller", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*PLAYSTATION(R)3Conteroller", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*PLAYSTATION(R)3Conteroller-PANHAI", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*PS(R) Gamepad", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*PS3 GamePad", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="Sony Interactive Entertainment Wireless Controller", ENV{ID_INPUT_JOYSTICK}="1"\n')
            file.write('# Disable PS3/PS4 pads motion sensors\n')
            file.write('SUBSYSTEM=="input", ATTRS{name}=="*Motion Sensors", RUN+="/bin/rm %E{DEVNAME}", ENV{ID_INPUT_JOYSTICK}=""\n')
            file.write('# Device Blacklist\n')
            for vendor, product in dev_blacklist:
                file.write('SUBSYSTEM=="input", ATTRS{idVendor}=="%s", ATTRS{idProduct}=="%s", ENV{ID_INPUT_JOYSTICK}=="?*", ENV{ID_INPUT_JOYSTICK}=""\n' % (vendor, product))
                file.write('SUBSYSTEM=="input", ATTRS{idVendor}=="%s", ATTRS{idProduct}=="%s", KERNEL=="js[0-9]*", RUN+="/bin/rm %%E{DEVNAME}", ENV{ID_INPUT_JOYSTICK}=""\n' % (vendor, product))
        # Reload the rules
        cmd('udevadm control --reload && udevadm trigger')

def enable_audio_jack():
    jack = '#dtoverlay=audremap,pins_18_19'
    gpio = 'dtoverlay=audremap,pins_18_19'
    chg_boot_param(gpio,jack)

def disable_audio_jack():
    jack = '#dtoverlay=audremap,pins_18_19'
    gpio = 'dtoverlay=audremap,pins_18_19'
    chg_boot_param(jack,gpio)

def enable_overclock():
    # Increase arm_freq in 100Mhz (up to 2100) steps and +1 over_voltage steps also
    # gpu_freq max is 750 and base is 500
    # dvfs=3 does automatic over_voltage
    oc1ko = '#arm_freq=2000'
    oc1ok = 'arm_freq=2000'
    oc2ko = '#gpu_freq=700'
    oc2ok = 'gpu_freq=700'
    oc3ko = '#dvfs=3'
    oc3ok = 'dvfs=3'
    chg_boot_param(oc1ko,oc1ok)
    chg_boot_param(oc2ko,oc2ok)
    chg_boot_param(oc3ko,oc3ok)

def disable_overclock():
    oc1ko = '#arm_freq=2000'
    oc1ok = 'arm_freq=2000'
    oc2ko = '#gpu_freq=700'
    oc2ok = 'gpu_freq=700'
    oc3ko = '#dvfs=3'
    oc3ok = 'dvfs=3'
    chg_boot_param(oc1ok,oc1ko)
    chg_boot_param(oc2ok,oc2ko)
    chg_boot_param(oc3ok,oc3ko)

def init_fan():
    if rtk.cfg_fan == 'off':
        disable_fan()

def enable_fan():
    cmd('systemctl start argon-btn-fan.service')

def disable_fan():
    cmd('systemctl stop argon-btn-fan.service')
    try:
        bus = smbus.SMBus(1)
        bus.write_byte(0x1a,0x00)
    except:
        pass

''' Data '''

## System Utils

def get_system_index(system):
    add_index = 0
    index = 0
    if is_tate():
        if 'kodi' in cglobals.system_names_tate:
            add_index += 1
        if 'favorites' in cglobals.system_names_tate:
            add_index += 1
        if 'recents' in cglobals.system_names_tate:
            add_index += 1
        index = cglobals.system_names_tate.index(system)
        new_index = index - add_index
        rtk.logging.info('Getting system %s. Real index: %d, Virtual index: %d (%d)', system, index, new_index, add_index)
        return new_index
    else:
        if 'kodi' in cglobals.system_names:
            add_index += 1
        if 'favorites' in cglobals.system_names:
            add_index += 1
        if 'recents' in cglobals.system_names:
            add_index += 1
        index = cglobals.system_names.index(system)
        new_index = index - add_index
        rtk.logging.info('Getting system %s. Real index: %d, Virtual index: %d (%d)', system, index, new_index, add_index)
        return new_index

def get_system_short_names():
    if is_tate():
        return cglobals.system_names_tate
    else:
        return cglobals.system_names

def get_system_short_name(index):
    if is_tate():
        return cglobals.system_names_tate[index]
    else:
        return cglobals.system_names[index]

def get_system_full_names():
    if is_tate():
        systems = cglobals.systems_tate
    else:
        systems = cglobals.systems
    names = []
    for system in systems:
        name = system["Name"]
        if name == 'favorites':
            name = '<heart> ' + rtk.get_translation(name)
        elif name == 'lightgun':
            name = '<lightgun> ' + rtk.get_translation(name)
        elif name == 'kodi':
            name = '<tv> ' + rtk.get_translation(name)
        elif name == 'recents':
            name = rtk.get_translation(name)
        names.append(name)
    return names

def get_system_full_name(short_name, break_name=False):
    for system in cglobals.systems:
        if system['System'] == short_name:
            name = system['Name']
            break
    else:
        name = system
    if break_name:
        if not '(' in name:
            name = name.split("/")[0]
    if is_tate():
        name = name.split(" ")[0]
    return name

def get_system_info(index):
    if is_tate():
        developer = rtk.get_translation(name=cglobals.systems_tate[index]["Developer"])
        release = cglobals.systems_tate[index]["Release"]
        info = developer + ',' + release
    else:
        developer = rtk.get_translation(name=cglobals.systems[index]["Developer"])
        release = cglobals.systems[index]["Release"]
        info = developer + ',' + release
    return info

def _infer_recent_system(path, core_name, core_path):
    text = (path + ' ' + core_name + ' ' + core_path).lower()
    if 'mame' in text or 'fbneo' in text or 'finalburn' in text or '/arcade/' in text:
        return 'arcade'
    if 'flycast' in text or 'dreamcast' in text or '/dc/' in text:
        return 'dreamcast'
    if 'bsnes' in text or 'snes9x' in text or 'super nintendo' in text or '/snes/' in text:
        return 'snes'
    if 'genesis' in text or 'mega drive' in text:
        if 'sg-1000' in text:
            return 'sg1000'
        if 'master system' in text:
            return 'mastersystem'
        if 'mega-cd' in text or 'sega cd' in text:
            return 'segacd'
        return 'megadrive'
    if 'geolith' in text or 'neo geo' in text:
        return 'neogeo'
    if 'swanstation' in text or 'playstation' in text:
        return 'psx'
    return 'arcade'

def _all_loaded_games():
    games = []
    for group in cglobals.games:
        games.extend(group)
    return games

def load_recent_history(limit=25):
    history_file = '/storage/playlists/builtin/content_history.lpl'
    cglobals.recents = []
    if not os.path.isfile(history_file):
        return
    try:
        with open(history_file, encoding='utf-8') as file:
            items = json.load(file).get('items', [])
    except Exception as error:
        rtk.logging.error('Error loading recents: %s', error)
        return
    all_games = _all_loaded_games()
    by_path = {game.get('File', ''): game for game in all_games}
    by_basename = {}
    for game in all_games:
        by_basename.setdefault(os.path.basename(game.get('File', '')).lower(), game)
    seen = set()
    for item in items:
        path = item.get('path', '')
        if not path or path in seen:
            continue
        seen.add(path)
        game = by_path.get(path) or by_basename.get(os.path.basename(path).lower())
        if game:
            recent = game.copy()
        elif os.path.isfile(path):
            name = item.get('label') or os.path.splitext(os.path.basename(path))[0]
            system = _infer_recent_system(path, item.get('core_name', ''), item.get('core_path', ''))
            recent = {
                'Id':'',
                'Hash':'',
                'System':system,
                'Subsystem':system,
                'File':path,
                'Name':name,
                'Genre':'',
                'Developer':'?',
                'Year':'?',
                'Players':'?'
            }
        else:
            continue
        cglobals.recents.append(recent)
        if len(cglobals.recents) >= limit:
            break

def gen_game_files(dats_path=None):
    try:
        if dats_path:
            path = dats_path
        else:
            path = cglobals.mount_point + '/dats'
        path_games = path + '/games.dat'
        path_fav = path + '/favorites.dat'
        path_fav_tate = path + '/favorites_tate.dat'
        fieldnames = ['Id','Hash','File','System','Subsystem','Name','Genre','Developer','Year','Players']
        if not os.path.isfile(path_games):
            with open(path_games, 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
                writer.writeheader()
        if not os.path.isfile(path_fav):
            with open(path_fav, 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
                writer.writeheader()
        if not os.path.isfile(path_fav_tate):
            with open(path_fav_tate, 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
                writer.writeheader()
        return True
    except Exception as error:
        errot_txt = 'Error creating folders: ' + str(error)
        rtk.logging.error(errot_txt)
        rtk.error_msg.display(title='error_title',text=errot_txt)
        return False

## Games Utils

def get_games(system):
    if is_tate():
        if system == 'favorites':
            return get_favorites()
        elif system == 'recents':
            load_recent_history()
            return cglobals.recents
        else:
            return cglobals.games_tate
    else:
        if system == 'favorites':
            return get_favorites()
        elif system == 'recents':
            load_recent_history()
            return cglobals.recents
        else:
            system_index = get_system_index(system)
            return cglobals.games[system_index]

def has_games():
    if is_tate():
        return len(cglobals.system_names_tate) > 1 and cglobals.system_names_tate[0] != 'none'
    else:
        return len(cglobals.system_names) > 1 and cglobals.system_names[0] != 'none'

def load_tate_db():
    cglobals.tate_games_db = set(line.strip() for line in open(rtk.path_rgbpi_data + '/tate_games.dat'))

def load_bios_db():
    cglobals.bios_db = set(line.strip() for line in open(rtk.path_rgbpi_data + '/bios.dat'))

## Autoplay

def load_auto_play():
    auto_play = rtk.path_rgbpi_data + '/autoplay.dat'
    if os.path.isfile(auto_play):
        with open(auto_play, encoding='utf-8') as file:
            autoplay_info = file.readline().replace('\n','')
            if autoplay_info:
                autoplay_info = autoplay_info.split('|')
                system = autoplay_info[0]
                sub_system = autoplay_info[1]
                game_path = autoplay_info[2]
                if check_rom_path(game_path):
                    cglobals.autoplay['do_launch'] = True
                    cglobals.autoplay['system']    = system
                    cglobals.autoplay['sub_system']= sub_system
                    cglobals.autoplay['game_path'] = game_path

## Favorite Utils

def get_favorites():
    if is_tate():
        return cglobals.favorites_tate
    else:
        return cglobals.favorites

def load_favorites():
    path_favs = cglobals.mount_point + '/dats/favorites.dat'
    path_favs_tate = cglobals.mount_point + '/dats/favorites_tate.dat'
    cglobals.favorites = []
    cglobals.favorites_tate = []
    if os.path.isfile(path_favs):
        with open(path_favs, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in reader:
                full_path = cglobals.mount_point + row['File']
                if check_rom_path(full_path):
                    row['File'] = full_path
                    cglobals.favorites.append(row)
    if os.path.isfile(path_favs_tate):
        with open(path_favs_tate, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in reader:
                full_path = cglobals.mount_point + row['File']
                if check_rom_path(full_path):
                    row['File'] = full_path
                    cglobals.favorites_tate.append(row)

def has_favs():
    if is_tate():
        if cglobals.favorites_tate:
            return True
        else:
            return False
    else:
        if cglobals.favorites:
            return True
        else:
            return False

def write_favorites():
    path_favs = cglobals.mount_point + '/dats/favorites.dat'
    path_favs_tate = cglobals.mount_point + '/dats/favorites_tate.dat'
    # Remove unit path
    favs = []
    favs_tate = []
    for fav in cglobals.favorites:
        rtk.logging.info('wrt: 1 fav %s',fav['File'])
        temp = fav.copy()
        temp['File'] = temp['File'].replace(cglobals.mount_point, '')
        favs.append(temp)
        rtk.logging.info('wrt: 2 fav %s',fav['File'])
    for fav in cglobals.favorites_tate:
        temp = fav.copy()
        temp['File'] = temp['File'].replace(cglobals.mount_point, '')
        favs_tate.append(temp)
    # Write files
    with open(path_favs, 'w', encoding='utf-8') as csvfile:
        fieldnames = ['Id','Hash','System','Subsystem','File','Name','Genre','Developer','Year','Players']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(favs)
    with open(path_favs_tate, 'w', encoding='utf-8') as csvfile:
        fieldnames = ['Id','Hash','System','Subsystem','File','Name','Genre','Developer','Year','Players']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(favs_tate)

def update_sys_favs():
    system_fav = {'System':'favorites','Name':'favorites','Release':'19XX-200X','Developer':'various','Formats':'','Subsystems':''}
    # Systems Tate
    if cglobals.games_tate:
        if has_favs() and 'favorites' not in cglobals.system_names_tate:
            cglobals.system_names_tate.insert(0,'favorites')
            cglobals.systems_tate.insert(0,system_fav)
        elif not has_favs() and 'favorites' in cglobals.system_names_tate:
            del cglobals.system_names_tate[0]
            del cglobals.systems_tate[0]
    else:
        if 'favorites' in cglobals.system_names_tate:
            del cglobals.system_names_tate[0]
            del cglobals.systems_tate[0]
    # Systems Yoko
    if cglobals.games:
        if has_favs() and 'favorites' not in cglobals.system_names:
            cglobals.system_names.insert(0,'favorites')
            cglobals.systems.insert(0,system_fav)
        elif not has_favs() and 'favorites' in cglobals.system_names:
            del cglobals.system_names[0]
            del cglobals.systems[0]
    else:
        if 'favorites' in cglobals.system_names:
            del cglobals.system_names[0]
            del cglobals.systems[0]

def update_sys_recents():
    system_recent = {'System':'recents','Name':'recents','Release':'Recent','Developer':'Lakka','Formats':'','Subsystems':''}
    if rtk.cfg_show_recents == 'on':
        if not is_tate():
            if 'recents' not in cglobals.system_names:
                index = 0
                if 'favorites' in cglobals.system_names:
                    index += 1
                if 'kodi' in cglobals.system_names:
                    index += 1
                cglobals.system_names.insert(index,'recents')
                cglobals.systems.insert(index,system_recent)
        else:
            if 'recents' not in cglobals.system_names_tate:
                index = 0
                if 'favorites' in cglobals.system_names_tate:
                    index += 1
                cglobals.system_names_tate.insert(index,'recents')
                cglobals.systems_tate.insert(index,system_recent)
    else:
        if 'recents' in cglobals.system_names:
            index = cglobals.system_names.index('recents')
            del cglobals.system_names[index]
            del cglobals.systems[index]
        if 'recents' in cglobals.system_names_tate:
            index = cglobals.system_names_tate.index('recents')
            del cglobals.system_names_tate[index]
            del cglobals.systems_tate[index]

def gen_sys_kodi():
    if rtk.cfg_show_kodi == 'on':
        # Systems Yoko
        if not is_tate():
            system_kodi = {'System':'kodi','Name':'kodi','Release':'2003','Developer':'Kodi Team','Formats':'','Subsystems':''}
            if 'kodi' not in cglobals.system_names:
                index = 0
                if 'favorites' in cglobals.system_names:
                    index += 1
                cglobals.system_names.insert(index,'kodi')
                cglobals.systems.insert(index,system_kodi)

## Load ROMs

def bck_dat_files():
    games = cglobals.mount_point + '/dats/games.dat'
    favs = cglobals.mount_point + '/dats/favorites.dat'
    favs_tate = cglobals.mount_point + '/dats/favorites_tate.dat'
    cmd('cp -f ' + games + ' ' + cglobals.mount_point + '/dats/games.bck')
    cmd('cp -f ' + favs + ' ' + cglobals.mount_point + '/dats/favorites.bck')
    cmd('cp -f ' + favs_tate + ' ' + cglobals.mount_point + '/dats/favorites_tate.bck')

def restore_dat_files():
    games = cglobals.mount_point + '/dats/games.bck'
    favs = cglobals.mount_point + '/dats/favorites.bck'
    favs_tate = cglobals.mount_point + '/dats/favorites_tate.bck'
    cmd('cp -f ' + games + ' ' + cglobals.mount_point + '/dats/games.dat')
    cmd('cp -f ' + favs + ' ' + cglobals.mount_point + '/dats/favorites.dat')
    cmd('cp -f ' + favs_tate + ' ' + cglobals.mount_point + '/dats/favorites_tate.dat')

def is_game_tate(game_path):
    game_name = game_path.split('/')[-1]
    if game_name in cglobals.tate_games_db:
        return True
    else:
        return False

def load_roms():
    cglobals.system_names = []
    cglobals.system_names_tate = []
    cglobals.systems = []
    cglobals.systems_tate = []
    cglobals.games = []
    cglobals.games_tate = []
    try:
        load_games()
    except:
        restore_dat_files()
        load_games()
    load_systems()

def load_games():
    # Load Games
    last_system = None
    with open(cglobals.mount_point + '/dats/games.dat', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        games = []
        for row in reader:
            system = row["System"]
            game_path = cglobals.mount_point + row['File']
            if check_rom_path(game_path):
                game_name = game_path.split('/')[-1]
                # Add System
                if last_system != system:
                    # Add all system game list
                    if games:
                        cglobals.games.append(games)
                    games = []
                    last_system = system
                    cglobals.system_names.append(system)
                # Add Game
                row['File'] = cglobals.mount_point + row['File']
                games.append(row)
                # Add Tate Game
                if system == 'arcade' and game_name in cglobals.tate_games_db:
                    cglobals.games_tate.append(row)
        # Add last system
        if games:
            cglobals.games.append(games)

def load_systems():
    now = datetime.datetime.now()
    no_system = {'System':'none','Name':'none','Release':str(now.year),'Developer':'RGB-Pi','Formats':'none','Subsystems':'none'}
    # Load Systems
    with open(rtk.path_rgbpi_data + '/systems.dat', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            system = row["System"]
            if system in cglobals.system_names:
                cglobals.systems.append(row) 
    if not cglobals.systems:
        cglobals.system_names.append('none')
        cglobals.systems.append(no_system)
    # Get Tate Systems
    if cglobals.games_tate:
        # Systems Short
        cglobals.system_names_tate.append('arcade')
        # Systems Full
        for system in cglobals.systems:
            if system["System"] == 'arcade':
                cglobals.systems_tate.append(system)
                break
    else:
        cglobals.system_names_tate.append('none')
        cglobals.systems_tate.append(no_system)

## Scan & Scrap Utils

def gen_scrap_info_img():
    # YOKO
    path = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/info.bmp'
    surface = pygame.Surface((256, 192)).convert()
    surface.fill(rtk.scrap_bg_color)
    pygame.draw.rect(surface, rtk.scrap_border_color, (0,0,256,192), 1)
    pygame.image.save(surface, path)
    # TATE
    path = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/info_tate.bmp'
    surface = pygame.Surface((192, 256)).convert()
    surface.fill(rtk.scrap_bg_color)
    pygame.draw.rect(surface, rtk.scrap_border_color, (0,0,192,256), 1)
    pygame.image.save(surface, path)

def scan_scrap_games_from_ui():
    scan_games(do_scrap=True)
    scan_from_ui_common()
    cglobals.scr_saver_view.gen_screen_saver(is_active=False,is_refresh=True)
    goto_view('last_view')
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def scan_from_ui_common():
    rtk.logging.info('Loading favs...')
    load_favorites()
    rtk.logging.info('Loading games...')
    load_roms()
    rtk.logging.info('Updating system kodi...')
    gen_sys_kodi()
    rtk.logging.info('Updating system favs...')
    update_sys_favs()
    rtk.logging.info('Updating system recents...')
    update_sys_recents()
    rtk.logging.info('Refreshing system view...')
    cglobals.systems_view.refresh_view()
    rtk.logging.info('Refreshing game views...')
    refresh_all_game_views(reload_game_data=True)
    if rtk.logger_root_level == 'DEBUG':
        garbage_stats()

def scan_games(do_scrap=True):
    try:
        path_games = cglobals.mount_point + '/dats/games.dat'
        path_fav = cglobals.mount_point + '/dats/favorites.dat'
        path_fav_tate = cglobals.mount_point + '/dats/favorites_tate.dat'
        systems_file = rtk.path_rgbpi_data + '/systems.dat'
        scanned_games = []
        # Scan Games
        with open(systems_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in reader:
                system = row["System"]
                formats = row["Formats"]
                subsystems = row["Subsystems"].split('|')
                search_paths = [
                    cglobals.mount_point + '/roms/' + system,
                    cglobals.mount_point + '/' + system,
                ]
                seen_paths = set()
                for search_path in search_paths:
                    if not os.path.isdir(search_path):
                        continue
                    for entry in scantree(search_path):
                        if entry.path in seen_paths:
                            continue
                        seen_paths.add(entry.path)
                        subsystem = get_subsystem(path=entry.path, system=system, subsystems=subsystems)
                        is_supported_format = entry.name.lower().endswith(tuple(formats.split('|')))
                        is_hidden = entry.name.startswith('.')
                        is_special = entry.name.startswith('(')
                        is_part = (
                            re.findall("\(disc.*[0-9].*\)", entry.name.lower())
                            #or re.findall("\(disk.*[0-9].*\)", entry.name.lower())
                            #or re.findall("\(tape.*[0-9].*\)", entry.name.lower())
                            #or re.findall("\(side.*[a-b].*\)", entry.name.lower())
                        )
                        short_path = entry.path.replace(cglobals.mount_point,'')
                        if subsystem and is_supported_format and not is_hidden and not is_special and \
                                entry.name not in cglobals.bios_db and entry.name not in cglobals.scan_black_list and \
                                not is_part:
                            game = {'Id':'','Hash':'','File':short_path,'System':system,'Subsystem':subsystem,'Name':'','Genre':'','Developer':'','Year':'','Players':''}
                            scanned_games.append(game)
        # Prepare favorites
        short_favs = []
        short_favs_tate = []
        for row in cglobals.favorites:
            row['File'] = row['File'].replace(cglobals.mount_point,'')
            short_favs.append(row)
        for row in cglobals.favorites_tate:
            row['File'] = row['File'].replace(cglobals.mount_point,'')
            short_favs_tate.append(row)
        # Scrap Games
        scraped_games = scrap_games(game_list=scanned_games,do_scrap=do_scrap)
        scraped_favs = scrap_games(game_list=short_favs,do_scrap=do_scrap)
        scraped_favs_tate = scrap_games(game_list=short_favs_tate,do_scrap=do_scrap)
        scraped_games = dedupe_games(scraped_games)
        scraped_favs = dedupe_games(scraped_favs)
        scraped_favs_tate = dedupe_games(scraped_favs_tate)
        # Write to file
        write_games(games=scraped_games, path_file=path_games)
        write_games(games=scraped_favs, path_file=path_fav)
        write_games(games=scraped_favs_tate, path_file=path_fav_tate)
    except Exception as error:
        rtk.error_msg.display(title='error_title',text='Error scanning roms: ' + str(error))
        rtk.logging.error('Error scanning roms (data_source = %s): %s', rtk.cfg_data_source, error)
        cmd('ls -R '+ cglobals.mount_point + '/roms > /storage/rgbpi/logs/rom_list.log')

def get_subsystem(path, system, subsystems):
    subsystem = None
    if subsystems == [""]:
        subsystems = None
    if not subsystems:
        subsystem = system
    elif subsystems:
        for s in subsystems:
            if s in path:
                subsystem = s
    if subsystems and not subsystem:
        # User has created non supported custom folder
        subsystem = None
    return subsystem

def write_games(games, path_file):
    # Save game list to file
    with open(path_file, 'w', encoding='utf-8') as csvfile:
        fieldnames = ['Id','Hash','System','Subsystem','File','Name','Genre','Developer','Year','Players']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(games)

def _rom_preference_score(game):
    path = game.get('File', '').lower()
    score = 0
    for token, value in (
        ('(usa', 50),
        ('(world', 45),
        ('(europe', 40),
        ('(japan', 10),
    ):
        if token in path:
            score += value
    for token in ('(beta', '(proto', '(sample', '(demo', '(pirate', '(unl', '(hack', '(bad'):
        if token in path:
            score -= 25
    return score

def dedupe_games(games):
    selected = {}
    order = []
    for game in games:
        name = game.get('Name') or os.path.splitext(os.path.basename(game.get('File', '')))[0]
        key = (game.get('System', ''), game.get('Subsystem', ''), normalize(name))
        if key not in selected:
            selected[key] = game
            order.append(key)
            continue
        if _rom_preference_score(game) > _rom_preference_score(selected[key]):
            selected[key] = game
    return [selected[key] for key in order]

def normalize(name):
    game_name = name.upper()
    game_name = game_name.split('(')[0]
    game_name = game_name.replace(' ','')
    game_name = game_name.replace("'",'')
    game_name = game_name.replace('.','')
    game_name = game_name.replace(':','')
    game_name = game_name.replace('-','')
    game_name = game_name.replace('+','')
    game_name = game_name.replace('/','')
    game_name = game_name.replace('~','')
    game_name = game_name.replace('_','')
    game_name = game_name.replace('&','')
    game_name = game_name.replace('#','')
    game_name = game_name.replace('!','')
    game_name = game_name.replace(',','')
    game_name = game_name.replace('%','')
    game_name = game_name.replace('{','')
    game_name = game_name.replace('}','')
    game_name = game_name.replace('$','')
    return game_name

def scrap_games(game_list,do_scrap):
    scraped_games = []
    #if not cglobals.scraper_db:
    #    load_scraper_db()
    for game in game_list:
        scraped_game = game
        if do_scrap:
            rtk.logging.info('System = %s, Subsystem = %s',game['System'],game['Subsystem'])
            system = game['System']
            if system == 'neogeo':
                system = 'arcade'
            elif system == 'lightgun':
                system = game['Subsystem']
                if system == 'fbneo' or system == 'mame' or system == 'naomi':
                    system = 'arcade'
            file_name = game['File'].split('/')[-1]
            file_name = file_name.rsplit('.',1)[0]
            file_name = normalize(file_name)
            hash = get_hash(system + file_name)
            game_info = cglobals.scraper_db.get(hash,None)
        else:
            game_info = None
        if game_info:
            scraped_game['Id'] = game_info['ID']
            scraped_game['Hash'] = game_info['HASH']
            game_file = scraped_game['File'].lower()
            if 'usa' in game_file and rtk.cfg_scrap_region == 'usa':
                scraped_game['Name'] = game_info['NAME_USA']
            elif 'europe' in game_file and rtk.cfg_scrap_region == 'eur':
                scraped_game['Name'] = game_info['NAME_EUR']
            elif 'japan' in game_file and rtk.cfg_scrap_region == 'jap':
                scraped_game['Name'] = game_info['NAME_JAP']
            elif 'usa' in game_file:
                scraped_game['Name'] = game_info['NAME_USA']
            elif 'europe' in game_file:
                scraped_game['Name'] = game_info['NAME_EUR']
            elif 'japan' in game_file:
                scraped_game['Name'] = game_info['NAME_JAP']
            else:
                scraped_game['Name'] = game_info['NAME_' + rtk.cfg_scrap_region.upper()]
            scraped_game['Genre'] = game_info['GENRE']
            scraped_game['Developer'] = game_info['DEVELOPER']
            scraped_game['Year'] = game_info['YEAR']
            scraped_game['Players'] = game_info['PLAYERS']
        else:
            game_name = game['File'].split('/')[-1]
            game_name = game_name.rsplit('.',1)[0]
            game_name = game_name.strip()
            scraped_game['Id'] = ''
            scraped_game['Hash'] = ''
            scraped_game['Name'] = game_name
            scraped_game['Genre'] = '?'
            scraped_game['Developer'] = '?'
            scraped_game['Year'] = '19XX'
            scraped_game['Players'] = '1'
        scraped_games.append(scraped_game)
    return scraped_games

def load_scraper_db():
    with open(rtk.path_rgbpi_scraper + '/scraper.dat', 'r', encoding='utf-8') as csvfile:
        games = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for game in games:
            id = game['ID']
            hash = game['HASH']
            name_usa = game['NAME_USA']
            name_eur = game['NAME_EUR']
            name_jap = game['NAME_JAP']
            genre = game['GENRE']
            developer = game['DEVELOPER']
            year = game['YEAR']
            players = game['PLAYERS']
            game_info = {'ID':id,'HASH':hash,'NAME_USA':name_usa,'NAME_EUR':name_eur,'NAME_JAP':name_jap,'GENRE':genre,'DEVELOPER':developer,'YEAR':year,'PLAYERS':players}
            cglobals.scraper_db[hash] = game_info
            cglobals.scraper_db_2[id] = game_info

## Themes

def load_themes():
    theme_path = rtk.path_rgbpi_themes
    themes = [f.split("/")[-1] for f in glob.glob(theme_path + "/**", recursive=False)]
    themes.sort()
    cglobals.themes = themes

## Sound

def load_music():
    # Get music playlists
    cglobals.music_files = []
    sound_formats = ".mp3|.ogg|.xm|.mod|.it"
    # Scan system playlists
    cglobals.playlist_folders = [f.split("/")[-1] for f in glob.glob(rtk.path_rgbpi_music + "/**", recursive=False)]
    for playlist in cglobals.playlist_folders:
        search_path = rtk.path_rgbpi_music + '/' + playlist
        for entry in sorted(os.scandir(search_path), key=lambda e: e.name):
            if (entry.is_file):
                is_supported_format = entry.name.lower().endswith(tuple(sound_formats.split('|')))
                is_hidden = entry.name.startswith('.')
                is_special = entry.name.startswith('(')
                if is_supported_format and not is_hidden and not is_special:
                    music = {'Playlist':playlist,'File':entry.path}
                    cglobals.music_files.append(music)
    # Scan theme playlist
    playlist = rtk.cfg_theme
    cglobals.playlist_folders.append(playlist)
    search_path = rtk.path_rgbpi_themes + '/' + rtk.cfg_theme + '/sounds/music'
    for entry in sorted(os.scandir(search_path), key=lambda e: e.name):
        if (entry.is_file):
            is_supported_format = entry.name.lower().endswith(tuple(sound_formats.split('|')))
            is_hidden = entry.name.startswith('.')
            is_special = entry.name.startswith('(')
            if is_supported_format and not is_hidden and not is_special:
                music = {'Playlist':playlist,'File':entry.path}
                cglobals.music_files.append(music)
    # Add mix playlist and check that current selected album was not deleted
    if cglobals.playlist_folders:
        cglobals.playlist_folders.sort()
        cglobals.playlist_folders.insert(0,'mix')
        if rtk.cfg_playlist not in cglobals.playlist_folders:
            rtk.cfg_playlist = 'mix'    

def get_playlists():
    return cglobals.playlist_folders

def get_songs(name):
    playlist = []
    if name == 'mix':
        for music in cglobals.music_files:
            playlist.append(music['File'])
        random.shuffle(playlist)
    else:
        for music in cglobals.music_files:
            if music['Playlist'] == name:
                playlist.append(music['File'])
        random.shuffle(playlist)
    return playlist

def load_eq_presets():
    # Scan EQ Presets
    for entry in sorted(os.scandir(rtk.path_rgbpi_eq), key=lambda e: e.name):
        if (entry.is_file):
            is_supported_format = entry.name.lower().endswith('.eq')
            is_hidden = entry.name.startswith('.')
            is_special = entry.name.startswith('(')
            if is_supported_format and not is_hidden and not is_special:
                preset = entry.name.split('.')[0]
                cglobals.presets[preset] = None
    # Add selected preset if the same was deleted to prevent crashes
    if rtk.cfg_preset not in cglobals.presets:
        rtk.cfg_preset = 'Flat'
    # Set values
    for preset in cglobals.presets:
        eq_file = rtk.path_rgbpi_eq + '/' + preset + ".eq"
        config = configparser.RawConfigParser()
        config.read(eq_file)
        # Get freq values
        eq_31 = config.get('Freqs', '31hz')
        eq_63 = config.get('Freqs', '63hz')
        eq_125 = config.get('Freqs', '125hz')
        eq_250 = config.get('Freqs', '250hz')
        eq_500 = config.get('Freqs', '500hz')
        eq_1 = config.get('Freqs', '1khz')
        eq_2 = config.get('Freqs', '2khz')
        eq_4 = config.get('Freqs', '4khz')
        eq_8 = config.get('Freqs', '8khz')
        eq_16 = config.get('Freqs', '16khz')
        volume = config.get('Clipping', 'volume')
        eq = [eq_31,eq_63,eq_125,eq_250,eq_500,eq_1,eq_2,eq_4,eq_8,eq_16,volume]
        cglobals.presets[preset] = eq

def get_presets():
    presets = []
    for preset in cglobals.presets:
        presets.append(preset)
    presets.sort()
    presets.remove('Flat')
    presets.insert(0,'Flat')
    return presets

def save_preset():
    preset = rtk.cfg_preset
    eq_file = rtk.path_rgbpi_eq + '/' + preset + ".eq"
    # Create in memory new preset configuration
    config = configparser.RawConfigParser()
    config.add_section('Freqs')
    config.set('Freqs', '31hz', rtk.cfg_31hz)
    config.set('Freqs', '63hz', rtk.cfg_63hz)
    config.set('Freqs', '125hz', rtk.cfg_125hz)
    config.set('Freqs', '250hz', rtk.cfg_250hz)
    config.set('Freqs', '500hz', rtk.cfg_500hz)
    config.set('Freqs', '1khz', rtk.cfg_1khz)
    config.set('Freqs', '2khz', rtk.cfg_2khz)
    config.set('Freqs', '4khz', rtk.cfg_4khz)
    config.set('Freqs', '8khz', rtk.cfg_8khz)
    config.set('Freqs', '16khz', rtk.cfg_16khz)
    config.add_section('Clipping')
    config.set('Clipping', 'volume', rtk.cfg_clipping)
    # Write configuration to preset file
    with open(eq_file, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

''' Input '''

def check_ips():
    if get_view_name() == 'sys_opt_network_view':
        cglobals.sys_opt_network_view.set_ips()

def check_joys():
    if not cglobals.is_in_task:
        num_joysticks = len(glob.glob('/dev/input/js*'))
        is_joy_cfg_view = get_view_name() == 'joy_cfg_view'
        is_lgun_cfg_view = get_view_name() == 'lgun_cfg_view'
        # Init all new joys
        if cglobals.num_joysticks != num_joysticks:
            rtk.popup_msg.display(text='loading')
            cglobals.num_joysticks = num_joysticks
            if is_joy_cfg_view:
                cglobals.joy_cfg_view.cancel_cfg()
            if is_lgun_cfg_view:
                cglobals.lgun_cfg_view.cancel_cfg()
            cglobals.input_mgr.init_joysticks()
            cglobals.input_mgr.init_lgun()
            cglobals.sys_opt_control_view.refresh_values()
            rtk.logging.debug('Number of joysticks: %s', cglobals.num_joysticks)
            rtk.popup_msg.hide()
        # Configure joys without mapping
        if not is_joy_cfg_view and cglobals.input_mgr.joy_cfg_queue:
            cglobals.joy_cfg_view.config_joy(index=cglobals.input_mgr.joy_cfg_queue[0])

def prettify_joy_name(joy_name):
    if 'JoyPi' in joy_name:
        joy_name = joy_name.replace('JoyPi','RGB-Pi')
    else:
        name = []
        [name.append(x) for x in joy_name.split() if x not in name]
        joy_name =  " ".join(name)
    return joy_name

def remove_amiga_remaps():
    tarjet_amiga_remaps = cglobals.mount_point + '/remaps/system/PUAE/PUAE.rmp'
    cmd('rm ' + tarjet_amiga_remaps)

def remove_neogeo_remaps():
    tarjet_neogeo_remaps = cglobals.mount_point + '/remaps/system/FinalBurn Neo/FinalBurn Neo.rmp'
    tarjet_neogeocd_remaps = cglobals.mount_point + '/remaps/system/NeoCD/NeoCD.rmp'
    cmd('rm "' + tarjet_neogeo_remaps + '"')
    cmd('rm ' + tarjet_neogeocd_remaps)

def copy_amiga_remaps():
    # Get source paths
    source_amiga_remaps = rtk.path_rgbpi_remaps + '/PUAE/Amiga_PUAE.rmp'
    source_amigacd_remaps = rtk.path_rgbpi_remaps + '/PUAE/AmigaCD32_PUAE.rmp'
    # Get tarjet paths
    tarjet_amiga_remaps = cglobals.mount_point + '/remaps/system/PUAE'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir ' + tarjet_amiga_remaps)
    # Clean remaps current amiga/amigacd remaps
    remove_amiga_remaps()
    # Copy remaps
    cmd('cp -fp ' + source_amiga_remaps + ' ' + tarjet_amiga_remaps + '/PUAE.rmp')
    cmd('cp -fp ' + source_amigacd_remaps + ' ' + tarjet_amiga_remaps + '/PUAE.rmp')

def copy_neogeo_remaps():
    # Get source paths
    source_neogeo_remaps = rtk.path_rgbpi_remaps + '/Neogeo/FinalBurn Neo.rmp'
    source_neogeocd_remaps = rtk.path_rgbpi_remaps + '/Neogeo/NeoCD.rmp'
    # Get tarjet paths
    tarjet_neogeo_remaps = cglobals.mount_point + '/remaps/system/FinalBurn Neo'
    tarjet_neogeocd_remaps = cglobals.mount_point + '/remaps/system/NeoCD'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir "' + tarjet_neogeo_remaps + '"')
    cmd('mkdir ' + tarjet_neogeocd_remaps)
    # Clean remaps current neogeo/neogeocd remaps
    remove_neogeo_remaps()
    # Copy remaps
    cmd('cp -fp "' + source_neogeo_remaps + '" "' + tarjet_neogeo_remaps + '"')
    cmd('cp -fp ' + source_neogeocd_remaps + ' ' + tarjet_neogeocd_remaps)

def copy_pc_remaps():
    # Get source paths
    source_remaps = rtk.path_rgbpi_remaps + '/DOSBox-pure/DOSBox-pure.rmp'
    # Get tarjet paths
    tarjet_remaps = cglobals.mount_point + '/remaps/system/DOSBox-pure'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir ' + tarjet_remaps)
    # Copy remaps
    cmd('cp -fp ' + source_remaps + ' ' + tarjet_remaps)

def copy_x68k_remaps():
    # Get source paths
    source_remaps = rtk.path_rgbpi_remaps + '/PX68K/PX68K.rmp'
    # Get tarjet paths
    tarjet_remaps = cglobals.mount_point + '/remaps/system/PX68K'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir ' + tarjet_remaps)
    # Copy remaps
    cmd('cp -fp ' + source_remaps + ' ' + tarjet_remaps)

def copy_pce_remaps():
    # Get source paths
    source_remaps = rtk.path_rgbpi_remaps + '/Beetle SuperGrafx/Beetle SuperGrafx.rmp'
    # Get tarjet paths
    tarjet_remaps = cglobals.mount_point + '/remaps/system/Beetle SuperGrafx'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir "' + tarjet_remaps + '"')
    # Copy remaps
    cmd('cp -fp "' + source_remaps + '" "' + tarjet_remaps + '"')

def copy_nes_remaps():
    # Get source paths
    source_remaps = rtk.path_rgbpi_remaps + '/FCEUmm/FCEUmm.rmp'
    # Get tarjet paths
    tarjet_remaps = cglobals.mount_point + '/remaps/system/FCEUmm'
    # Check folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir "' + tarjet_remaps + '"')
    # Copy remaps
    cmd('cp -fp "' + source_remaps + '" "' + tarjet_remaps + '"')

def copy_jamma_remaps():
    # Get paths
    rgbpi_fbneo_remaps     = rtk.path_rgbpi_remaps + '/FinalBurn Neo'
    rgbpi_mame_remaps      = rtk.path_rgbpi_remaps + '/MAME'
    rgbpi_naomi_remaps     = rtk.path_rgbpi_remaps + '/Flycast'
    retroarch_fbneo_remaps = cglobals.mount_point + '/remaps/system/FinalBurn Neo'
    retroarch_mame_remaps  = cglobals.mount_point + '/remaps/system/MAME'
    retroarch_naomi_remaps = cglobals.mount_point + '/remaps/system/Flycast'
    # Create all requiered folders
    cmd('mkdir ' + cglobals.mount_point + '/remaps/system')
    cmd('mkdir "' + retroarch_fbneo_remaps + '"')
    cmd('mkdir ' + retroarch_mame_remaps)
    cmd('mkdir ' + retroarch_naomi_remaps)
    # Copy custom JAMMA remaps
    cmd('cp -n "' + rgbpi_fbneo_remaps + '"/* "' + retroarch_fbneo_remaps + '"')
    cmd('cp -n "' + rgbpi_mame_remaps + '"/* "' + retroarch_mame_remaps + '"')
    cmd('cp -n "' + rgbpi_naomi_remaps + '"/* "' + retroarch_naomi_remaps + '"')

def gen_retroarch_autoconf(enable_free_play=False):

    for joy_id, config in cglobals.input_mgr.joy_configs.items():

        ''' Get config data '''

        joy_name = config.get('name')
        vendor_id = config.get('vid')
        product_id = config.get('pid')
        style = config.get('style')
        up_btn = config.get('D-Pad Up')
        down_btn = config.get('D-Pad Down')
        left_btn = config.get('D-Pad Left')
        right_btn = config.get('D-Pad Right')
        a_btn = config.get('A')
        b_btn = config.get('B')
        x_btn = config.get('X')
        y_btn = config.get('Y')
        select_btn = config.get('Select')
        start_btn = config.get('Start')
        hotkey_btn = config.get('Hotkey')
        l1_btn = config.get('L1/LB')
        r1_btn = config.get('R1/RB')
        l2_btn = config.get('L2/LT Btn')
        r2_btn = config.get('R2/RT Btn')
        l2_axis = config.get('L2/LT Axis')
        r2_axis = config.get('R2/RT Axis')
        left_analog_up = config.get('Left Analog Up')
        left_analog_left = config.get('Left Analog Left')
        right_analog_up = config.get('Right Analog Up')
        right_analog_left = config.get('Right Analog Left')

        ''' Write Retroarch autoconfig file '''

        file_name = rtk.path_autoconfig + '/' + joy_id.replace(' ', '_').replace('/', '_') + '.cfg'
        with open(file_name, 'w', encoding='utf-8') as file:

            ''' Input attributes '''

            file.write('input_device = "' + joy_name + '"\n')
            file.write('input_device_display_name = "' + prettify_joy_name(joy_name) + '"\n')
            file.write('input_vendor_id = "' + vendor_id + '"\n')
            file.write('input_product_id = "' + product_id + '"\n')
            
            if joy_name == 'Namco GunCon 2':
                file.write('input_btn_style = "snes"\n')
                # Joystick
                file.write('input_up_btn = "h0up"\n')
                file.write('input_down_btn = "h0down"\n')
                file.write('input_left_btn = "h0left"\n')
                file.write('input_right_btn = "h0right"\n')
                file.write('input_a_btn = "3"\n')
                file.write('input_b_btn = "4"\n')
                file.write('input_x_btn = "5"\n')
                file.write('input_l2_btn = "nul"\n')
                file.write('input_r2_btn = "nul"\n')
                file.write('input_select_btn = "6"\n')
                file.write('input_start_btn = "7"\n')
                file.write('input_l_x_plus_btn = "h0right"\n')
                file.write('input_l_x_minus_btn = "h0left"\n')
                file.write('input_l_y_plus_btn = "h0down"\n')
                file.write('input_l_y_minus_btn = "h0up"\n')
                file.write('input_r_x_plus_btn = "h0right"\n')
                file.write('input_r_x_minus_btn = "h0left"\n')
                file.write('input_r_y_plus_btn = "h0down"\n')
                file.write('input_r_y_minus_btn = "h0up"\n')
                # LGun
                file.write('input_gun_trigger_mbtn = "1"\n')
                file.write('input_gun_select_btn = "6"\n')
                file.write('input_gun_start_btn = "7"\n')
                file.write('input_gun_dpad_up_btn = "h0up"\n')
                file.write('input_gun_dpad_down_btn = "h0down"\n')
                file.write('input_gun_dpad_left_btn = "h0left"\n')
                file.write('input_gun_dpad_right_btn = "h0right"\n')
                file.write('input_gun_aux_a_btn = "3"\n')
                file.write('input_gun_aux_b_btn = "4"\n')
                file.write('input_gun_aux_c_btn = "5"\n')
                file.write('input_gun_offscreen_shot_btn = "4"\n')
                file.write('ui_input_a_btn = "0"\n')
                file.write('ui_input_b_btn = "1"\n')
                file.write('ui_input_select_btn = "3"\n')
                file.write('ui_input_start_btn = "4"\n')
            else:
                file.write('input_btn_style = "' + style + '"\n')

                ''' Input mappings '''

                # Digital Pad
                up_btn_is_hat = up_btn[0] == 'is_hat' or joy_name == 'TOMMO NEOGEOX Arcade Stick' or joy_name == 'EXAR USB JOYSTICK PS3'
                if up_btn_is_hat:
                    file.write('input_up_btn = "h0up"\n')
                    file.write('input_down_btn = "h0down"\n')
                    file.write('input_left_btn = "h0left"\n')
                    file.write('input_right_btn = "h0right"\n')
                elif up_btn[0] == 'is_axis':
                    file.write('input_up_axis = "-' + str(up_btn[1]) + '"\n')
                    file.write('input_down_axis = "+' + str(down_btn[1]) + '"\n')
                    file.write('input_left_axis = "-' + str(left_btn[1]) + '"\n')
                    file.write('input_right_axis = "+' + str(right_btn[1]) + '"\n')
                elif up_btn[0] == 'is_button':
                    file.write('input_up_btn = "' + str(up_btn[1]) + '"\n')
                    file.write('input_down_btn = "' + str(down_btn[1]) + '"\n')
                    file.write('input_left_btn = "' + str(left_btn[1]) + '"\n')
                    file.write('input_right_btn = "' + str(right_btn[1]) + '"\n')
                # Buttons
                if a_btn and a_btn[1] != '':
                    file.write('input_a_btn = "' + str(a_btn[1]) + '"\n')
                if b_btn and b_btn[1] != '':
                    file.write('input_b_btn = "' + str(b_btn[1]) + '"\n')
                if x_btn and x_btn[1] != '':
                    file.write('input_x_btn = "' + str(x_btn[1]) + '"\n')
                if y_btn and y_btn[1] != '':
                    file.write('input_y_btn = "' + str(y_btn[1]) + '"\n')
                if l1_btn and l1_btn[1] != '':
                    file.write('input_l_btn = "' + str(l1_btn[1]) + '"\n')
                if r1_btn and r1_btn[1] != '':
                    file.write('input_r_btn = "' + str(r1_btn[1]) + '"\n')
                # Special Button + Axis
                if l2_btn and l2_btn[1] != '':
                    file.write('input_l2_btn = "' + str(l2_btn[1]) + '"\n')
                if l2_axis and l2_axis[1] != '':
                    file.write('input_l2_axis = "+' + str(l2_axis[1]) + '"\n')
                if r2_btn and r2_btn[1] != '':
                    file.write('input_r2_btn = "' + str(r2_btn[1]) + '"\n')
                if r2_axis and r2_axis[1] != '':
                    file.write('input_r2_axis = "+' + str(r2_axis[1]) + '"\n')
                # Enable freeplay
                if rtk.cfg_free_play == 'on' and enable_free_play:
                    if start_btn and start_btn[1] != '':
                        file.write('input_start_btn = "' + str(start_btn[1]) + '"\n')
                        file.write('input_select_btn = "' + str(start_btn[1]) + '"\n')
                else:
                    if start_btn and start_btn[1] != '':
                        file.write('input_start_btn = "' + str(start_btn[1]) + '"\n')
                    if select_btn and select_btn[1] != '':
                        file.write('input_select_btn = "' + str(select_btn[1]) + '"\n')
                # Analog Axes
                if left_analog_up and left_analog_up[1] != '':
                    file.write('input_l_y_minus_axis = "-' + str(left_analog_up[1]) + '"\n')
                    file.write('input_l_y_plus_axis = "+' + str(left_analog_up[1]) + '"\n')
                if left_analog_left and left_analog_left[1] != '':
                    file.write('input_l_x_minus_axis = "-' + str(left_analog_left[1]) + '"\n')
                    file.write('input_l_x_plus_axis = "+' + str(left_analog_left[1]) + '"\n')
                if right_analog_up and right_analog_up[1] != '':
                    file.write('input_r_y_minus_axis = "-' + str(right_analog_up[1]) + '"\n')
                    file.write('input_r_y_plus_axis = "+' + str(right_analog_up[1]) + '"\n')
                if right_analog_left and right_analog_left[1] != '':
                    file.write('input_r_x_minus_axis = "-' + str(right_analog_left[1]) + '"\n')
                    file.write('input_r_x_plus_axis = "+' + str(right_analog_left[1]) + '"\n')
                # Menu (home) button
                if hotkey_btn and hotkey_btn[1] != '':
                    file.write('input_menu_toggle_btn = "' + str(hotkey_btn[1]) + '"\n')

def scan_bt_joys():
    names = cglobals.bt_mgr.get_available_devices()
    cglobals.sys_opt_bt_view.set_bt_joy_names(names)
    cglobals.sys_opt_bt_view.refresh_values()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def unpair_bt_joys():
    cglobals.bt_mgr.remove_pairings()
    cglobals.sys_opt_bt_view.set_bt_joy_names()
    cglobals.sys_opt_bt_view.refresh_values()
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

def pair_bt_joys():
    device_number = int(cglobals.sys_opt_bt_view.get_current_option()[-1])
    rtk.logging.debug('Pairing device number %s', device_number)
    cglobals.bt_mgr.quick_connect(device_number)
    rtk.popup_msg.hide()
    cglobals.is_in_task = False

# Retroarch Cores

def set_core_psx_force_analog():
    if rtk.cfg_psx_control == 'analog_forced':
        set_core_option(option='duckstation_Controller1.ForceAnalogOnReset',value='true')
        set_core_option(option='duckstation_Controller2.ForceAnalogOnReset',value='true')
    else:
        set_core_option(option='duckstation_Controller1.ForceAnalogOnReset',value='false')
        set_core_option(option='duckstation_Controller2.ForceAnalogOnReset',value='false')

def set_core_fbneo_overclock(oc):
    if oc:
        set_core_option(option='fbneo-cpu-speed-adjust',value='400%')
    else:
        set_core_option(option='fbneo-cpu-speed-adjust',value='100%')

def set_core_fbneo_60(force):
    if force == 'on':
        set_core_option(option='fbneo-force-60hz',value='enabled')
    else:
        set_core_option(option='fbneo-force-60hz',value='disabled')

def set_core_overclock():
    if rtk.cfg_slowdown_fix == 'on':
        set_core_option(option='genesis_plus_gx_overclock',value='200%')
        set_core_option(option='fceumm_overclocking',value='2x-Postrender') # disabled, 2x-Postrender, 2x-VBlank
        set_core_option(option='snes9x_overclock_cycles',value='compatible') # disabled, light , compatible, max
        set_core_option(option='snes9x_overclock_superfx',value='200%')
        set_core_option(option='duckstation_CPU.Overclock',value='200')
        set_core_option(option='fbneo-cpu-speed-adjust',value='400%') # 400 needed for MS2 2P mode
    else:
        set_core_option(option='genesis_plus_gx_overclock',value='100%')
        set_core_option(option='fceumm_overclocking',value='disabled')
        set_core_option(option='snes9x_overclock_cycles',value='disabled')
        set_core_option(option='snes9x_overclock_superfx',value='100%')
        set_core_option(option='duckstation_CPU.Overclock',value='100')
        set_core_option(option='fbneo-cpu-speed-adjust',value='100%')

def set_core_gb_mode(mode):
    if mode == '.gbc':
        set_core_option(option='mgba_gb_model',value='Game Boy Color')
    else:
        set_core_option(option='mgba_gb_model',value='Super Game Boy')

def set_core_nes_color():
    set_core_option(option='fceumm_palette',value=rtk.cfg_nes_color)

def set_core_sgb_color():
    set_core_option(option='mgba_gb_colors',value=rtk.cfg_sgb_color)

def set_core_ntsc_filter():
    if rtk.cfg_ntsc_filter == 'on':
        set_core_option(option='genesis_plus_gx_blargg_ntsc_filter',value='svideo')
    elif rtk.cfg_ntsc_filter == 'off':
        set_core_option(option='genesis_plus_gx_blargg_ntsc_filter',value='disabled')

def set_core_sms_fm():
    if rtk.cfg_sms_sound == 'on':
        set_core_option(option='genesis_plus_gx_ym2413',value='enabled')
    elif rtk.cfg_sms_sound == 'off':
        set_core_option(option='genesis_plus_gx_ym2413',value='disabled')

def set_core_borders(borders):
    if borders:
        set_core_option(option='genesis_plus_gx_overscan',value='top/bottom')
    else:
        set_core_option(option='genesis_plus_gx_overscan',value='disabled')

def set_core_crosshair(crosshair):
    if crosshair:
        set_core_option(option='fceumm_show_crosshair',value='enabled')
        set_core_option(option='snes9x_superscope_crosshair',value='2')
    else:
        set_core_option(option='fceumm_show_crosshair',value='disabled')
        set_core_option(option='snes9x_superscope_crosshair',value='0')

def set_core_neogeo_mode(mode):
    if mode == 'aes':
        set_core_option(option='fbneo-neogeo-mode',value='AES_EUR')
    elif mode == 'mvs':
        set_core_option(option='fbneo-neogeo-mode',value='MVS_EUR')
    elif mode == 'uni':
        set_core_option(option='fbneo-neogeo-mode',value='UNIBIOS')

def set_core_naomi_rotation(is_tate):
    if is_tate:
        set_core_option(option='reicast_screen_rotation',value='vertical')
    else:
        set_core_option(option='reicast_screen_rotation',value='horizontal')

def set_core_enable_patch_support():
    set_core_option(option='fbneo-allow-patched-romsets',value='enabled')

def set_core_disable_patch_support():
    set_core_option(option='fbneo-allow-patched-romsets',value='disabled')

def set_core_dosbox_kb():
    if rtk.cfg_language == 'de':
        set_core_option(option='dosbox_pure_keyboard_layout',value='gr')
    elif rtk.cfg_language == 'en':
        set_core_option(option='dosbox_pure_keyboard_layout',value='us')
    elif rtk.cfg_language == 'es':
        set_core_option(option='dosbox_pure_keyboard_layout',value='sp')
    elif rtk.cfg_language == 'fr':
        set_core_option(option='dosbox_pure_keyboard_layout',value='fr')
    elif rtk.cfg_language == 'it':
        set_core_option(option='dosbox_pure_keyboard_layout',value='it')
    elif rtk.cfg_language == 'pt':
        set_core_option(option='dosbox_pure_keyboard_layout',value='po')

def set_core_region():
    if rtk.cfg_core_region == 'AUTO':
        set_core_option(option='puae_video_standard',           value='PAL auto')
        set_core_option(option='vice_c64_model',                value='C64 NTSC auto')
        set_core_option(option='genesis_plus_gx_region_detect', value='auto')
        set_core_option(option='neocd_region',                  value='USA')
        set_core_option(option='fceumm_region',                 value='Auto')
        set_core_option(option='ngp_language',                  value='english')
        set_core_option(option='duckstation_Console.Region',    value='Auto')
        set_core_option(option='picodrive_region',              value='Auto')
        set_core_option(option='snes9x_region',                 value='auto')
        set_core_option(option='reicast_region',                value='Default')
    elif rtk.cfg_core_region == 'USA':
        set_core_option(option='puae_video_standard',           value='NTSC auto')
        set_core_option(option='vice_c64_model',                value='C64 NTSC auto')
        set_core_option(option='genesis_plus_gx_region_detect', value='ntsc-u')
        set_core_option(option='neocd_region',                  value='USA')
        set_core_option(option='fceumm_region',                 value='NTSC')
        set_core_option(option='ngp_language',                  value='english')
        set_core_option(option='duckstation_Console.Region',    value='NTSC-U')
        set_core_option(option='picodrive_region',              value='US')
        set_core_option(option='snes9x_region',                 value='ntsc')
        set_core_option(option='reicast_region',                value='USA')
    elif rtk.cfg_core_region == 'EUR':
        set_core_option(option='puae_video_standard',           value='PAL auto')
        set_core_option(option='vice_c64_model',                value='C64 PAL auto')
        set_core_option(option='genesis_plus_gx_region_detect', value='pal')
        set_core_option(option='neocd_region',                  value='Europe')
        set_core_option(option='fceumm_region',                 value='PAL')
        set_core_option(option='ngp_language',                  value='english')
        set_core_option(option='duckstation_Console.Region',    value='PAL')
        set_core_option(option='picodrive_region',              value='Europe')
        set_core_option(option='snes9x_region',                 value='pal')
        set_core_option(option='reicast_region',                value='Europe')
    elif rtk.cfg_core_region == 'JAP':
        set_core_option(option='puae_video_standard',           value='PAL auto')
        set_core_option(option='vice_c64_model',                value='C64 NTSC auto')
        set_core_option(option='genesis_plus_gx_region_detect', value='ntsc-j')
        set_core_option(option='neocd_region',                  value='Japan')
        set_core_option(option='fceumm_region',                 value='Auto')
        set_core_option(option='ngp_language',                  value='japanese')
        set_core_option(option='duckstation_Console.Region',    value='NTSC-J')
        set_core_option(option='picodrive_region',              value='Japan NTSC')
        set_core_option(option='snes9x_region',                 value='auto')
        set_core_option(option='reicast_region',                value='Japan')
    
def set_core_option(option, value):
    cfg_file = rtk.path_rgbpi_data + '/cores.cfg'
    if os.path.isfile(cfg_file):
        with open(cfg_file, 'r', encoding='utf-8') as file:
            for line in file:
                if option in line:
                    old_line = line
                    new_line = option + ' = ' + '"' + value + '"\n'
                    break
        replace_text_line(file_path=cfg_file,search_string=old_line,replace_string=new_line)

''' Webservices '''

def ws_send_stats(url, system, game, time):
    try:
        stats = {
            'user':              rtk.cfg_nick,
            'system':            system,
            'game':              game,
            'time':              time,
            'has_cheats':        str(has_cheats()),
            'is_rgbpi':          str(cglobals.is_rgbpi),
            'is_jamma':          str(cglobals.is_jamma),
            'os_name':           rtk.cfg_os_name+'/'+str(rtk.cfg_os_ver),
            'os_version':        'v'+str(rtk.cfg_os_int_ver)+' ('+str(rtk.cfg_os_date_ver)+')',
            'adv_mode':          rtk.cfg_adv_mode,
            'scr_crt_type':      rtk.cfg_crt_type,
            'scr_dynares':       rtk.cfg_dynares,
            'scr_ui_rotation':   rtk.cfg_ui_rotation,
            'scr_native_csync':  rtk.cfg_native_csync,
            'scr_handheld_full': cglobals.launcher['handheld_mode'],
            'snd_preset':        rtk.cfg_preset,
            'snd_audio_jack':    rtk.cfg_audio_jack,
            'net_wifi':          rtk.cfg_wifi,
            'dsk_data_source':   rtk.cfg_data_source,
            'dsk_global_nfs':    str(is_global_nfs()),
            'sys_language':      rtk.cfg_language,
            'sys_theme':         rtk.cfg_theme,
            'emu_user_remaps':   str(rtk.cfg_user_remaps),
            'has_fresh_jamma_remaps': str(cglobals.has_fresh_jamma_remaps)
        }
        response = requests.post(url, data=stats, timeout=2, verify=False)
        rtk.logging.info('ws_send_stats: %s Status code: %s', url, response.status_code)
        if response.status_code in (200, 201):
            return True
        else:
            return None
    except Exception as error:
        rtk.logging.error('Error ws_send_stats %s %s', error, stats)
        return None

def ws_get_osversion(url):
    try:
        response = requests.post(url, data=None, timeout=2, verify=False)
        rtk.logging.info('ws_get_osversion: %s Status code: %s', url, response.status_code)
        if response.status_code in (200, 201):
            response = response.text
            response = response.split(',')
            return response
        else:
            return None
    except Exception as error:
        rtk.logging.error('Error ws_get_osversion %s', error)
        return None

def ws_get_scrversion(url):
    try:
        response = requests.post(url, data=None, timeout=2, verify=False)
        rtk.logging.info('ws_get_scrversion: %s Status code: %s', url, response.status_code)
        if response.status_code in (200, 201):
            response = response.text
            return response
        else:
            return None
    except Exception as error:
        rtk.logging.error('Error ws_get_scrversion %s', error)
        return None

def ws_download_file(type, file_name):
    def download(url,dest_path):
        with requests.get(url, allow_redirects=False, stream=True, verify=False) as r:
            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    url1 = 'https://' + rtk.url_downloads + '/' + type + '/' + file_name
    url2 = 'http://'  + rtk.url_downloads + '/' + type + '/' + file_name
    dest_path = rtk.path_rgbpi_temp + '/' + file_name
    try:
        rtk.logging.info('ws_download_file URL %s', url1)
        download(url1,dest_path)
    except:
        rtk.logging.info('ws_download_file URL %s', url2)
        download(url2,dest_path)
    return dest_path

def ws_send_netplay_info(url):
    try:
        info = {
            'user'     : rtk.cfg_nick,
            'operation': 'add'
        }
        response = requests.post(url, data=info, timeout=2, verify=False)
        rtk.logging.info('ws_send_netplay_info: %s Status code: %s', url, response.status_code)
        if response.status_code in (200, 201):
            return True
        else:
            return None
    except Exception as error:
        rtk.logging.error('Error ws_send_netplay_info %s', error)
        return None

def ws_get_netplay_info(url):
    try:
        info = {
            'operation': 'get'
        }
        response = requests.post(url, data=info, timeout=2, verify=False)
        rtk.logging.info('ws_get_netplay_info: %s Status code: %s', url, response.status_code)
        if response.status_code in (200, 201):
            response = response.text
            response = response.split('|')
            del response[-1]
            return response
        else:
            return None
    except Exception as error:
        rtk.logging.error('Error ws_get_netplay_info %s', error)
        return None
