from os import name
import rtk
import cglobals
import utils

class Vkeyb_View(object):
    def __init__(self, is_active=False):
        self.gen_keyboard(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.vkeyb_info_y = rtk.vkeyb_info_y_tate
            self.vkeyb_y = rtk.vkeyb_y_tate
            self.help_y = rtk.help_y_tate
        else:
            self.vkeyb_info_y = rtk.vkeyb_info_y
            self.vkeyb_y = rtk.vkeyb_y
            self.help_y = rtk.help_y

    def gen_keyboard(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.mode = None
        # Option title
        self.title = rtk.RtkText(
            name      = 'vkeyb_title',
            text      = 'vkeyb',
            is_active = is_active,
            color     = rtk.vkeyb_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.vkeyb_title_x,rtk.vkeyb_title_y),
            colorkey  = rtk.color_key)
        # Virtual keyboard
        self.vkeyb = rtk.RtkVirtuaKb(
            name                 = 'virtual_keyboard',
            text                 = '',
            is_active            = is_active,
            bg_color             = rtk.vkeyb_bg_color,
            border_color         = rtk.vkeyb_border_color,
            txt_box_color        = rtk.vkeyb_txt_box_color,
            txt_box_border_color = rtk.vkeyb_txt_box_border_color,
            position             = ('center',self.vkeyb_y)
        )
        # Item info
        self.item_info = rtk.RtkText(
            name      = 'vkeyb_item_info',
            text      = '',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            color     = rtk.vkeyb_info_color,
            position  = ('center',self.vkeyb_info_y),
            colorkey  = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='vkeyb_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.vkeyb,
            self.item_info,
            self.helper))
        self.__update_vkeyb_pos()

    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'vkeyb_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'vkeyb_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'vkeyb_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'vkeyb_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'vkeyb_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'vkeyb_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'vkeyb_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'vkeyb_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'vkeyb_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'vkeyb_helper',
                image     = image,
                is_active = is_active,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_info(self):
        self.item_info.set_position(position=('center',self.vkeyb_info_y),is_tate=utils.is_tate())

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_vkeyb_pos(self):
        self.vkeyb.set_position(position=('center',self.vkeyb_y),is_tate=utils.is_tate())

    def __update_title(self):
        self.title.set_text(is_tate=utils.is_tate(),position=(rtk.vkeyb_title_x,rtk.vkeyb_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.__update_vkeyb_pos()
        self.__update_info()
        self.__update_helper()

    def set_view(self,title,text,info,mode):
        self.title.set_text(text=title,is_tate=utils.is_tate(),position=(rtk.vkeyb_title_x,rtk.vkeyb_title_y))
        self.vkeyb.set_text(text)
        self.item_info.set_text(info)
        self.__update_info()
        self.mode = mode

    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def confirm(self):
        if cglobals.vkeyb_txt:
            if self.mode == 'kiosk':
                if rtk.cfg_kiosk_mode == 'off':
                    rtk.cfg_kiosk_mode = 'on'
                    rtk.cfg_kiosk_pwd = cglobals.vkeyb_txt
                    cglobals.sys_opt_main_view.refresh_options()
                    cglobals.event_mgr.submit_event('save_config')
                    rtk.notif_msg.display(text='locked', l_icon='clocker',allow_hide=False)
                elif rtk.cfg_kiosk_mode == 'on':
                    if cglobals.vkeyb_txt == str(rtk.cfg_kiosk_pwd):
                        rtk.cfg_kiosk_mode = 'off'
                        cglobals.sys_opt_main_view.refresh_options()
                        cglobals.event_mgr.submit_event('save_config')
                        rtk.notif_msg.display(text='unlocked', l_icon='olocker',allow_hide=False)
                    elif cglobals.vkeyb_txt != str(rtk.cfg_kiosk_pwd):
                        rtk.notif_msg.display(text='wrong_pwd', l_icon='forbidden',allow_hide=False)
                self.close(goto_view='last_view')
            elif self.mode == 'wifi_pwd':
                rtk.cfg_wifi_pwd = cglobals.vkeyb_txt
                rtk.cfg_wifi_ssid = str(cglobals.tmp_value)
                rtk.cfg_wifi = 'on'
                cglobals.event_mgr.submit_event('save_config')
                utils.set_wifi_config()
                utils.wifi_connect()
                cglobals.sys_opt_network_view.set_ssid_name(name=utils.get_active_wifi_ssid())
                cglobals.sys_opt_network_view.refresh_values()
                cglobals.sys_opt_wifi_view.set_wifi_names()
                cglobals.sys_opt_wifi_view.refresh_values()
                return_view = 'sys_opt_network_view'
                utils.clear_navigation(up_to_view=return_view)
                self.close(goto_view=return_view)
            elif self.mode == 'nick':
                rtk.cfg_nick = cglobals.vkeyb_txt
                cglobals.event_mgr.submit_event('save_config')
                cglobals.sys_opt_netplay_view.set_nick_name(name=cglobals.vkeyb_txt)
                cglobals.sys_opt_netplay_view.refresh_values()
                self.close(goto_view='last_view')
            elif self.mode == 'reset_config':
                if cglobals.vkeyb_txt != '1234':
                    rtk.notif_msg.display(text='wrong_pwd', l_icon='forbidden',allow_hide=False)
                else:
                    utils.restore_config()
                self.close(goto_view='last_view')
            elif self.mode == 'nfs':
                if cglobals.tmp_value == 'nfsa':
                    rtk.cfg_nfsa = cglobals.vkeyb_txt
                elif cglobals.tmp_value == 'nfsb':
                    rtk.cfg_nfsb = cglobals.vkeyb_txt
                cglobals.event_mgr.submit_event('save_config')
                cglobals.sys_opt_storage_view.set_server_shares()
                cglobals.sys_opt_storage_view.refresh_values()
                return_view = 'sys_opt_storage_view'
                utils.clear_navigation(up_to_view=return_view)
                self.close(goto_view=return_view)
            elif self.mode == 'cheevos_pwd':
                rtk.cfg_cheevos_pwd = cglobals.vkeyb_txt
                cglobals.event_mgr.submit_event('save_config')
                self.close(goto_view='last_view')

    def close(self,goto_view):
        self.mode = None
        cglobals.vkeyb_txt = ''
        self.vkeyb.clear_value()
        utils.goto_view(goto_view)

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'D-Pad Up':
                    self.vkeyb.move_prev_row()
                elif event.key == 'D-Pad Down':
                    self.vkeyb.move_next_row()
                elif event.key == 'D-Pad Left':
                    self.vkeyb.move_prev_key()
                elif event.key == 'D-Pad Right':
                    self.vkeyb.move_next_key()
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    value = self.vkeyb.select_char()
                    if value == 'key_end':
                        self.confirm()
                    else:
                        cglobals.vkeyb_txt = value
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE' or event.key == 'K_ESCAPE':
                    self.close('last_view')
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    value = self.vkeyb.delete_last_char()
                    cglobals.vkeyb_txt = value

    # Draw UI object animations
    def draw(self, time_step):
        self.vkeyb.animate(time_step)
