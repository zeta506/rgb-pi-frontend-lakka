import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['PYGAME_BLEND_ALPHA_SDL2'] = "1"
# Lakka-port: the bundled aarch64 pygame wheel lacks kmsdrm/fbcon, so render
# with SDL's dummy backend and mirror the RGB-Pi surface to /dev/fb0.
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_FBDEV', '/dev/fb0')
# Lakka-port: SDL2 silently drops joystick events when the video window has
# no focus. Dummy video never has focus, so without this hint the FE menu
# sees zero gamepad input.
os.environ.setdefault('SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS', '1')
os.environ.setdefault('SDL_GAMECONTROLLER_ALLOW_BACKGROUND_EVENTS', '1')
# Keep SDL using the kernel evdev path (not legacy /dev/input/js*).
os.environ.setdefault('SDL_LINUX_JOYSTICK_USE_DEPRECATED_INTERFACE', '0')
import sys
# Lakka-port: SSH blindado — re-enable on every frontend launch so that even
# a botched WiFi action can't lock us out. Done before any rtk import so logs
# go through normal stderr if rtk fails to load.
try:
    os.makedirs('/storage/.cache/services', exist_ok=True)
    with open('/storage/.cache/services/sshd.conf', 'w') as _f:
        _f.write('SSHD_START=true\n')
    os.system('systemctl start sshd >/dev/null 2>&1')
except Exception as _e:
    pass
# Lakka-port: stub optional Pi-specific native libs before any downstream import
import lakka_optional_deps  # noqa: F401
import rtk
import pygame
import cglobals
import utils
import launcher
from signal_mgr import Signal_Manager
from event_mgr import Event_Manager
from input_mgr import Input_Manager
from sound_mgr import Sound_Manager
from sys_mon_mgr import Sys_Mon_Mgr
from bluetooth_mgr import Bluetooth_Manager
from systems_view import Systems_View
from games_view import Games_View
from favs_view import Favs_View
from lgun_view import Lgun_View
from joy_cfg_view import Joy_Cfg_View
from games_opt_view import Games_Opt_View
from sys_opt_main_view import Sys_Opt_Main_View
from sys_opt_display_view import Sys_Opt_Display_View
from sys_opt_grid_view import Sys_Opt_Grid_View
from sys_opt_sound_view import Sys_Opt_Sound_View
from sys_opt_playlist_view import Sys_Opt_Playlist_View
from sys_opt_eq_view import Sys_Opt_EQ_View
from sys_opt_control_view import Sys_Opt_Control_View
from sys_opt_bt_view import Sys_Opt_BT_View
from sys_opt_network_view import Sys_Opt_Network_View
from sys_opt_wifi_view import Sys_Opt_Wifi_View
from sys_opt_netplay_view import Sys_Opt_Netplay_View
from sys_opt_system_view import Sys_Opt_System_View
from sys_opt_lang_view import Sys_Opt_Lang_View
from sys_opt_theme_view import Sys_Opt_Theme_View
from sys_opt_emulation_view import Sys_Opt_Emulation_View
from sys_opt_storage_view import Sys_Opt_Storage_View
from sys_opt_info_view import Sys_Opt_Info_View
from vkeyb_view import Vkeyb_View
from screen_saver import Screen_Saver
from sel_shutdown_view import Sel_Shutdown_View
from sel_scan_view import Sel_Scan_View
from sel_nfs_view import Sel_NFS_View
from sel_ng_mode_view import Sel_NG_Mode_View
from sel_handheld_mode_view import Sel_Handheld_Mode_View
from info_keys_view import Info_Keys_View
from lgun_cfg_view import Lgun_Cfg_View

os.chdir('/storage/rgbpi')

boot_img_2 = pygame.image.load(rtk.path_rgbpi_images + '/boot_2.bmp').convert()
boot_img_3 = pygame.image.load(rtk.path_rgbpi_images + '/boot_3.bmp').convert()
boot_img_4 = pygame.image.load(rtk.path_rgbpi_images + '/boot_4.bmp').convert()
boot_img_5 = pygame.image.load(rtk.path_rgbpi_images + '/boot_5.bmp').convert()

cglobals.sys_mon_mgr = Sys_Mon_Mgr()
cglobals.signal_mgr = Signal_Manager()
cglobals.event_mgr = Event_Manager()

if rtk.cfg_fst_boot:

    ''' Input '''
    cglobals.input_mgr = Input_Manager()

    ''' Disk '''
    rtk.user_msg.display(title='expand_title',text='expand_info')
    cglobals.event_mgr.submit_event('expand_sd')

    ''' Program loop '''

    utils.cmd('clear')

    while True:

        ''' Logic '''
        cglobals.time_step = rtk.step_timer.get_ticks()
        cglobals.event_mgr.check_events()
        rtk.step_timer.start()

        ''' Render '''
        rtk.render()
else:

    ''' Hardware '''
    rtk.screen.blit(boot_img_2, (0, 0))
    pygame.display.update()
    utils.init_rgbpi()
    utils.init_jamma()
    utils.check_native_csync_support()
    cglobals.event_mgr.submit_event('init_fan')
    if not cglobals.is_rgbpi:
        rtk.error_msg.display(title='warning_title',text='cable_error')
    # Create special joy udev rules
    utils.create_udev_rules_file()
    # Fix XBOX ONE S BT Pair issue
    utils.fix_xbox_one_bt()
    # Fix KB leds
    utils.fix_kb_capslock()
    utils.set_scroll_led()
    # Set screen rotation
    rtk.set_screen_mode(is_tate=utils.is_tate())

    ''' Disk '''
    rtk.screen.blit(boot_img_3, (0, 0))
    pygame.display.update()
    utils.check_boot_disk()
    utils.check_folders()
    utils.gen_scrap_info_img()

    ''' Data '''
    rtk.screen.blit(boot_img_4, (0, 0))
    pygame.display.update()
    utils.load_tate_db()
    utils.load_bios_db()
    utils.gen_game_files()
    utils.load_auto_play()
    utils.load_favorites()
    utils.load_roms()
    utils.gen_sys_kodi()
    utils.update_sys_favs()
    utils.update_sys_recents()
    utils.load_music()
    utils.load_eq_presets()
    utils.load_themes()
    utils.load_scraper_db()

    ''' Input '''
    cglobals.input_mgr = Input_Manager()
    cglobals.input_mgr.init_joysticks()
    cglobals.input_mgr.init_lgun()

    ''' System Screens '''
    rtk.screen.blit(boot_img_5, (0, 0))
    pygame.display.update()
    cglobals.systems_view = Systems_View()
    cglobals.joy_cfg_view = Joy_Cfg_View()
    cglobals.games_opt_view = Games_Opt_View(is_fav=False)
    cglobals.favs_opt_view = Games_Opt_View(is_fav=True)
    cglobals.sys_opt_main_view = Sys_Opt_Main_View()
    cglobals.sys_opt_display_view = Sys_Opt_Display_View()
    cglobals.sys_opt_grid_view = Sys_Opt_Grid_View()
    cglobals.sys_opt_sound_view = Sys_Opt_Sound_View()
    cglobals.sys_opt_playlist_view = Sys_Opt_Playlist_View()
    cglobals.sys_opt_eq_view = Sys_Opt_EQ_View()
    cglobals.sys_opt_control_view = Sys_Opt_Control_View()
    cglobals.sys_opt_bt_view = Sys_Opt_BT_View()
    cglobals.sys_opt_network_view = Sys_Opt_Network_View()
    cglobals.sys_opt_wifi_view = Sys_Opt_Wifi_View()
    cglobals.sys_opt_netplay_view = Sys_Opt_Netplay_View()
    cglobals.sys_opt_system_view = Sys_Opt_System_View()
    cglobals.sys_opt_lang_view = Sys_Opt_Lang_View()
    cglobals.sys_opt_theme_view = Sys_Opt_Theme_View()
    cglobals.sys_opt_emulation_view = Sys_Opt_Emulation_View()
    cglobals.sys_opt_storage_view = Sys_Opt_Storage_View()
    cglobals.sys_opt_info_view = Sys_Opt_Info_View()
    cglobals.vkeyb_view = Vkeyb_View()
    cglobals.scr_saver_view = Screen_Saver()
    cglobals.sel_shutdown_view = Sel_Shutdown_View()
    cglobals.sel_scan_view = Sel_Scan_View()
    cglobals.sel_nfs_view = Sel_NFS_View()
    cglobals.sel_ng_mode_view = Sel_NG_Mode_View()
    cglobals.sel_handheld_mode_view = Sel_Handheld_Mode_View()
    cglobals.info_key_view = Info_Keys_View()
    cglobals.lgun_cfg_view = Lgun_Cfg_View()
    for sys_name in utils.get_system_short_names():
        if sys_name != 'none':
            if sys_name == 'favorites':
                cglobals.__dict__[sys_name + '_view'] = Favs_View(sys_name)
            elif sys_name == 'lightgun':
                cglobals.__dict__[sys_name + '_view'] = Lgun_View(sys_name)
            elif sys_name == 'kodi':
                continue
            else:
                cglobals.__dict__[sys_name + '_view'] = Games_View(sys_name)

    ''' Network '''
    utils.disable_netplay()
    if rtk.cfg_wifi == 'off':
        utils.wifi_disconnect()
    utils.set_random_nick()
    
    ''' Sound '''
    cglobals.sound_mgr = Sound_Manager()

    ''' Bluetooth '''
    cglobals.bt_mgr = Bluetooth_Manager()

    ''' Program loop '''

    utils.fix_permissions()
    utils.cmd('clear')

    while not cglobals.input_mgr.quit_attempt:
        current_view = eval('cglobals.' + utils.get_view_name())

        ''' Events '''
        if not cglobals.is_in_task:
            event = cglobals.input_mgr.get_event()
            if event:
                cglobals.sound_mgr.update(event)
                current_view.update(event)
                # Take screenshot
                if event.down and event.key == 'K_PRINT':
                    rtk.print_screen()
                # Enable action button each loop iteration
                cglobals.stop_action = False
                # Avoid Screen Saver
                cglobals.scr_wait_time = 0
        else:
            cglobals.stop_action = True
            # Avoid Screen Saver
            cglobals.scr_wait_time = 0

        ''' Logic '''
        # Lang selection
        if not rtk.cfg_lang_selected:
            rtk.cfg_lang_selected = 'configuring'
            utils.goto_view('sys_opt_lang_view')

        # Autoplay
        if cglobals.autoplay['do_launch'] == True:
            cglobals.autoplay['do_launch'] = False
            cglobals.launcher['return_view'] = 'systems_view'
            cglobals.launcher['game_path'] = cglobals.autoplay['game_path']
            cglobals.launcher['system'] = cglobals.autoplay['sub_system']
            if cglobals.autoplay['system'] == 'lightgun':
                cglobals.launcher['lgun_mode'] = True
            cglobals.launcher['neogeo_mode'] = 'MVS_EUR'
            cglobals.launcher['arcade_mode'] = None
            launcher.launch_content()

        # RTK objects
        cglobals.time_step = rtk.step_timer.get_ticks()
        rtk.draw_background(cglobals.time_step)
        rtk.draw_transition(cglobals.time_step)
        rtk.draw_custom_sprites(cglobals.time_step,utils.is_tate())
        rtk.draw_messages(cglobals.time_step)

        # Custom objects
        current_view.draw(cglobals.time_step)
        if utils.get_view_name() == 'joy_cfg_view':
            cglobals.joy_cfg_view.do_mapping()
        if utils.get_view_name() != 'scr_saver_view':
            utils.check_scrsvr_wait_time()

        # Time counter to perform tasks every certain time interval
        cglobals.time += cglobals.time_step/1000
        if cglobals.time - cglobals.last_time_check > cglobals.hardware_check_interval:
            cglobals.event_mgr.submit_event('interval_check')

        # System events
        cglobals.event_mgr.check_events()
            
        # Reset timer
        rtk.step_timer.start()
        
        # Sound
        cglobals.sound_mgr.play_bg_music()

        ''' Render '''
        
        rtk.render()

# Quit program
utils.disable_jamma()
pygame.quit()
sys.exit(0)
