import rtk
import utils
import cglobals
import launcher

class Info_Keys_View(object):
    def __init__(self, is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.help_y = rtk.help_y_tate
            self.key_img_x = 24
            self.key_img_y = 58
            self.key_info_x = 44
            self.key_info_y = 56
        else:
            self.help_y = rtk.help_y
            self.key_img_x = 24
            self.key_img_y = 58
            self.key_info_x = 44
            self.key_info_y = 56

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        # Option title
        self.title = rtk.RtkText(
            name      = 'key_info_title',
            text      = 'hotkeys',
            is_active = is_active,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.selector_title_x,rtk.selector_title_y),
            colorkey  = rtk.color_key)
        # Image information
        self.key_img = rtk.RtkImage(
            name      = 'key_info_img',
            image     = 'key_info_icons.bmp',
            is_active = is_active,
            position  = (self.key_img_x,self.key_img_y),
            colorkey  = rtk.color_key)
        # Key information
        self.key_inf = rtk.RtkText(
            name      = 'key_info',
            text      = 'key_info',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            translate = True,
            position  = (self.key_info_x,self.key_info_y),
            colorkey  = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='key_info_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.key_img,
            self.key_inf,
            self.helper))
            
    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'sel_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'sel_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'sel_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'sel_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'sel_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'sel_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'sel_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'sel_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'sel_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'key_info_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())
        self.__update_info()

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_info(self):
        self.key_img.change_image(image='key_info_icons.bmp', colorkey=rtk.color_key)
        self.key_img.set_position(position=(self.key_img_x,self.key_img_y),is_tate=utils.is_tate())
        self.key_inf.set_text(position=(self.key_info_x,self.key_info_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_info()
        self.__update_helper()
    
    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    launcher.launch_content()
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        pass