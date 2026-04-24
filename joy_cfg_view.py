from datetime import time
import rtk
import pygame
import cglobals
import time
import utils
import traceback

'''
apt install joystick
jstest /dev/input/js0
check device names:
for i in $(ls /dev/input/event*);do A=$(udevadm info -a --name $i|grep name);echo "$i --> $A"; done
check device types:
for i in $(ls /dev/input/event*);do A=$(udevadm info --query=all --name=$i|grep -e ID_INPUT_JOYSTICK -e ID_INPUT_KEYBOARD -e ID_INPUT_MOUSE);echo "$i --> $A"; done

for i in $(ls /dev/input/js*);do A=$(udevadm info -a --name $i|grep name);echo "$i --> $A"; done
for i in $(ls /dev/input/js*);do A=$(udevadm info --query=all --name=$i|grep -e ID_INPUT_JOYSTICK -e ID_INPUT_KEYBOARD -e ID_INPUT_MOUSE);echo "$i --> $A"; done


https://forums.libretro.com/t/joypad-fixed-order-at-startup-on-linux/26229
'''

class Joy_Cfg_View(object):
    def __init__(self,is_active=False):
        # Menu initialization
        self.gen_menu(is_active)

    def __set_positions(self):
        if utils.is_tate():
            self.map_info_y = rtk.map_info_y_tate
        else:
            self.map_info_y = rtk.map_info_y

    def gen_menu(self, is_active, is_refresh=False):
        self.__set_positions()
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        # System title
        self.title = rtk.RtkText(
            name      = 'joy_map_title',
            text      = 'joy_mapping',
            is_active = is_active,
            color     = rtk.map_title_color,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = (rtk.map_title_x,rtk.map_title_y),
            colorkey  = rtk.color_key)
        # Joy name
        self.joy_name_lbl = rtk.RtkText(
            name      = 'joy_map_name',
            text      = 'joy_name',
            is_active = is_active,
            color     = rtk.map_title_color,
            font      = 'list',
            is_upper  = False,
            position  = (rtk.map_joy_name_x,rtk.map_joy_name_y),
            colorkey  = rtk.color_key)
        # Press for label
        self.press_for = rtk.RtkText(
            name      = 'joy_map_press_for',
            text      = 'press_for',
            is_active = is_active,
            color     = rtk.map_title_color,
            font      = 'list',
            is_upper  = False,
            position  = (rtk.map_press_for_x,rtk.map_press_for_y),
            colorkey  = rtk.color_key)
        # System info
        self.item_info = rtk.RtkText(
            name      = 'joy_map_sys_item_inf',
            text      = 'skip_config_info',
            is_active = is_active,
            font      = 'info',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            color     = rtk.map_info_color,
            position  = ('center',self.map_info_y),
            colorkey  = rtk.color_key)
        # Helper
        self.gen_helper(is_active)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='joy_map_cfg_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.title,
            self.joy_name_lbl,
            self.press_for,
            self.item_info,
            self.joy_styles,
            self.joy_map,
            self.selector))

    def gen_helper(self, is_active):
        # Get images
        if cglobals.is_jamma:
            joy_names = 'joy_map_names_jamma.bmp'
            joy_map = 'joy_map_jamma.bmp'
            selector = 'joy_map_sel_jamma.bmp'
        else:
            joy_names = 'joy_map_names.bmp'
            joy_map = 'joy_map.bmp'
            selector = 'joy_map_sel.bmp'
        # Create image objects
        self.joy_styles = rtk.RtkSprite(
            name      = 'joy_map_joy_names',
            is_active = is_active,
            image     = joy_names,
            position  = (rtk.map_joy_styles_x,rtk.map_joy_styles_y),
            colorkey  = rtk.color_key)
        self.joy_map  = rtk.RtkBoxSprite(
            name      = 'joy_map_joy_mappings',
            is_active = is_active,
            image     = joy_map,
            box_size  = 134,
            position  = (rtk.map_joy_map_x,rtk.map_joy_map_y),
            colorkey  = rtk.color_key)
        self.selector = rtk.RtkSprite(
            name      = 'joy_map_selector',
            is_active = is_active,
            image     = selector,
            position  = (rtk.map_selector_x,rtk.map_selector_y),
            colorkey  = rtk.color_key)

    def refresh_view(self):
        pass

    def activate(self):
        self.container_view.activate()

    def deactivate(self):
        self.container_view.deactivate()

    def cancel_cfg(self):
        self.joy_config = self.joy_cfg_bck.copy()
        try: cglobals.input_mgr.joy_cfg_queue.remove(self.joy_index)
        except: pass # When cancelling joys that have already any config
        utils.goto_view('last_view')

    def config_joy(self, index):
        self.joy_index = index
        self.pressed_time = 0
        self.is_joy_configured = False
        self.is_btn_configured = False
        self.was_last_button_skipped = False
        self.were_all_btns_skipped = True
        self.btn_counter = 0
        self.joy_map.reset_box()
        self.max_time = 1
        self.threshold = 0.7
        # Presh & release management
        self.btn_index = None
        self.hat_index = None
        self.axis_index = None
        self.is_btn_pressed = False
        self.is_hat_pressed = False
        self.is_axis_pressed = False
        self.btn_current = None
        self.hat_current = None
        self.axis_current = None
        # Get joy object data
        joystick = eval('cglobals.input_mgr.joy_' + str(self.joy_index))
        joy_name = joystick['name']
        joy_vendor_id = joystick['vid']
        joy_product_id = joystick['pid']
        self.joy_id = joy_name + '_' + joy_vendor_id + '_' + joy_product_id
        self.joy_obj = joystick['object']
        self.joy_name_lbl.set_text(text=utils.prettify_joy_name(joy_name))
        rtk.logging.info('Preparing Joy %s (%s) for mapping', self.joy_index, self.joy_obj.get_name())
        # Get joy config
        self.joy_cfg_bck = cglobals.input_mgr.joy_configs.get(self.joy_id,{})
        self.joy_config = {}
        self.joy_config['name'] = joy_name
        self.joy_config['vid'] = joy_vendor_id
        self.joy_config['pid'] = joy_product_id
        # Wait until there is no joy activity before continuing
        has_activity = True
        while has_activity:
            pygame.event.pump()
            has_activity = False
            for btn_index in range(self.joy_obj.get_numbuttons()):
                button_status = self.joy_obj.get_button(btn_index)
                if button_status == 1: # 1 Pressed, 0 Released
                    has_activity = True
        # Identify triggers
        self.identify_triggers()
        utils.goto_view('joy_cfg_view')

    def identify_triggers(self):
        self.triggers = {}
        axes = self.joy_obj.get_numaxes()
        for axis in range(axes):
            status = self.joy_obj.get_axis(axis)
            rtk.logging.info('Axis [%s] status is %s', axis, status)
            if abs(status) > self.threshold:
                # Unless the player was holding the stick all the way when the game started
                # then this axis is an analog trigger
                self.triggers[axis] = True
                rtk.logging.info('Axis [%s] is trigger', axis)

    def do_mapping(self):
        try:
            btn_name = cglobals.input_mgr.buttons_layout[self.btn_counter]
            num_buttons = len(cglobals.input_mgr.buttons_layout)
            self.is_btn_configured = self.config_button(btn_name)
            if self.is_btn_configured == True:
                if not self.was_last_button_skipped:
                    self.were_all_btns_skipped = False
                if btn_name in ('L2/LT','R2/RT'):
                    self.identify_triggers() # Fix SDL1 wrong btn status before fst btn press
                self.btn_counter += 1
                self.joy_map.move_box(num_px=27)
            self.is_joy_configured = self.btn_counter == num_buttons
            if self.is_joy_configured:
                if self.were_all_btns_skipped:
                    self.cancel_cfg()
                else:
                    cglobals.input_mgr.joy_configs[self.joy_id] = self.joy_config
                    cglobals.input_mgr.set_joy_btn_style(self.joy_index, style='auto')
                    try:
                        is_queue = len(cglobals.input_mgr.joy_cfg_queue) > 1
                        cglobals.input_mgr.joy_cfg_queue.remove(self.joy_index)
                    except:
                        # When doing manual mapping there is no queue
                        is_queue = False
                    if not is_queue:
                        cglobals.input_mgr.load_joy_btn_style()
                        cglobals.sys_opt_control_view.refresh_values()
                        utils.gen_retroarch_autoconf()
                    utils.goto_view('last_view')
        except Exception as error:
            rtk.logging.error('Error in do_mapping: %s\n> %s\n', error, traceback.format_exc())
            self.cancel_cfg()

    def config_button(self, btn_name):
        is_configured = False
        now = time.time()

        ''' Check buttons for activity... '''

        if not self.is_btn_pressed:
            # Captures the pressed button and the time it was pressed
            for index in range(self.joy_obj.get_numbuttons()):
                button_status = self.joy_obj.get_button(index)
                if button_status == 1: # 1 Pressed, 0 Released
                    self.pressed_time = now
                    self.btn_index = index
                    self.is_btn_pressed = True
                    self.btn_current = btn_name
        elif self.is_btn_pressed:
            # Check if the button is pressed for more than 1 sec. If so, skip configuration
            if self.btn_index != None and self.joy_obj.get_button(self.btn_index) == 1 and (now - self.pressed_time >= self.max_time) and not self.was_last_button_skipped:
                is_skipped = ('is_skipped','')
                self.is_btn_pressed = False
                self.was_last_button_skipped = True
                self.joy_config[btn_name] = is_skipped
                is_configured = True
                rtk.logging.info('[%s] button skipped', btn_name)
                return is_configured
            elif self.joy_obj.get_button(self.btn_index) == 0: # If button released
                if not self.was_last_button_skipped:
                    rtk.logging.info('[%s] button released',btn_name)
                    if not is_configured and btn_name in ['D-Pad Up','D-Pad Down','D-Pad Left','D-Pad Right',
                        'Select','Start','Hotkey','A','B','X','Y','L1/LB','R1/RB','L2/LT','R2/RT']:
                        if self.allow_map_btn('is_button', self.btn_index):
                            if self.btn_current == btn_name:
                                if btn_name in ('L2/LT','R2/RT'):
                                    self.joy_config[btn_name + ' Btn'] = ('is_button', self.btn_index)
                                else:
                                    self.joy_config[btn_name] = ('is_button', self.btn_index)
                                is_configured = True
                                rtk.logging.info('[%s] (%s) button configured', btn_name, self.btn_index)
                self.is_btn_pressed = False
                self.was_last_button_skipped = False

        ''' Check hats for activity... '''

        # (hats are the basic direction pads)
        if not self.is_hat_pressed:
            for hat_index in range(self.joy_obj.get_numhats()):
                hat_status = self.joy_obj.get_hat(hat_index)
                x = abs(hat_status[0]) # -1=Left 0=Center 1=Right
                y = abs(hat_status[1]) # -1=Down 0=Center 1=Up
                if x or y:
                    self.hat_index = hat_index
                    self.hat_current = btn_name
                    self.is_hat_pressed = True
        elif self.is_hat_pressed:
            if not is_configured and btn_name in ['D-Pad Up','D-Pad Down','D-Pad Left','D-Pad Right']:
                hat_status = self.joy_obj.get_hat(self.hat_index)
                x = abs(hat_status[0]) # -1=Left 0=Center 1=Right
                y = abs(hat_status[1]) # -1=Down 0=Center 1=Up
                if not x and not y:
                    if self.hat_current == btn_name:
                        self.joy_config[btn_name] = ('is_hat', self.hat_index)
                        is_configured = True
                        rtk.logging.info('[%s] (%s) hat configured', btn_name, self.hat_index)
                    self.is_hat_pressed = False

        ''' Check axes for activity... '''
        
        if not self.is_axis_pressed:
            for axis_index in range(self.joy_obj.get_numaxes()):
                    is_pressed = False
                    is_analog = 'Analog' in btn_name
                    is_hat = 'D-Pad' in btn_name
                    if self.allow_map_btn('is_axis', axis_index) or is_hat:
                        axis_status = self.joy_obj.get_axis(axis_index)
                        if (is_analog or is_hat) and axis_index not in self.triggers:
                            axis_status = abs(axis_status)
                        axis_status = (axis_status + 1) / 2.0
                        if abs(axis_status) < self.threshold:
                            axis_status = 0
                        else:
                            axis_status = 1
                        if axis_status:
                            rtk.logging.info('[%s] (%s) (%s) axis pressed', btn_name, axis_index, axis_status)
                            is_pressed = True
                        if is_pressed:
                            self.axis_index = axis_index
                            self.axis_current = btn_name
                            self.is_axis_pressed = True
        elif self.is_axis_pressed:
            # For controllers that have both btn and axis in same phisical button like PS3
            if btn_name in ('L2/LT','R2/RT') and is_configured:
                is_configured = False
            if not is_configured and btn_name in ['D-Pad Up','D-Pad Down','D-Pad Left','D-Pad Right',
                        'Left Analog Up','Left Analog Left','Right Analog Up','Right Analog Left',
                        'L2/LT','R2/RT']:
                is_analog = 'Analog' in btn_name
                is_hat = 'D-Pad' in btn_name
                axis_status = self.joy_obj.get_axis(self.axis_index)
                if (is_analog or is_hat) and self.axis_index not in self.triggers:
                    axis_status = abs(axis_status)
                axis_status = (axis_status + 1) / 2.0
                if abs(axis_status) < self.threshold:
                    axis_status = 0
                else:
                    axis_status = 1
                if not axis_status:
                    if self.allow_map_btn('is_axis', self.axis_index) or is_hat:
                        if self.axis_current == btn_name:
                            if btn_name in ('L2/LT','R2/RT'):
                                self.joy_config[btn_name + ' Axis'] = ('is_axis', self.axis_index)
                            else:
                                self.joy_config[btn_name] = ('is_axis', self.axis_index)
                            is_configured = True
                            rtk.logging.info('[%s] (%s) (%s) axis configured', btn_name, self.axis_index, axis_status)
                    self.is_axis_pressed = False

        if is_configured:
            cglobals.sound_mgr.play_confirm()
        return is_configured

    def allow_map_btn(self, type, btn_index):
        allow_map = True
        for btn_name in cglobals.input_mgr.buttons_layout:
            config = self.joy_config.get(btn_name,self.joy_config.get(btn_name + ' Axis'))
            if config != None and config[0] == type and config[1] == btn_index:
                allow_map = False
        return allow_map

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == 'K_ESCAPE':
                    self.cancel_cfg()

    # Draw UI object animations
    def draw(self, time_step):
        self.selector.blink(speed=100,time_step=time_step)