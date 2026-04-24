import rtk
import utils
import cglobals

class Games_Opt_View(object):
    def __init__(self, is_fav, is_active=False):
        # Menu initialization
        self.gen_menu(is_fav, is_active)

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

    def gen_menu(self, is_fav, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        if is_fav:
            self.type = 'fav'
        else:
            self.type = 'game'
        # Option title
        self.title = rtk.RtkText(
            name      = self.type + '_opt_title',
            text      = 'options',
            is_active = is_active,
            color     = rtk.opt_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.opt_title_x,rtk.opt_title_y),
            colorkey  = rtk.color_key)
        # Option list
        if is_fav:
            self.options = [
                'sort_by_name',
                'sort_by_dev',
                'sort_by_genre',
                'sort_by_year',
                'sort_by_players',
                'sort_by_system',
                'toggle_favorite',
                'auto_play'
            ]
        else:
            self.options = [
                'sort_by_name',
                'sort_by_dev',
                'sort_by_genre',
                'sort_by_year',
                'sort_by_players',
                'toggle_favorite',
                'auto_play'
            ]
        self.option_list = rtk.RtkTextList(
            name         = self.type + '_opt_list',
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
            name       = self.type + '_opt_sel',
            is_active  = is_active,
            position   = (rtk.opt_selector_x,rtk.opt_selector_y),
            line_space = rtk.opt_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = self.type + '_opt_page',
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
            self.container_view = rtk.ContainerMgr.create(name=self.type+'_opt_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
            self.helper))
            
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
                name      = self.type+'_opt_helper',
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

    def __get_current_option(self):
        item_index = self.option_list.get_list_info()[0]
        return self.options[item_index]
    
    def __change_sort(self, sort_by):
        rtk.popup_msg.display(text='loading')
        games_view = eval('cglobals.' + cglobals.nav_history[-2])
        games_view.change_sort(sort_by)
        rtk.popup_msg.hide()

    def __toggle_auto_play(self):
        rtk.popup_msg.display(text='loading')
        games_view = eval('cglobals.' + cglobals.nav_history[-2])
        games_view.toggle_autoplay()
        rtk.popup_msg.hide()

    def __toggle_fav(self):
        rtk.popup_msg.display(text='loading')
        games_view = eval('cglobals.' + cglobals.nav_history[-2])
        games_view.toggle_favorite()
        rtk.popup_msg.hide()

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
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if self.__get_current_option() == 'sort_by_name':
                        self.__change_sort(sort_by='Name')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'sort_by_dev':
                        self.__change_sort(sort_by='Developer')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'sort_by_genre':
                        self.__change_sort(sort_by='Genre')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'sort_by_year':
                        self.__change_sort(sort_by='Year')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'sort_by_players':
                        self.__change_sort(sort_by='Players')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'sort_by_system':
                        self.__change_sort(sort_by='System')
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'toggle_favorite':
                        self.__toggle_fav()
                        utils.goto_view('last_view')
                    elif self.__get_current_option() == 'auto_play':
                        if rtk.cfg_kiosk_mode == 'off':
                            self.__toggle_auto_play()
                            utils.goto_view('last_view')
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.scroll_item_sel(speed=96, time_step=time_step)
        self.option_list.anim_selector(time_step=time_step)