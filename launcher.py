import os
import time
import cglobals
import rtk
import utils
import pygame
import lakka_switchres

''' Config files '''

def apply_lakka_super_viewport(config):
    # Lakka already owns the 3840x240 viewport in retroarch.cfg.
    # Keep the appendconfig from perturbing SwitchRes/video geometry.
    pass

def start_video_info_notifier():
    return

def make_common(system, game_path, config, is_global_nfs):
    # Video
    config.append('video_driver = "gl"\n')
    config.append('video_shared_context = "false"\n')
    config.append('driver_switch_enable = "true"\n')
    config.append('video_fullscreen = "true"\n')
    config.append('video_smooth = "false"\n')
    config.append('vrr_runloop_enable = "false"\n')
    # Lakka-port: write switchres.ini and emit stock crt_switch_* keys
    lakka_switchres.write_switchres_ini(
        rtk.path_rgbpi_data + '/switchres.ini',
        crt_type=rtk.cfg_crt_type,
        super_width=lakka_switchres.SUPER_WIDTH.get(rtk.cfg_dynares, '3840'))
    lakka_switchres.apply_crt_settings(
        config,
        cfg_crt_type=rtk.cfg_crt_type,
        cfg_dynares=rtk.cfg_dynares,
        cfg_overscan=rtk.cfg_overscan,
        cfg_video_info='off',
        cfg_show_fps=getattr(rtk, 'cfg_show_fps', 'off'),
        cfg_flicker_reduction=rtk.cfg_flicker_reduction)
    # Set Fake LGun Color Replacement
    if rtk.cfg_lgun_color_rep == 'on':
        config.append('video_shader_enable = true\n')
    else:
        config.append('video_shader_enable = false\n')
    # Audio
    config.append('audio_driver = "alsa"\n')
    config.append('audio_device = "hw:1,0"\n')
    config.append('audio_enable = "true"\n')
    config.append('audio_mute_enable = "false"\n')
    config.append('audio_resampler_quality = "3"\n')
    # Lakka: keep the USB DAC path simple while validating game audio.
    config.append('audio_dsp_plugin = ""\n')
    # Input
    config.append('input_driver = "udev"\n') # linuxraw, sdl2, udev, wayland
    config.append('input_joypad_driver = "udev"\n') # hid, linuxraw, sdl2, udev, xinput
    if rtk.cfg_keyb_mouse == 'on' and system in cglobals.allow_keyb_mouse:
        config.append('input_auto_game_focus = "1"\n')
    if system == 'n64':
        config.append('input_player1_analog_dpad_mode = "0"\n')
        config.append('input_player2_analog_dpad_mode = "0"\n')
        config.append('input_player3_analog_dpad_mode = "0"\n')
        config.append('input_player4_analog_dpad_mode = "0"\n')
        config.append('input_player5_analog_dpad_mode = "0"\n')
    else:
        config.append('input_player1_analog_dpad_mode = "1"\n')
        config.append('input_player2_analog_dpad_mode = "1"\n')
        config.append('input_player3_analog_dpad_mode = "1"\n')
        config.append('input_player4_analog_dpad_mode = "1"\n')
        config.append('input_player5_analog_dpad_mode = "1"\n')
    # LGun P1/P2 configuration
    if cglobals.input_mgr.num_lguns == 1:
        config.append('input_player1_mouse_index = "0"\n')
        config.append('input_player2_mouse_index = "0"\n')
    elif cglobals.input_mgr.num_lguns == 2:
        config.append('input_player1_mouse_index = "0"\n')
        config.append('input_player2_mouse_index = "1"\n')
    # Latency
    if rtk.cfg_inputlag_fix == 'disabled':
        config.append('run_ahead_enabled = "false"\n')
        config.append('video_frame_delay_auto = "false"\n')
    elif rtk.cfg_inputlag_fix == 'standard':
        config.append('video_frame_delay_auto = "true"\n')
    elif rtk.cfg_inputlag_fix == 'extreme':
        config.append('video_frame_delay_auto = "true"\n')
        if system in cglobals.allow_runahead:
            config.append('run_ahead_enabled = "true"\n')
        else:
            config.append('run_ahead_enabled = "false"\n')
    config.append('run_ahead_frames = "1"\n')
    config.append('run_ahead_hide_warnings = "false"\n')
    config.append('run_ahead_secondary_instance = "true"\n')
    # Hotkeys
    config.append('input_hotkey_block_delay = "nul"\n')
    config.append('input_toggle_fast_forward = "nul"\n')
    config.append('input_hold_slowmotion = "nul"\n')
    config.append('input_save_state = "nul"\n')
    config.append('input_load_state = "nul"\n')
    config.append('input_toggle_fullscreen = "nul"\n')
    config.append('input_state_slot_increase = "nul"\n')
    config.append('input_state_slot_decrease = "nul"\n')
    config.append('input_movie_record_toggle = "nul"\n')
    config.append('input_pause_toggle = "nul"\n')
    config.append('input_frame_advance = "nul"\n')
    config.append('input_reset = "nul"\n')
    config.append('input_shader_next = "nul"\n')
    config.append('input_shader_prev = "nul"\n')
    config.append('input_cheat_index_plus = "nul"\n')
    config.append('input_cheat_index_minus = "nul"\n')
    config.append('input_cheat_toggle = "nul"\n')
    config.append('input_audio_mute = "nul"\n')
    config.append('input_fps_toggle = "nul"\n')
    config.append('input_send_debug_info = "nul"\n')
    config.append('input_netplay_game_watch = "nul"\n')
    config.append('input_netplay_player_chat = "nul"\n')
    config.append('input_volume_up = "nul"\n')
    config.append('input_volume_down = "nul"\n')
    config.append('input_grab_mouse_toggle = "nul"\n')
    config.append('input_desktop_menu_toggle = "nul"\n')
    #config.append('input_game_focus_toggle = "scroll_lock"\n')
    config.append('input_game_focus_toggle = "capslock"\n')
    config.append('input_screenshot = "sysreq"\n')
    config.append('input_osk_toggle = "f10"\n')
    # RetroPad button combination to toggle menu
    # 0: None
    # 1: Down + Y + L1 + R1
    # 2: L3 + R3
    # 3: L1 + R1 + Start + Select
    # 4: Start + Select
    # 5: L3 + R1
    # 6: L1 + R1
    # 7: Hold Start (2 seconds)
    # 8: Hold Select (2 seconds)
    # 9: Down + Select
    # 10: L2 + R2
    if rtk.cfg_menu_toggle == 'only_menu_btn':
        config.append('input_menu_toggle_gamepad_combo = "0"\n')
    else:
        if cglobals.is_jamma:
            config.append('input_menu_toggle_gamepad_combo = "7"\n')
        else:
            if rtk.cfg_menu_toggle == 'start_select' and cglobals.has_select:
                config.append('input_menu_toggle_gamepad_combo = "4"\n')
            elif rtk.cfg_menu_toggle == 'start_2s' or not cglobals.has_select:
                config.append('input_menu_toggle_gamepad_combo = "7"\n')
    # Netplay
    config.append('netplay_ip_port = "55439"\n')
    config.append('netplay_nickname = "rgbpi"\n')
    config.append('netplay_public_announce = "false"\n')
    config.append('netplay_stateless_mode = "true"\n')
    config.append('netplay_input_latency_frames_min = "' + str(rtk.cfg_input_latency) + '"\n')
    # Cheevos
    if rtk.cfg_cheevos == 'on':
        config.append('cheevos_enable = "true"\n')
    else:
        config.append('cheevos_enable = "false"\n')
    if rtk.cfg_leaderboards == 'on':
        config.append('cheevos_leaderboards_enable = "true"\n')
    else:
        config.append('cheevos_leaderboards_enable = "false"\n')
    if rtk.cfg_cheevos_all == 'on':
        config.append('cheevos_start_active = "true"\n')
        config.append('cheevos_test_unofficial = "true"\n')
    else:
        config.append('cheevos_start_active = "false"\n')
        config.append('cheevos_test_unofficial = "false"\n')
    config.append('cheevos_hardcore_mode_enable = "true"\n')
    config.append('cheevos_username = "' + str(rtk.cfg_nick) + '"\n')
    config.append('cheevos_password = "' + str(rtk.cfg_cheevos_pwd) + '"\n')
    config.append('cheevos_token = ""\n')
    config.append('cheevos_unlock_sound_enable = "true"\n')
    config.append('cheevos_verbose_enable = "true"\n')
    config.append('cheevos_richpresence_enable = "true"\n')
    # Paths
    config.append('libretro_directory = "' + rtk.path_cores + '"\n')
    config.append('libretro_info_path = "' + rtk.path_cores + '"\n')
    config.append('joypad_autoconfig_dir = "' + rtk.path_autoconfig + '"\n')
    if rtk.cfg_user_remaps == 'on':
        config.append('input_remapping_directory = "' + cglobals.mount_point + '/remaps/user"\n')
    elif rtk.cfg_user_remaps == 'off':
        config.append('input_remapping_directory = "' + cglobals.mount_point + '/remaps/system"\n')
    config.append('system_directory = "' + cglobals.mount_point + '/bios"\n')
    config.append('core_options_path = "' + rtk.path_rgbpi_data + '/cores.cfg"\n')
    config.append('rgui_config_directory = "' + cglobals.mount_point + '/gameconfig"\n')
    config.append('cheat_database_path = "' + cglobals.mount_point + '/cheats"\n')
    if 'fbneo' in game_path:
        config.append('savefile_directory = "' + cglobals.mount_point + '/saves/arcade/fbneo"\n')
        config.append('savestate_directory = "' + cglobals.mount_point + '/saves/arcade/fbneo"\n')
        config.append('screenshot_directory = "' + cglobals.mount_point + '/screenshots/arcade/fbneo"\n')
    elif 'mame' in game_path:
        config.append('savefile_directory = "' + cglobals.mount_point + '/saves/arcade/mame"\n')
        config.append('savestate_directory = "' + cglobals.mount_point + '/saves/arcade/mame"\n')
        config.append('screenshot_directory = "' + cglobals.mount_point + '/screenshots/arcade/mame"\n')
    elif 'naomi' in game_path:
        config.append('savefile_directory = "' + cglobals.mount_point + '/saves/arcade/naomi"\n')
        config.append('savestate_directory = "' + cglobals.mount_point + '/saves/arcade/naomi"\n')
        config.append('screenshot_directory = "' + cglobals.mount_point + '/screenshots/arcade/naomi"\n')
    else:
        config.append('savefile_directory = "' + cglobals.mount_point + '/saves/' + system + '"\n')
        config.append('savestate_directory = "' + cglobals.mount_point + '/saves/' + system + '"\n')
        config.append('screenshot_directory = "' + cglobals.mount_point + '/screenshots/' + system + '"\n')  
    # Lang
    if rtk.cfg_language == 'de': config.append('user_language = "4"\n')    # de
    elif rtk.cfg_language == 'en': config.append('user_language = "0"\n')  # en
    elif rtk.cfg_language == 'es': config.append('user_language = "3"\n')  # es
    elif rtk.cfg_language == 'fr': config.append('user_language = "2"\n')  # fr
    elif rtk.cfg_language == 'it': config.append('user_language = "5"\n')  # it
    elif rtk.cfg_language == 'pt': config.append('user_language = "7"\n')  # pt_br
    elif rtk.cfg_language == 'se': config.append('user_language = "25"\n') # sv
    else: config.append('user_language = "0"\n')
    # RA log
    config.append('libretro_log_level = "3"\n') # DEBUG = 0, INFO = 1, WARN = 2, ERROR = 3.
    config.append('log_dir = "' + rtk.path_rgbpi_logs + '"\n')
    if rtk.logger_root_level in ('DEBUG','INFO'):
        config.append('log_verbosity = "true"\n')
        config.append('log_to_file = "true"\n')
        config.append('log_to_file_timestamp = "true"\n')
    # RGUI
    config.append('rgui_menu_color_theme = "0"\n')
    config.append('rgui_menu_theme_preset = "' + rtk.path_retroarch_assets + '/rgui/RGBPi Brogrammer.cfg"\n')
    config.append('rgui_entry_normal_color = "0xFF00FF66"\n')
    config.append('rgui_entry_hover_color = "0xFFFFFFFF"\n')
    config.append('rgui_title_color = "0xFFFFB000"\n')
    config.append('rgui_bg_dark_color = "0xFF101010"\n')
    config.append('rgui_bg_light_color = "0xFF202020"\n')
    config.append('rgui_border_dark_color = "0xFFFF6600"\n')
    config.append('rgui_border_light_color = "0xFFFFC000"\n')
    config.append('rgui_wallpaper = ""\n')
    config.append('menu_dynamic_wallpaper_enable = "false"\n')
    config.append('rgui_border_filler_enable = "true"\n')
    config.append('rgui_background_filler_thickness_enable = "true"\n')
    config.append('menu_rgui_shadows = "true"\n')
    config.append('menu_ticker_speed = "4"\n')
    config.append('menu_ticker_type = "Bounce Left/Right"\n')
    config.append('menu_timedate_enable = "false"\n')
    config.append('menu_battery_level_enable = "false"\n')
    config.append('menu_show_start_screen = "false"\n')
    theme_fx_path = rtk.path_rgbpi_themes + '/' + rtk.cfg_theme + '/sounds/ra'
    if os.path.isfile(theme_fx_path + '/sounds/unlock.ogg'):
        config.append('assets_directory = "' + theme_fx_path + '"\n')
    else:
        config.append('assets_directory = "' + rtk.path_retroarch_assets + '"\n')
    # OSD & Notifications. Display > Show FPS controls FPS only.
    if getattr(rtk, 'cfg_show_fps', 'off') == 'on':
        config.append('video_font_enable = "true"\n')
        config.append('video_font_size = "12.000000"\n')
        config.append('video_message_color = "00ffff"\n')
        config.append('video_message_pos_x = "0.050000"\n')
        config.append('video_message_pos_y = "0.050000"\n')
    else:
        config.append('video_font_enable = "false"\n')
    if getattr(rtk, 'cfg_show_fps', 'off') == 'on':
        config.append('fps_show = "true"\n')
        config.append('video_fps_show = "true"\n')
        config.append('statistics_show = "true"\n')
        config.append('framecount_show = "false"\n')
    else:
        config.append('fps_show = "false"\n')
        config.append('video_fps_show = "false"\n')
        config.append('statistics_show = "false"\n')
        config.append('framecount_show = "false"\n')
    config.append('notification_show_autoconfig = "false"\n')
    config.append('notification_show_remap_load = "false"\n')
    config.append('notification_show_config_override_load = "false"\n')
    config.append('notification_show_set_initial_disk = "false"\n')
    config.append('notification_show_cheats_applied = "false"\n')
    config.append('notification_show_refresh_rate = "false"\n')
    config.append('network_cmd_enable = "true"\n')
    config.append('network_cmd_port = "55355"\n')
    # Menu options
    config.append('menu_driver = "rgui"\n')
    config.append('menu_linear_filter = "true"\n')
    config.append('rgui_aspect_ratio_lock = "3"\n')
    config.append('menu_enable_widgets = "false"\n')
    config.append('menu_mouse_enable = "false"\n')
    config.append('menu_show_online_updater = "false"\n')
    config.append('menu_show_load_core = "false"\n')
    config.append('menu_show_load_content = "false"\n')
    config.append('menu_show_configurations = "false"\n')
    config.append('menu_show_help = "false"\n')
    config.append('menu_show_restart_retroarch = "false"\n')
    config.append('menu_show_overlays = "false"\n')
    config.append('menu_show_video_layout = "false"\n')
    config.append('menu_show_sublabels = "true"\n')
    config.append('content_show_history = "false"\n')
    config.append('content_show_playlists = "false"\n')
    config.append('content_show_netplay = "false"\n')
    config.append('quick_menu_show_shaders = "false"\n')
    config.append('quick_menu_show_save_content_dir_overrides = "false"\n')
    config.append('quick_menu_show_information = "false"\n')
    config.append('quick_menu_show_add_to_favorites = "false"\n')
    config.append('quick_menu_show_download_thumbnails = "false"\n')
    config.append('quick_menu_show_reset_core_association = "false"\n')
    config.append('quick_menu_show_set_core_association = "false"\n')
    config.append('quick_menu_show_recording = "false"\n')
    config.append('quick_menu_show_start_recording = "false"\n')
    config.append('quick_menu_show_undo_save_load_state = "false"\n')
    config.append('quick_menu_show_core_options_flush = "false"\n')
    config.append('quick_menu_show_resume_content = "true"\n')
    config.append('quick_menu_show_close_content = "true"\n')
    config.append('settings_show_accessibility = "false"\n')
    config.append('settings_show_ai_service = "false"\n')
    config.append('settings_show_playlists = "false"\n')
    config.append('settings_show_power_management = "false"\n')
    config.append('settings_show_directory = "false"\n')
    config.append('settings_show_network = "false"\n')
    config.append('settings_show_file_browser = "false"\n')
    config.append('settings_show_logging = "false"\n')
    config.append('settings_show_onscreen_display = "false"\n')
    config.append('settings_show_user = "false"\n')
    config.append('settings_show_saving = "false"\n')
    config.append('settings_show_frame_throttle = "false"\n')
    config.append('settings_show_configuration = "false"\n')
    config.append('settings_show_core = "false"\n')
    # Advanced options
    config.append('youtube_stream_key = "' + rtk.cfg_youtube_stream_key + '"\n')
    config.append('twitch_stream_key = "' + rtk.cfg_twitch_stream_key + '"\n')
    config.append('rewind_enable = "false"\n') # Disabled by default due to high perfromance impact
    config.append('config_save_on_exit = "false"\n')
    config.append('input_overlay_enable = "false"\n')
    config.append('global_core_options = "true"\n')
    config.append('video_layout_enable = "false"\n')
    config.append('quit_on_close_content = "1"\n')
    if is_global_nfs:
        config.append('quick_menu_show_restart_content = "false"\n')
        config.append('quick_menu_show_save_load_state = "false"\n')
        config.append('quick_menu_show_cheats = "false"\n')
        config.append('menu_pause_libretro = "false"\n')
        config.append('input_hold_fast_forward = "nul"\n')
        config.append('input_rewind = "nul"\n')
    else:
        config.append('quick_menu_show_restart_content = "true"\n')
        config.append('quick_menu_show_save_load_state = "true"\n')
        config.append('quick_menu_show_cheats = "true"\n')
        config.append('menu_pause_libretro = "true"\n')
        if system in cglobals.allow_rewind_fastforward:
            config.append('input_hold_fast_forward = "f"\n')
            config.append('input_rewind = "r"\n')
        else:
            config.append('input_hold_fast_forward = "nul"\n')
            config.append('input_rewind = "nul"\n')
    if rtk.cfg_adv_mode == 'god':
        config.append('rgbpi_restrict_ui = "false"\n')
        config.append('content_show_settings = "true"\n')
        config.append('menu_core_enable = "true"\n')
        config.append('menu_show_information = "true"\n')
        config.append('menu_content_show_latency = "true"\n')
        config.append('menu_show_latency = "true"\n')
        config.append('menu_show_rewind = "true"\n')
        config.append('quick_menu_show_save_core_overrides = "true"\n')
        config.append('quick_menu_show_save_game_overrides = "true"\n')
        config.append('quick_menu_show_streaming = "true"\n')
        config.append('quick_menu_show_start_streaming = "true"\n')
        config.append('quick_menu_show_controls = "true"\n')
        config.append('quick_menu_show_options = "true"\n')
        config.append('settings_show_drivers = "true"\n')
        config.append('settings_show_video = "true"\n')
        config.append('settings_show_audio = "true"\n')
        config.append('settings_show_input = "true"\n')
        config.append('settings_show_user_interface = "true"\n')
        config.append('settings_show_achievements = "true"\n')
        config.append('settings_show_recording = "true"\n')
    else:
        config.append('content_show_settings = "false"\n')
        config.append('menu_core_enable = "false"\n')
        config.append('menu_show_information = "false"\n')
        config.append('menu_content_show_latency = "false"\n')
        config.append('menu_show_latency = "false"\n')
        config.append('quick_menu_show_save_core_overrides = "false"\n')
        config.append('quick_menu_show_save_game_overrides = "false"\n')
        config.append('settings_show_drivers = "false"\n')
        config.append('settings_show_video = "false"\n')
        config.append('settings_show_audio = "false"\n')
        config.append('settings_show_input = "false"\n')
        config.append('settings_show_user_interface = "false"\n')
        config.append('settings_show_achievements = "false"\n')
        if is_global_nfs or rtk.cfg_kiosk_mode == 'on':
            config.append('quick_menu_show_controls = "false"\n')
            config.append('quick_menu_show_options = "false"\n')
            config.append('rgbpi_restrict_ui = "true"\n')
            config.append('menu_show_rewind = "false"\n')
            config.append('quick_menu_show_streaming = "false"\n')
            config.append('quick_menu_show_start_streaming = "false"\n')
            config.append('settings_show_recording = "false"\n')
        else:
            config.append('quick_menu_show_controls = "true"\n')
            config.append('quick_menu_show_options = "true"\n')
            if rtk.cfg_adv_mode == 'suser':
                config.append('rgbpi_restrict_ui = "false"\n')
                config.append('menu_show_rewind = "true"\n')
                config.append('quick_menu_show_streaming = "true"\n')
                config.append('quick_menu_show_start_streaming = "true"\n')
                config.append('settings_show_recording = "true"\n')
            else:
                config.append('rgbpi_restrict_ui = "true"\n')
                config.append('menu_show_rewind = "false"\n')
                config.append('quick_menu_show_streaming = "false"\n')
                config.append('quick_menu_show_start_streaming = "false"\n')
                config.append('settings_show_recording = "false"\n')
    if rtk.cfg_user_scrap == 'on':
        config.append('quick_menu_show_take_screenshot = "true"\n')
    else:
        config.append('quick_menu_show_take_screenshot = "false"\n')

def make_arcade_cfg_file(game_path, is_global_nfs):
    config = []
    is_game_tate = utils.is_game_tate(game_path)
    rotation_cfg = rtk.cfg_ui_rotation
    # Common config
    make_common('arcade', game_path, config, is_global_nfs)
    # Video
    if is_game_tate and rotation_cfg == 'no_rotation' and 'naomi' not in game_path:
        config.append('aspect_ratio_index = "23"\n')
        config.append('video_fullscreen_x = "640"\n')
        config.append('video_fullscreen_y = "480"\n')
        config.append('custom_viewport_width = "336"\n')
        config.append('custom_viewport_height = "448"\n')
        config.append('video_scale_integer = "false"\n')
        config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/native.ttf"\n')
        config.append('video_font_size = "12"\n')
    elif rtk.cfg_dynares == 'superx':
        apply_lakka_super_viewport(config)
        # Pick the font that matches the active CRT mode height. Arcade can
        # be 240p (most fbneo/mame) or 480i (Tekken/CPS3/etc); switchres
        # decides per game so we pick the heavier font for safety.
        if utils.is_game_480i(game_path):
            config.append('aspect_ratio_index = "22"\n')
            config.append('video_aspect_ratio_auto = "false"\n')
            config.append('video_scale_integer = "false"\n')
            config.append('video_fullscreen_x = "0"\n')
            config.append('video_fullscreen_y = "0"\n')
            config.append('custom_viewport_width = "0"\n')
            config.append('custom_viewport_height = "0"\n')
            config.append('custom_viewport_x = "0"\n')
            config.append('custom_viewport_y = "0"\n')
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/SuperResolucion.ttf"\n')
        else:
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/SuperResolucion.ttf"\n')
    elif rtk.cfg_dynares == 'native':
        config.append('aspect_ratio_index = "21"\n')
        config.append('video_scale_integer = "true"\n')
        config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/native.ttf"\n')
    # By default emulators display TATE games left rotated to be played in 4/3 TV
    # The video_rotation angle is <value> * 90 degrees counter-clockwise
    if 'naomi' in game_path:
        config.append('video_rotation = "0"\n') # The core manages the rotation
    elif not is_game_tate and rotation_cfg == 'no_rotation':
        config.append('video_rotation = "0"\n')
    elif not is_game_tate and rotation_cfg == 'rotate_full':
        config.append('video_rotation = "4"\n')
    elif is_game_tate and rotation_cfg == 'rotate_cw':
        config.append('video_rotation = "3"\n')
    elif is_game_tate and rotation_cfg == 'rotate_ccw':
        config.append('video_rotation = "1"\n')
    elif is_game_tate and rotation_cfg == 'no_rotation':
        config.append('video_rotation = "0"\n')
    else:
        config.append('video_rotation = "0"\n')
    # Write file
    retroarch_cfg_file = rtk.path_rgbpi_data + '/retroarch.cfg'
    with open(retroarch_cfg_file, 'w', encoding='utf-8') as file:
        file.writelines(config)
    return retroarch_cfg_file

def make_console_cfg_file(system, is_global_nfs):
    config = []
    handheld_mode = cglobals.launcher['handheld_mode']
    # Common config
    make_common(system, system, config, is_global_nfs)
    # Video
    if rtk.cfg_dynares == 'superx':
        apply_lakka_super_viewport(config)
        if (system == 'dreamcast' or system == 'naomi'):
            # Let Lakka CRT switchres use the active mode dimensions:
            # 3840x240 for 240p and 3840x480 for 480i. A fixed 480-line
            # viewport makes 240p content too tall.
            config.append('aspect_ratio_index = "22"\n')
            config.append('video_aspect_ratio_auto = "false"\n')
            config.append('video_scale_integer = "false"\n')
            config.append('video_fullscreen_x = "0"\n')
            config.append('video_fullscreen_y = "0"\n')
            config.append('custom_viewport_width = "0"\n')
            config.append('custom_viewport_height = "0"\n')
            config.append('custom_viewport_x = "0"\n')
            config.append('custom_viewport_y = "0"\n')
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/SuperResolucion.ttf"\n')
        else:
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/SuperResolucion.ttf"\n')
    elif rtk.cfg_dynares == 'native':
        if(system == 'snes'):
            config.append('aspect_ratio_index = "23"\n')
            config.append('video_fullscreen_x = "512"\n')
            config.append('video_fullscreen_y = "224"\n')
            config.append('custom_viewport_width = "512"\n')
            config.append('custom_viewport_height = "224"\n')
            config.append('video_scale_integer = "true"\n')
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/native.ttf"\n')
            config.append('video_font_size = "6"\n')
        else:
            config.append('aspect_ratio_index = "21"\n')
            config.append('video_scale_integer = "true"\n')
            config.append('video_font_path = "' + rtk.path_retroarch_fonts + '/native.ttf"\n')
    # Lakka-port: dynares_handheld_full dropped; stock RA has no equivalent.
    # Handheld full-screen semantics now handled by per-core-override aspect.
    _ = handheld_mode
    config.append('video_rotation = "0"\n')
    # Write file
    retroarch_cfg_file = rtk.path_rgbpi_data + '/retroarch.cfg'
    with open(retroarch_cfg_file, 'w', encoding='utf-8') as file:
        file.writelines(config)
    return retroarch_cfg_file

def set_device_type(system, game_path):
    command = ''
    if system == 'arcade':
        # FBNeo: 0 = None, 1 = RetroPad, 4 = Lightgun, 5 = Classic, 6 = Pointer,  517 = Modern
        if   'fbneo' in game_path:          command = ' --device=1:5 --device=2:5 --device=3:5 --device=4:5 --device=5:5 '
        elif 'mame' in game_path:           command = ' --device=1:1 --device=2:1 --device=3:1 --device=4:1 --device=5:1 '
    else:
        if cglobals.launcher['lgun_mode']:
            if   system == 'nes':           command = ' --device=1:513 --device=2:258 '
            elif system == 'snes':          command = ' --device=1:1   --device=2:260 '
            elif system == 'mastersystem':  command = ' --device=1:260 --device=2:769 '
            elif system == 'megadrive':     command = ' --device=1:1   --device=2:516 '
            elif system == 'segacd':        command = ' --device=1:1   --device=2:516 '
            elif system == 'dreamcast' or \
                system == 'naomi':          command = ' --device=1:4   --device=2:4 '
            elif system == 'psx':           command = ' --device=1:260 --device=2:260 '
            elif system == 'fbneo':         command = ' --device=1:4   --device=2:4 '
            else:                           command = ''
        else:
            if system == 'mastersystem':    command = ' --device=1:769 --device=2:769 --device=3:0 --device=4:0 --device=5:0 '
            elif system == 'megadrive' or \
                system == 'segacd':         command = ' --device=1:513 --device=2:513 --device=3:513 --device=4:513 --device=5:513 '
            elif system == 'zxspectrum':    command = ' --device=1:513 --device=2:513 --device=3:259 --device=4:None --device=5:None '
            elif system == 'neogeo' or \
                system == 'neocd' or \
                system == 'pcengine' or \
                system == 'pcenginecd' or \
                system == '32x' or \
                system == 'snes' or \
                system == 'dreamcast' or \
                system == 'naomi':          command = ' --device=1:1 --device=2:1 --device=3:1 --device=4:1 --device=5:1 '
            elif system == 'pc':            command = ' --device=1:257 --device=2:1 --device=3:1 --device=4:1 --device=5:1 '
            elif system == 'psx':
                if rtk.cfg_psx_control == 'digital':
                                            command = ' --device=1:1 --device=2:1 --device=3:1 --device=4:1 --device=5:1 '
                elif rtk.cfg_psx_control == 'analog' or rtk.cfg_psx_control == 'analog_forced':
                                            command = ' --device=1:261 --device=2:261 --device=3:261 --device=4:261 --device=5:261 '
    return command

''' Launch game '''

def launch_content():
    # Get game launch info
    arcade_mode     = cglobals.launcher['arcade_mode']
    neogeo_mode     = cglobals.launcher['neogeo_mode']
    lgun_mode       = cglobals.launcher['lgun_mode']
    system          = cglobals.launcher['system']
    game_path       = cglobals.launcher['game_path']
    game_id         = cglobals.launcher['game_id']
    return_view     = cglobals.launcher['return_view']
    is_global_nfs   = utils.is_global_nfs()

    # Check if is NFS and the game is being played by other user
    if os.path.isfile(game_path + '.bussy'):
        rtk.notif_msg.display(text='game_in_use_info')
    else:
        cglobals.sound_mgr.pause_music()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        # Lakka-port: black-screen the framebuffer before tearing down pygame
        # so the user never sees a stale FE frame while the DRM mode flips.
        try:
            with open('/dev/fb0', 'wb', buffering=0) as _fb:
                _fb.write(b'\x00' * (3840 * 480 * 4))
        except Exception:
            pass
        pygame.display.quit()

        ''' Check if there is any specific EQ Preset for this system '''
        
        eq_preset = rtk.cfg_preset
        is_system_preset = False
        if system in cglobals.presets:
            is_system_preset = True
            cglobals.sound_mgr.set_preset(preset=system)

        ''' Launch data '''
        
        # NFS Check & Lock
        if is_global_nfs:
            # Create file to check if game is beign played
            utils.cmd('touch ' + game_path + '.bussy')
            # Delete autoload to avoid cheats
            auto_load_file = game_path.rsplit('.',1)[0] + '.state.auto'
            utils.cmd('rm "' + auto_load_file + '"')
        # Set game netplay info
        if cglobals.netplay == 'on':
            if cglobals.netplay_mode == 'client':
                netplay_cmd = ' --connect ' + cglobals.network_server_ip
            elif cglobals.netplay_mode == 'server':
                netplay_cmd = ' --host '
        else:
            netplay_cmd = ''
        # Set Fake LGun Color Replacement
        if cglobals.launcher['lgun_mode'] and rtk.cfg_lgun_color_rep == 'on':
            if rtk.cfg_flicker_reduction == 'on':
                color_cmd = ' --set-shader /storage/rgbpi/data/shaders/lgun_linear.glslp '
            else:
                color_cmd = ' --set-shader /storage/rgbpi/data/shaders/lgun_nolinear.glslp '
        else:
            color_cmd = ''
        # Get paths
        path_retroarch          = rtk.path_retroarch
        path_cores              = rtk.path_cores
        # Set time for stats info
        start_date = time.time()
        # Write log info
        rtk.logging.info('Game launch info:')
        rtk.logging.info('> arcade_mode: %s',arcade_mode)
        rtk.logging.info('> neogeo_mode: %s',neogeo_mode)
        rtk.logging.info('> lgun_mode: %s',lgun_mode)
        rtk.logging.info('> system: %s',system)
        rtk.logging.info('> game_path: %s',game_path)
        rtk.logging.info('> netplay_cmd: %s',netplay_cmd)
        rtk.logging.info('> color_cmd: %s',color_cmd)
        rtk.logging.info('> path_retroarch: %s',path_retroarch)
        rtk.logging.info('> path_cores: %s',path_cores)

        ''' Create retroarch and core configurations '''

        if system == 'ports' or system == 'kodi' or system == 'scripts':
            pass
        elif system == 'arcade':
            # Apply core configs
            utils.set_core_neogeo_mode('mvs')
            utils.set_core_fbneo_60(rtk.cfg_force_arcade_60)
            if rtk.cfg_slowdown_fix == 'on':
                utils.set_core_fbneo_overclock(oc=False)
            if rtk.cfg_cheevos == 'on':
                utils.set_core_disable_patch_support()
            if 'naomi' in game_path:
                is_ui_rotated = rtk.cfg_ui_rotation == 'rotate_cw' or rtk.cfg_ui_rotation == 'rotate_ccw' 
                utils.set_core_naomi_rotation(is_ui_rotated)
            # Do remaps
            if not is_global_nfs:
                if not cglobals.has_fresh_jamma_remaps:
                    if (
                        (
                            cglobals.is_jamma
                            or rtk.cfg_button_style == 'jamma3'
                            or rtk.cfg_button_style == 'jamma6'
                            or rtk.cfg_button_style == 'mvs'
                        )
                        and rtk.cfg_user_remaps == 'off'):
                        utils.copy_jamma_remaps()
                        cglobals.has_fresh_jamma_remaps = True
            # Create retroarch configuration
            retroarch_cfg_file = make_arcade_cfg_file(game_path, is_global_nfs)
            rtk.logging.debug('> retroarch_cfg_file (arcade): %s',retroarch_cfg_file)
        else:
            # Apply core configs
            if cglobals.launcher['lgun_mode']:
                utils.set_core_crosshair(crosshair=False)
            else:
                utils.set_core_crosshair(crosshair=True)
            if system in ('mastersystem','sg1000'):
                utils.set_core_borders(borders=True)
            elif system in ('megadrive','segacd'):
                utils.set_core_borders(borders=False)
            elif system == 'neogeo':
                if rtk.cfg_slowdown_fix == 'on':
                    utils.set_core_fbneo_overclock(oc=True)
                if rtk.cfg_cheevos == 'on':
                    utils.set_core_disable_patch_support()
                utils.set_core_neogeo_mode(neogeo_mode)
            elif system == 'sgb':
                filename, file_extension = os.path.splitext(game_path)
                utils.set_core_gb_mode(file_extension)
            elif system == 'psx':
                utils.set_core_psx_force_analog()
            # Do remaps
            if not is_global_nfs:
                if (system == 'amiga' or system == 'amigacd') and rtk.cfg_user_remaps == 'off':
                    utils.copy_amiga_remaps()
                elif (system == 'neogeo' or system == 'neocd') and rtk.cfg_user_remaps == 'off':
                    utils.copy_neogeo_remaps()
                elif (system == 'pc') and rtk.cfg_user_remaps == 'off':
                    utils.copy_pc_remaps()
                elif (system == 'x68000') and rtk.cfg_user_remaps == 'off':
                    utils.copy_x68k_remaps()
                elif ((system == 'pcengine') or (system == 'pcenginecd')) and rtk.cfg_user_remaps == 'off':
                    utils.copy_pce_remaps()
                elif (system == 'nes') and rtk.cfg_user_remaps == 'off':
                    utils.copy_nes_remaps()
            # Remove remaps if lgun
            if cglobals.launcher['lgun_mode']:
                utils.remove_neogeo_remaps()
            # Create retroarch configuration
            retroarch_cfg_file = make_console_cfg_file(system, is_global_nfs)
            rtk.logging.debug('> retroarch_cfg_file (console): %s',retroarch_cfg_file)

        ''' Set Controller Types '''

        device_cmd = set_device_type(system, game_path)

        ''' Check Freeplay '''

        if not is_global_nfs and system == 'arcade' and rtk.cfg_free_play == 'on':
            utils.gen_retroarch_autoconf(enable_free_play=True)

        ''' Scraper '''
        if rtk.cfg_user_scrap == 'on' and not cglobals.launcher['lgun_mode']:
            utils.clean_screenshot(system)

        ''' Close display '''
        utils.cmd('clear')
        pygame.display.quit()
                    
        ''' Launch game '''
        try:
            if system == 'arcade' or system == 'fbneo' or system == 'mame':
                if 'fbneo' in game_path:
                    launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/fbneo_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
                elif 'mame' in game_path:
                    launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mame_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
                elif 'naomi' in game_path:
                    launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/flycast_libretro.so </dev/null --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'atari2600':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/stella_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'atari7800':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/prosystem_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'pcengine':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mednafen_supergrafx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'pcenginecd':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mednafen_supergrafx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'nes':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/fceumm_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'snes':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/bsnes-jg_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'n64':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mupen64plus_next_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'sgb':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mgba_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'gba':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mgba_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'sg1000':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/genesis_plus_gx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'mastersystem':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/genesis_plus_gx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'megadrive':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/genesis_plus_gx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'segacd':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/genesis_plus_gx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'sega32x':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/picodrive_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'dreamcast' or system == 'naomi':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/flycast_libretro.so </dev/null --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'neogeo':
                if game_path.lower().endswith('.neo'):
                    launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/geolith_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
                else:
                    launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/fbneo_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'neocd':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/neocd_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'ngp':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/mednafen_ngp_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'psx':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/swanstation_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'amstradcpc':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/cap32_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'c64':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/vice_x64_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'amiga':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/puae_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'amigacd':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/puae_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'x68000':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/px68k_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'msx':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/bluemsx_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'zxspectrum':
                launch_command = path_retroarch + color_cmd + device_cmd + netplay_cmd + ' -L ' + path_cores + '/fuse_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'pc':
                launch_command = path_retroarch + color_cmd + device_cmd + ' -L ' + path_cores + '/dosbox_pure_libretro.so --appendconfig=' + retroarch_cfg_file + ' "' + game_path + '"'
            elif system == 'ports':
                launch_command = '"' + game_path +'"'
                utils.cmd('chmod +x ' + launch_command)
            elif system == 'kodi':
                launch_command = '"' + game_path +'"'
                utils.cmd('chmod +x ' + launch_command)
            elif system == 'scripts':
                launch_command = '"' + game_path +'"'
                utils.cmd('chmod +x ' + launch_command)
            # Launch game
            start_video_info_notifier()
            if system == 'scripts':
                utils.cmd(launch_command, True)
            else:
                utils.cmd(launch_command)
            # Write stats info
            utils.write_stats(start=start_date,end=time.time())
            rtk.logging.info('> launch_command: %s', launch_command)
        except Exception as error:
            rtk.logging.error('Error in [Launcher]: %s', error)

        ''' Restore nfs, keys, timing, launcher data '''

        # Lakka-port: black-screen again after retroarch exits to hide the
        # last game frame while pygame re-initialises and the FE redraws.
        try:
            with open('/dev/fb0', 'wb', buffering=0) as _fb:
                _fb.write(b'\x00' * (3840 * 480 * 4))
        except Exception:
            pass
        # Pygame
        utils.set_sync()
        rtk.init_video()
        try:
            cglobals.sound_mgr.init_mixer()
            cglobals.sound_mgr.load_sound_fx()
            cglobals.sound_mgr.set_bg_music_volume()
            cglobals.sound_mgr.set_menu_sounds_volume()
            cglobals.sound_mgr.status = 'Stopped'
        except Exception as error:
            rtk.logging.error('Error restoring FE audio: %s', error)
        # Clean remaps
        if not is_global_nfs:
            if (system == 'amiga' or system == 'amigacd') and rtk.cfg_user_remaps == 'off':
                utils.remove_amiga_remaps()
            elif (system == 'neogeo' or system == 'neocd') and rtk.cfg_user_remaps == 'off':
                utils.remove_neogeo_remaps()
        # NFS Check & Unlock
        if is_global_nfs:
            # Create file to check if game is beign played
            utils.cmd('rm ' + game_path + '.bussy')
        # Reset freeplay
        if not is_global_nfs and system == 'arcade' and rtk.cfg_free_play == 'on':
            utils.gen_retroarch_autoconf()
        # Cheevos
        if (system == 'arcade' or system == 'neogeo') and rtk.cfg_cheevos == 'on':
            utils.set_core_enable_patch_support()
        # Reset keys pressed
        utils.reset_key_pressed()
        try:
            cglobals.input_mgr.init_joysticks()
            cglobals.input_mgr.load_joy_btn_style()
        except Exception as error:
            rtk.logging.error('Error restoring FE controls: %s', error)
        try:
            utils.refresh_recents_view()
        except Exception as error:
            rtk.logging.error('Error refreshing recents: %s', error)
        # Restore EQ Preset
        if is_system_preset:
            cglobals.sound_mgr.set_preset(preset=eq_preset)

    ''' Scraper '''
    if game_id and rtk.cfg_user_scrap == 'on' and not cglobals.launcher['lgun_mode']:
        rtk.popup_msg.display(text='loading')
        utils.gen_screenshot(game_id, system, game_path)
        rtk.popup_msg.hide()
    
    ''' Restore Exetuted Sytem '''
    utils.reset_launcher()

    ''' Return to game view '''
    if cglobals.autoplay['do_launch'] == None: # Autoplay not executed
        if system != 'kodi':
            utils.clear_navigation(up_to_view=return_view)
        utils.goto_view(return_view)
