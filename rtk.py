import os
# Lakka-port: stub optional native libs as early as possible so any module
# imported alongside rtk (sound_mgr, input_mgr, bluetooth_mgr, utils...) gets
# safe fallbacks instead of ImportError.
import lakka_optional_deps  # noqa: F401
import pygame
import string
import logging
import logging.config
import traceback
import configparser
import random
import csv
from datetime import datetime
from math import ceil, floor, pi, cos, sin, radians, degrees
from PIL import Image
from pygame.locals import *

# Lakka-port: inject path constants (rgbpi-lakka)
from lakka_paths import *
ensure_dirs()

''' Global constants '''

scr_w = 320
scr_h = 240
fps = 60
msg_title_x = 'center'
msg_title_y = 24
msg_text_x = 24
msg_text_y = 56

''' Main Sprite Container '''

all_sprites = pygame.sprite.LayeredDirty()

''' Utility Functions '''

def get_display_inf():
    return pygame.display.Info()

def print_screen():
    screen_copy = screen.copy().convert()
    capture_file = os.path.join(capture_dir, 'capture_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.bmp')
    pygame.image.save(screen_copy, capture_file)

def parse_val(value):
    try:
        if 'Rtk' in value:
            val = value.replace(' ','')
        else:
            val = eval(value) # int and list
    except:
        # bool
        if value.lower() in ("yes", "true", "t", "1"):
            val = True
        elif value.lower() in ("no", "false", "f", "0"):
            val = False
        elif value.lower() == 'none':
            val = None
        else:
            val = value # string
    return val

def get_color_key(image):
    return image.get_at((0, 0))

def load_image(image, colorkey=None):
    try:
        img_path = os.path.join(path_rgbpi_images, image)
        img_path_2 = os.path.join(img_dir, image)
        if os.path.isfile(img_path):
            image = pygame.image.load(img_path)
        else:
            image = pygame.image.load(img_path_2)
        rect = image.get_rect()
    except Exception as error:
        logging.debug('Cannot load image: %s, error: %s', image, error)
    else:
        image = image.convert()
        if colorkey is not None:
            if colorkey == 'auto':
                colorkey = get_color_key(image)
            image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, rect

def load_image_at(image, rectangle, colorkey=None):
    # Load a specific image from a specific rectangle
    # Rectangle = x, y, x+offset, y+offset
    rect = pygame.Rect(rectangle)
    subimage = pygame.Surface(rect.size).convert()
    subimage.blit(image, (0, 0), rect)
    if colorkey is not None:
        if colorkey == 'auto':
            colorkey = get_color_key(subimage)
        subimage.set_colorkey(colorkey, pygame.RLEACCEL)
    return subimage

def load_images_at(image, rects, colorkey=None):
    # Load a whole bunch of images and return them as a list.
    return [load_image_at(image, rect, colorkey) for rect in rects]

def load_rect(w, h, color, colorkey=None):
    image = pygame.Surface((w, h))
    image.fill(color)
    image = image.convert()
    if colorkey is not None:
        if colorkey == 'auto':
            colorkey = get_color_key(image)
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

def load_translations():
    translations = []
    with open(trans_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            translation = {'Lang':row["Lang"],'Name':row["Name"],'Value':row["Value"]}
            translations.append(translation)
    return translations

def get_translation(name):
    for translation in translations:
        if translation["Name"] == name and translation["Lang"] == cfg_language:
            return translation["Value"]
    return name

def load_font_map(font_file):
    # Load font map from data sheet
    font_map = {}
    with open(font_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n','')
            char_map = line.split(',')
            # Fix comma char and comma separator
            if len(char_map) == 6:
                del char_map[0]
                char_map[0] = ','
            if len(char_map[0]) > 1: # lower key words
                char_map[0] = char_map[0].lower()
            font_map[char_map[0]] = char_map[1:]
    # Get char size
    rectangle = font_map['0']
    char_width = int(rectangle[2])
    char_height = int(rectangle[3])
    return font_map, char_width, char_height

def get_random_id():
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=8))

def load_trasition(is_refresh=False):
    global transition, transition_tate
    global err_draw_trans
    err_draw_trans = False
    opid=get_random_id()
    if is_refresh:
        try:
            cont_bg = ContainerMgr.containers['Background']
            for widget in cont_bg.widgets:
                if widget.name in ('Transition','Transition_Tate'):
                    cont_bg.remove(widget=widget,opid=opid)
        except:
            pass
    try:
        transition = RtkAniGif(name='Transition', image='transition.gif', position=(tran_x,tran_y), speed=tran_speed, loop=False)
        transition_tate = RtkAniGif(name='Transition_Tate', image='transition_tate.gif', position=(tran_x,tran_y), speed=tran_speed, loop=False)
    except Exception as error:
        logging.error('Error loading transition image. Falling back on RtkRect. %s\n%s', error, traceback.format_exc())
        transition = RtkRect(name='Transition', position=(0,0), w=0, h=0)
        transition_tate = RtkRect(name='Transition_Tate', position=(0,0), w=0, h=0)
    transition._layer = 5
    transition_tate._layer = 5
    ContainerMgr.append(parent=container_bg, child=transition)
    ContainerMgr.append(parent=container_bg, child=transition_tate)

def load_mouse(is_refresh=False):
    global mouse
    global err_draw_mouse
    err_draw_mouse = False
    opid=get_random_id()
    if is_refresh:
        try:
            cont_bg = ContainerMgr.containers['Background']
            for widget in cont_bg.widgets:
                if widget.name in ('Mouse'):
                    cont_bg.remove(widget=widget,opid=opid)
        except:
            pass
    try:
        mouse = RtkImage(name='lgun_aim', image='lgun_aim.bmp', is_active=False, position=(0,0), colorkey=color_key)
    except:
        logging.error('Error loading mouse image. Falling back on RtkRect')
        mouse = RtkRect(name='Transition', position=(0,0), w=8, h=8)
    mouse._layer = 5
    ContainerMgr.append(parent=container_bg, child=mouse)

def draw_transition(time_step):
    global err_draw_trans
    try:
        transition_tate.animate(time_step)
        transition.animate(time_step)
    except Exception as error:
        if not err_draw_trans:
            logging.error('Error drawing transition. %s', error)
            err_draw_trans = True

def load_messages(is_refresh=False):
    global error_msg, user_msg, popup_msg, notif_msg
    if is_refresh:
        try:
            opid=get_random_id()
            error_msg.destroy(opid=opid)
            user_msg.destroy(opid=opid)
            popup_msg.destroy(opid=opid)
            notif_msg.destroy(opid=opid)
        except:
            pass
    error_msg = RtkTxtMsg(name='Error',type='full',title='error_title',text='Error text',txt_color=msg_error_txt_color,bg_color=msg_error_bg_color, duration=5)
    user_msg = RtkTxtMsg(name='Info',type='full',title='info_title',text='Info text',txt_color=msg_info_txt_color,bg_color=msg_info_bg_color)
    popup_msg = RtkTxtMsg(name='Popup',type='popup',text=' Popup text ',txt_color=msg_popup_txt_color,bg_color=msg_popup_bg_color, bg_border_color=msg_popup_bg_border_color)
    notif_msg = RtkTxtMsg(name='Notif',type='popup',text=' Popup text ',txt_color=msg_notif_txt_color,bg_color=msg_notif_bg_color, bg_border_color=msg_notif_bg_border_color, duration=2)

def draw_messages(time_step):
    error_msg.draw_msg(time_step)
    user_msg.draw_msg(time_step)
    popup_msg.draw_msg(time_step)
    notif_msg.draw_msg(time_step)

def load_background(is_refresh=False):
    global background, background_tate
    global container_bg
    global err_draw_bg
    err_draw_bg = False
    opid=get_random_id()
    if is_refresh:
        try:
            cont_bg = ContainerMgr.containers['Background']
            for widget in cont_bg.widgets:
                if widget.name in ('Background','Background_Tate'):
                    cont_bg.remove(widget=widget,opid=opid)
        except:
            pass
    try:
        if bg_type == 'static':
            background = RtkSprite(name='Background', image='background.bmp', position=(0,0), opid=opid)
            background_tate = RtkSprite(name='Background_Tate', image='background_tate.bmp', position=(0,0), opid=opid)
        elif bg_type == 'ani_gif':
            background = RtkAniGif(name='Background', image='background.gif', position=(0,0), speed=bg_speed, opid=opid)
            background_tate = RtkAniGif(name='Background_Tate', image='background_tate.gif', position=(0,0), speed=bg_speed, opid=opid)
        elif bg_type == 'scroll_left':
            background = RtkScrollBg(name='Background', image='background.bmp', type='h', position=(0, 0), opid=opid)
            background.set_scroll(state=-1)
            background_tate = RtkScrollBg(name='Background_Tate', image='background_tate.bmp', type='h', is_tate=True, position=(0, 0), opid=opid)
            background_tate.set_scroll(state=-1)
        elif bg_type == 'scroll_right':
            background = RtkScrollBg(name='Background', image='background.bmp', type='h', position=(0, 0), opid=opid)
            background.set_scroll(state=1)
            background_tate = RtkScrollBg(name='Background_Tate', image='background_tate.bmp', type='h', is_tate=True, position=(0, 0), opid=opid)
            background_tate.set_scroll(state=1)
        elif bg_type == 'scroll_up':
            background = RtkScrollBg(name='Background', image='background.bmp', type='v', position=(0, 0), opid=opid)
            background.set_scroll(state=-1)
            background_tate = RtkScrollBg(name='Background_Tate', image='background_tate.bmp', type='v', is_tate=True, position=(0, 0), opid=opid)
            background_tate.set_scroll(state=-1)
        elif bg_type == 'scroll_down':
            background = RtkScrollBg(name='Background', image='background.bmp', type='v', position=(0, 0), opid=opid)
            background.set_scroll(state=1)
            background_tate = RtkScrollBg(name='Background_Tate', image='background_tate.bmp', type='v', is_tate=True, position=(0, 0), opid=opid)
            background_tate.set_scroll(state=1)
        elif bg_type == 'parallax_left':
            background = RtkParallaxBg(name='Background', image='background.bmp', type='h', position=(0,0), opid=opid)
            background.set_scroll(state=-1)
            background_tate = RtkParallaxBg(name='Background_Tate', image='background_tate.bmp', type='h', position=(0, 0), opid=opid)
            background_tate.set_scroll(state=-1)
        elif bg_type == 'parallax_right':
            background = RtkParallaxBg(name='Background', image='background.bmp', type='h', position=(0,0), opid=opid)
            background.set_scroll(state=1)
            background_tate = RtkParallaxBg(name='Background_Tate', image='background_tate.bmp', type='h', position=(0, 0), opid=opid)
            background_tate.set_scroll(state=1)
        elif bg_type == 'parallax_up':
            background = RtkParallaxBg(name='Background', image='background.bmp', type='v', position=(0,0), opid=opid)
            background.set_scroll(state=-1)
            background_tate = RtkParallaxBg(name='Background_Tate', image='background_tate.bmp', type='v', position=(0, 0), opid=opid)
            background_tate.set_scroll(state=-1)
        elif bg_type == 'parallax_down':
            background = RtkParallaxBg(name='Background', image='background.bmp', type='v', position=(0,0), opid=opid)
            background.set_scroll(state=1)
            background_tate = RtkParallaxBg(name='Background_Tate', image='background_tate.bmp', type='v', position=(0, 0), opid=opid)
            background_tate.set_scroll(state=1)
        else:
            logging.error('Error loading background. %s type is not valid. Falling back on RtkRect', bg_type)
            background = RtkRect(name='Background', position=(0,0), w=scr_w, h=scr_h, color=d_blue, opid=opid)
            background_tate = RtkRect(name='Background_Tate', position=(0,0), w=scr_h, h=scr_w, color=d_blue, opid=opid)
    except Exception as error:
        logging.error('Error loading background. %s', error)
        background = RtkRect(name='Background', position=(0,0), w=scr_w, h=scr_h, color=d_blue, opid=opid)
        background_tate = RtkRect(name='Background_Tate', position=(0,0), w=scr_h, h=scr_w, color=d_blue, opid=opid)
    background._layer = 0
    background_tate._layer = 0
    # Create default background container
    if not is_refresh:
        container_bg = ContainerMgr.create(name='Background', opid=opid)
    ContainerMgr.append(parent=container_bg, child=background, opid=opid)
    ContainerMgr.append(parent=container_bg, child=background_tate, opid=opid)

def set_screen_mode(is_tate):
    if is_tate:
        background.deactivate()
        background_tate.activate()
        transition.deactivate()
        transition_tate.activate()
        if fg_display:
            foreground.deactivate()
            foreground_tate.activate()
        set_custom_sprites_rotation(is_tate)
        error_msg.set_rotation(is_tate)
        user_msg.set_rotation(is_tate)
        popup_msg.set_rotation(is_tate)
        notif_msg.set_rotation(is_tate)
    else:
        background.activate()
        background_tate.deactivate()
        transition.activate()
        transition_tate.deactivate()
        if fg_display:
            foreground.activate()
            foreground_tate.deactivate()
        set_custom_sprites_rotation(is_tate)
        error_msg.set_rotation(is_tate)
        user_msg.set_rotation(is_tate)
        popup_msg.set_rotation(is_tate)
        notif_msg.set_rotation(is_tate)

def draw_background(time_step):
    global err_draw_bg
    try:
        if bg_type == 'ani_gif':
            background_tate.animate(time_step)
            background.animate(time_step)
        elif 'scroll' in bg_type or 'parallax' in bg_type:
            background_tate.scroll(bg_speed, time_step)
            background.scroll(bg_speed, time_step)
    except Exception as error:
        if not err_draw_bg:
            logging.error('Error drawing background. %s', error)
            err_draw_bg = True

def load_foreground(is_refresh=False):
    global foreground, foreground_tate
    global container_fg
    global err_draw_fg
    err_draw_fg = False
    opid=get_random_id()
    if is_refresh:
        try:
            cont_fg = ContainerMgr.containers['Foreground']
            for widget in cont_fg.widgets:
                if widget.name in ('Foreground','Foreground_Tate'):
                    cont_fg.remove(widget=widget,opid=opid)
        except:
            container_fg = ContainerMgr.create(name='Foreground', opid=opid)
    try:
        if fg_display:
            foreground = RtkSprite(name='Foreground', image='foreground.bmp', position=(0,0), colorkey=color_key, opid=opid)
            foreground_tate = RtkSprite(name='Foreground_Tate', image='foreground_tate.bmp', position=(0,0), colorkey=color_key, opid=opid)
            if fg_sent_back:
                foreground._layer = 1
                foreground_tate._layer = 1
            else:
                foreground._layer = 3
                foreground_tate._layer = 3
            # Create default foreground container
            if not is_refresh:
                container_fg = ContainerMgr.create(name='Foreground', opid=opid)
            ContainerMgr.append(parent=container_fg, child=foreground, opid=opid)
            ContainerMgr.append(parent=container_fg, child=foreground_tate, opid=opid)
        else:
            logging.debug('Foreground inactive')
    except Exception as error:
        logging.error('Error loading foreground. %s', error)

def load_custom_sprites(is_refresh=False):
    global cust_sprites
    if is_refresh:
        try:
            opid=get_random_id()
            cont_bg = ContainerMgr.containers['Background']
            for sprite in cust_sprites:
                for widget in cont_bg.widgets:
                    if widget.name == sprite.name:
                        cont_bg.remove(widget=widget,opid=opid)
                sprite.destroy(opid=opid)
            cust_sprites = []
        except:
            pass
    if has_custom_sprites:
        global err_draw_cust_sprites
        err_draw_cust_sprites = False
        cust_sprites = []
        try:
            names = cust_sprt_name.replace(' ','').split(',')
            types = cust_sprt_type.replace(' ','').split(',')
            positions = cust_sprt_position
            angles = cust_sprt_angle
            num_frames = cust_sprt_num_frames
            ani_rev_cycles = cust_sprt_ani_rev_cycle.replace(' ','').split(',')
            wobbles = cust_sprt_wobble.replace(' ','').split(',')
            for i, name in enumerate(names):
                position = positions[i]
                angle = angles[i]
                num_frms = num_frames[i]
                ani_rev_cycle = parse_val(ani_rev_cycles[i])
                wobble = wobbles[i]
                if types[i] == 'RtkSprite':
                    sprite = RtkSprite(name=name, image=name+'.bmp', position=position, colorkey=color_key)
                    sprite._layer = 0
                    cust_sprites.append(sprite)
                elif types[i] == 'RtkAniSprite':
                    sprite = RtkAniSprite(name=name, image=name+'.bmp', angle=angle, num_frames=num_frms, position=position, colorkey=color_key, rev_cycle=ani_rev_cycle)
                    sprite._layer = 0
                    cust_sprites.append(sprite)
                if wobble:
                    cust_sprites[i].set_wobble(state=1)                    
            # Add custom sprites to background container
            ContainerMgr.append(parent=container_bg, child=cust_sprites)
        except Exception as error:
            logging.error('Error loading custom sprites. %s', error)

def set_custom_sprites_rotation(is_tate):
    if has_custom_sprites:
        if is_tate:
            positions = cust_sprt_position_tate
        else:
            positions = cust_sprt_position
        for i, sprite in enumerate(cust_sprites):
            position = positions[i]
            sprite.set_position(position)
            sprite.start_pos = position

def draw_custom_sprites(time_step, is_tate=False):
    if has_custom_sprites:
        global err_draw_cust_sprites
        try:
            wobbles = cust_sprt_wobble.replace(' ','').split(',')
            wobble_speeds = cust_sprt_wobble_speed
            wobble_limits = cust_sprt_wobble_limit
            any_speeds = cust_sprt_any_speed
            bounces = cust_sprt_bounce.replace(' ','').split(',')
            bounce_speeds = cust_sprt_bounce_speed
            for i, sprite in enumerate(cust_sprites):
                wobble = wobbles[i]
                wobble_speed = wobble_speeds[i]
                wobble_limit = wobble_limits[i]
                any_speed = any_speeds[i]
                bounce = bounces[i]
                bounce_speed = bounce_speeds[i]
                if sprite.wobble_state !=0:
                    sprite.wobble(mode=wobble, speed=wobble_speed, limit=wobble_limit, time_step=time_step)
                if type(sprite).__name__ == 'RtkAniSprite':
                    sprite.animate(speed=any_speed, time_step=time_step)
                if bounce == 'true':
                    sprite.bounce(speed=bounce_speed, time_step=time_step, is_tate=is_tate)
        except Exception as error:
            if not err_draw_cust_sprites:
                logging.error('Error drawing custom sprites. %s', error)
                err_draw_cust_sprites = True

def render():
    try:
        global screen, screen_tate, fb_presenter
        if cfg_ui_rotation == 'rotate_ccw':
            all_sprites.draw(screen_tate)
            scr_tate = pygame.transform.rotate(screen_tate, 90)
            screen.blit(scr_tate, (0, 0))
        elif cfg_ui_rotation == 'rotate_cw':
            all_sprites.draw(screen_tate)
            scr_tate = pygame.transform.rotate(screen_tate, 270)
            screen.blit(scr_tate, (0, 0))
        elif cfg_ui_rotation == 'rotate_full':
            all_sprites.draw(screen)
            scr = pygame.transform.rotate(screen, 180)
            screen.blit(scr, (0, 0))
        else:
            all_sprites.draw(screen)
        if fb_presenter:
            fb_presenter.present()
        pygame.display.update() # Removed rects to allow proper rotation
        clock.tick(fps) # Removing the framerate makes vsync adjust to the same monitor freq
    except Exception as error:
        logging.error('Error drawing custom sprites. %s', error)

''' Configuration Files '''

def load_app_cfg():
    global main_dir, dat_dir, capture_dir
    global cfg_file, trans_file
    # Directories
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    dat_dir = os.path.join(main_dir, 'data')
    capture_dir = os.path.join(main_dir, 'captures')
    # Files
    cfg_file = os.path.join(main_dir, 'config.ini')
    trans_file = os.path.join(dat_dir, 'translations.dat')
    # Inilialize logging
    logging.config.fileConfig(cfg_file)
    logging.debug('*** Starting Program ***')
    # Load configuration file
    load_cfg_file()

def load_cfg_file():
    # Open config file
    config = configparser.RawConfigParser()
    config.read(cfg_file)
    # Read configuration
    for section in config.sections():
        for (option, value) in config.items(section):
            if section == 'cfg':
                if option == 'theme':
                    globals()[section + '_' + option] = str(value)
                else:
                    globals()[section + '_' + option] = parse_val(value)
            else:
                globals()[section + '_' + option] = value
    logging.debug('Program configuration loaded')

def save_cfg_file():
    # Open config file
    configr = configparser.RawConfigParser()
    configr.read(cfg_file)
    # Create new configuration
    configw = configparser.RawConfigParser()
    # Set configuration values
    for section in configr.sections():
        configw.add_section(section)
        for (option, value) in configr.items(section):
            try:
                configw.set(section, option, globals()[section + '_' + option])
            except:
                configw.set(section, option, value)
    # Write configuration to file
    with open(cfg_file, 'w', encoding='utf-8') as configfile:
        configw.write(configfile)
    logging.debug('Program configuration saved')

def load_theme_cfg():
    global themes_dir, theme_dir, img_dir, snd_dir, music_dir, font_dir, cfg_theme, cfg_playlist
    global fnt_title_file, fnt_title_dat_file, fnt_list_file, fnt_list_dat_file, fnt_info_file, fnt_info_dat_file, \
        fnt_helper_file, fnt_helper_dat_file, theme_cfg_file
    global has_custom_sprites, title_font_map, title_char_width, title_char_height, list_font_map, list_char_width, list_char_height, \
        info_font_map, info_char_width, info_char_height, helper_font_map, helper_char_width, helper_char_height
    # Directories
    themes_dir = os.path.join(main_dir, 'themes')
    theme_dir = os.path.join(themes_dir, cfg_theme)
    if not (os.path.exists(theme_dir) and os.path.isdir(theme_dir)):
        cfg_theme = cfg_default_theme
        theme_dir = os.path.join(themes_dir, cfg_theme)
        cfg_playlist = cfg_theme
    img_dir = os.path.join(theme_dir, 'images')
    snd_dir = os.path.join(theme_dir, 'sounds')
    music_dir = os.path.join(theme_dir, 'music')
    font_dir = os.path.join(theme_dir, 'fonts')
    # Files
    fnt_title_file = os.path.join(font_dir, 'title.bmp')
    fnt_title_dat_file = os.path.join(font_dir, 'title.dat')
    fnt_list_file = os.path.join(font_dir, 'list.bmp')
    fnt_list_dat_file = os.path.join(font_dir, 'list.dat')
    fnt_info_file = os.path.join(font_dir, 'info.bmp')
    fnt_info_dat_file = os.path.join(font_dir, 'info.dat')
    fnt_helper_file = os.path.join(font_dir, 'helper.bmp')
    fnt_helper_dat_file = os.path.join(font_dir, 'helper.dat')
    theme_cfg_file = os.path.join(theme_dir, 'theme.ini')
    # Load font data
    title_font_map, title_char_width, title_char_height = load_font_map(fnt_title_dat_file)
    list_font_map, list_char_width, list_char_height = load_font_map(fnt_list_dat_file)
    info_font_map, info_char_width, info_char_height = load_font_map(fnt_info_dat_file)
    helper_font_map, helper_char_width, helper_char_height = load_font_map(fnt_helper_dat_file)
    # Open config file
    config = configparser.RawConfigParser()
    config.read(theme_cfg_file)
    # Read configuration
    has_custom_sprites = False
    for section in config.sections():
        for (option, value) in config.items(section):
            if section == 'cust_sprt':
                has_custom_sprites = True
            if section == 'pal':
                globals()[option] = parse_val(value)
            else:
                globals()[section + '_' + option] = parse_val(value)
    if has_custom_sprites:
        logging.debug('Custom sprites found')
    logging.debug('Theme configuration loaded')

''' Load config '''

load_app_cfg()
load_theme_cfg()

''' RTK Classes '''

class RtkEvent:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class RtkStepTimer:
    def __init__(self):
        self.timer()

    def timer(self):
        # The clock time when the timer started
        self.start_ticks = 0
        # The ticks stored when the timer was paused
        self.paused_ticks = 0
        # The timer status
        self.paused = False
        self.started = False

    def start(self):
        # Start the timer
        self.started = True
        # Unpause the timer
        self.paused = False
        # Get the current clock time
        self.start_ticks = pygame.time.get_ticks()
        self.paused_ticks = 0

    def stop(self):
        # Stop the timer
        self.started = False
        # Unpause the timer
        self.paused = False
        # Clear tick variables
        self.start_ticks = 0
        self.paused_ticks = 0

    def pause(self):
        # If the timer is running and isn't already paused
        if self.started and not self.paused:
            # Pause the timer
            self.paused = True
            # Calculate the paused ticks
            self.paused_ticks = pygame.time.get_ticks() - self.start_ticks
            self.start_ticks = 0

    def unpause(self):
        # If the timer is running and paused
        if self.started and self.paused:
            # Unpause the timer
            self.paused = False
            # Reset the starting ticks
            self.start_ticks = pygame.time.get_ticks() - self.paused_ticks
            # Reset the paused ticks
            self.paused_ticks = 0

    def get_ticks(self):
        # The actual timer time
        time = 0
        # If the timer is running
        if self.started:
            # If the timer is paused
            if self.paused:
                # Return the number of ticks when the timer was paused
                time = self.paused_ticks
            else:
                # Return the current time minus the start time
                time = pygame.time.get_ticks() - self.start_ticks
        return time

    def is_started(self):
        return self.started

    def is_paused(self):
        return self.paused and self.started

class RtkImage(pygame.sprite.DirtySprite):
    def __init__(self, name, image, is_active=True, position=(0,0), colorkey=None, opid=get_random_id()):
        pygame.sprite.DirtySprite.__init__(self)
        self.name = name
        logging.debug('OpID %s, Created %s %s', opid, type(self).__name__, self.name)
        if is_active:
            self.activate()
        else:
            self.deactivate()
        self.parent = None
        self.is_sprite = True
        self.position = position # This is the current position
        self.__set_surface_size()
        self.__load_image(image, colorkey)
        self.set_position(self.position)
        self.start_pos = self.position # This is the used for reseting the position
        self._layer = 2
        self.draw()

    def set_parent(self, par_obj):
        self.parent = par_obj

    def __set_surface_size(self):
        screen = get_display_inf()
        self.screen_w = screen.current_w
        self.screen_h = screen.current_h

    def __load_image(self, image, colorkey):
        self.fallback_image, self.fallback_rect = load_rect(w=scr_w, h=scr_h, color=color_key, colorkey=colorkey)
        try:
            self.image, self.rect = load_image(image=image, colorkey=colorkey)
        except:
            self.image = self.fallback_image
            self.rect = self.fallback_rect

    def change_image(self, image, colorkey=None):
        try:
            self.image, self.rect = load_image(image=image, colorkey=colorkey)
            img_exists = True
        except:
            self.image = self.fallback_image
            self.rect = self.fallback_rect
            img_exists = False
        self.set_position(position=self.start_pos)
        return img_exists

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
    
    def set_position(self, position, use_center=False, is_tate=False):
        x, y = position
        if x == 'center':
            if is_tate:
                x = self.screen_h / 2
            else:
                x = self.screen_w / 2
            self.rect.centerx = x
            x = self.rect.left
        else:
            if use_center:
                self.rect.centerx = x
            else:
                self.rect.left = x
        if y == 'center':
            if is_tate:
                y = self.screen_w / 2
            else:
                y = self.screen_h / 2
            self.rect.centery = y
            y = self.rect.top
        else:
            if use_center:
                self.rect.centery = y
            else:
                self.rect.top = y
        self.position = (x, y)
        self.draw()

    def draw(self):
        self.dirty = 1

    def show(self):
        self.visible = 1
        self.dirty = 1

    def hide(self):
        self.visible = 0
        self.dirty = 1

    def destroy(self, opid):
        logging.debug('OpID %s, Removing %s widget', opid, self.name)
        self.kill()

    def activate(self):
        self.is_active = True
        self.show()

    def deactivate(self):
        self.is_active = False
        self.hide()

class RtkSprite(pygame.sprite.DirtySprite):
    def __init__(self, name, image=None, parent=None, is_active=True, is_tate=False, flip=False, angle=0, position=(0,0), align='left', colorkey=None, opid=get_random_id()):
        pygame.sprite.DirtySprite.__init__(self)
        self.name = name
        logging.debug('OpID %s, Created %s %s', opid, type(self).__name__, self.name)
        self.parent = parent
        if is_active:
            self.activate()
        else:
            self.deactivate()
        self.is_sprite = True
        self.position = position # This is the current position
        self.align = align
        self.wobble_state = 0
        self.wobble_y_counter = None
        self.wobble_x_counter = None
        self.wobble_elapsed_time = 0
        self.magnify_state = 0
        self.magnify_counter = 0
        self.magnify_elapsed_time = 0
        self.ani_elapsed_time = 0
        self.alpha = 255
        self.alpha_state = 0
        self.__set_surface_size()
        self.set_angle(angle)
        if image:
            self.__load_image(image, colorkey)
            self.set_position(position=position,is_tate=is_tate)
            if flip:
                self.__flip()
        self.start_pos = self.position # This is the used for reseting the position
        self._layer = 2
        self.draw()
    
    def __del__(self):
        #logging.debug('Destroyed %s with id %s', type(self).__name__, self.name)
        pass

    def set_parent(self, par_obj):
        self.parent = par_obj

    def __load_image(self, image, colorkey):
        self.image, self.rect = load_image(image=image, colorkey=colorkey)
        self.original_img = self.image.copy()

    def __set_surface_size(self):
        screen = get_display_inf()
        self.screen_w = screen.current_w
        self.screen_h = screen.current_h

    def change_image(self, image, colorkey=None):
        self.image, self.rect = load_image(image=image, colorkey=colorkey)

    def __flip(self):
        self.image = pygame.transform.flip(self.image, True, False)

    def change_color(self, color, repcolor):
        # Apply to main image
        pixel_array = pygame.PixelArray(self.image)
        pixel_array.replace(color, repcolor)
        pixel_array.close()
        # Apply to original image
        pixel_array = pygame.PixelArray(self.original_img)
        pixel_array.replace(color, repcolor)
        pixel_array.close()
        self.dirty = 1

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()

    def set_wobble(self, state):
        self.wobble_state = state # -1 left/up 0 stop 1 rigth/down

    def set_mangnify(self, state):
        self.magnify_state = state # -1 inactive 0 normal 1 magnify
        if state == 0: # Restore image zoom
            self.magnify_counter = 0
            self.image = self.original_img.copy()
            self.rect = self.image.get_rect()
            self.set_position(position=self.start_pos)

    def handle(self, event):
        handler = f'handle_{event}'
        if hasattr(self, handler):
            method = getattr(self, handler)
            method(event)
        elif self.parent is not None:
            self.parent.handle(event)
        elif hasattr(self, 'handle_default'):
            self.handle_default(event)

    def handle_default(self, event):
        logging.debug('%s, handle_default %s', self.name, event)

    def set_position(self, position, is_tate=False):
        x, y = position
        # X
        if x == 'center':
            if is_tate:
                x = self.screen_h / 2
            else:
                x = self.screen_w / 2
            self.rect.centerx = x
            x = self.rect.left
        else:
            if self.align == 'right':
                self.rect.right = x
                x = self.rect.left
            self.rect.left = x
        # Y
        if y == 'center':
            if is_tate:
                y = self.screen_w / 2
            else:
                y = self.screen_h / 2
            self.rect.centery = y
            y = self.rect.top
        else:
            self.rect.top = y
        self.position = (x, y)
        self.draw()

    def move(self, displacement):
        # Change current position
        x = self.position[0] + displacement[0]
        y = self.position[1] + displacement[1]
        self.set_position((x, y))
        # Change start position
        x = self.start_pos[0] + displacement[0]
        y = self.start_pos[1] + displacement[1]
        self.start_pos = (x, y)

    def set_angle(self, angle):
        # Normalize angle
        angle = radians(angle)
        circle_turn = radians(360)
        normalized_angle = angle % circle_turn # Remainder of any angle by a circle turn removes all extra turns
        self.angle = normalized_angle

    def __get_quadrant(self):
        angle = round(degrees(self.angle))
        quadrant = 1
        if angle >= 0 and angle < 90:
            quadrant = 1
        elif angle >= 90 and angle < 180:
            quadrant = 2
        elif angle >= 180 and angle < 270:
            quadrant = 3
        elif angle >= 270 and angle <= 360:
            quadrant = 4
        return quadrant

    def advance(self, speed, time_step):
        x, y = self.position
        distance = speed * (time_step/1000)
        x += cos(self.angle) * distance
        y -= sin(self.angle) * distance
        self.set_position((x, y))

    def fade(self, speed, time_step):
        if self.alpha_state == 0:
            self.alpha += speed * (time_step/1000)
        elif self.alpha_state == 1:
            self.alpha -= speed * (time_step/1000)
        if self.alpha_state == 0 and self.alpha >= 255:
            self.alpha_state = 1
        elif self.alpha_state == 1 and self.alpha <= 0:
            self.alpha_state = 0
        self.image.set_alpha(self.alpha)
    
    def set_alpha(self, alpha):
        self.alpha = alpha
        self.image.set_alpha(self.alpha)

    def bounce(self, speed, time_step, is_tate=False):
        quadrant = self.__get_quadrant()
        new_angle = None
        x = None
        y = None
        # Set simple collider point based on angle quadrant
        if quadrant == 1:
            x, y = self.rect.topright
        elif quadrant == 2:
            x, y = self.rect.topleft
        elif quadrant == 3:
            x, y = self.rect.bottomleft
        elif quadrant == 4:
            x, y = self.rect.bottomright
        # Calculate new trayectory
        if x != None and y != None:
            if is_tate:
                screen_w = self.screen_h
                screen_h = self.screen_w
            else:
                screen_w = self.screen_w
                screen_h = self.screen_h
            # The angle of reflection is equal to the angle of incidence
            if x > screen_w or x < 0:
                new_angle = (180 - degrees(self.angle))
            elif y > screen_h or y < 0:
                new_angle = (360 - degrees(self.angle))
            if new_angle == 0:
                new_angle = 360
        if new_angle:
            self.set_angle(angle=new_angle)
        #logging.debug('>>> quadrant %s, new_angle %s, pos %s, rect_pos %s',quadrant, new_angle, self.position, (x,y))
        self.advance(speed, time_step)

    def wobble(self, mode, speed, limit, time_step):
        if mode == 'horizontal':
            self.__wobble_h(speed, limit, time_step)
        elif mode == 'vertical':
            self.__wobble_v(speed, limit, time_step)

    def __wobble_v(self, speed, limit, time_step):
        distance = speed * (time_step/1000)
        if not self.wobble_y_counter:
            self.wobble_y_counter = abs(limit)
        x = self.position[0]
        y = self.position[1] + distance * self.wobble_state
        if self.wobble_y_counter <= 0:
            self.wobble_y_counter = abs(limit*2)
            self.wobble_state *= -1
            # The below code corrects positions caused by python micro cuts
            if self.position[1] < self.start_pos[1] - limit:
                y = self.start_pos[1] - limit
            elif self.position[1] > self.start_pos[1] + limit:
                y = self.start_pos[1] + limit
        self.wobble_y_counter -= distance
        self.set_position(position=(x,y))

    def __wobble_h(self, speed, limit, time_step):
        distance = speed * (time_step/1000)
        if not self.wobble_x_counter:
            self.wobble_x_counter = abs(limit)
        x = self.position[0] + distance * self.wobble_state
        y = self.position[1]
        if self.wobble_x_counter <= 0:
            self.wobble_x_counter = abs(limit*2)
            self.wobble_state *= -1
            # The below code corrects positions caused by python micro cuts
            if self.position[0] < self.start_pos[0] - limit:
                x = self.start_pos[0] - limit
            elif self.position[0] > self.start_pos[0] + limit:
                x = self.start_pos[0] + limit
        self.wobble_x_counter -= distance
        self.set_position(position=(x,y))

    def blink(self, speed, time_step):
        if self.is_active:
            self.ani_elapsed_time += time_step
            if self.ani_elapsed_time > speed:
                self.ani_elapsed_time = 0
                if self.visible == 1:
                    self.hide()
                else:
                    self.show()

    def magnify(self, zoom, speed, time_step):
        if self.magnify_state == 1:
            self.magnify_elapsed_time += time_step
            duration = 1000/speed
            if self.magnify_elapsed_time > duration:
                key_frames = 8
                self.magnify_counter += 1
                current_zoom = self.original_img.get_width() * 100 / self.image.get_width()
                if current_zoom < zoom and self.magnify_counter < key_frames:
                    zoom_factor = (((zoom-100)/(key_frames-self.magnify_counter))/100)+1
                    w = self.original_img.get_width()
                    h = self.original_img.get_height()
                    new_w = w * zoom_factor
                    new_h = h * zoom_factor
                    self.image = pygame.transform.scale(self.original_img, (round(new_w), round(new_h)))
                    self.rect = self.image.get_rect()
                    # Center position
                    x = self.start_pos[0] - (new_w - w) / 2
                    y = self.start_pos[1] - (new_h - h) / 2
                    new_position = (x, y)
                    self.magnify_elapsed_time = 0
                    self.set_position(position=new_position)
                else:
                    self.set_mangnify(state=-1)
    
    '''def magnify2(self):
        # TODO - Refactor using these standard method example
        def __init__(self, center, image):
            super().__init__()
            self.original_image = image
            self.image = image
            self.rect = self.image.get_rect(center = center)
            self.mode = 1
            self.grow = 0

        def update(self):
            if self.grow > 100:
                self.mode = -1
            if self.grow < 1:
                self.mode = 1
            self.grow += 1 * self.mode 
            orig_x, orig_y = self.original_image.get_size()
            size_x = orig_x + round(self.grow)
            size_y = orig_y + round(self.grow)
            self.image = pygame.transform.scale(self.original_image, (size_x, size_y))
            self.rect = self.image.get_rect(center = self.rect.center)'''

    def draw(self):
        self.dirty = 1

    def show(self):
        self.visible = 1
        self.dirty = 1

    def hide(self):
        self.visible = 0
        self.dirty = 1

    def destroy(self, opid):
        logging.debug('OpID %s, Removing %s widget', opid, self.name)
        self.kill()

    def activate(self):
        self.is_active = True
        self.show()

    def deactivate(self):
        self.is_active = False
        self.hide()

    # Next are just placeholder interface method definitions
    def set_scroll(self, state):
        pass

    def rewind(self):
        pass        

class RtkRect(RtkSprite):
    def __init__(self, name, parent=None, is_active=True, position=(0,0), w=0, h=0, color=black, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, parent=parent, is_active=is_active, position=position, opid=opid)
        self.__load_rect(w, h, color)

    def __load_rect(self, w, h, color):
        self.image, self.rect = load_rect(w=w, h=h, color=color)

    def fill_gradient(self, start_color, final_color, vertical=True, forward=True):
        x1,x2 = self.rect.left, self.rect.right
        y1,y2 = self.rect.top, self.rect.bottom
        if vertical: h = y2-y1
        else:        h = x2-x1
        if forward: a, b = start_color, final_color
        else:       b, a = start_color, final_color
        rate = (
            float(b[0]-a[0])/h,
            float(b[1]-a[1])/h,
            float(b[2]-a[2])/h
        )
        if vertical:
            for line in range(y1,y2):
                start_color = (
                    min(max(a[0]+(rate[0]*(line-y1)),0),255),
                    min(max(a[1]+(rate[1]*(line-y1)),0),255),
                    min(max(a[2]+(rate[2]*(line-y1)),0),255)
                )
                pygame.draw.line(self.image, start_color, (x1,line), (x2,line))
        else:
            for col in range(x1,x2):
                start_color = (
                    min(max(a[0]+(rate[0]*(col-x1)),0),255),
                    min(max(a[1]+(rate[1]*(col-x1)),0),255),
                    min(max(a[2]+(rate[2]*(col-x1)),0),255)
                )
                pygame.draw.line(self.image, start_color, (col,y1), (col,y2))

class RtkBoxSprite(RtkSprite):
    def __init__(self, name, image, box_size=None, parent=None, is_active=True, position=(0,0), colorkey=None, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, image=image, parent=parent, is_active=is_active, position=position, colorkey=colorkey, opid=opid)
        # Images and rect for scroll box effects
        self.box_size = box_size
        self.box_image = pygame.Surface((self.image.get_width()*2, self.image.get_height())).convert()
        self.box_image.fill(colorkey)
        self.box_image.blit(self.image, (0, 0))
        self.box_area = [0, 0, self.image.get_width(), self.image.get_height()]
        # Cut image to the box_area size if feasible to match the image box
        try:
            box_area = [self.box_area[0], 0, self.box_size, self.image.get_height()]
            self.image = self.box_image.subsurface(box_area)
        except:
            pass
        if colorkey is not None:
            self.image.set_colorkey(colorkey, pygame.RLEACCEL)
            self.box_image.set_colorkey(colorkey, pygame.RLEACCEL)
    
    def move_box(self, num_px):
        # Calc subsurface for simulating movement inside the fixed sprite rect
        x = self.box_area[0] + num_px
        self.box_area = [x, 0, self.box_size, self.image.get_height()]
        try:
            self.image = self.box_image.subsurface(self.box_area)
        except:
            pass # Image box is smaller than box so can't move
        self.draw()

    def reset_box(self):
        self.box_area = [0, 0, self.image.get_width(), self.image.get_height()]
        try:
            self.image = self.box_image.subsurface(self.box_area)
        except:
            pass # Image box is smaller than box so can't move
        self.draw()
                
class RtkAniSprite(RtkSprite):
    def __init__(self, name, image, num_frames, flip=False, angle=0, parent=None, is_active=True, position=(0,0), colorkey=None, rev_cycle=False, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, parent=parent, is_active=is_active, angle=angle, position=position, opid=opid)
        self.current_frame = 0
        self.frames = []
        self.strip = load_image(image, colorkey=None)[0]
        self.__get_frames(image, num_frames, flip, colorkey, rev_cycle)
        self.end_frame = len(self.frames)-1
        self.start_frame = 0

    def __get_frames(self, image, num_frames, flip, colorkey, rev_cycle):
        # Get spritesheet information
        # Note: tile images must have 1px border to avoid sprite clipping rect precission issues
        x = 0
        y = 0
        frame_width = round(self.strip.get_width() / num_frames)
        frame_height = round(self.strip.get_height())
        rects = []
        counter = 1
        # Get sprite strip rects
        for frame_num in range(num_frames):
            x = frame_width * frame_num
            rect = (x, 0, frame_width, frame_height)
            rects.append(rect)
            counter += 1
        # Get images from tile sheet
        images = load_images_at(image=self.strip, rects=rects, colorkey=colorkey)
        for image in images:
            if flip:
                self.frames.append([self.__flip(image), image.get_rect()])
            else:
                self.frames.append([image, image.get_rect()])
        # Add reverse animation cycle
        if rev_cycle:
            for image in reversed(images):
                if flip:
                    self.frames.append([self.__flip(image), image.get_rect()])
                else:
                    self.frames.append([image, image.get_rect()])
            # Remove duplicated middle and end frames
            del self.frames[-1]
            del self.frames[round(len(self.frames)/2)]
        # Set initial frame
        self.__update_image()

    def __flip(self, image):
        return pygame.transform.flip(image, True, False)

    def animate(self, speed, time_step):
        self.ani_elapsed_time += time_step
        duration = 1000/speed
        if self.ani_elapsed_time > duration:
            self.current_frame += 1
            if self.current_frame > self.end_frame:
                self.current_frame = self.start_frame
            self.ani_elapsed_time = 0   
            self.__update_image()

    def __update_image(self):
        self.image = self.frames[self.current_frame][0]
        self.rect = self.frames[self.current_frame][1]
        self.set_position(self.position)

    def magnify(self, zoom, speed, time_step):
        ''' TODO '''
        pass

class RtkSelector(RtkAniSprite):
    def __init__(self, name, is_active, position, line_space, image='selector.bmp'):
        RtkAniSprite.__init__(self, name=name, image=image, num_frames=sel_num_frames, is_active=is_active, position=position, colorkey=color_key, rev_cycle=True, opid=get_random_id())
        self.line_space = line_space
        if sel_wobble:
            self.set_wobble(state=1)
        self._layer = 1

    def refresh(self):
        try:
            item_index, num_items, list_size = self.parent.get_list_info()
        except:
            item_index, num_items, list_size = 0,1,1
        x = self.position[0] #self.start_pos[0]
        y = (self.start_pos[1] + (item_index % list_size) * self.line_space)
        self.set_position(position=(x, y))

    def draw_selector(self, time_step):
        if sel_num_frames > 1:
            self.animate(speed=sel_ani_speed, time_step=time_step)
        if sel_wobble:
            self.wobble(mode=sel_wobble, speed=sel_wobble_speed, limit=sel_wobble_limit, time_step=time_step)

class RtkAniGif(RtkSprite):
    def __init__(self, name, image, parent=None, is_active=True, position=(0,0), speed=None, loop=True, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, parent=parent, is_active=is_active, position=position, opid=opid)
        self.loop = loop
        self.speed = speed
        self.__load_gif_image(image=image)
        self.frames = []
        self.__get_frames()
        self.current_frame = 0
        self.end_frame = len(self.frames)-1
        self.start_frame = 0
        self.__update_image()

    def __load_gif_image(self, image):
        img_path = os.path.join(img_dir, image)
        try:
            image = Image.open(img_path)
            rect = pygame.rect.Rect((0,0), image.size)
            self.image_gif, self.rect_gif = image, rect
        except Exception as error:
            logging.error('Cannot load image: %s, error: %s', img_path, error)

    def __get_frames(self):
        if isinstance(self.speed, str):
            self.speed = None
        image = self.image_gif
        try:
            while True:
                # Create new empty frame
                new_frame = Image.new('RGBA', image.size)
                new_frame.paste(image, (0, 0), image.convert('RGBA'))
                # Get animation speed
                if self.speed: duration = self.speed
                else:
                    try:    duration = image.info["duration"]
                    except: duration = 100
                # Transform frame into pygame format and save into frames list
                frame = pygame.image.fromstring(new_frame.tobytes(), new_frame.size, new_frame.mode)
                self.frames.append([frame, frame.get_rect(), duration])
                # Go to next frame
                image.seek(image.tell() + 1)
        except EOFError:
            pass

    def animate(self, time_step):
        if self.is_active and self.visible == 1:
            self.ani_elapsed_time += time_step
            duration = self.frames[self.current_frame][2]
            if self.ani_elapsed_time > duration:
                self.ani_elapsed_time = 0
                self.current_frame += 1
                if self.loop:
                    if self.current_frame > self.end_frame:
                        self.current_frame = self.start_frame
                    self.__update_image()
                else:
                    if self.current_frame > self.end_frame:
                        self.current_frame = self.start_frame
                        self.hide()
                    else:
                        self.__update_image()

    def rewind(self):
        if self.is_active:
            self.current_frame = self.start_frame
            self.show()
    
    def __update_image(self):
        self.image = self.frames[self.current_frame][0]
        self.rect = self.frames[self.current_frame][1]
        self.set_position(self.position)

    def magnify(self, zoom, speed, time_step):
        ''' TODO '''
        pass

class RtkText(RtkSprite):
    def __init__(self, name, text, font, is_upper=False, l_icon=None, r_icon=None, l_icon_space=True, r_icon_space=False, box_size=None, parent=None, is_active=True, fit_text=False, \
        translate=True, angle=0, position=(0,0), align='left', is_tate=False, color='default', bg_color=None, bg_border_color=None, colorkey=None, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, parent=parent, is_active=is_active, angle=angle, position=position, align=align, opid=opid)
        global translations
        self.text = text
        self.font = font
        if font == 'title':
            self.sheet = sheet_fnt_title_file
            self.font_map = title_font_map
            self.char_width = title_char_width
            self.char_height = title_char_height
            self.char_space = fnt_title_char_space
        elif font == 'list':
            self.sheet = sheet_fnt_list_file
            self.font_map = list_font_map
            self.char_width = list_char_width
            self.char_height = list_char_height
            self.char_space = fnt_list_char_space
        elif font == 'info':
            self.sheet = sheet_fnt_info_file
            self.font_map = info_font_map
            self.char_width = info_char_width
            self.char_height = info_char_height
            self.char_space = fnt_info_char_space
        elif font == 'helper':
            self.sheet = sheet_fnt_helper_file
            self.font_map = helper_font_map
            self.char_width = helper_char_width
            self.char_height = helper_char_height
            self.char_space = fnt_helper_char_space
        self.l_icon_space = l_icon_space
        self.r_icon_space = r_icon_space
        self.translate = translate
        self.is_upper = is_upper
        self.box_size = box_size
        self.fit_text = fit_text
        self.color = color
        self.bg_color = bg_color
        self.bg_border_color = bg_border_color
        self.is_tate = is_tate
        if colorkey == 'auto':
            self.colorkey = get_color_key(self.sheet)
        else:
            self.colorkey = colorkey
        self.set_scroll(0)
        self.set_text(text, l_icon, r_icon)
        self.start_pos = position

    def set_text(self, text=None, l_icon=None, r_icon=None, position=None, is_tate=None, allow_keyword=True):
        if text != None:
            self.text = text
        if is_tate != None:
            self.is_tate = is_tate
        # Get text translated as a list of chars
        if self.translate:
            text = list(get_translation(name=self.text))
        else:
            text = list(self.text)
        if self.is_upper:
            for i, char in enumerate(text):
                text[i] = char.upper()
        # Set char space
        if self.char_space == 'narrow':
            self.char_space = -2
        elif self.char_space == 'normal':
            self.char_space = 0
        elif self.char_space == 'wide':
            self.char_space = 2
        elif self.char_space == 'x-wide':
            self.char_space = 4
        # Remove last comma from lists with empty field at the end
        if text and text[-1] == ',':
            text.pop(-1)
        # Set icon
        if l_icon:
            if isinstance(l_icon, tuple) or isinstance(l_icon, list):
                icons = []
                for i in l_icon:
                    icons.insert(len(icons),i)
                if icons[-1] != ' ':
                    icons.insert(len(icons),' ')
                text = icons + text
            else:
                text.insert(0,l_icon)
                if self.l_icon_space:
                    text.insert(1,' ')
        if r_icon:
            if isinstance(r_icon, tuple) or isinstance(r_icon, list):
                icons = []
                for i in r_icon:
                    icons.insert(len(icons),i)
                if icons[-1] == ' ':
                    icons.pop(-1)
                text.append(' ')
                text = text + icons
            else:
                if self.r_icon_space:
                    text.insert(len(text),' ')
                text.insert(len(text),r_icon)
        # Get text image width
        char_w = self.char_width + self.char_space
        if '|' in text:
            self.txt_width = scr_w
            self.char_height = scr_h
        else:
            # Calculate icon sizes
            icons = 0
            is_keyword = False
            keyword_chars = 0
            if allow_keyword:
                for char in text:
                    if char == '<':
                        is_keyword = True
                    elif char == '>':
                        if is_keyword:
                            keyword_chars += 1
                            is_keyword = False
                            icons += 1
                    if is_keyword:
                        keyword_chars += 1
            icons_w = icons * char_w
            keyword_w = keyword_chars * char_w
            self.txt_width = len(text) * char_w - keyword_w + icons_w + abs(self.char_space)
        # Fit text to screen size
        num_lines = 1
        if self.fit_text:
            new_txt = []
            word = []
            counter = 0
            for i, char in enumerate(text):
                if self.is_tate:
                    is_new_line = counter * char_w + msg_text_x >= scr_h - msg_text_x
                else:
                    is_new_line = counter * char_w + msg_text_x >= scr_w - msg_text_x
                if char == ' ' or char == '|':
                    if is_new_line:
                        num_lines += 1
                        new_txt += ['|'] + word + [char]
                        counter = len(word)
                        word = []
                    else:
                        word.append(char)
                        new_txt += word
                        word = []
                        if char == '|':
                            counter = 0
                        elif char == ' ':
                            counter += 1
                else:
                    word.append(char)
                    counter += 1
                if i == len(text)-1: # Do not miss the last word at the end of the loop
                    if is_new_line:
                        num_lines += 1
                        word.insert(0,'|')
                    new_txt += word
            text = new_txt
        # Create image from image chars
        img_height = num_lines * self.char_height
        if self.bg_border_color:
            image = pygame.Surface((self.txt_width+4, img_height+4)).convert()
        else:
            image = pygame.Surface((self.txt_width, img_height)).convert()
        if self.bg_color != None:
            image.fill(self.bg_color)
        else:
            image.fill(self.colorkey)
        # Render text
        char_pos = 0
        y = 0
        key_word = ''
        is_keyword = False
        #try:
        for char in text:
            if is_keyword:
                if char == '>':
                    img_char = self.__get_char(key_word, self.colorkey)
                    if self.bg_border_color:
                        image.blit(img_char, (char_pos*char_w+2, y+2))
                    else:
                        image.blit(img_char, (char_pos*char_w, y))
                    key_word = ''
                    is_keyword = False
                    char_pos += 1
                else:
                    key_word += char
            else:
                if char == '|':
                    char_pos = 0
                    y += msg_line_space
                elif allow_keyword and char == '<':
                    is_keyword = True
                else:
                    img_char = self.__get_char(char, self.colorkey)
                    # Set text color (avoid icons)
                    if len(char) == 1 and self.color != 'default':
                        self.__change_color_char(img_char, white, self.color)
                    if self.bg_border_color:
                        image.blit(img_char, (char_pos*char_w+2, y+2))
                    else:
                        image.blit(img_char, (char_pos*char_w, y))
                    char_pos += 1
        #except Exception as error:
        #    logging.error('Error getting char/keyword: %s in font %s', error, self.font)
        # Sprite image and rect
        self.image = image
        self.original_img = self.image.copy()
        self.rect = image.get_rect()
        # Images and rect for scroll box effects
        self.oversize = 64 # This create the motion pause effect. The more pixels the longer pause
        box_r_padding = 8 # Optional free space at right side of the original image
        txt_width = self.txt_width+box_r_padding
        self.scroll_box_image = pygame.Surface((txt_width, self.char_height)).convert()
        self.scroll_box_image.fill(self.colorkey)
        self.scroll_box_image.blit(self.original_img, (0, 0))
        self.box_area = [0, 0, txt_width, self.char_height]
        # Cut image to the box_area size if feasible to match the scroll_box
        try:
            box_area = [self.box_area[0], 0, self.box_size, self.char_height]
            self.image = self.scroll_box_image.subsurface(box_area)
        except:
            pass
        # Set colorkey transparency
        if self.colorkey is not None:
            self.image.set_colorkey(self.colorkey, pygame.RLEACCEL)
            self.original_img.set_colorkey(self.colorkey, pygame.RLEACCEL)
            self.scroll_box_image.set_colorkey(self.colorkey, pygame.RLEACCEL)
        # Set position
        if position:
            self.set_position(position,self.is_tate)
        else:
            self.set_position(self.position,self.is_tate)
        # Add surface border
        if self.bg_border_color:
            w = self.image.get_width()
            h = self.image.get_height()
            pygame.draw.rect(self.image, self.bg_border_color, (0, 0, w, h), 1)

    def truncate(self,max_size):
        try:
            #logging.info('RTK Truncate: %s, %s', self.text, max_size)
            self.image = self.image.subsurface(0,0,max_size,self.image.get_height())
            img_char = self.__get_char(char='elipsis',colorkey=None)
            self.image.blit(img_char, (max_size-self.char_width, 0))
        except Exception as error:
            pass

    def update_scroll_box(self, box_size):
        self.box_size = box_size
        box_r_padding = 8 # Optional free space at right side of the original image
        txt_width = self.txt_width+box_r_padding
        self.scroll_box_image = pygame.Surface((txt_width, self.char_height)).convert()
        self.scroll_box_image.fill(self.colorkey)
        self.scroll_box_image.blit(self.original_img, (0, 0))
        self.box_area = [0, 0, txt_width, self.char_height]
        # Set colorkey transparency
        if self.colorkey is not None:
            self.scroll_box_image.set_colorkey(self.colorkey, pygame.RLEACCEL)
        try:
            self.image = self.original_img.subsurface(0, 0, self.box_size, self.char_height)
        except:
            pass

    def change_color(self, color, repcolor):
        RtkSprite.change_color(self, color, repcolor)
        # Apply to main image
        pixel_array = pygame.PixelArray(self.scroll_box_image)
        pixel_array.replace(color, repcolor)
        pixel_array.close()
        self.dirty = 1
        self.color = repcolor
    
    def __change_color_char(self, char, color, repcolor):
        pixel_array = pygame.PixelArray(char)
        pixel_array.replace(color, repcolor)
        pixel_array.close()

    def __get_char(self, char, colorkey):
        try:
            if len(char) > 1: # lower key words
                char = char.lower()
            x = int(self.font_map[char][0])
            y = int(self.font_map[char][1])
            w = int(self.font_map[char][2])
            h = int(self.font_map[char][3])
            rectangle = (x, y, w, h)
            # Extract char image from sheet
            char = load_image_at(image=self.sheet, rectangle=rectangle, colorkey=colorkey)
        except:
            char = load_image_at(image=self.sheet, rectangle=(0, 0, 1, 1), colorkey=colorkey)
        return char

    def set_scroll(self, state):
        self.scroll_state = state # -1 left 0 stop 1 rigth

    def scroll(self, speed, limit, time_step):
        # Calc movement direction
        start_x = self.start_pos[0]
        collider_margin = 16 # Add free space at both sides of the collider
        if self.scroll_state in (0, 1):
            x, y = self.position
            if self.scroll_state == 0:
                self.set_position(position=self.start_pos)
            elif self.scroll_state == 1:
                if x > start_x + collider_margin:
                    self.scroll_state = -1
        elif self.scroll_state == -1:
            x, y = self.rect.topright
            if x < limit - collider_margin:
                self.scroll_state = 1
        # Move text
        x, y = self.position
        x += speed*(time_step/1000) * self.scroll_state
        self.set_position((x, y))

    def scroll_box(self, speed, time_step):
        # Calc subsurface for simulating movement inside the fixed sprite rect
        x = self.box_area[0]
        x -= speed*(time_step/1000) * self.scroll_state
        min_x = 0
        max_x = int(self.scroll_box_image.get_width() - self.box_size)
        if x < min_x - self.oversize:
            x = min_x
            self.scroll_state *= -1
        elif x > max_x + self.oversize:
            x = max_x
            self.scroll_state *= -1
        self.box_area = [x, 0, self.box_size, self.char_height]
        try:
            self.image = self.scroll_box_image.subsurface(self.box_area)
        except:
            pass # Text box is smaller than scroll box so no need to scroll
        self.draw()

    def magnify(self, zoom, speed, time_step):
        '''
            TODO 
            Not working with scroll box text
        '''
        RtkSprite.magnify(self, zoom, speed, time_step)

class RtkScrollBg(RtkSprite):
    def __init__(self, name, image, type='h', parent=None, is_active=True, position=(0,0), is_tate=False, colorkey=None, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, image=image, parent=parent, is_active=is_active, position=position, colorkey=colorkey, opid=opid)
        self.type = type
        self.is_tate = is_tate
        self.img_bg = self.image.copy()
        self.set_scroll(-1)
        self.x = 0
        self.y = 0

    def set_scroll(self, state):
        self.scroll_state = state # h: -1 left 1 rigth v: -1 up 1 down

    def scroll(self, speed, time_step):
        if self.type == 'h':
            self.__scroll_h(speed, time_step)
        elif self.type == 'v':
            self.__scroll_v(speed, time_step)

    def __scroll_h(self, speed, time_step):
        if self.is_tate:
            scr_x = self.screen_h
        else:
            scr_x = self.screen_w
        rel_x = self.x % self.rect.width
        self.image.blit(self.img_bg, (rel_x - self.rect.width,0))
        if rel_x < scr_x:
            self.image.blit(self.img_bg, (rel_x, 0))
        self.x += speed*(time_step/1000) * self.scroll_state
        self.draw()

    def __scroll_v(self, speed, time_step):
        if self.is_tate:
            scr_y = self.screen_w
        else:
            scr_y = self.screen_h
        rel_y = self.y % self.rect.height
        self.image.blit(self.img_bg, (0, rel_y - self.rect.height))
        if rel_y < scr_y:
            self.image.blit(self.img_bg, (0, rel_y))
        self.y += speed*(time_step/1000) * self.scroll_state
        self.draw()

class RtkParallaxBg(RtkSprite):
    def __init__(self, name, image, type='h', parent=None, is_active=True, position=(0,0), opid=get_random_id()):
        RtkSprite.__init__(self, name=name, image=image, parent=parent, is_active=is_active, position=position, opid=opid)
        self.type = type
        self.img_bg = self.image.copy()
        self.__load_images()
        self.set_scroll(-1)

    def __load_images(self):
        self.images = []
        if self.type == 'h':
            self.num_tiles = 30
            self.tile_size = 8
            self.x = [0] * self.num_tiles
            for i in range(self.num_tiles):
                tile_rect = [0, i*self.tile_size, self.rect.width, self.tile_size]
                self.images.append(self.img_bg.subsurface(tile_rect))
        elif self.type == 'v':
            self.num_tiles = 20
            self.tile_size = 16
            self.y = [0] * self.num_tiles
            for i in range(self.num_tiles):
                tile_rect = [i*self.tile_size, 0, self.tile_size, self.rect.height]
                self.images.append(self.img_bg.subsurface(tile_rect))

    def set_scroll(self, state):
        self.scroll_state = state # h: -1 left 1 rigth v: -1 up 1 down

    def scroll(self, speed, time_step):
        if self.type == 'h':
            self.__scroll_h(speed, time_step)
        elif self.type == 'v':
            self.__scroll_v(speed, time_step)

    def __scroll_h(self, speed, time_step):
        for i, image in enumerate(self.images):
            rel_x = self.x[i] % self.rect.width
            self.image.blit(self.images[i], (rel_x-self.rect.width, i*self.tile_size))
            if rel_x < self.screen_w:
                self.image.blit(self.images[i], (rel_x, i*self.tile_size))
            self.x[i] += speed[i]*(time_step/1000) * self.scroll_state
        self.draw()

    def __scroll_v(self, speed, time_step):
        for i, image in enumerate(self.images):
            rel_y = self.y[i] % self.rect.height
            self.image.blit(self.images[i], (i*self.tile_size, rel_y-self.rect.height))
            if rel_y < self.screen_h:
                self.image.blit(self.images[i], (i*self.tile_size, rel_y))
            self.y[i] += speed[i]*(time_step/1000) * self.scroll_state
        self.draw()

class RtkContainerMgr:
    def __init__(self):
        logging.debug('Created %s', type(self).__name__)
        self.containers = {}
        self.create(name='Window', opid=get_random_id()) # Create main parent container

    def create(self, name, parent=None, is_active=True, opid=get_random_id()):
        logging.debug('OpID %s, RtkContainerMgr create', opid)
        if name in self.containers:
            logging.debug('OpID %s, Duplicated container found', opid)
            self.destroy(name, opid)
        self.containers[name] = RtkContainer(name, parent, is_active, opid=opid)
        self.containers['Window'].append(self.containers[name], opid)
        logging.debug('OpID %s, The total number of containers %s is %s', opid, list(self.containers.keys()), len(self.containers))
        return self.containers[name]

    def append(self, parent, child, opid=get_random_id()):
        logging.debug('OpID %s, RtkContainerMgr append', opid)
        # If child widget has already a parent, remove all widgets from parent
        if isinstance(child, tuple) or isinstance(child, list):
            for c in child:
                if c.parent:
                    c.parent.remove(c, opid)
        else:
            if child.parent:
                child.parent.remove(child, opid)
        # Add child to the new parent
        parent.append(child, opid)

    def destroy(self, name, opid=get_random_id()):
        logging.debug('OpID %s, RtkContainerMgr destroy', opid)
        if name in self.containers:
            logging.debug('OpID %s, Removing %s container', opid, name)
            self.containers[name].destroy(opid)
            self.containers.pop(name)
            logging.debug('OpID %s, The total number of containers %s is %s', opid, list(self.containers.keys()), len(self.containers))

class RtkContainer:
    def __init__(self, name, parent=None, is_active=True, opid=get_random_id()):
        self.name = name
        self.parent = parent
        logging.debug('OpID %s, Created %s %s', opid, type(self).__name__, self.name)
        self.is_active = is_active
        self.is_sprite = False
        self.widgets = []

    def set_parent(self, par_obj):
        self.parent = par_obj

    def handle(self, event):
        print(self.name,'event:',event)
        handler = f'handle_{event}'
        if hasattr(self, handler):
            method = getattr(self, handler)
            print(self.name,'method:',handler)
            method(event)
        elif self.parent is not None:
            self.parent.handle(event)
        elif hasattr(self, 'handle_default'):
            self.handle_default(event)

    def handle_test(self, event):
        print(self.name,'handle_test:',event)

    def handle_default(self, event):
        logging.debug('%s, handle_default %s', self.name, event)

    def append(self, widget, opid=get_random_id()):
        def add(widget):
            self.widgets.append(widget)
            widget.set_parent(par_obj=self)
            if widget.is_sprite:
                # To avoid in-memory duplicated sprites (memory leak), sprite names must be unique
                for sprite in all_sprites:
                    if widget.name == sprite.name:
                        all_sprites.remove(sprite)
                all_sprites.add(widget)
                logging.debug('OpID %s, The total number of sprites is %s', opid, len(all_sprites))
        if isinstance(widget, tuple) or isinstance(widget, list):
            logging.debug('OpID %s, Appending widgets to %s container', opid, self.name)
            for w in widget:
                if w.is_sprite:
                    add(w)
                    logging.debug('OpID %s, Container %s appened to %s container', opid, w.name, self.name)
                else:
                    add(w)
                    logging.debug('OpID %s, Sprite %s appened to %s container', opid, w.name, self.name)
            logging.debug('OpID %s, The number of widgets in %s container is %s', opid, self.name, len(self.widgets))
        else:
            if widget.is_sprite:
                logging.debug('OpID %s, Appending %s sprite to container %s', opid, widget.name,self.name)
                add(widget)
                logging.debug('OpID %s, The number of widgets in %s container is %s', opid, self.name, len(self.widgets))
            else:
                logging.debug('OpID %s, Appending %s container to %s container', opid, widget.name, self.name)
                add(widget)
                logging.debug('OpID %s, The number of widgets in %s container is %s', opid, self.name, len(self.widgets))

    def move(self, displacement):
        # Change child positions
        for widget in self.widgets:
            widget.move(displacement)

    def remove(self, widget, opid):
        logging.debug('OpID %s, Removing %s widget from %s container', opid, widget.name, self.name)
        self.widgets.remove(widget)
        widget.destroy(opid)
        logging.debug('OpID %s, The number of widgets in %s container is %s', opid, self.name, len(self.widgets))

    def show(self):
        for widget in self.widgets:
            widget.show()

    def hide(self):
        for widget in self.widgets:
            widget.hide()

    def destroy(self, opid):
        # Destroy child widgets
        for widget in self.widgets:
            widget.destroy(opid)
        # Destroy parent link
        logging.debug('OpID %s, Removing %s container from parent %s container', opid, self.name, self.parent.name)
        try:
            self.parent.remove(self, opid)
        except:
            logging.debug('OpID %s, %s container was not in parent. Nothing removed', opid, self.name)

    def activate(self):
        self.is_active = True
        for widget in self.widgets:
            widget.activate()

    def deactivate(self):
        self.is_active = False
        for widget in self.widgets:
            widget.deactivate()

class RtkTextList(RtkContainer):
    def __init__(self, name, text, font, translate, line_space, list_size, box_size, is_upper=False, color='default', color_select='default', bg_color=None, \
        position=(0,0), align='left', parent=None, is_active=True, opid=get_random_id()):
        RtkContainer.__init__(self, name=name, parent=parent, is_active=is_active, opid=opid)
        self.position = position
        self.align = align
        self.font = font
        self.translate = translate
        self.box_size = box_size
        self.line_space = line_space
        self.list_size = list_size
        self.color = color
        self.color_sel = color_select
        self.bg_color = bg_color
        self.opid = opid
        self.is_upper = is_upper
        self.is_tate = False
        self.set_txt_list(text)

    def set_position(self, position, is_tate=False):
        self.position = position
        self.is_tate = is_tate
        self.refresh(force_refresh=True)

    def set_txt_list(self, text, l_icon_space=True, r_icon_space=False, index=0):
        self.index = index
        self.l_icon_space = l_icon_space
        self.r_icon_space = r_icon_space
        self.page = -1
        self.txt_list = text # Text list (all items)
        self.txt_items = [] # Sprite based list (curret page items)
        self.txt_items_selected = [] # Same as txt_items but including selected item
        self.num_lines = len(self.txt_list)
        self.max_item_sizes = []
        # TODO - Pagination in memory
        '''self.pre_load()'''
        self.refresh()

    def set_max_sizes(self, max_item_sizes):
        self.max_item_sizes = max_item_sizes
        self.refresh(force_refresh=True)

    def get_list_info(self):
        return self.index, self.num_lines, self.list_size

    def goto_next_item(self):
        if(self.index == self.num_lines - 1):
            self.index = 0
        else:
            self.index += 1
        self.refresh()

    def goto_prev_item(self):
        if(self.index == 0):
            self.index = self.num_lines - 1
        else:
            self.index -= 1
        self.refresh()

    def goto_next_page(self):
        num_pages = ceil(self.num_lines / self.list_size)
        if num_pages > 1:
            jump_to = self.index + 1 + self.list_size
            if jump_to >= self.num_lines:
                # Check if jump item is in the same page or in next page
                if ceil(self.num_lines/self.list_size) - ceil(float(self.index+1)/self.list_size) == 1: # In next page
                    self.index = self.num_lines - 1
                elif ceil(self.num_lines/self.list_size) - ceil(float(self.index+1)/self.list_size) == 0: # In same page
                    self.index = 0
            else:
                self.index = jump_to - 1
        else:
            self.index = self.num_lines - 1
        self.refresh()

    def goto_prev_page(self):
        num_pages = ceil(self.num_lines / self.list_size)
        if num_pages > 1:
            jump_to = self.index - self.list_size
            if jump_to < 0:
                self.index = self.num_lines - 1
            else:
                self.index = jump_to
        else:
            self.index = 0
        self.refresh()

    def get_txt_item_sizes(self):
        txt_item_sizes = []
        for item in self.txt_items_selected:
            txt_item_sizes.append(item.txt_width)
        return txt_item_sizes
    
    def pre_load(self):
        x, y = self.position
        self.txt_items = []
        for i, line in enumerate(self.txt_list):
            if '|' in line:
                line = line.split('|')
                l_icon = line[0]
                text   = line[1]
                try: r_icon = line[2]
                except: r_icon = None
                try: color = eval(line[3])
                except: color = self.color
            else:
                l_icon = None
                text   = line
                r_icon = None
                color = self.color
            self.txt_items.append(RtkText(name=self.name+'_Item'+str(i), text=text, is_upper=self.is_upper, l_icon=l_icon, r_icon=r_icon, \
                l_icon_space=self.l_icon_space, r_icon_space=self.r_icon_space, font=self.font, position=(x,y), align=self.align, box_size=self.box_size, \
                translate=self.translate, color=color, colorkey=color_key, is_active=self.is_active, is_tate=self.is_tate))
            y += self.line_space

    def refresh(self, force_refresh=False):
        # Recreate text object items based on current index page
        x, y = self.position
        current_page = int(self.index / self.list_size)
        # Create on screen text items
        if self.page != current_page or force_refresh:
            self.txt_items = []
            self.page = current_page
            for i, line in enumerate(self.txt_list):
                item_page = int(i / self.list_size)
                if item_page == current_page:
                    if '|' in line:
                        line = line.split('|')
                        l_icon = line[0]
                        text   = line[1]
                        try: r_icon = line[2]
                        except: r_icon = None
                        try: color = eval(line[3])
                        except: color = self.color
                    else:
                        l_icon = None
                        text   = line
                        r_icon = None
                        color = self.color
                    self.txt_items.append(RtkText(name=self.name+'_Item'+str(i), text=text, is_upper=self.is_upper, l_icon=l_icon, r_icon=r_icon, \
                        l_icon_space=self.l_icon_space, r_icon_space=self.r_icon_space, font=self.font, position=(x,y), align=self.align, box_size=self.box_size, \
                        translate=self.translate, color=color, colorkey=color_key, is_active=self.is_active, is_tate=self.is_tate))
                    y += self.line_space
                elif item_page > current_page:
                    break
        # Create selected text item
        selected_item_index = self.index % self.list_size
        y = self.txt_items[selected_item_index].position[1]
        line = self.txt_list[self.index]
        if '|' in line:
            line = line.split('|')
            l_icon = line[0]
            text   = line[1]
            try: r_icon = line[2]
            except: r_icon = None
        else:
            l_icon = None
            text   = line
            r_icon = None
        self.selected_item = RtkText(name=self.name+'_Item_Selected', text=text, is_upper=self.is_upper, l_icon=l_icon, r_icon=r_icon, \
            l_icon_space=self.l_icon_space, r_icon_space=self.r_icon_space, font=self.font, position=(x,y), align=self.align, box_size=self.box_size, \
            translate=self.translate, color=self.color_sel, bg_color=self.bg_color, colorkey=color_key, is_active=self.is_active, is_tate=self.is_tate)
        self.selected_item.set_scroll(state=1)
        # Update the selected object in the item list
        self.txt_items_selected = []
        for i, item in enumerate(self.txt_items):
            if i == selected_item_index:
                if self.max_item_sizes:
                    self.selected_item.update_scroll_box(self.max_item_sizes[i]*8)
                self.txt_items_selected.append(self.selected_item)
            else:
                if self.is_active and not self.txt_items[i].is_active:
                    self.txt_items[i].activate()
                if self.max_item_sizes:
                    size = self.max_item_sizes[i]*8
                    self.txt_items[i].truncate(size)
                self.txt_items_selected.append(self.txt_items[i])
        logging.debug('Number of items in %s = %s', self.name, len(self.txt_items_selected))
        # Append all text list items as widgets
        self.append_widgets()
        # Refresh all child widget indicators
        self.refresh_indicators()

    def append(self, widget, opid=get_random_id()):
        RtkContainer.append(self, widget, self.opid)
        self.refresh_indicators()

    def refresh_indicators(self):
        items = ('RtkPageIndicator','RtkSelector')
        for widget in self.widgets:
            if type(widget).__name__ in items:
                widget.refresh()

    def append_widgets(self):
        self.destroy_widgets()
        RtkContainer.append(self, self.txt_items_selected, self.opid)

    def destroy_widgets(self):
        # Destroy child widgets
        for widget in self.widgets:
            if type(widget).__name__ == 'RtkText':
                widget.destroy(self.opid)
        # Remove all widgets from list except the indicators
        indicators = ('RtkPageIndicator','RtkSelector')
        self.widgets[:] = [widget for widget in self.widgets if type(widget).__name__ in indicators]

    def move(self, displacement):
        RtkContainer.move(self, displacement)
        x = self.position[0] + displacement[0]
        y = self.position[1] + displacement[1]
        self.position = (x, y)
        self.refresh(force_refresh=True)

    def hide_selector(self):
        for widget in self.widgets:
            if type(widget).__name__ == 'RtkSelector':
                widget.hide()
                break
    
    def show_selector(self):
        for widget in self.widgets:
            if type(widget).__name__ == 'RtkSelector':
                widget.show()
                break

    def scroll_item_sel(self, speed, time_step):
        self.selected_item.scroll_box(speed, time_step)

    def anim_selector(self, time_step):
        for widget in self.widgets:
            if type(widget).__name__ == 'RtkSelector':
                widget.draw_selector(time_step)
                break

class RtkPageIndicator(RtkText):
    def __init__(self, name, font, text='[0/0]', color='default', is_active=True, position=(0,0), colorkey=None, opid=get_random_id()):
        RtkText.__init__(self, name=name+'_PageIndicator', text=text, font=font, color=color, position=position, is_active=is_active, colorkey=colorkey, opid=opid)
        self.page_info = text
        self._layer = 3
        self.refresh()

    def refresh(self):
        # Refresh page info
        try:
            item_index, num_items, list_size = self.parent.get_list_info()
        except:
            item_index, num_items, list_size = 0,1,1
        current_page = floor(item_index / list_size) + 1
        total_pages = int(ceil(num_items / list_size))
        # Create page info
        page_info = '[' + str(current_page) + '/' + str(total_pages) + ']'
        if self.page_info != page_info:
            self.set_text(text=page_info)
            self.page_info = page_info

class RtkTxtMsg(RtkContainer):
    def __init__(self, name, type, text, txt_color, bg_color, bg_border_color=None, duration=-1, title=None, parent=None, is_active=False, position=('center','center'), opid=get_random_id()):
        RtkContainer.__init__(self, name=name, parent=parent, is_active=is_active, opid=opid)
        self.type = type
        self.title = title
        self.text = text
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.bg_border_color = bg_border_color
        self.duration = duration * 1000
        self.position = position
        self.opid = opid
        self.msg_items = []
        self.elapsed_time = 0
        self.allow_hide = True
        self.is_tate = False
        self.refresh()

    def set_text(self, text, l_icon=None, title=None):
        self.title = title
        self.text = text
        for widget in self.widgets:
            if 'Title' in widget.name:
                widget.set_text(text=title)
                widget.set_position(position=(msg_title_x,msg_title_y),is_tate=self.is_tate)
            elif 'Msg' in widget.name:
                if self.type == 'popup':
                    widget.set_text(text=text,l_icon=l_icon)
                    widget.set_position(position=('center','center'),is_tate=self.is_tate)
                else:
                    widget.set_text(text=text)

    def refresh(self):
        # Create on screen text items
        if self.type == 'full':
            # BG
            if self.bg_color:
                bg = RtkRect(name=self.name + 'Bg', color=self.bg_color, w=scr_w, h=scr_h, is_active=self.is_active)
                if msg_bg_gradient:
                    bg.fill_gradient(self.bg_color, black, vertical=True, forward=True)
                bg._layer = 6
                self.msg_items.append(bg)
            # Title
            title = RtkText(name=self.name + 'Title', text=self.title, font='title', is_upper=True, color=msg_title_color, \
                is_active=self.is_active, position=(msg_title_x,msg_title_y), colorkey=color_key)
            title._layer = 6
            self.msg_items.append(title)
            # Text message
            text = RtkText(name=self.name + 'Msg', text=self.text, font='list', color=self.txt_color, fit_text=True, \
                is_active=self.is_active, position=(msg_text_x, msg_text_y), colorkey=color_key)
            text._layer = 6
            self.msg_items.append(text)
        elif self.type == 'popup':
            text = RtkText(name=self.name + 'Msg', text=self.text, font='list', color=self.txt_color, bg_color=self.bg_color, bg_border_color=self.bg_border_color, \
                is_active=self.is_active, position=('center','center'), colorkey=color_key)
            text._layer = 4
            self.msg_items.append(text)        
        # Append all text list items as widgets
        self.append_widgets()

    def append_widgets(self):
        self.destroy_widgets()
        RtkContainer.append(self, self.msg_items, self.opid)

    def destroy_widgets(self):
        # Destroy child widgets
        for widget in self.widgets:
            widget.destroy(self.opid)
        # Remove all widgets from list
        self.widgets.clear()

    def move(self, displacement):
        RtkContainer.move(self, displacement)
        x = self.position[0] + displacement[0]
        y = self.position[1] + displacement[1]
        self.position = (x, y)
        self.refresh()

    def show(self):
        self.is_active = True
        self.elapsed_time = 0
        for item in self.msg_items:
            item.activate()

    def hide(self):
        self.is_active = False
        for item in self.msg_items:
            item.deactivate()

    def set_rotation(self, is_tate):
        self.is_tate = is_tate
    
    def draw_msg(self, time_step):
        self.elapsed_time += time_step
        if self.duration < 0 or self.elapsed_time < self.duration:
            for item in self.msg_items:
                item.draw()
        else:
            self.hide()

    def display(self, text, l_icon=None, title=None, allow_hide=True):
        self.allow_hide = allow_hide
        self.set_text(title=title,l_icon=l_icon,text=text)
        self.show()
        render()

class RtkVKbLayout(RtkSprite):
    def __init__(self, name, bg_color, border_color, txt_box_color, txt_box_border_color, position, parent=None, is_active=True, colorkey=None, opid=get_random_id()):
        RtkSprite.__init__(self, name=name, parent=parent, is_active=is_active, position=position, opid=opid)
        self.chars = ('A','B','C','D','E','F','G','H','I','J','K','L','M',
                    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                    'a','b','c','d','e','f','g','h','i','j','k','l','m',
                    'n','o','p','q','r','s','t','u','v','w','x','y','z',
                    '1','2','3','4','5','6','7','8','9','0','#','/','\\',
                    '*','@','$','%','&','=','[',']','{','}','<','>',' ',
                    '-','_','.',',',':',';',"'",'!','?','(',')','del','end')
        self.row_num_chars = 13
        self.bg_color = bg_color
        self.border_color = border_color
        self.txt_box_border_color = txt_box_border_color
        self.txt_box_color = txt_box_color
        self.color_key = colorkey
        self.vkeyb_x_margin = 6
        self.vkeyb_y_margin = 5
        self.vkeyb_char_space = 16
        self.font_map = list_font_map
        self.sheet = sheet_fnt_list_file
        self.char_height = list_char_height
        self.gen_keyboard()

    def gen_keyboard(self):
        # Keyboard background
        width = self.row_num_chars * self.vkeyb_char_space + self.vkeyb_x_margin
        height = int((len(self.chars) / self.row_num_chars * self.char_height) + self.vkeyb_y_margin * 2 + self.char_height * 2)
        self.keyboard = pygame.Surface((width, height)).convert()
        self.keyboard.fill(self.bg_color)
        pygame.draw.rect(self.keyboard, self.border_color, (0,0,width, height), 1)
        # Text box background
        width = self.row_num_chars * self.vkeyb_char_space + self.vkeyb_x_margin
        height = self.char_height * 2
        txt_box = pygame.Surface((width, height)).convert()
        txt_box.fill(self.txt_box_color)
        pygame.draw.rect(txt_box, self.txt_box_border_color, (0,0,width, height), 1)
        self.keyboard.blit(txt_box, (0, 0))
        # Keyboard layout
        x = 0
        y = self.char_height * 2
        for i, char in enumerate(self.chars):
            if i > 0 and int(i % self.row_num_chars) == 0:
                x = 0
                y += self.char_height
            img_char = self.__get_char(char, self.color_key)
            self.keyboard.blit(img_char, (x+self.vkeyb_x_margin, y+self.vkeyb_y_margin))
            x += self.vkeyb_char_space
        self.image = self.keyboard
        self.original_img = self.image.copy()
        self.rect = self.keyboard.get_rect()
        self.set_position(self.position)

    def __get_char(self, char, colorkey):
        x = int(self.font_map[char][0])
        y = int(self.font_map[char][1])
        w = int(self.font_map[char][2])
        h = int(self.font_map[char][3])
        rectangle = (x, y, w, h)
        # Extract char image from sheet
        char = load_image_at(image=self.sheet, rectangle=rectangle, colorkey=colorkey)
        return char

class RtkVirtuaKb(RtkContainer):
    def __init__(self, name, text, bg_color, border_color, txt_box_color, txt_box_border_color, \
        position=(0,0), parent=None, is_active=True, opid=get_random_id()):
        RtkContainer.__init__(self, name=name, parent=parent, is_active=is_active, opid=opid)
        self.bg_color = bg_color,
        self.border_color = border_color,
        self.txt_box_color = txt_box_color,
        self.txt_box_border_color = txt_box_border_color
        self.is_active = is_active
        self.position = position
        self.opid = opid
        self.gen_vkeyb(text)

    def gen_vkeyb(self, text):
        self.selector_index = 0
        self.vkeyb_x_margin = 6
        self.vkeyb_y_margin = 5
        self.vkeyb_items = [] # Sprite based list
        self.text_box = []
        # Virtual Keyboard Layout
        self.vkeyb_layout = RtkVKbLayout(
            name                 = 'vkeyb_layout',
            bg_color             = self.bg_color,
            border_color         = self.border_color,
            txt_box_color        = self.txt_box_color,
            txt_box_border_color = self.txt_box_border_color,
            position             = (self.position),
            is_active            = self.is_active,
            colorkey             = color_key)
        self.position = self.vkeyb_layout.position
        self.row_num_chars = self.vkeyb_layout.row_num_chars
        self.chars = self.vkeyb_layout.chars
        self.vkeyb_char_space = self.vkeyb_layout.vkeyb_char_space
        # Character selector
        vkeyb_char_sel_pos = (self.position[0] + 3 , self.position[1] + (list_char_height * 2) + 4)
        self.vkeyb_char_sel = RtkSprite(
            name      = 'vkeyb_char_sel',
            image     = 'vkeyb_char_sel.bmp',
            position  = vkeyb_char_sel_pos,
            is_active = self.is_active,
            colorkey  = color_key)
        # Text box
        vkeyb_vkeyb_text_box_pos = (self.position[0] + self.vkeyb_x_margin, self.position[1] + self.vkeyb_y_margin)
        self.vkeyb_text_box = RtkText(
            name      = 'vkeyb_text_box',
            text      = text,
            translate = False,
            is_active = self.is_active,
            font      = 'list',
            position  = vkeyb_vkeyb_text_box_pos,
            colorkey  = color_key)
        # Typing Cursor
        vkeyb_vkeyb_cursor_pos = (self.position[0] + self.vkeyb_x_margin, self.position[1] + self.vkeyb_y_margin + 4)
        self.vkeyb_cursor = RtkSprite(
            name      = 'vkeyb_cursor',
            is_active = self.is_active,
            position  = vkeyb_vkeyb_cursor_pos,
            image     = 'vkeyb_cursor.bmp',
            colorkey  = color_key)
        # Append all items as widgets
        self.vkeyb_items.append(self.vkeyb_layout)
        self.vkeyb_items.append(self.vkeyb_char_sel)
        self.vkeyb_items.append(self.vkeyb_text_box)
        self.vkeyb_items.append(self.vkeyb_cursor)
        self.append_widgets()

    def append(self, widget, opid=get_random_id()):
        RtkContainer.append(self, widget, self.opid)

    def append_widgets(self):
        self.destroy_widgets()
        RtkContainer.append(self, self.vkeyb_items, self.opid)

    def destroy_widgets(self):
        # Destroy child widgets
        for widget in self.widgets:
            widget.destroy(self.opid)
        # Remove all widgets from list
        self.widgets.clear()

    def move(self, displacement):
        RtkContainer.move(self, displacement)
        x = self.position[0] + displacement[0]
        y = self.position[1] + displacement[1]
        self.position = (x, y)

    def set_position(self, position, is_tate):
        # Virtual Keyboard Layout
        self.vkeyb_layout.set_position(position, is_tate)
        self.position = self.vkeyb_layout.position
        # Text box
        vkeyb_vkeyb_text_box_pos = (self.position[0] + self.vkeyb_x_margin, self.position[1] + self.vkeyb_y_margin)
        self.vkeyb_text_box.set_position(vkeyb_vkeyb_text_box_pos, is_tate=is_tate)
        # Typing Cursor
        self.__set_cursor_position()
        # Character selector
        self.__set_char_selector_position()

    def __get_value(self):
        value = ''.join(self.text_box)
        if not value:
            value = ''
        return value

    def clear_value(self):
        self.selector_index = 0
        self.text_box = []
        self.vkeyb_text_box.set_text(text='', allow_keyword=False)
        self.__set_cursor_position()
        self.__set_char_selector_position()

    def set_text(self, text):
        self.text_box = []
        for char in text:
            self.text_box.append(char)
        self.vkeyb_text_box.set_text(text=text[-24:], allow_keyword=False)
        self.__set_cursor_position()
        self.__set_char_selector_position()
    
    def select_char(self, char=None):
        if char:
            char = char
        else:
            char = self.chars[self.selector_index]
        if char == 'end':
            value = 'key_end'
            self.clear_value()
        elif char == 'del':
            value = self.delete_last_char()
        else:
            if len(self.text_box) < 24:
                self.text_box.append(self.chars[self.selector_index])
                value = self.__get_value()
                self.vkeyb_text_box.set_text(text=value[-24:], allow_keyword=False)
                self.__set_cursor_position()
            else:
                self.text_box.append(self.chars[self.selector_index])
                value = self.__get_value()
                self.vkeyb_text_box.set_text(text=value[-24:], allow_keyword=False)
                self.__set_cursor_position()
        return value

    def __set_cursor_position(self):
        vkeyb_vkeyb_cursor_pos_x = self.position[0] + self.vkeyb_x_margin + self.vkeyb_text_box.image.get_width()
        vkeyb_vkeyb_cursor_pos_y = self.position[1] + self.vkeyb_y_margin + 4
        self.vkeyb_cursor.set_position((vkeyb_vkeyb_cursor_pos_x,vkeyb_vkeyb_cursor_pos_y))

    def __set_char_selector_position(self):
        vkeyb_char_sel_pos_x = self.position[0] + (self.vkeyb_char_space * (self.selector_index % self.row_num_chars)) + 3
        vkeyb_char_sel_pos_y = self.position[1] + (list_char_height * int(self.selector_index / self.row_num_chars)) + (list_char_height * 2) + 4
        if self.selector_index == len(self.chars)-1:
            vkeyb_char_sel_pos_x +=1
        self.vkeyb_char_sel.set_position((vkeyb_char_sel_pos_x,vkeyb_char_sel_pos_y))

    def delete_last_char(self):
        if len(self.text_box) > 0:
            del self.text_box[-1]
            value = self.__get_value()
            self.vkeyb_text_box.set_text(text=value[-24:], allow_keyword=False)
            self.__set_cursor_position()
        else:
            value = self.__get_value()
        return value

    def move_prev_key(self):
        if self.selector_index % self.row_num_chars == 0:
            self.selector_index += self.row_num_chars - 1
        elif self.selector_index > 0:
            self.selector_index -= 1
        self.__set_char_selector_position()

    def move_next_key(self):
        if (self.selector_index + 1) % self.row_num_chars == 0:
            self.selector_index -= self.row_num_chars - 1
        elif self.selector_index < len(self.chars)-1:
            self.selector_index += 1
        self.__set_char_selector_position()

    def move_prev_row(self):
        if int(self.selector_index / self.row_num_chars) == 0:
            self.selector_index += int((len(self.chars)-1) / self.row_num_chars) * self.row_num_chars
        elif int(self.selector_index / self.row_num_chars) > 0:
            self.selector_index -= self.row_num_chars
        self.__set_char_selector_position()

    def move_next_row(self):
        if int((self.selector_index + (self.row_num_chars - 1)) / self.row_num_chars) > int((len(self.chars)-1) / self.row_num_chars):
            self.selector_index = self.selector_index % self.row_num_chars
        elif int(self.selector_index / self.row_num_chars) < int((len(self.chars)-1) / self.row_num_chars):
            self.selector_index += self.row_num_chars
        else:
            self.selector_index = 0
        self.__set_char_selector_position()

    def animate(self, time_step):
        self.vkeyb_char_sel.blink(speed=96,time_step=time_step)
        self.vkeyb_cursor.blink(speed=96,time_step=time_step)

def load_theme(name, is_tate):
    global cfg_theme, sheet_fnt_title_file, sheet_fnt_list_file, sheet_fnt_info_file, sheet_fnt_helper_file, themes_dir, cfg_default_theme, theme_dir
    all_sprites.empty()
    theme_dir = os.path.join(themes_dir, name)
    if os.path.exists(theme_dir) and os.path.isdir(theme_dir):
        cfg_theme = name
    else:
        theme_dir = os.path.join(themes_dir, cfg_default_theme)
        cfg_theme = cfg_default_theme
    load_theme_cfg()
    sheet_fnt_title_file = load_image(fnt_title_file, colorkey=None)[0]
    sheet_fnt_list_file = load_image(fnt_list_file, colorkey=None)[0]
    sheet_fnt_info_file = load_image(fnt_info_file, colorkey=None)[0]
    sheet_fnt_helper_file = load_image(fnt_helper_file, colorkey=None)[0]
    load_background(is_refresh=True)
    load_custom_sprites(is_refresh=True)
    load_foreground(is_refresh=True)
    load_messages(is_refresh=True)
    load_trasition(is_refresh=True)
    # load_mouse(is_refresh=True)
    set_screen_mode(is_tate)
    
''' Load common modules and configuration '''

# Pygame
def init_video():
    global screen, screen_tate, fb_presenter
    fb_presenter = None
    try:
        pygame.display.init()
    except pygame.error:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.quit()
        pygame.display.init()
    pygame.mouse.set_visible(0)
    pygame.key.set_repeat() # (delay, interval)
    #screen = pygame.display.set_mode((scr_w, scr_h), pygame.SCALED)
    #screen = pygame.display.set_mode((scr_w, scr_h), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
    display_surface = pygame.display.set_mode((scr_w, scr_h))
    display_driver = pygame.display.get_driver()
    if display_driver in ('dummy', 'offscreen'):
        # SDL dummy may ignore the requested 320x240 size and expose the
        # 3840x240 fbdev mode. Keep RGB-Pi's logical canvas fixed at 320x240,
        # then mirror it explicitly to /dev/fb0.
        screen = pygame.Surface((scr_w, scr_h)).convert()
    else:
        screen = display_surface
    screen_tate = pygame.Surface((scr_h, scr_w)).convert()
    if display_driver in ('dummy', 'offscreen'):
        try:
            import lakka_fbdisplay
            fb_presenter = lakka_fbdisplay.install(pygame, screen)
        except Exception as error:
            logging.warning('Framebuffer presenter unavailable: %s', error)
    display_info = get_display_inf()
    logging.debug('Init video. Driver: %s, Info: %s', display_driver, display_info)
    os.system('clear')
init_video()

# Prepare Game Objects
translations = load_translations()
step_timer = RtkStepTimer()
clock = pygame.time.Clock()
ContainerMgr = RtkContainerMgr()

# Preload font types
sheet_fnt_title_file = load_image(fnt_title_file, colorkey=None)[0]
sheet_fnt_list_file = load_image(fnt_list_file, colorkey=None)[0]
sheet_fnt_info_file = load_image(fnt_info_file, colorkey=None)[0]
sheet_fnt_helper_file = load_image(fnt_helper_file, colorkey=None)[0]

# Standard objects
load_background()
load_custom_sprites()
load_foreground()
load_messages()
load_trasition()
load_mouse()

# Create a backgound for cleaning dirty sprites
bg_clear = pygame.Surface(screen.get_size())
bg_clear = bg_clear.convert()
bg_clear.fill(black)

# Refresh sprites with the bg_clear
all_sprites.clear(screen, bg_clear)
