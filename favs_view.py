import rtk
import utils
import cglobals
import os
from par_games_view import Par_Games_View

class Favs_View(Par_Games_View):
    
    def get_items(self):
        self.items = utils.get_games(self.system)

    def get_game_names(self):
        self.game_names = []
        for game in self.items:
            game_file = game['File']
            game_name = game['Name']
            is_autoplay = self.is_auto_play(game_file)
            if is_autoplay:
                game_name = '<star> ' + game_name
            self.game_names.append(game_name)

    def update_info(self):
        self.item_index = self.game_list.get_list_info()[0]
        item = self.items[self.item_index]
        system = utils.get_system_full_name(short_name=item['System'], break_name=True)
        self.title.set_text(text=system, l_icon='heart',position=(rtk.game_title_x,rtk.game_title_y))
        super().update_info(system)

    def gen_helper(self, is_active, force_refresh=False):
        if rtk.cfg_button_style == 'snes':
            self.helper_game_img = 'game_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            self.helper_game_img = 'game_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            self.helper_game_img = 'game_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            self.helper_game_img = 'game_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            self.helper_game_img = 'game_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            self.helper_game_img = 'game_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            self.helper_game_img = 'game_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            self.helper_game_img = 'game_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            self.helper_game_img = 'game_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name       = self.system + '_games_helper',
                is_active  = is_active,
                image      = self.helper_game_img,
                position   = (rtk.help_x,self.help_y),
                colorkey   = rtk.color_key)
            self.helper._layer = 3
        if force_refresh:
            self.helper.change_image(image=self.helper_game_img, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def toggle_favorite(self):
        # Update vars
        super().toggle_favorite()
        # Update view
        if not utils.has_favs():
            self.exit()
        else:
            if self.item_index > 0:
                self.item_index -= 1
            self.get_items()
            self.sort_items()
            self.get_game_names()
            self.game_list.set_txt_list(text=self.game_names)
            self.game_list.index = self.item_index
            self.game_list.refresh(force_refresh=True)
            self.update_info()  

    def launch_content(self):
        system = self.items[self.item_index]['System']
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
                    self.exit()
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    self.toggle_img_mode()
                elif event.key == cglobals.input_mgr.joy_action_4 or event.key == 'K_Y':
                    self.hide_img()
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
                    utils.goto_view('favs_opt_view')