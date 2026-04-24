import rtk
import utils
import cglobals

class Sys_Opt_Main_View(object):
    def __init__(self,is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.help_y = rtk.help_y_tate
            self.opt_pager_x = rtk.opt_pager_x_tate
            self.opt_pager_y = rtk.opt_pager_y_tate
            self.opt_list_size = rtk.opt_list_size_tate
            self.opt_line_size = rtk.opt_line_size_tate
        else:
            self.help_y = rtk.help_y
            self.opt_pager_x = rtk.opt_pager_x
            self.opt_pager_y = rtk.opt_pager_y
            self.opt_list_size = rtk.opt_list_size
            self.opt_line_size = rtk.opt_line_size

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        self.is_help_mode = False
        # Option title
        self.title = rtk.RtkText(
            name      = 'main_opt_title',
            text      = 'options',
            is_active = is_active,
            color     = rtk.opt_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.opt_title_x,rtk.opt_title_y),
            colorkey  = rtk.color_key)
        # Option list >> left_icon | text | right icon | color
        self.options = [
            'tv|display|elipsis',
            'speaker|sound|elipsis',
            'joystick|control|elipsis',
            'network|network|elipsis',
            'avatar|online|elipsis',
            'config|system|elipsis',
            'usb|storage|elipsis|' + str(rtk.opt_list_highlight),
            'invader|emulation|elipsis',
            'magnifier|scan_games||' + str(rtk.opt_list_highlight),
            'info|information',
            'help|system_help',
            'olocker|kiosk_mode',
            'power|shutdown||' + str(rtk.opt_list_highlight_2)
        ]
        self.option_list = rtk.RtkTextList(
            name         = 'main_opt_list',
            text         = self.options,
            is_active    = is_active,
            font         = 'list',
            translate    = True,
            box_size     = self.opt_line_size,
            color        = rtk.opt_list_color,
            color_select = rtk.opt_list_select_color,
            bg_color     = rtk.opt_list_select_color_bg,
            position     = (rtk.opt_list_x,rtk.opt_list_y),
            line_space   = rtk.opt_list_line_space,
            list_size    = self.opt_list_size)
        # Item selector
        self.item_selector = rtk.RtkSelector(
            name       = 'main_opt_sel',
            is_active  = is_active,
            position   = (rtk.opt_selector_x,rtk.opt_selector_y),
            line_space = rtk.opt_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = 'main_opt_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.opt_pager_color,
            position    = (self.opt_pager_x,self.opt_pager_y),
            colorkey    = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Help Image
        self.help_img = rtk.RtkImage(name='help_qr', image='help_qr.bmp', is_active=is_active, position=('center','center'), colorkey=rtk.color_key)
        self.help_img._layer = 3
        # Bind objects to list object
        self.option_list.append(self.page_indicator)
        self.option_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='main_opt_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
            self.helper,
            self.help_img))

    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'opt_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'opt_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'opt_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'opt_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'opt_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'opt_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'opt_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'opt_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'opt_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'main_opt_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_list(self):
        self.option_list.list_size = self.opt_list_size
        self.option_list.box_size = self.opt_line_size
        self.option_list.refresh(force_refresh=True)

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_page_indicator(self):
        self.page_indicator.set_position(position=(self.opt_pager_x, self.opt_pager_y),is_tate=utils.is_tate())

    def __update_title(self):
        self.title.set_text(is_tate=utils.is_tate(),position=(rtk.opt_title_x,rtk.opt_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.__update_list()
        self.__update_helper()
        self.__update_page_indicator()

    def refresh_options(self):
        if rtk.cfg_kiosk_mode == 'on':
            self.options[11] = 'clocker|kiosk_mode'
        elif rtk.cfg_kiosk_mode == 'off':
            self.options[11] = 'olocker|kiosk_mode'
        self.option_list.set_txt_list(text=self.options, index=self.item_index)

    def __get_current_option(self):
        item_index = self.option_list.get_list_info()[0]
        option = self.options[item_index]
        if '|' in option:
            option = option.split('|')[1]
        return option

    def __toggle_help_mode(self):
        if self.is_help_mode:
            self.__hide_help()
        else:
            self.__show_help()

    def __show_help(self):
        self.is_help_mode = True
        self.option_list.hide_selector()
        self.option_list.hide()
        self.title.set_text(text='system_help')
        self.help_img.set_position(('center','center'),is_tate=utils.is_tate())
        self.help_img.show()

    def __hide_help(self):
        self.is_help_mode = False
        self.help_img.hide()
        self.title.set_text(text='options')
        self.option_list.show()
        self.option_list.show_selector()

    def activate(self):
        self.container_view.activate()
        self.__hide_help()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'D-Pad Up':
                    self.__hide_help()
                    self.option_list.goto_prev_item()
                elif event.key == 'D-Pad Down':
                    self.__hide_help()
                    self.option_list.goto_next_item()
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if self.__get_current_option() == 'display':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_display_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'sound':
                        if rtk.cfg_kiosk_mode == 'off':
                            cglobals.sys_opt_sound_view.refresh_values()
                            utils.goto_view('sys_opt_sound_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'control':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_control_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'network':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_network_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'online':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_netplay_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'system':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_system_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'storage':
                        if rtk.cfg_kiosk_mode == 'off':
                            cglobals.event_mgr.submit_event('refresh_storage_names')
                            utils.goto_view('sys_opt_storage_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'emulation':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sys_opt_emulation_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'scan_games':
                        if rtk.cfg_kiosk_mode == 'off':
                            utils.goto_view('sel_scan_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                    elif self.__get_current_option() == 'information':
                        rtk.popup_msg.display(text='loading')
                        cglobals.sys_opt_info_view.refresh_values()
                        utils.goto_view('sys_opt_info_view')
                        rtk.popup_msg.hide()
                    elif self.__get_current_option() == 'system_help':
                        self.__toggle_help_mode()
                    elif self.__get_current_option() == 'kiosk_mode':
                        cglobals.vkeyb_view.set_view(title='kiosk_mode',text='',info='password',mode='kiosk')
                        utils.goto_view('vkeyb_view')
                    elif self.__get_current_option() == 'shutdown':
                        utils.goto_view('sel_shutdown_view')
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    self.__hide_help()
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    self.__hide_help()
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.scroll_item_sel(speed=96, time_step=time_step)
        self.option_list.anim_selector(time_step=time_step)