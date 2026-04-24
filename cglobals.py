import rtk

# System
time_step = 0
is_rgbpi = False
is_jamma = False
has_native_csync_support = False
has_fresh_jamma_remaps = False
has_select = False
has_audio = True
favs_has_changed = False
auto_has_changed = False
stop_action = False
is_in_task = False
mount_point = rtk.path_media_sd
nav_history = ['systems_view']
button_styles = ('snes','smd','psx','xbox','neogeo','pce','mvs','jamma3','jamma6')
launcher = {
    'arcade_mode':  None,
    'neogeo_mode':  None,
    'lgun_mode':    None,
    'handheld_mode':None,
    'system':       None,
    'game_path':    None,
    'game_id':      None,
    'return_view':  None
}
autoplay = {
    'do_launch':   None,
    'system':      None,
    'sub_system':  None,
    'game_path':   None
}
allow_overclock = ('a03111','b03111','b03112','c03111','c03112')
allow_rewind_fastforward = ('atari2600','atari7800','sgb','gba','ngp','pcengine','pcenginecd','nes','snes','sg1000','mastersystem','megadrive','segacd','sega32x')
allow_runahead = ('pcengine','pcenginecd','nes','snes','sg1000','mastersystem','megadrive','segacd','sega32x','neogeo')
allow_keyb_mouse = ('amstradcpc','c64','amiga','msx','zxspectrum','pc')
# Network
is_connecting = False
netplay_server_name = '-'
network_server_ip = '192.168.9.9'
server_names = []
server_ips = []
netplay = 'off'
netplay_mode = 'client'
cheevos = 'off'
# Hardware
hardware_check_interval = 2
time = 0
last_time_check = 0
scr_wait_time = 0
num_joysticks = 0
num_drives = 0
# Data
system_names = []
system_names_tate = []
systems = [] ############## [{system}, {}, ...]
systems_tate = []
games = [] ################ [games, games, ...] where games = tuple of system game rows, each row is dict
games_tate = [] ########### [games, games, ...]
favorites = []
favorites_tate = []
translations = [] ######### [{translation}, {}, ...]
tate_games_db = []
bios_db = []
scraper_db = {} ########### {hash:{game_info}, ...}
scraper_db_2 = {} ########### {id:{game_info}, ...}
scan_black_list = ["puae_libretro.uae"]
presets = {}
music_files = []
playlist_folders = []
themes = []
vkeyb_txt = ''
tmp_value = ''
# Frontend objects
signal_mgr = None
event_mgr = None
input_mgr = None
sound_mgr = None
bt_mgr = None
sys_mon_mgr = None
systems_view = None
joy_cfg_view = None
games_opt_view = None
favs_opt_view = None
sys_opt_info_view = None
sys_opt_main_view = None
sys_opt_display_view = None
sys_opt_grid_view = None
sys_opt_sound_view = None
sys_opt_playlist_view = None
sys_opt_eq_view = None
sys_opt_control_view = None
sys_opt_bt_view = None
sys_opt_network_view = None
sys_opt_wifi_view = None
sys_opt_netplay_view = None
sys_opt_system_view = None
sys_opt_lang_view = None
sys_opt_theme_view = None
sys_opt_storage_view = None
sys_opt_emulation_view = None
sys_info_view = None
vkeyb_view = None
scr_saver_view = None
sel_shutdown_view = None
sel_scan_view = None
sel_nfs_view = None
sel_ng_mode_view = None
sel_handheld_mode_view = None
info_key_view = None
lgun_cfg_view = None
# Debug
debug01 = []