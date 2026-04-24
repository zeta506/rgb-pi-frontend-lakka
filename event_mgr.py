import cglobals
import utils
import rtk
import time

class Event_Manager(object):
    def __init__(self):
        self.events = []
        # Bind signals to functions
        cglobals.signal_mgr.connect('sig_expand_sd', utils.expand_sd)
        cglobals.signal_mgr.connect('sig_check_usb_drive', utils.check_usb_drive)
        cglobals.signal_mgr.connect('sig_save_cfg', rtk.save_cfg_file)
        cglobals.signal_mgr.connect('sig_check_joys', utils.check_joys)
        cglobals.signal_mgr.connect('sig_check_ips', utils.check_ips)
        cglobals.signal_mgr.connect('sig_scan_scrap_games', utils.scan_scrap_games_from_ui)
        cglobals.signal_mgr.connect('sig_save_preset', utils.save_preset)
        cglobals.signal_mgr.connect('sig_scan_bt', utils.scan_bt_joys)
        cglobals.signal_mgr.connect('sig_unpair_bt', utils.unpair_bt_joys)
        cglobals.signal_mgr.connect('sig_pair_bt', utils.pair_bt_joys)
        cglobals.signal_mgr.connect('sig_wifi_connect', utils.wifi_connect)
        cglobals.signal_mgr.connect('sig_wifi_disconnect', utils.wifi_disconnect)
        cglobals.signal_mgr.connect('sig_enable_netplay', utils.enable_netplay)
        cglobals.signal_mgr.connect('sig_disable_netplay', utils.disable_netplay)
        cglobals.signal_mgr.connect('sig_refresh_list_mode', utils.refresh_list_mode)
        cglobals.signal_mgr.connect('sig_save_autoconf', utils.gen_retroarch_autoconf)    
        cglobals.signal_mgr.connect('sig_refresh_lang', utils.refresh_lang)
        cglobals.signal_mgr.connect('sig_refresh_storage_names', utils.refresh_storage_names)
        cglobals.signal_mgr.connect('sig_refresh_sys_info', utils.refresh_sys_info)
        cglobals.signal_mgr.connect('sig_refresh_helpers', utils.refresh_helpers)
        cglobals.signal_mgr.connect('sig_mount_sd', utils.evt_mount_sd)
        cglobals.signal_mgr.connect('sig_mount_usb1', utils.evt_mount_usb1)
        cglobals.signal_mgr.connect('sig_mount_usb2', utils.evt_mount_usb2)
        cglobals.signal_mgr.connect('sig_format_usb1', utils.evt_format_usb1)
        cglobals.signal_mgr.connect('sig_format_usb2', utils.evt_format_usb2)
        cglobals.signal_mgr.connect('sig_mount_nfsa', utils.evt_mount_nfsa)
        cglobals.signal_mgr.connect('sig_mount_nfsb', utils.evt_mount_nfsb)
        cglobals.signal_mgr.connect('sig_set_nes_color', utils.set_core_nes_color)
        cglobals.signal_mgr.connect('sig_set_sgb_color', utils.set_core_sgb_color)
        cglobals.signal_mgr.connect('sig_set_sms_fm', utils.set_core_sms_fm)
        cglobals.signal_mgr.connect('sig_set_core_region', utils.set_core_region)
        cglobals.signal_mgr.connect('sig_sys_mon_mgr', cglobals.sys_mon_mgr.check)
        cglobals.signal_mgr.connect('sig_scan_wifi', utils.scan_wifi)
        cglobals.signal_mgr.connect('sig_sys_update', utils.sys_update)
        cglobals.signal_mgr.connect('sig_scr_update', utils.scr_update)
        cglobals.signal_mgr.connect('sig_set_scroll_led', utils.set_scroll_led)
        cglobals.signal_mgr.connect('sig_enable_audio_jack', utils.enable_audio_jack)
        cglobals.signal_mgr.connect('sig_disable_audio_jack', utils.disable_audio_jack)
        cglobals.signal_mgr.connect('sig_enable_overclock', utils.enable_overclock)
        cglobals.signal_mgr.connect('sig_disable_overclock', utils.disable_overclock)
        cglobals.signal_mgr.connect('sig_enable_fan', utils.enable_fan)
        cglobals.signal_mgr.connect('sig_disable_fan', utils.disable_fan)
        cglobals.signal_mgr.connect('sig_init_fan', utils.init_fan)
        cglobals.signal_mgr.connect('sig_set_ntsc_filter', utils.set_core_ntsc_filter)
        cglobals.signal_mgr.connect('sig_set_core_overclock', utils.set_core_overclock)
        cglobals.signal_mgr.connect('sig_load_scraper_db', utils.load_scraper_db)

    def submit_signal(self, signal):
        cglobals.signal_mgr.amit(signal)

    def submit_event(self, event):
        self.events.append(event)

    def check_events(self):
        if 'expand_sd' in self.events:
            self.events.remove('expand_sd')
            self.submit_signal('sig_expand_sd')
        elif 'sd_expanded' in self.events:
            self.events.remove('sd_expanded')
            rtk.user_msg.display(title='expand_title',text='expand_complete_info')
            rtk.cfg_fst_boot = 'false'
            time.sleep(5)
            utils.shutdown(reboot=True, save_cfg=True)
        elif 'interval_check' in self.events:
            self.events.remove('interval_check')
            cglobals.last_time_check = cglobals.time
            self.submit_signal('sig_check_usb_drive')
            self.submit_signal('sig_check_joys')
            self.submit_signal('sig_check_ips')
            self.submit_signal('sig_sys_mon_mgr')
        elif 'save_config' in self.events:
            self.events.remove('save_config')
            self.submit_signal('sig_save_cfg')
        elif 'scan_scrap_games' in self.events:
            self.events.remove('scan_scrap_games')
            self.submit_signal('sig_scan_scrap_games')
        elif 'save_preset' in self.events:
            self.events.remove('save_preset')
            self.submit_signal('sig_save_preset')
        elif 'scan_bt' in self.events:
            self.events.remove('scan_bt')
            self.submit_signal('sig_scan_bt')
        elif 'unpair_bt' in self.events:
            self.events.remove('unpair_bt')
            self.submit_signal('sig_unpair_bt')
        elif 'pair_bt' in self.events:
            self.events.remove('pair_bt')
            self.submit_signal('sig_pair_bt')
        elif 'wifi_connect' in self.events:
            self.events.remove('wifi_connect')
            self.submit_signal('sig_wifi_connect')
        elif 'wifi_disconnect' in self.events:
            self.events.remove('wifi_disconnect')
            self.submit_signal('sig_wifi_disconnect')
        elif 'scan_wifi' in self.events:
            self.events.remove('scan_wifi')
            self.submit_signal('sig_scan_wifi')
        elif 'enable_netplay' in self.events:
            self.events.remove('enable_netplay')
            self.submit_signal('sig_enable_netplay')
        elif 'disable_netplay' in self.events:
            self.events.remove('disable_netplay')
            self.submit_signal('sig_disable_netplay')
        elif 'refresh_list_mode' in self.events:
            self.events.remove('refresh_list_mode')
            self.submit_signal('sig_refresh_list_mode')
        elif 'save_autoconf' in self.events:
            self.events.remove('save_autoconf')
            self.submit_signal('sig_save_autoconf')
        elif 'refresh_lang' in self.events:
            self.events.remove('refresh_lang')
            self.submit_signal('sig_refresh_lang')
        elif 'refresh_storage_names' in self.events:
            self.events.remove('refresh_storage_names')
            self.submit_signal('sig_refresh_storage_names')
        elif 'refresh_sys_info' in self.events:
            self.events.remove('refresh_sys_info')
            self.submit_signal('sig_refresh_sys_info')
        elif 'mount_sd' in self.events:
            self.events.remove('mount_sd')
            self.submit_signal('sig_mount_sd')
        elif 'mount_usb1' in self.events:
            self.events.remove('mount_usb1')
            self.submit_signal('sig_mount_usb1')
        elif 'mount_usb2' in self.events:
            self.events.remove('mount_usb2')
            self.submit_signal('sig_mount_usb2')
        elif 'format_usb1' in self.events:
            self.events.remove('format_usb1')
            self.submit_signal('sig_format_usb1')
        elif 'format_usb2' in self.events:
            self.events.remove('format_usb2')
            self.submit_signal('sig_format_usb2')
        elif 'mount_nfsa' in self.events:
            self.events.remove('mount_nfsa')
            self.submit_signal('sig_mount_nfsa')
        elif 'mount_nfsb' in self.events:
            self.events.remove('mount_nfsb')
            self.submit_signal('sig_mount_nfsb')
        elif 'set_nes_color' in self.events:
            self.events.remove('set_nes_color')
            self.submit_signal('sig_set_nes_color')
        elif 'set_sgb_color' in self.events:
            self.events.remove('set_sgb_color')
            self.submit_signal('sig_set_sgb_color')
        elif 'set_sms_fm' in self.events:
            self.events.remove('set_sms_fm')
            self.submit_signal('sig_set_sms_fm')
        elif 'set_core_region' in self.events:
            self.events.remove('set_core_region')
            self.submit_signal('sig_set_core_region')
        elif 'sys_update' in self.events:
            self.events.remove('sys_update')
            self.submit_signal('sig_sys_update')
        elif 'scr_update' in self.events:
            self.events.remove('scr_update')
            self.submit_signal('sig_scr_update')
        elif 'set_scroll_led' in self.events:
            self.events.remove('set_scroll_led')
            self.submit_signal('sig_set_scroll_led')
        elif 'refresh_helpers' in self.events:
            self.events.remove('refresh_helpers')
            self.submit_signal('sig_refresh_helpers')
        elif 'enable_audio_jack' in self.events:
            self.events.remove('enable_audio_jack')
            self.submit_signal('sig_enable_audio_jack')
        elif 'disable_audio_jack' in self.events:
            self.events.remove('disable_audio_jack')
            self.submit_signal('sig_disable_audio_jack')
        elif 'enable_overclock' in self.events:
            self.events.remove('enable_overclock')
            self.submit_signal('sig_enable_overclock')
        elif 'disable_overclock' in self.events:
            self.events.remove('disable_overclock')
            self.submit_signal('sig_disable_overclock')
        elif 'enable_fan' in self.events:
            self.events.remove('enable_fan')
            self.submit_signal('sig_enable_fan')
        elif 'disable_fan' in self.events:
            self.events.remove('disable_fan')
            self.submit_signal('sig_disable_fan')
        elif 'init_fan' in self.events:
            self.events.remove('init_fan')
            self.submit_signal('sig_init_fan')
        elif 'set_ntsc_filter' in self.events:
            self.events.remove('set_ntsc_filter')
            self.submit_signal('sig_set_ntsc_filter')
        elif 'set_core_overclock' in self.events:
            self.events.remove('set_core_overclock')
            self.submit_signal('sig_set_core_overclock')
        elif 'load_scraper_db' in self.events:
            self.events.remove('load_scraper_db')
            self.submit_signal('sig_load_scraper_db')