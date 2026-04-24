import rtk
import utils
import cglobals

class Sys_Opt_Grid_View(object):
    def __init__(self, is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.help_y = rtk.help_y_tate
            self.color_inf_x = 24
            self.color_inf_y = 56
            self.overscan_inf_x = 24
            self.overscan_inf_y = 32
        else:
            self.help_y = rtk.help_y
            self.color_inf_x = 72
            self.color_inf_y = 56
            self.overscan_inf_x = 72
            self.overscan_inf_y = 48

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        # Image grids
        self.color_grid = rtk.RtkImage(name='color_grid', image='grid_colors.bmp', is_active=is_active, position=(0,0))
        self.overscan_grid = rtk.RtkImage(name='overscan_grid', image='grid_overscan.bmp', is_active=is_active, position=(0,0))
        self.color_grid_tate = rtk.RtkImage(name='color_grid_tate', image='grid_colors.bmp', is_active=is_active, position=(0,0))
        self.overscan_grid_tate = rtk.RtkImage(name='overscan_grid_tate', image='grid_overscan.bmp', is_active=is_active, position=(0,0))
        self.color_grid_tate.rotate(angle=90)
        self.overscan_grid_tate.rotate(angle=90)
        # Color grid information
        self.color_inf = rtk.RtkText(
            name      = 'color_info',
            text      = 'color_info',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            position  = (self.color_inf_x,self.color_inf_y),
            colorkey  = rtk.color_key)
        # Overscan grid information
        self.overscan_inf = rtk.RtkText(
            name      = 'overscan_info',
            text      = 'overscan_info',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            position  = (self.overscan_inf_x,self.overscan_inf_y),
            colorkey  = rtk.color_key)
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='grid_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.color_grid,
            self.overscan_grid,
            self.color_grid_tate,
            self.overscan_grid_tate,
            self.color_inf,
            self.overscan_inf,
            self.helper))
            
    def gen_helper(self, is_active):
        if rtk.cfg_button_style == 'snes':
            image = 'grid_help_snes.bmp'
        elif rtk.cfg_button_style == 'smd':
            image = 'grid_help_smd.bmp'
        elif rtk.cfg_button_style == 'neogeo':
            image = 'grid_help_neogeo.bmp'
        elif rtk.cfg_button_style == 'psx':
            image = 'grid_help_psx.bmp'
        elif rtk.cfg_button_style == 'xbox':
            image = 'grid_help_xbox.bmp'
        elif rtk.cfg_button_style == 'jamma3':
            image = 'grid_help_jamma3.bmp'
        elif rtk.cfg_button_style == 'jamma6':
            image = 'grid_help_jamma6.bmp'
        elif rtk.cfg_button_style == 'mvs':
            image = 'grid_help_mvs.bmp'
        elif rtk.cfg_button_style == 'pce':
            image = 'grid_help_pce.bmp'
        if not self.helper:
            self.helper = rtk.RtkSprite(
                name      = 'grid_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_info(self):
        self.color_inf.set_text(position=(self.color_inf_x,self.color_inf_y))
        self.overscan_inf.set_text(position=(self.overscan_inf_x,self.overscan_inf_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_info()
        self.__update_helper()
    
    def activate(self):
        if utils.is_tate():
            self.color_grid_tate.activate()
            self.color_inf.activate()
            self.helper.activate()
        else:
            self.color_grid.activate()
            self.color_inf.activate()
            self.helper.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if self.item_index == 0:
                        self.item_index += 1
                        if utils.is_tate():
                            self.color_grid_tate.deactivate()
                            self.overscan_grid_tate.activate()
                        else:
                            self.color_grid.deactivate()
                            self.overscan_grid.activate()
                        self.color_inf.deactivate()
                        self.overscan_inf.activate()
                    elif self.item_index == 1:
                        self.item_index = 0
                        utils.goto_view('last_view')
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    if self.item_index == 0:
                        self.item_index = 0
                        utils.goto_view('last_view')
                    elif self.item_index == 1:
                        self.item_index -= 1
                        if utils.is_tate():
                            self.color_grid_tate.activate()
                            self.overscan_grid_tate.deactivate()
                        else:
                            self.color_grid.activate()
                            self.overscan_grid.deactivate()
                        self.overscan_inf.deactivate()
                        self.color_inf.activate()
                elif event.key == cglobals.input_mgr.joy_action_3 or event.key == 'K_X':
                    if self.item_index == 0:
                        if self.color_inf.visible:
                            self.color_inf.deactivate()
                        else:
                            self.color_inf.activate()

    # Draw UI object animations
    def draw(self, time_step):
        pass