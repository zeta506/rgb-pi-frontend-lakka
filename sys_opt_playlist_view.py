import rtk
import utils
import cglobals

class Sys_Opt_Playlist_View(object):
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
        else:
            self.opt_value_list_x = rtk.opt_value_list_x
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
            name      = 'playlist_opt_title',
            text      = 'playlist',
            is_active = is_active,
            color     = rtk.opt_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.opt_title_x,rtk.opt_title_y),
            colorkey  = rtk.color_key)
        # Option list >> left_icon | text | right icon | color
        self.options = cglobals.playlist_folders
        self.option_list = rtk.RtkTextList(
            name         = 'playlist_opt_list',
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
            name       = 'playlist_opt_sel',
            is_active  = is_active,
            position   = (rtk.opt_selector_x,rtk.opt_selector_y),
            line_space = rtk.opt_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = 'playlist_opt_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.opt_pager_color,
            position    = (self.opt_pager_x,self.opt_pager_y),
            colorkey    = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Bind objects to list object
        self.option_list.append(self.page_indicator)
        self.option_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='playlist_opt_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
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
                name      = 'playlist_opt_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def update_list(self):
        utils.load_music()
        self.options = cglobals.playlist_folders
        self.option_list.set_txt_list(text=self.options)
        self.option_list.list_size = self.opt_list_size
        self.option_list.box_size = self.opt_line_size
        self.option_list.index=0
        self.option_list.set_position(position=(rtk.opt_list_x,rtk.opt_list_y))
        self.item_selector.set_position(position=(rtk.opt_selector_x,rtk.opt_selector_y))
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
        self.update_list()
        self.__update_helper()
        self.__update_page_indicator()
        self.refresh_values()

    def __get_current_option(self):
        item_index = self.option_list.get_list_info()[0]
        option = self.options[item_index]
        if '|' in option:
            option = option.split('|')[1]
        return option

    def set_playlist(self, name):
        rtk.cfg_playlist = name
        cglobals.event_mgr.submit_event('save_config')
        cglobals.sound_mgr.set_playlist()
        cglobals.sound_mgr.stop_music()
        cglobals.sound_mgr.play_bg_music()

    def refresh_values(self):
        pass
            
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
                elif event.key == 'D-Pad Down':
                    self.option_list.goto_next_item()
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    utils.goto_view('systems_view')
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    rtk.popup_msg.display(text='loading')
                    self.set_playlist(name=self.__get_current_option())
                    rtk.popup_msg.hide()
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    cglobals.sys_opt_sound_view.set_playlist_name(name=rtk.cfg_playlist)
                    cglobals.sys_opt_sound_view.refresh_values()
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.scroll_item_sel(speed=96, time_step=time_step)
        self.option_list.anim_selector(time_step=time_step)