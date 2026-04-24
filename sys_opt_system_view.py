import rtk
import utils
import cglobals

class Sys_Opt_System_View(object):
    def __init__(self,is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.opt_value_list_x = rtk.opt_value_list_x_tate
            self.help_y = rtk.help_y_tate
            self.opt_pager_x = rtk.opt_pager_x_tate
            self.opt_pager_y = rtk.opt_pager_y_tate
            self.opt_list_size = rtk.opt_list_size_tate
            self.opt_line_size = rtk.opt_line_size_tate
            self.opt_info_y = rtk.opt_info_y_tate
        else:
            self.opt_value_list_x = rtk.opt_value_list_x
            self.help_y = rtk.help_y
            self.opt_pager_x = rtk.opt_pager_x
            self.opt_pager_y = rtk.opt_pager_y
            self.opt_list_size = rtk.opt_list_size
            self.opt_line_size = rtk.opt_line_size
            self.opt_info_y = rtk.opt_info_y

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        # Option title
        self.title = rtk.RtkText(
            name      = 'system_opt_title',
            text      = 'system',
            is_active = is_active,
            color     = rtk.opt_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.opt_title_x,rtk.opt_title_y),
            colorkey  = rtk.color_key)
        # Option list >> left_icon | text | right icon | color
        self.options = [
            'translation|language|elipsis',
            'theme|theme|elipsis',
            'list_mode',
            'show_kodi',
            'retroarch_notif',
            'show_hotkey',
            'overclock',
            'fan',
            'update|scr_update',
            'update|sys_update',
            'reset|reset_config||' + str(rtk.opt_list_highlight_3)
        ]
        if rtk.cfg_adv_mode == 'user':
            self.options.pop(7)
            self.options.pop(8-1)
        self.non_switches = ('language','theme','scr_update','sys_update','reset_config')
        self.option_list = rtk.RtkTextList(
            name         = 'system_opt_list',
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
        # Value list
        self.values = {
            'language'       :(),
            'theme'          :(),
            'list_mode'      :('flat_list','folder_list'),
            'show_kodi'      :('off','on'),
            'retroarch_notif':('off','on'),
            'show_hotkey'    :('off','on'),
            'overclock'      :('off','on'),
            'fan'            :('off','on'),
            'scr_update'     :(),
            'sys_update'     :(),
            'reset_config'   :()
        }
        if rtk.cfg_adv_mode == 'user':
            self.values.pop('fan')
            self.values.pop('scr_update')
        self.value_list = rtk.RtkTextList(
            name         = 'system_value_list',
            text         = 'dummy',
            is_active    = is_active,
            font         = 'list',
            translate    = True,
            box_size     = self.opt_line_size,
            color        = rtk.opt_list_val_color,
            color_select = rtk.opt_list_select_val_color,
            bg_color     = rtk.opt_list_select_color_bg,
            position     = (self.opt_value_list_x,rtk.opt_value_list_y),
            align        = 'right',
            line_space   = rtk.opt_list_line_space,
            list_size    = self.opt_list_size)
        self.refresh_values()
        # Item selector
        self.item_selector = rtk.RtkSelector(
            name       = 'system_opt_sel',
            is_active  = is_active,
            position   = (rtk.opt_selector_x,rtk.opt_selector_y),
            line_space = rtk.opt_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = 'system_opt_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.opt_pager_color,
            position    = (self.opt_pager_x,self.opt_pager_y),
            colorkey    = rtk.color_key)
        # Info
        self.item_info = rtk.RtkText(
            name      = 'system_opt_item_info',
            text      = '',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            color     = rtk.opt_info_color,
            translate = True,
            position  = ('center',self.opt_info_y),
            colorkey  = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Bind objects to list object
        self.option_list.append(self.page_indicator)
        self.option_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='system_opt_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
            self.value_list,
            self.item_info,
            self.helper))

    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'opt_2_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'opt_2_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'opt_2_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'opt_2_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'opt_2_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'opt_2_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'opt_2_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'opt_2_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'opt_2_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'system_opt_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_list(self):
        self.value_list.list_size = self.opt_list_size
        self.value_list.box_size = self.opt_line_size
        self.option_list.list_size = self.opt_list_size
        self.option_list.box_size = self.opt_line_size
        self.value_list.refresh(force_refresh=True)
        self.__set_max_sizes() # This already do option_list.refresh

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_page_indicator(self):
        self.page_indicator.set_position(position=(self.opt_pager_x, self.opt_pager_y),is_tate=utils.is_tate())

    def __update_value_list_pos(self):
        self.value_list.set_position((self.opt_value_list_x,rtk.opt_value_list_y))

    def __update_title(self):
        self.title.set_text(is_tate=utils.is_tate(),position=(rtk.opt_title_x,rtk.opt_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.__update_list()
        self.__update_value_list_pos()
        self.__update_info()
        self.__update_helper()
        self.__update_page_indicator()

    def __get_current_option(self):
        item_index = self.option_list.get_list_info()[0]
        option = self.options[item_index]
        if '|' in option:
            option = option.split('|')[1]
        return option
    
    def set_prev_value(self):
        current_option = self.__get_current_option()
        current_value = str(eval('rtk.cfg_'+current_option))
        current_value_index = self.values[current_option].index(current_value)
        if current_value_index > 0:
            current_value_index -= 1
            current_value = self.values[current_option][current_value_index]
            rtk.__dict__['cfg_'+current_option] = current_value
            return True
        else:
            return False

    def set_next_value(self):
        current_option = self.__get_current_option()
        current_value = str(eval('rtk.cfg_'+current_option))
        current_value_index = self.values[current_option].index(current_value)
        if current_value_index < len(self.values[current_option])-1:
            current_value_index += 1
            current_value = self.values[current_option][current_value_index]
            rtk.__dict__['cfg_'+current_option] = current_value
            return True
        else:
            return False

    def refresh_values(self):
        values = []
        for option in self.options:
            try:
                if '|' in option:
                    option = option.split('|')[1]
                if not isinstance(self.values[option], tuple) and not isinstance(self.values[option], list):
                    values.append(self.values[option])
                else:
                    current_value = str(eval('rtk.cfg_'+option))
                    current_value_index = self.values[option].index(current_value)
                    if current_value == 'on':
                        values.append('<l_on><r_on>')
                    elif current_value == 'off':
                        values.append('<l_off><r_off>')
                    else:
                        if current_value_index == 0:
                            if len(self.values[option]) == 1:
                                values.append('|' + current_value)
                            else:
                                values.append('|' + current_value + '|r_arrow')
                        elif current_value_index == len(self.values[option])-1:
                            values.append('l_arrow|' + current_value)
                        else:
                            values.append('l_arrow|' + current_value + '|r_arrow')
            except:
                values.append('')
        item_index = self.option_list.get_list_info()[0]
        self.value_list.set_txt_list(text=values, index=item_index, l_icon_space=False)
        # Update option text item sizes
        self.__set_max_sizes()

    def __update_info(self):
        current_option = self.__get_current_option()
        if current_option == 'overclock':
            self.item_info.set_text(text='voids_warranty')
            self.item_info.set_position(position=('center',self.opt_info_y),is_tate=utils.is_tate())
        elif current_option == 'retroarch_menu':
            self.item_info.set_text(text='dr_perf_inf')
            self.item_info.set_position(position=('center',self.opt_info_y),is_tate=utils.is_tate())
        elif current_option == 'show_kodi':
            self.item_info.set_text(text='reboot_required')
            self.item_info.set_position(position=('center',self.opt_info_y),is_tate=utils.is_tate())
        else:
            self.item_info.set_text(text='')

    def __set_max_sizes(self):
        value_sizes = self.value_list.get_txt_item_sizes()
        max_item_sizes = utils.get_max_item_sizes(value_sizes)
        self.option_list.set_max_sizes(max_item_sizes)

    def apply_option(self):
        current_option = self.__get_current_option()
        if current_option == 'list_mode':
            rtk.popup_msg.display(text='loading')
            cglobals.is_in_task = True
            cglobals.event_mgr.submit_event('refresh_list_mode')
        elif current_option == 'retroarch_menu':
            cglobals.event_mgr.submit_event('save_autoconf')
            if rtk.cfg_retroarch_menu == 'on':
                rtk.notif_msg.display(text='dr_perf_inf', l_icon='info')
        elif current_option == 'overclock':
            if rtk.cfg_overclock == 'on':
                cglobals.event_mgr.submit_event('enable_overclock')
            elif rtk.cfg_overclock == 'off':
                cglobals.event_mgr.submit_event('disable_overclock')
            rtk.notif_msg.display(text='reboot_required', l_icon='info')
        elif current_option == 'fan':
            if rtk.cfg_fan == 'on':
                cglobals.event_mgr.submit_event('enable_fan')
            elif rtk.cfg_fan == 'off':
                cglobals.event_mgr.submit_event('disable_fan')
            
    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                current_option = self.__get_current_option()
                if event.key == 'D-Pad Up':
                    self.option_list.goto_prev_item()
                    self.value_list.goto_prev_item()
                    self.__update_info()
                elif event.key == 'D-Pad Down':
                    self.option_list.goto_next_item()
                    self.value_list.goto_next_item()
                    self.__update_info()
                elif event.key == 'D-Pad Left':
                    if current_option not in self.non_switches:
                        if self.set_prev_value():
                            self.refresh_values()
                            self.apply_option()
                            cglobals.event_mgr.submit_event('save_config')
                elif event.key == 'D-Pad Right':
                    if current_option not in self.non_switches:
                        '''if current_option == 'overclock' and cglobals.sys_opt_info_view.cpu_info.revision not in cglobals.allow_overclock:
                            rtk.notif_msg.display(text='overclock_ko', l_icon='forbidden')'''
                        if current_option == 'fan' and not cglobals.has_native_csync_support:
                            rtk.notif_msg.display(text='not_supported', l_icon='forbidden')
                        else:
                            if self.set_next_value():
                                self.refresh_values()
                                self.apply_option()
                                cglobals.event_mgr.submit_event('save_config')
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    utils.goto_view('systems_view')
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if current_option == 'language':
                        utils.goto_view('sys_opt_lang_view')
                    elif current_option == 'theme':
                        cglobals.sys_opt_theme_view.update_list()
                        utils.goto_view('sys_opt_theme_view')
                    elif current_option == 'scr_update':
                        rtk.popup_msg.display(text='searching_update', l_icon='magnifier')
                        cglobals.is_in_task = True
                        cglobals.event_mgr.submit_event('scr_update')
                    elif current_option == 'sys_update':
                        rtk.popup_msg.display(text='searching_update', l_icon='magnifier')
                        cglobals.is_in_task = True
                        cglobals.event_mgr.submit_event('sys_update')
                    elif current_option == 'reset_config':
                        cglobals.vkeyb_view.set_view(title='reset_config',text='',info='password',mode='reset_config')
                        utils.goto_view('vkeyb_view')
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.scroll_item_sel(speed=96, time_step=time_step)
        self.option_list.anim_selector(time_step=time_step)