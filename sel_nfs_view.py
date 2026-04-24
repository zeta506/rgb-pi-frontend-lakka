import rtk
import utils
import cglobals
import os

class Sel_NFS_View(object):
    def __init__(self, is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.help_y = rtk.help_y_tate
            self.list_y = rtk.selector_list_y_tate
            self.selector_y = rtk.selector_y_tate
        else:
            self.help_y = rtk.help_y
            self.list_y = rtk.selector_list_y
            self.selector_y = rtk.selector_y

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        self.item_index = 0
        # Option title
        self.title = rtk.RtkText(
            name      = 'nfs_title',
            text      = 'nfs',
            is_active = is_active,
            color     = rtk.selector_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.selector_title_x,rtk.selector_title_y),
            colorkey  = rtk.color_key)
        # Option list
        self.options = [
            'mount_unit',
            'configure'
        ]
        self.option_list = rtk.RtkTextList(
            name         = 'nfs_list',
            text         = self.options,
            is_active    = is_active,
            font         = 'title',
            is_upper     = True,
            translate    = True,
            box_size     = 128,
            position     = ('center',self.list_y),
            line_space   = rtk.selector_list_line_space,
            list_size    = 2)
        # Item selector
        sel_img = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/selector_sel_view.bmp'
        if not os.path.isfile(sel_img):
            sel_img = rtk.path_rgbpi + '/themes/' + rtk.cfg_theme + '/images/selector.bmp'
        self.item_selector = rtk.RtkSelector(
            name       = 'nfs_sel',
            is_active  = is_active,
            image      = sel_img,
            position   = (self.option_list.txt_items[0].position[0]-16,self.selector_y),
            line_space = rtk.selector_list_line_space)
        # Recalculate positions to fix tate
        self.__update_list()
        # Helper
        self.helper = None
        self.gen_helper(is_active)
        # Bind objects to list object
        self.option_list.append(self.item_selector)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='sel_nfs_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.option_list,
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
                name      = 'nfs_helper',
                is_active = is_active,
                image     = image,
                position  = (rtk.help_x,self.help_y),
                colorkey  = rtk.color_key)
            self.helper._layer = 3
        else:
            self.helper.change_image(image=image, colorkey=rtk.color_key)
            self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_list(self):
        self.item_index = 0
        self.option_list.index=0
        self.option_list.set_position(position=('center',self.list_y),is_tate=utils.is_tate())
        selector_x = self.option_list.txt_items[0].position[0]-16
        self.item_selector.start_pos = (selector_x,self.selector_y)
        self.item_selector.set_position(position=(selector_x,self.selector_y))
    
    def __update_sel_pos(self):
        x = self.option_list.txt_items[self.item_index].position[0]-16
        #y = self.option_list.txt_items[self.item_index].position[1]
        y = self.selector_y + (self.item_index * rtk.selector_list_line_space)
        self.item_selector.start_pos = (x,y)
        self.item_selector.set_position(position=(x,y))

    def __update_helper(self):
        self.helper.set_position(position=(rtk.help_x,self.help_y),is_tate=utils.is_tate())

    def __update_title(self):
        self.title.set_text(is_tate=utils.is_tate(),position=(rtk.selector_title_x,rtk.selector_title_y))

    def refresh_view(self):
        self.__set_positions()
        self.__update_title()
        self.__update_list()
        self.__update_helper()

    def __get_current_option(self):
        return self.options[self.item_index]
    
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
                    self.item_index = self.option_list.index
                    self.__update_sel_pos()
                elif event.key == 'D-Pad Down':
                    self.option_list.goto_next_item()
                    self.item_index = self.option_list.index
                    self.__update_sel_pos()
                elif event.key == cglobals.input_mgr.joy_action_1 or event.key == 'K_RETURN':
                    if self.__get_current_option() == 'mount_unit':
                        rtk.popup_msg.display(text='mounting_unit')
                        cglobals.is_in_task = True
                        cglobals.event_mgr.submit_event('mount_' + cglobals.tmp_value)
                    elif self.__get_current_option() == 'configure':
                        cglobals.vkeyb_view.set_view(title='nfs',text=eval('rtk.cfg_'+cglobals.tmp_value),info='server_share',mode='nfs')
                        utils.goto_view('vkeyb_view')
                elif event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE':
                    utils.goto_view('last_view')

    # Draw UI object animations
    def draw(self, time_step):
        self.option_list.anim_selector(time_step=time_step)