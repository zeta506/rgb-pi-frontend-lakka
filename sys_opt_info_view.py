import rtk
import utils
import cglobals

class Sys_Opt_Info_View(object):
    def __init__(self,is_active=False):
        self.cpu_info = utils.get_cpu_info()
        self.ram_info = utils.get_ram_info()
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.opt_value_list_x = rtk.opt_value_list_x_tate
            self.opt_info_y = rtk.opt_info_y_tate
            self.help_y = rtk.help_y_tate
            self.opt_pager_x = rtk.opt_pager_x_tate
            self.opt_pager_y = rtk.opt_pager_y_tate
            self.opt_list_size = rtk.opt_list_size_tate
            self.opt_line_size = rtk.opt_line_size_tate
        else:
            self.opt_value_list_x = rtk.opt_value_list_x
            self.opt_info_y = rtk.opt_info_y
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
        # Option title
        self.title = rtk.RtkText(
            name      = 'sys_opt_info_title',
            text      = 'information',
            is_active = is_active,
            color     = rtk.opt_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.opt_title_x,rtk.opt_title_y),
            colorkey  = rtk.color_key)
        # Option list >> left_icon | text | right icon | color
        self.options = [
            'os_name',
            'os_version',
            'curret_freq',
            'ram_mem',
            'temperature',
            'disk_total',
            'disk_used',
            'disk_free',
            'num_games',
            'game_plays',
            'game_time',
            'top_system'
        ]
        self.option_list = rtk.RtkTextList(
            name         = 'sys_opt_info_list',
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
        self.value_list = rtk.RtkTextList(
            name         = 'sys_opt_info_value_list',
            text         = 'dummy',
            is_active    = is_active,
            font         = 'list',
            translate    = False,
            box_size     = self.opt_line_size,
            color        = rtk.opt_list_color,
            color_select = rtk.opt_list_select_color,
            bg_color     = rtk.opt_list_select_color_bg,
            position     = (self.opt_value_list_x,rtk.opt_value_list_y),
            align        = 'right',
            line_space   = rtk.opt_list_line_space,
            list_size    = self.opt_list_size)
        self.refresh_values()
        # Item selector
        self.item_selector = rtk.RtkSelector(
            name       = 'sys_opt_info_sel',
            is_active  = is_active,
            position   = (rtk.opt_selector_x,rtk.opt_selector_y),
            line_space = rtk.opt_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = 'sys_opt_info_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.opt_pager_color,
            position    = (self.opt_pager_x,self.opt_pager_y),
            colorkey    = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Credits
        self.item_info = rtk.RtkText(
            name      = 'credits',
            text      = 'Created By Ruben Tomas',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            color     = rtk.opt_info_color,
            translate = False,
            position  = ('center',self.opt_info_y),
            colorkey  = rtk.color_key
        )
        self.__update_info()
        # Bind objects to list object
        self.option_list.append(self.page_indicator)
        self.option_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='sys_opt_info_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
            self.value_list,
            self.item_info,
            self.helper
        ))

    def refresh_values(self):
        try:
            sensor_info = utils.get_sensor_info()
            disk_info = utils.get_disk_info()
            stats = utils.get_stats()
            values = [
                utils.get_lakka_system_version(),
                utils.get_lakka_build_version(),
                str(self.cpu_info.current_freq) + ' (' + str(self.cpu_info.revision) + ')',
                str(self.ram_info.total),
                str(sensor_info.temp),
                str(disk_info.total),
                str(disk_info.used),
                str(disk_info.free),
                str(stats.num_games),
                str(stats.num_game_plays),
                str(stats.time_game_plays),
                str(stats.top_system)
            ]
        except Exception as error:
            rtk.logging.error('Error reading info: %s', error)
            values = [
                utils.get_lakka_system_version(),
                utils.get_lakka_build_version(),
                'Error',
                'Error',
                'Error',
                'Error',
                'Error',
                'Error',
                'Error',
                'Error',
                'Error',
                'Error'
            ]
        item_index = self.option_list.get_list_info()[0]
        self.value_list.set_txt_list(text=values, index=item_index)
        # Update option text item sizes
        self.__set_max_sizes()

    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'opt_4_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'opt_4_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'opt_4_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'opt_4_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'opt_4_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'opt_4_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'opt_4_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'opt_4_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'opt_4_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'sys_opt_info_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_info(self):
        self.item_info.set_position(position=('center',self.opt_info_y),is_tate=utils.is_tate())

    def __set_max_sizes(self):
        value_sizes = self.value_list.get_txt_item_sizes()
        max_item_sizes = utils.get_max_item_sizes(value_sizes)
        self.option_list.set_max_sizes(max_item_sizes) 

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
        #self.option_list.refresh(force_refresh=True)
        self.__update_value_list_pos()
        self.__update_info()
        self.__update_helper()
        self.__update_page_indicator()

    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'D-Pad Up':
                    self.option_list.goto_prev_item()
                    self.value_list.goto_prev_item()
                elif event.key == 'D-Pad Down':
                    self.option_list.goto_next_item()
                    self.value_list.goto_next_item()
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    utils.goto_view('systems_view')
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    rtk.popup_msg.display(text='loading')
                    cglobals.is_in_task = True
                    cglobals.event_mgr.submit_event('refresh_sys_info')
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.scroll_item_sel(speed=96, time_step=time_step)
        self.option_list.anim_selector(time_step=time_step)
