import rtk
import utils
import cglobals
import launcher

class Systems_View(object):
    def __init__(self, is_active=True):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.sys_info_y = rtk.sys_info_y_tate
            self.help_y = rtk.help_y_tate
            self.sys_pager_x = rtk.sys_pager_x_tate
            self.sys_pager_y = rtk.sys_pager_y_tate
        else:
            self.sys_info_y = rtk.sys_info_y
            self.help_y = rtk.help_y
            self.sys_pager_x = rtk.sys_pager_x
            self.sys_pager_y = rtk.sys_pager_y

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        # System title
        self.title = rtk.RtkText(
            name      = 'systems_title',
            text      = 'systems',
            is_active = is_active,
            color     = rtk.sys_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.sys_title_x,rtk.sys_title_y),
            colorkey  = rtk.color_key)
        # System list
        self.system_list = rtk.RtkTextList(
            name         = 'systems_list',
            text         = utils.get_system_full_names(),
            is_active    = is_active,
            font         = 'list',
            translate    = True,
            box_size     = rtk.sys_line_size,
            color        = rtk.sys_list_color,
            color_select = rtk.sys_list_select_color,
            bg_color     = rtk.sys_list_select_color_bg,
            position     = (rtk.sys_list_x,rtk.sys_list_y),
            line_space   = rtk.sys_list_line_space,
            list_size    = rtk.sys_list_size)
        # Item selector
        self.item_selector = rtk.RtkSelector(
            name       = 'system_selector',
            is_active  = is_active,
            position   = (rtk.sys_selector_x,rtk.sys_selector_y),
            line_space = rtk.sys_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = 'systems_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.sys_pager_color,
            position    = (self.sys_pager_x,self.sys_pager_y),
            colorkey    = rtk.color_key)
        # System info
        self.item_info = rtk.RtkText(
            name      = 'system_item_info',
            text      = '',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            translate = False, # It is translated later
            color     = rtk.sys_info_color,
            position  = ('center',self.sys_info_y),
            colorkey  = rtk.color_key)
        self.__update_info()
        # System image
        self.system_img = rtk.RtkImage(name='system_image', image=None, colorkey=rtk.color_key)
        self.system_img._layer = 0 # Send image to BG
        self.__update_img()
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Bind objects to list object
        self.system_list.append(self.page_indicator)
        self.system_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='systems_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.system_img,
            self.title,
            self.system_list,
            self.item_info,
            self.helper))

    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'sys_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'sys_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'sys_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'sys_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'sys_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'sys_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'sys_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'sys_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'sys_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'systems_helper',
                image     = image,
                is_active = is_active,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_info(self):
        # Get sys info
        self.item_index = self.system_list.get_list_info()[0]
        self.system_name = utils.get_system_short_name(self.item_index)
        info = utils.get_system_info(self.item_index)
        # Set text and icon
        if 'usb' in rtk.cfg_data_source:
            self.item_info.set_text(text=info, l_icon='usb')
        elif 'nfs' in rtk.cfg_data_source:
            self.item_info.set_text(text=info, l_icon='nfs')
        else:
            self.item_info.set_text(text=info, l_icon='sd')
        self.item_info.set_position(position=('center',self.sys_info_y),is_tate=utils.is_tate())

    def __update_img(self):
        # Set system image if any
        if utils.is_tate():
            self.system_img.change_image(image=self.system_name + '_tate.bmp')
        else:
            self.system_img.change_image(image=self.system_name + '.bmp')

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())
    
    def __update_page_indicator(self):
        self.page_indicator.set_position(position=(self.sys_pager_x, self.sys_pager_y),is_tate=utils.is_tate())

    def __update_title(self):
        self.title.set_text(is_tate=utils.is_tate(),position=(rtk.sys_title_x,rtk.sys_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.system_list.set_txt_list(text=utils.get_system_full_names())
        self.item_index = self.system_list.index = 0
        self.system_list.refresh(force_refresh=True)
        self.__update_info()
        self.__update_img()
        self.__update_helper()
        self.__update_page_indicator()

    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def _launch_kodi(self):
        cglobals.launcher['game_id'] = ''
        cglobals.launcher['return_view'] = 'same_view'
        cglobals.launcher['game_path'] = rtk.path_kodi + '/kodi.sh'
        cglobals.launcher['system'] = 'kodi'
        launcher.launch_content()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'D-Pad Up':
                    self.system_list.goto_prev_item()
                    self.__update_info()
                    self.__update_img()
                elif event.key == 'D-Pad Down':
                    self.system_list.goto_next_item()
                    self.__update_info()
                    self.__update_img()
                elif event.key == 'D-Pad Left':
                    self.system_list.goto_prev_page()
                    self.__update_info()
                    self.__update_img()
                elif event.key == 'D-Pad Right':
                    self.system_list.goto_next_page()
                    self.__update_info()
                    self.__update_img()
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if self.system_name != 'none':
                        if self.system_name == 'kodi':
                            self._launch_kodi()
                        else:
                            utils.goto_view(self.system_name + '_view')
                elif event.key == cglobals.input_mgr.joy_special_1 or event.key == 'K_PAGEDOWN':
                    cglobals.sound_mgr.vol_down()
                elif event.key == cglobals.input_mgr.joy_special_2 or event.key == 'K_PAGEUP':
                    cglobals.sound_mgr.vol_up()
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    if cglobals.is_jamma and not rtk.cfg_button_style == 'jamma6':
                        cglobals.sound_mgr.vol_up()
                elif event.key == cglobals.input_mgr.joy_action_4 or event.key == 'K_Y':
                    if cglobals.is_jamma and not rtk.cfg_button_style == 'jamma6':
                        cglobals.sound_mgr.vol_down()
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    utils.goto_view('sys_opt_main_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.system_list.scroll_item_sel(speed=96, time_step=time_step)
        self.system_list.anim_selector(time_step=time_step)