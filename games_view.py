import rtk
import utils
import cglobals
import os
from par_games_view import Par_Games_View

class Games_View(Par_Games_View):
    def gen_menu(self, system, is_active, is_refresh=False):
        # Folder params
        self.reset_folder_params(system)
        super().gen_menu(system, is_active, is_refresh)
    
    def reset_folder_params(self,system):
        self.is_current_helper_folder = False
        self.root_deep = len((cglobals.mount_point + '/roms').split('/')) + 1 # +1 to take into account the current system menu folder 
        self.current_deep = self.root_deep
        self.current_path = (cglobals.mount_point + '/roms').split('/')
        self.current_path.append(system)
        self.tracking_folder_index = [0]
    
    def get_items(self,reload=False):
        if self.system == 'recents':
            self.items = utils.get_games(self.system)
            return
        # Get game items in folder mode or plain list
        if rtk.cfg_list_mode == 'folder_list':
            # Clear all current items
            self.items = []
            paths = []
            # Get the full list of items if was not already retrieved
            if not self.items_backup or reload:
                self.items_backup = utils.get_games(self.system)
                self.item_index = 0
            # Traverse all items in the current folder deep
            for game in self.items_backup:
                item = game['File'].split('/')
                item_deep = len(item) - 1 # -1 to remove the item name from the path
                # Skip items in upper folder levels with no parents in the current folder deep
                if item_deep >= self.current_deep:
                    item_path = item[:self.current_deep]
                    item_name = item[self.current_deep]
                    # Retrieve items corresponding only to the current folder
                    if item_path == self.current_path:
                        # Check if it is game or folder item
                        folder_path = '/'.join(item_path) + '/' + item_name
                        #if os.path.isdir(folder_path): # Performance issues on folders with thousands of files
                        if '.' not in item_name:
                            if folder_path not in paths:
                                paths.append(folder_path)
                                item = {'Id':'','Hash':'','System':game['System'],'Subsystem':game['Subsystem'],'File':'#is_folder','Name':'<folder> '+item_name,'Genre':'','Developer':'','Year':'','Players':''}
                                self.items.append(item)
                        else:
                            item = game
                            self.items.append(item)
        elif rtk.cfg_list_mode == 'flat_list':
            self.items = utils.get_games(self.system)

    def get_game_names(self):
        self.folders = []
        self.game_names = []
        for game in self.items:
            game_file = game['File']
            game_name = game['Name']
            if game_file == '#is_folder' and game_name not in self.folders:
                self.folders.append(game_name)
            is_favorite = self.is_game_fav(game_file)
            is_autoplay = self.is_auto_play(game_file)
            if is_favorite:
                game_name = '<heart> ' + game_name
            if is_autoplay:
                game_name = '<star> ' + game_name
            self.game_names.append(game_name)

    def update_info(self):
        self.item_index = self.game_list.get_list_info()[0]
        if self.__is_item_folder():
            self.item_info.set_text(text='folder', l_icon='folder')
            self.item_info.set_position(position=(self.game_info_x,self.game_info_y))
        else:
            if self.system == 'recents':
                system = utils.get_system_full_name(short_name=self.items[self.item_index]['System'], break_name=True)
            else:
                system = utils.get_system_full_name(short_name=self.system, break_name=True)
            super().update_info(system)

    def sort_items(self):
        if self.system == 'recents':
            return
        super().sort_items()

    def gen_helper(self, is_active, force_refresh=False):
        if rtk.cfg_button_style == 'snes':
            self.helper_game_img = 'game_help_snes.bmp'
            self.helper_folder_img = 'folder_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            self.helper_game_img = 'game_help_smd.bmp'
            self.helper_folder_img = 'folder_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            self.helper_game_img = 'game_help_neogeo.bmp'
            self.helper_folder_img = 'folder_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            self.helper_game_img = 'game_help_psx.bmp'
            self.helper_folder_img = 'folder_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            self.helper_game_img = 'game_help_xbox.bmp'
            self.helper_folder_img = 'folder_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            self.helper_game_img = 'game_help_jamma3.bmp'
            self.helper_folder_img = 'folder_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            self.helper_game_img = 'game_help_jamma6.bmp'
            self.helper_folder_img = 'folder_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            self.helper_game_img = 'game_help_mvs.bmp'
            self.helper_folder_img = 'folder_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            self.helper_game_img = 'game_help_pce.bmp'
            self.helper_folder_img = 'folder_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name       = self.system + '_games_helper',
                is_active  = is_active,
                image      = self.helper_game_img,
                position   = (rtk.help_x,self.help_y),
                colorkey   = rtk.color_key)
            self.helper._layer = 3
        if self.__is_item_folder() != self.is_current_helper_folder or force_refresh:
            self.is_current_helper_folder = self.__is_item_folder()
            if self.is_current_helper_folder:
                self.helper.change_image(image=self.helper_folder_img, colorkey=rtk.color_key)
            else:
                self.helper.change_image(image=self.helper_game_img, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __is_item_folder(self):
        item = self.items[self.item_index]
        return item['File'] == '#is_folder'
    
    def __is_in_folder(self):
        return self.current_deep > self.root_deep

    def __drill_down_folder(self):
        self.current_path.append(self.items[self.item_index]['Name'].replace('<folder> ',''))
        self.tracking_folder_index[-1] = self.item_index # Save current
        self.current_deep += 1
        self.item_index = 0
        self.tracking_folder_index.append(self.item_index) # Save new
        self.get_items()
        self.sort_items()
        self.get_game_names()
        self.game_list.set_txt_list(text=self.game_names)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)

    def __drill_up_folder(self):
        self.current_path.pop()
        self.tracking_folder_index.pop()
        self.current_deep -= 1
        self.item_index = self.tracking_folder_index[-1]
        self.get_items()
        self.sort_items()
        self.get_game_names()
        self.game_list.set_txt_list(text=self.game_names)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)

    def toggle_favorite(self):
        # Update vars
        super().toggle_favorite()
        # Update view
        self.get_game_names()
        self.game_list.set_txt_list(text=self.game_names)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)    

    def launch_content(self,system=None):
        if not system:
            system = self.system
        if self.system == 'recents':
            system = self.items[self.item_index]['System']
        rtk.logging.info('system %s', system)
        super().launch_content(system)
    
    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'D-Pad Up':
                    self.game_list.goto_prev_item()
                    self.update_info()
                    self.gen_helper(is_active=True)
                    #self.hide_img()
                    self.update_img()
                elif event.key == 'D-Pad Down':
                    self.game_list.goto_next_item()
                    self.update_info()
                    self.gen_helper(is_active=True)
                    #self.hide_img()
                    self.update_img()
                elif event.key == 'D-Pad Left':
                    if self.is_img_mode:
                        self.prev_img()
                    else:
                        self.game_list.goto_prev_page()
                        self.update_info()
                        self.gen_helper(is_active=True)
                        self.hide_img()
                elif event.key == 'D-Pad Right':
                    if self.is_img_mode:
                        self.next_img()
                    else:
                        self.game_list.goto_next_page()
                        self.update_info()
                        self.gen_helper(is_active=True)
                        self.hide_img()
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    self.hide_img()
                    if self.__is_item_folder():
                        self.__drill_down_folder()
                        self.set_max_sizes()
                        self.update_info()
                        self.gen_helper(is_active=True)
                    else:
                        # Check if game file exists
                        if not os.path.isfile(self.items[self.item_index]['File']):
                            rtk.notif_msg.display(text='no_game_info', l_icon='forbidden')
                        else:
                            # Check if is NFS and the game is being played by other user
                            if os.path.isfile(self.items[self.item_index]['File']+'.bussy'):
                                rtk.notif_msg.display(text='game_in_use_info', l_icon='forbidden')
                            else:
                                self.launch_content()
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    self.hide_img()
                    if self.__is_in_folder():
                        self.__drill_up_folder()
                        self.update_info()
                        self.gen_helper(is_active=True)
                    else:
                        self.exit()
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    if not self.__is_item_folder():
                        self.toggle_img_mode()
                elif event.key == cglobals.input_mgr.joy_action_4 or event.key == 'K_Y':
                    self.hide_img()
                    if not self.__is_item_folder():
                        if rtk.cfg_kiosk_mode == 'off':
                            self.toggle_favorite()
                        else:
                            rtk.notif_msg.display(text='kiosk_mode', l_icon='forbidden')
                elif event.key == cglobals.input_mgr.joy_special_1 or event.key == 'K_PAGEUP':
                    self.hide_img()
                    self.jump_back(jump_by=self.sort_by)
                elif event.key == cglobals.input_mgr.joy_special_2 or event.key == 'K_PAGEDOWN':
                    self.hide_img()
                    self.jump_ahead(jump_by=self.sort_by)
                elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                    self.hide_img()
                    utils.goto_view('games_opt_view')
