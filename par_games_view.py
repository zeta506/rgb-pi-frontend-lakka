import re
import rtk
import utils
import cglobals
import itertools
import os
import launcher

class Par_Games_View(object):
    def __init__(self, system, is_active=False):
        # Menu initialization
        self.gen_menu(system, is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.game_info_x = rtk.game_info_x_tate
            self.game_info_y = rtk.game_info_y_tate
            self.help_y = rtk.help_y_tate
            self.game_pager_x = rtk.game_pager_x_tate
            self.game_pager_y = rtk.game_pager_y_tate
            self.scrap_info_title_y = rtk.scrap_info_title_y_tate
            self.scrap_info_x = rtk.scrap_info_x_tate
            self.scrap_info_y = rtk.scrap_info_y_tate
            self.game_img_r_indicator_x = rtk.game_img_r_indicator_x_tate
            self.game_list_size = rtk.game_list_size_tate
            self.game_line_size = rtk.game_line_size_tate
        else:
            self.game_info_x = rtk.game_info_x
            self.game_info_y = rtk.game_info_y
            self.help_y = rtk.help_y
            self.game_pager_x = rtk.game_pager_x
            self.game_pager_y = rtk.game_pager_y
            self.scrap_info_title_y = rtk.scrap_info_title_y
            self.scrap_info_x = rtk.scrap_info_x
            self.scrap_info_y = rtk.scrap_info_y
            self.game_img_r_indicator_x = rtk.game_img_r_indicator_x
            self.game_list_size = rtk.game_list_size
            self.game_line_size = rtk.game_line_size

    def gen_menu(self, system, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.system = system
        self.item_index = 0
        self.sort_by = 'Name'
        self.is_img_mode = False
        self.img_types = ('title','ingame','box','info')
        self.img_type_index = 0
        if not is_refresh:
            self.items_backup = []
            # Gen game items
            self.get_items()
            # Sort items
            self.sort_items()
            # Get all game item names
            self.get_game_names()
        # Game title
        self.title = rtk.RtkText(
            name      = self.system + '_games_title',
            text      = utils.get_system_full_name(short_name=self.system,break_name=True),
            is_active = is_active,
            color     = rtk.game_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.game_title_x,rtk.game_title_y),
            colorkey  = rtk.color_key)
        # Game list
        #rtk.logging.info('%s Games %s',self.system,self.game_names)
        self.game_list = rtk.RtkTextList(
            name         = self.system + '_games_list',
            text         = self.game_names,
            is_active    = is_active,
            font         = 'list',
            translate    = False,
            box_size     = self.game_line_size,
            color        = rtk.game_list_color,
            color_select = rtk.game_list_select_color,
            bg_color     = rtk.game_list_select_color_bg,
            position     = (rtk.game_list_x,rtk.game_list_y),
            line_space   = rtk.game_list_line_space,
            list_size    = self.game_list_size)
        self.set_max_sizes()
        # Item selector
        self.item_selector = rtk.RtkSelector(
            name       = self.system + '_games_selector',
            is_active  = is_active,
            position   = (rtk.game_selector_x,rtk.game_selector_y),
            line_space = rtk.game_list_line_space)
        # Page indicator
        self.page_indicator = rtk.RtkPageIndicator(
            name        = self.system + '_games_page',
            is_active   = is_active,
            font        = 'helper',
            color       = rtk.game_pager_color,
            position    = (self.game_pager_x,self.game_pager_y),
            colorkey    = rtk.color_key)
        # Game info
        self.item_info = rtk.RtkText(
            name      = self.system + '_game_item_info',
            text      = 'dummy item info',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            color     = rtk.game_info_color,
            position  = (self.game_info_x,self.game_info_y),
            colorkey  = rtk.color_key)
        # Game scraper info text
        self.item_info_detail_title = rtk.RtkText(
            name      = self.system + '_game_item_info_detail_title',
            text      = 'details',
            is_active = is_active,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = ('center',self.scrap_info_title_y),
            colorkey  = rtk.color_key)
        self.item_info_detail = rtk.RtkText(
            name      = self.system + '_game_item_info_detail',
            text      = 'dummy item info',
            is_active = is_active,
            font      = 'list',
            is_tate   = utils.is_tate(),
            position  = (self.scrap_info_x,self.scrap_info_y),
            colorkey  = rtk.color_key)
        self.item_info_detail_title._layer = 3
        self.item_info_detail._layer = 3
        self.update_info()
        # Game image
        self.game_img = rtk.RtkImage(name=self.system + '_game_image', image=None, position=('center','center'), colorkey=rtk.color_key)
        self.game_img._layer = 3
        self.l_img_indicator = rtk.RtkSprite(
            name       = self.system + '_game_l_img_indicator',
            is_active  = is_active,
            image      = 'indicator.bmp',
            flip       = True,
            position   = (rtk.game_img_l_indicator_x,'center'),
            colorkey   = rtk.color_key)
        self.r_img_indicator = rtk.RtkSprite(
            name       = self.system + '_game_r_img_indicator',
            is_active  = is_active,
            image      = 'indicator.bmp',
            position   = (self.game_img_r_indicator_x,'center'),
            colorkey   = rtk.color_key)
        self.l_img_indicator._layer = 3
        self.r_img_indicator._layer = 3
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Bind objects to list object
        self.game_list.append(self.page_indicator)
        self.game_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name=self.system + '_games_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.game_list,
            self.item_info,
            self.helper,
            self.game_img,
            self.item_info_detail_title,
            self.item_info_detail,
            self.l_img_indicator,
            self.r_img_indicator))

    def sort_items(self):
        if self.sort_by == 'Name':
            self.items = sorted(self.items, key=lambda row:(row['File'].lower() != '#is_folder', row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['File'].lower() != '#is_folder', row['Name'].lower()), reverse=True)
        elif self.sort_by == 'Year':
            self.items = sorted(self.items, key=lambda row:(row['Year'],row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['Year'],row['Name'].lower()), reverse=True)
        elif self.sort_by == 'Players':
            self.items = sorted(self.items, key=lambda row:(row['Players'],row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['Players'],row['Name'].lower()), reverse=True)
        elif self.sort_by == 'System':
            self.items = sorted(self.items, key=lambda row:(row['System'],row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['System'],row['Name'].lower()), reverse=True)
        elif self.sort_by == 'Genre':
            self.items = sorted(self.items, key=lambda row:(row['Genre'],row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['Genre'],row['Name'].lower()), reverse=True)
        elif self.sort_by == 'Developer':
            self.items = sorted(self.items, key=lambda row:(row['Developer'],row['Name'].lower()), reverse=False)
            self.items_reverse = sorted(self.items, key=lambda row:(row['Developer'],row['Name'].lower()), reverse=True)

    def update_info(self, system):
        item = self.items[self.item_index]
        info = []
        icons = []
        if utils.is_tate(): max_chars = 14
        else:               max_chars = 20
        # File info
        file = item['File']
        rom_info = str(re.findall(r'\(.*?\)',file.lower()))
        rom_extra_info = str(re.findall(r'\[.*?\]',file.lower()))
        # Game title
        label = rtk.get_translation('title').upper()
        value = item['Name']
        detail_txt = utils.fit_text(label + ': ' + value, mode='short_multiline')
        # System
        label = rtk.get_translation('system').upper()
        value = system
        detail_txt += '|' + utils.fit_text(label + ': ' + value, mode='short_multiline')
        # Developer
        label = rtk.get_translation('developer').upper()
        value = item['Developer']
        if value != '?':
            value = value.replace('?','') # Fix char font missing
            info.append(value.upper())
        detail_txt += '|' + label + ': ' + value
        # Genre
        label = rtk.get_translation('genre').upper()
        value = item['Genre']
        if value != '?':
            icons.append(value)
            icons.append(' ')
            detail_txt += '|' + label + ': <' + value + '> ' + value
        else:
            detail_txt += '|' + label + ': ' + value
        # Year
        label = rtk.get_translation('year').upper()
        value = item['Year']
        info.append(value)
        detail_txt += '|' + label + ': ' + value
        # Num players
        num_players = item['Players']
        info.append(num_players+'P')
        label = rtk.get_translation('players').upper()
        detail_txt += '|' + label + ': ' + num_players
        # Core logo icon
        value = ''
        if 'fbneo' in file:
            value = 'fbneo'
        elif 'mame' in file:
            value = 'mame'
        if value:
            icons.append(value)
            icons.append(' ')
            detail_txt += '|CORE: <' + value + '> ' + value.capitalize()
        # Regions
        region = []
        if 'world' in rom_info:
            region.append('world')
        if 'usa' in rom_info:
            region.append('usa')
        if 'europe' in rom_info:
            region.append('europe')
        if 'japan' in rom_info:
            region.append('japan')
        if 'china' in rom_info:
            region.append('china')
        if 'korea' in rom_info:
            region.append('korea')
        if 'taiwan' in rom_info:
            region.append('taiwan')
        if 'asia' in rom_info:
            region.append('japan')
            region.append('china')
            region.append('korea')
            region.append('taiwan')
        if 'australia' in rom_info:
            region.append('australia')
        if 'spain' in rom_info:
            region.append('spain')
        if 'germany' in rom_info:
            region.append('germany')
        if 'france' in rom_info:
            region.append('france')
        if 'italy' in rom_info:
            region.append('italy')
        if 'brazil' in rom_info:
            region.append('brazil')
        if 'portugal' in rom_info:
            region.append('portugal')
        if 'sweden' in rom_info:
            region.append('sweden')
        if region:
            #icons.append('region')
            icons += region
            icons.append(' ')
            reg = []
            for r in region:
                reg.append(r.capitalize())
            region = (',').join(reg)
            label = rtk.get_translation('region').upper()
            detail_txt += '|' + utils.fit_text(label + ': <region> ' + region, mode='short_multiline')
        # Translation icon and flag
        translation = ''
        if re.findall(r't.spa',rom_extra_info):
            translation = 'spain'
        elif re.findall(r't.ger',rom_extra_info):
            translation = 'germany'
        elif re.findall(r't.fre',rom_extra_info):
            translation = 'france'
        elif re.findall(r't.ita',rom_extra_info):
            translation = 'italy'
        elif re.findall(r't.bra',rom_extra_info):
            translation = 'brazil'
        elif re.findall(r't.por',rom_extra_info):
            translation = 'portugal'
        elif re.findall(r't.eng',rom_extra_info):
            translation = 'english'
        if 'trans' in rom_info or 'tradu' in rom_info or 'trans' in rom_extra_info or 'tradu' in rom_extra_info or translation:
            icons.append('translation')
            icons.append(translation)
            icons.append(' ')
            label = rtk.get_translation('translation').upper()
            detail_txt += '|' + label + ': <translation> ' + translation.capitalize()
        # Special icons
        special = False
        misc = []
        if 'pirate' in rom_info or 'unl' in rom_info or 'hack' in rom_info:
            icons.append('skull')
            special=True
        if 'proto' in rom_info or 'beta' in rom_info:
            icons.append('pencil')
            special=True
        if special:
            icons.append(' ')
            if 'pirate' in rom_info:
                misc.append('<skull> Pirate')
            if 'unl' in rom_info:
                misc.append('<skull> Unlicense')
            if 'hack' in rom_info:
                misc.append('<skull> Hack')
            if 'proto' in rom_info:
                misc.append('<pencil> Prototype')
            if 'beta' in rom_info:
                misc.append('<pencil> Beta')
            misc = (',').join(misc)
            label = 'MISC: '
            detail_txt += '|' + utils.fit_text(label + misc, mode='short_multiline')
        # Save Game
        if self.__has_save(file):
            icons.append('save')
        # Update info
        info_txt = ','.join(info)
        self.item_info.set_text(text=info_txt, r_icon=icons, is_tate=utils.is_tate())
        self.item_info.set_position(position=(self.game_info_x,self.game_info_y),is_tate=utils.is_tate())
        # Add ID and file name
        detail_txt += '|ID: ' + item['Id']
        label = rtk.get_translation('file').upper()
        value = item['File'].split('/')[-1]
        text = utils.fit_text(label + ': ' + value, mode='short_multiline')
        detail_txt += '|' + text
        # Update detail info text
        self.item_info_detail.set_text(text=detail_txt)

    def set_max_sizes(self):
        # Set sizes and draw elipsis
        max_item_sizes = list(itertools.repeat(int(self.game_line_size/8), self.game_list_size))
        rtk.logging.debug('List max sizes: %s', max_item_sizes)
        self.game_list.set_max_sizes(max_item_sizes)
        self.game_list.box_size = self.game_line_size

    def update_list(self):
        self.item_index = 0
        self.game_list.list_size = self.game_list_size
        self.get_items()
        self.sort_items()
        self.get_game_names()
        self.game_list.set_txt_list(text=self.game_names)
        self.game_list.index = self.item_index
        self.game_list.box_size = self.game_line_size
        self.set_max_sizes()
        self.game_list.refresh(force_refresh=True)

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())
    
    def __update_page_indicator(self):
        self.page_indicator.set_position(position=(self.game_pager_x, self.game_pager_y),is_tate=utils.is_tate())

    def __update_scraper_info_pos(self):
        self.item_info_detail_title.set_position(position=('center',self.scrap_info_title_y),is_tate=utils.is_tate())
        self.item_info_detail.set_position(position=(self.scrap_info_x,self.scrap_info_y),is_tate=utils.is_tate())
        self.l_img_indicator.set_position((rtk.game_img_l_indicator_x,'center'),is_tate=utils.is_tate())
        self.r_img_indicator.set_position((self.game_img_r_indicator_x,'center'),is_tate=utils.is_tate())
    
    def __update_title(self):
        title = utils.get_system_full_name(short_name=self.system,break_name=True)
        self.title.set_text(text=title, is_tate=utils.is_tate(),position=(rtk.game_title_x,rtk.game_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.update_list()
        self.update_info()
        self.update_img()
        self.__update_helper()
        self.__update_page_indicator()
        self.__update_scraper_info_pos()

    def __has_save(self, game_path):
        save_file = ''
        auto_save_file = ''
        auto_save_file1 = ''
        auto_save_file2 = ''
        auto_save_file3 = ''
        auto_save_file4 = ''
        if game_path != '#is_folder':
            save_file = os.path.splitext(game_path)[0]+'.state'
            auto_save_file = os.path.splitext(game_path)[0]+'.state.auto'
            auto_save_file1 = os.path.splitext(game_path)[0]+'.state.auto1'
            auto_save_file2 = os.path.splitext(game_path)[0]+'.state.auto2'
            auto_save_file3 = os.path.splitext(game_path)[0]+'.state.auto3'
            auto_save_file4 = os.path.splitext(game_path)[0]+'.state.auto4'
        return (os.path.isfile(save_file) or os.path.isfile(auto_save_file) or os.path.isfile(auto_save_file1)
            or os.path.isfile(auto_save_file2) or os.path.isfile(auto_save_file3) or os.path.isfile(auto_save_file4))

    def is_auto_play(self, game_file):
        item = self.items[self.item_index]
        return item['System'] == cglobals.autoplay['system'] \
            and item['Subsystem'] == cglobals.autoplay['sub_system'] \
            and game_file == cglobals.autoplay['game_path']

    def is_game_fav(self, game_file):
        if utils.is_tate():
            for fav in cglobals.favorites_tate:
                if fav['File'] == game_file:
                    return True
        else:
            for fav in cglobals.favorites:
                if fav['File'] == game_file:
                    return True
        return False

    def update_img(self):
        item = self.items[self.item_index]
        id = item['Id']
        if not id: id = 'none'
        img_type = self.img_types[self.img_type_index]
        if img_type == 'info':
            if utils.is_tate():
                img = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/info_tate.bmp'
            else:
                img = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/info.bmp'
            self.item_info_detail_title.show()
            self.item_info_detail.show()
        else:
            img = rtk.path_rgbpi_scraper + '/images/' + id + '_' + img_type + '_' + rtk.cfg_scrap_region + '.png'
            if not os.path.isfile(img):
                img_usa = rtk.path_rgbpi_scraper + '/images/' + id + '_' + img_type + '_' + 'usa.png'
                img_eur = rtk.path_rgbpi_scraper + '/images/' + id + '_' + img_type + '_' + 'eur.png'
                img_jap = rtk.path_rgbpi_scraper + '/images/' + id + '_' + img_type + '_' + 'jap.png'
                if os.path.isfile(img_usa):
                    img = img_usa
                elif os.path.isfile(img_eur):
                    img = img_eur
                elif os.path.isfile(img_jap):
                    img = img_jap
                elif img_type == 'title':
                    img = rtk.path_rgbpi_images + '/no_title.png'
                elif img_type == 'ingame':
                    img = rtk.path_rgbpi_images + '/no_ingame.png'
                elif img_type == 'box':
                    img = rtk.path_rgbpi_images + '/no_box.png'
            self.item_info_detail_title.hide()
            self.item_info_detail.hide()
        self.has_img = self.game_img.change_image(img)
        self.game_img.set_position(position=('center','center'),is_tate=utils.is_tate())
    
    def next_img(self):
        self.has_img = False
        while not self.has_img:
            if self.img_type_index == len(self.img_types) - 1:
                self.img_type_index = 0
            else:
                self.img_type_index += 1
            self.update_img()

    def prev_img(self):
        self.has_img = False
        while not self.has_img:
            if self.img_type_index == 0:
                self.img_type_index = len(self.img_types) - 1
            else:
                self.img_type_index -= 1
            self.update_img()

    def toggle_img_mode(self):
        self.update_img()
        if self.is_img_mode:
            self.hide_img()
        else:
            self.__show_img()

    def __show_img(self):
        if self.has_img:
            self.is_img_mode = True
            self.game_list.hide_selector()
            self.l_img_indicator.show()
            self.r_img_indicator.show()
            self.game_img.show()

    def hide_img(self):
        self.is_img_mode = False
        self.img_type_index = 0
        self.l_img_indicator.hide()
        self.r_img_indicator.hide()
        self.game_img.hide()
        self.item_info_detail_title.hide()
        self.item_info_detail.hide()
        self.game_list.show_selector()

    def jump_ahead(self, jump_by):
        # Set jump pattern
        if jump_by == 'Name':
            current_game_search_pattern = self.items[self.item_index][jump_by][:1].lower()
        else:
            current_game_search_pattern = self.items[self.item_index][jump_by]
        # Do the jump
        jump_next = False
        for i, game in enumerate(self.items):
            if jump_by == 'Name':
                self.search_pattern = game[jump_by][:1].lower()
            else:
                self.search_pattern = game[jump_by]
            if self.search_pattern != current_game_search_pattern and i > self.item_index:
                self.item_index = i
                jump_next = True
                break
        if not jump_next:
            self.item_index = 0
            if jump_by == 'Name':
                self.search_pattern = self.items[self.item_index][jump_by][:1].lower()
            else:
                self.search_pattern = self.items[self.item_index][jump_by]
        if jump_by == 'System':
            self.search_pattern = utils.get_system_full_name(short_name=self.search_pattern)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)
        if self.search_pattern == '<':
            self.search_pattern = '<folder> <forward>'
        else:
            self.search_pattern = self.search_pattern.upper() + ' <forward>'
        rtk.notif_msg.display(text=self.search_pattern)

    def jump_back(self, jump_by):
        # Set jump pattern
        if jump_by == 'Name':
            current_game_search_pattern = self.items[self.item_index][jump_by][:1].lower()
        else:
            current_game_search_pattern = self.items[self.item_index][jump_by]
        # Do the jump
        jump_prev = False
        index_desc = len(self.items) - self.item_index - 1
        if jump_by == 'Name':
            current_game_search_pattern = self.items[self.item_index][jump_by][:1].lower()
        else:
            current_game_search_pattern = self.items[self.item_index][jump_by]
        jump_pattern = ''
        for i, game in enumerate(self.items_reverse):
            if jump_by == 'Name':
                self.search_pattern = game[jump_by][:1].lower()
            else:
                self.search_pattern = game[jump_by]
            if self.search_pattern != current_game_search_pattern and i > index_desc:
                jump_pattern = self.search_pattern
                jump_prev = True
                break
        if jump_prev:
            for i, game in enumerate(self.items):
                if jump_by == 'Name':
                    self.search_pattern = game[jump_by][:1].lower()
                else:
                    self.search_pattern = game[jump_by]
                if self.search_pattern == jump_pattern:
                    self.item_index = i
                    break
        else:
            self.item_index = len(self.items) - 1
            if jump_by == 'Name':
                self.search_pattern = self.items[self.item_index][jump_by][:1].lower()
            else:
                self.search_pattern = self.items[self.item_index][jump_by]
        if jump_by == 'System':
            self.search_pattern = utils.get_system_full_name(short_name=self.search_pattern)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)
        if self.search_pattern == '<':
            self.search_pattern = '<backward> <folder>'
        else:
            self.search_pattern = '<backward> ' + self.search_pattern.upper()
        rtk.notif_msg.display(text=self.search_pattern)

    def exit(self):
        if cglobals.favs_has_changed or cglobals.auto_has_changed:
            rtk.popup_msg.display(text='loading')
            if cglobals.favs_has_changed:
                cglobals.favs_has_changed = False
                if utils.is_tate():
                    if utils.has_favs() and 'favorites' not in cglobals.system_names_tate or \
                       not utils.has_favs() and 'favorites' in cglobals.system_names_tate:
                        utils.update_sys_favs()
                        cglobals.systems_view.refresh_view()
                else:
                    if utils.has_favs() and 'favorites' not in cglobals.system_names or \
                       not utils.has_favs() and 'favorites' in cglobals.system_names:
                        utils.update_sys_favs()
                        cglobals.systems_view.refresh_view()
                utils.write_favorites()
                utils.refresh_all_game_views()
            if cglobals.auto_has_changed:
                cglobals.auto_has_changed = False
                utils.refresh_all_game_views()
            rtk.popup_msg.hide()
        utils.goto_view('last_view')

    def activate(self):
        self.container_view.activate()
        self.hide_img()

    def deactivate(self):
        self.container_view.deactivate()

    def change_sort(self, sort_by):
        self.item_index = 0
        self.sort_by = sort_by
        self.sort_items()
        self.get_game_names()
        self.game_list.set_txt_list(text=self.game_names)
        self.game_list.index = self.item_index
        self.game_list.refresh(force_refresh=True)
        self.update_info()
        self.gen_helper(is_active=True)

    def toggle_autoplay(self):
        cglobals.auto_has_changed = True
        item = self.items[self.item_index]
        system = item['System']
        sub_system = item['Subsystem']
        game_file = item['File']
        auto_play = rtk.path_rgbpi_data + '/autoplay.dat'
        autoplay_info = system + '|' + sub_system + '|' + game_file
        if game_file != '#is_folder':
            if self.is_auto_play(game_file):
                cglobals.autoplay['do_launch'] = None
                cglobals.autoplay['system'] = None
                cglobals.autoplay['sub_system'] = None
                cglobals.autoplay['game_path'] = None
                with open(auto_play, 'w', encoding='utf-8') as file:
                    file.write('')
            else:
                cglobals.autoplay['system'] = system
                cglobals.autoplay['sub_system'] = sub_system
                cglobals.autoplay['game_path'] = game_file
                with open(auto_play, 'w', encoding='utf-8') as file:
                    file.write(autoplay_info)
            self.get_game_names()
            self.game_list.set_txt_list(text=self.game_names)
            self.game_list.index = self.item_index
            self.game_list.refresh(force_refresh=True)

    def toggle_favorite(self):
        # Update vars
        cglobals.favs_has_changed = True
        item = self.items[self.item_index]
        game_file = item["File"]
        if utils.is_tate():
            if self.is_game_fav(game_file):
                for i, fav in enumerate(cglobals.favorites_tate):
                    if fav['File'] == game_file:
                        del cglobals.favorites_tate[i]
                        break
            else:
                cglobals.favorites_tate.append(item)
        else:
            if self.is_game_fav(game_file):
                for i, fav in enumerate(cglobals.favorites):
                    if fav['File'] == game_file:
                        rtk.logging.info('del: fav %s, game %s',fav['File'],game_file)
                        del cglobals.favorites[i]
                        break
            else:
                rtk.logging.info('add: fav %s',game_file)
                cglobals.favorites.append(item)

    def launch_content(self,system):
        cglobals.launcher['game_id'] = self.items[self.item_index]['Id']
        cglobals.launcher['return_view'] = utils.get_view_name()
        cglobals.launcher['game_path'] = self.items[self.item_index]['File']
        # Set selected system
        cglobals.launcher['system'] = system
        if system == 'arcade':
            cglobals.launcher['neogeo_mode'] = 'MVS_EUR'
            if rtk.cfg_show_hotkey == 'on':
                utils.goto_view('info_key_view')
            else:
                launcher.launch_content()
        elif system == 'neogeo':
            utils.goto_view('sel_ng_mode_view')
        elif system == 'gba' or system == 'ngp':
            utils.goto_view('sel_handheld_mode_view')
        else:
            if rtk.cfg_show_hotkey == 'on':
                utils.goto_view('info_key_view')
            else:
                launcher.launch_content()

    # Draw UI object animations
    def draw(self, time_step):
        self.game_list.scroll_item_sel(speed=96, time_step=time_step)
        self.game_list.anim_selector(time_step=time_step)