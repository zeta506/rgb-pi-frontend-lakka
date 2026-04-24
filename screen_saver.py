import rtk
import utils
import cglobals
import random
import os
import random
import launcher

class Screen_Saver(object):
    def __init__(self,is_active=False):
        # Menu initialization
        self.gen_screen_saver(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.title_y = 18
            self.info_y = 298
        else:
            self.title_y = 18
            self.info_y = 210

    def gen_screen_saver(self, is_active, is_refresh=False):
        if rtk.cfg_screensaver == 'flying_logo':
            self.gen_flying_logo(is_active, is_refresh)
        elif rtk.cfg_screensaver == 'slide_show':
            self.gen_slide_show(is_active, is_refresh)
        elif rtk.cfg_screensaver == 'black_screen':
            self.gen_black_screen(is_active, is_refresh)

    def gen_black_screen(self, is_active, is_refresh=False):
        # Black BG
        self.black_img = rtk.RtkRect(name='black_img', w=rtk.scr_w, h=rtk.scr_h, is_active=is_active, position=(0,0))
        self.black_img_tate = rtk.RtkRect(name='black_img_tate', w=rtk.scr_h, h=rtk.scr_w, is_active=is_active, position=(0,0))
        self.black_img._layer = 5
        self.black_img_tate._layer = 5
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='screen_saver_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.black_img,
            self.black_img_tate
        ))

    def gen_flying_logo(self, is_active, is_refresh=False):
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.num_sprites = 20
        # Black BG
        self.black_img = rtk.RtkRect(name='black_img', w=rtk.scr_w, h=rtk.scr_h, is_active=is_active, position=(0,0))
        self.black_img_tate = rtk.RtkRect(name='black_img_tate', w=rtk.scr_h, h=rtk.scr_w, is_active=is_active, position=(0,0))
        self.black_img._layer = 5
        self.black_img_tate._layer = 5
        # Images
        self.sprites = []
        for i in range(0,self.num_sprites):
            name = 'flying_logo_' + str(i)
            angle = random.randrange(0,360,10)
            if angle == 0 or angle == 90 or angle == 180 or angle == 270 or angle == 360:
                angle += 10
            x = random.randrange(0,240,10)
            y = random.randrange(0,240,10)
            scr_srv_img = rtk.RtkSprite(
                name      = name,
                image     = 'scr_svr.bmp',
                angle     = angle,
                is_active = is_active,
                position  = (x,y),
                colorkey  = rtk.color_key)
            scr_srv_img._layer = 5
            self.sprites.append(scr_srv_img)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='screen_saver_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.black_img,
            self.black_img_tate
        ))
        rtk.ContainerMgr.append(parent=self.container_view, child=(self.sprites))

    def gen_slide_show(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.num_sprites = 1
        self.image_num = 0
        # Get scraper image files
        path = rtk.path_rgbpi_scraper + '/images'
        self.games = {}
        self.slide_show = []
        all_games = {}
        for sys_games in cglobals.games:
            for game in sys_games:
                id = game['Id']
                all_games[id] = game
        for entry in sorted(os.scandir(path), key=lambda e: e.name):
            if entry.is_file and 'ingame' in entry.name:
                image = entry.path.split('/')[-1]
                game_id = image.split('/')[-1].split('_')[0]
                # Add images only for existing games
                try:
                    game = all_games[game_id]
                    self.games[game_id] = {'System':game['System'], 'File':game['File']}
                    self.slide_show.append(path + '/' + image)
                except:
                    pass
        random.shuffle(self.slide_show)
        if not self.slide_show:
            self.slide_show.append('no_ingame.png')
        # Black BG
        self.black_img = rtk.RtkRect(name='black_img', w=rtk.scr_w, h=rtk.scr_h, is_active=is_active, position=(0,0))
        self.black_img_tate = rtk.RtkRect(name='black_img_tate', w=rtk.scr_h, h=rtk.scr_w, is_active=is_active, position=(0,0))
        self.black_img._layer = 5
        self.black_img_tate._layer = 5
        # Images
        self.sprites = []
        scr_srv_img = rtk.RtkSprite(
            name      = 'slide_show_0',
            image     = self.slide_show[self.image_num],
            is_active = is_active,
            is_tate   = utils.is_tate(),
            position  = ('center','center'),
            colorkey  = rtk.color_key)
        scr_srv_img._layer = 5
        self.sprites.append(scr_srv_img)
        # System Name
        self.item_title = rtk.RtkText(
            name      = 'slide_show_title',
            text      = self.get_system(),
            is_active = is_active,
            font      = 'list',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            translate = False,
            position  = ('center',self.title_y),
            colorkey  = rtk.color_key)
        self.item_title._layer = 6
        # Game Name
        self.item_info = rtk.RtkText(
            name      = 'slide_show_info',
            text      = self.get_name(),
            is_active = is_active,
            font      = 'list',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            translate = False,
            position  = ('center',self.info_y),
            colorkey  = rtk.color_key)
        self.item_info._layer = 6
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='screen_saver_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.black_img,
            self.black_img_tate,
            self.item_title,
            self.item_info
        ))
        rtk.ContainerMgr.append(parent=self.container_view, child=(self.sprites))

    def get_id(self):
        return self.slide_show[self.image_num].split('/')[-1].split('_')[0]

    def get_system(self):
        try:
            short_name = self.games[self.get_id()]['System']
            full_name = utils.get_system_full_name(short_name, break_name=False)
            return full_name
        except:
            return ''

    def get_name(self):
        try:
            game_id = self.get_id()
            if rtk.cfg_scrap_region == 'usa':
                game_name = cglobals.scraper_db_2[game_id]['NAME_USA']
            elif rtk.cfg_scrap_region == 'eur':
                game_name = cglobals.scraper_db_2[game_id]['NAME_EUR']
            elif rtk.cfg_scrap_region == 'jap':
                game_name = cglobals.scraper_db_2[game_id]['NAME_JAP']
            game_name = utils.fit_text(game_name, mode='full_elipsis')
            return game_name
        except:
            return ''

    def launch_game(self):
        game_id = self.get_id()
        if game_id in self.games:
            game_info = self.games[game_id]
            if utils.check_rom_path(game_info['File']):
                system = game_info['System']
                cglobals.launcher['game_id'] = game_id
                cglobals.launcher['return_view'] = utils.get_view_name()
                cglobals.launcher['game_path'] = game_info['File']
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

    def refresh_view(self):
        pass

    def activate(self):
        if utils.is_tate():
            self.black_img.deactivate()
            self.black_img_tate.activate()
        else:
            self.black_img.activate()
            self.black_img_tate.deactivate()
        if rtk.cfg_screensaver == 'slide_show':
            self.item_title.activate()
            self.item_info.activate()
        if rtk.cfg_screensaver in ('flying_logo','slide_show'):
            for i in range(0,self.num_sprites):
                self.sprites[i].activate()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                if event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    self.launch_game()
                else:
                    cglobals.stop_action = True
                    cglobals.scr_wait_time = 0
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        if rtk.cfg_screensaver == 'flying_logo':
            for i in range(0,self.num_sprites):
                self.sprites[i].bounce(64,time_step,utils.is_tate())
        elif rtk.cfg_screensaver == 'slide_show':
            self.sprites[0].fade(50, time_step)
            if self.sprites[0].alpha <= 0:
                self.__set_positions()
                self.image_num += 1
                if self.image_num == len(self.slide_show):
                    self.image_num = 0
                self.sprites[0].change_image(self.slide_show[self.image_num])
                self.sprites[0].set_position(('center','center'), is_tate=utils.is_tate())
                self.sprites[0].set_alpha(0)
                system_name = self.get_system()
                game_name = self.get_name()
                self.item_title.set_text(text=system_name, position=('center',self.title_y), is_tate=utils.is_tate())
                self.item_info.set_text(text=game_name, position=('center',self.info_y), is_tate=utils.is_tate())