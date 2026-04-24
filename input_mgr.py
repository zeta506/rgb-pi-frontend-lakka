import rtk
import cglobals
import os
import time
import configparser
import pygame
import pyudev
import utils
import evdev
from evdev import ecodes
from collections import namedtuple

Position = namedtuple('Position', ['x', 'y'])

# The individual event object that is returned.
# This serves as a proxy to pygame's event object and the key field is one of
# the strings in the button list listed below in the InputManager's constructor.
class Input_Event:
    def __init__(self, key, down):
        self.key = key
        self.down = down
        self.up = not down

class Input_Manager:
    def __init__(self):
        # Constants
        self.quit_attempt = False
        # Key Repeat engine
        self.key_repeat_start_time = 0.2
        self.key_repeat_speed = 0.08
        self.key_repeat_button = None
        self.key_repeat_last_repetition = 0
        self.key_repeat_pressed_time = 0
        self.key_repeat_last_kb_event = None
        self.key_repeat_last_kb_button = None
        self.key_repeat_device = None
        # Load joy and kb internal button layout
        self.__load_btn_layout()
        # Load joystick configuration from file
        self.__load_joy_config()

    def __load_btn_layout(self):
        # Set Joystick Layout
        self.buttons_layout = []
        if cglobals.is_jamma:
            self.buttons_layout = ['D-Pad Up','D-Pad Down','D-Pad Left','D-Pad Right',
                            'Select','Start','A','B','X','Y','L1/LB','R1/RB','Hotkey']
        else:
            self.buttons_layout = ['D-Pad Up','D-Pad Down','D-Pad Left','D-Pad Right',
                            'Select','Start','A','B','X','Y','L1/LB','R1/RB','L2/LT','R2/RT',
                            'Left Analog Up','Left Analog Left','Right Analog Up','Right Analog Left',
                            'Hotkey']
        # Set lightgun layout (raw input)
        self.lgun_buttons_layout = ['Trigger','PosX','PosY']
        self.lgun_x = 0
        self.lgun_y = 0
        # Set Keyboard Layout
        self.key_map = {
            pygame.K_UP:'D-Pad Up',     pygame.K_DOWN:'D-Pad Down',     pygame.K_LEFT:'D-Pad Left',     pygame.K_RIGHT:'D-Pad Right',
            pygame.K_x:'K_X',           pygame.K_y:'K_Y',               pygame.K_MINUS:'K_-',           pygame.K_PLUS:'K_+',
            pygame.K_RETURN:'K_RETURN', pygame.K_ESCAPE:'K_ESCAPE',     pygame.K_F1:'K_F1',             pygame.K_PRINT:'K_PRINT',
            pygame.K_PAGEUP:'K_PAGEUP', pygame.K_PAGEDOWN:'K_PAGEDOWN', pygame.K_BACKSPACE:'K_BACKSPACE'
        }
        # This dictionary will tell you which logical buttons are pressed, whether it's via the keyboard or joystick 
        self.btn_status = {}
        for btn_name in self.buttons_layout:
            self.btn_status[btn_name] = False
        for btn_name in self.lgun_buttons_layout:
            self.btn_status[btn_name] = False
    
    def __load_joy_config(self):
        self.joy_configs = {}
        invalid_map = ('None','')
        with os.scandir(rtk.path_autoconfig) as cfg_files:
            try:
                for cfg_file in cfg_files:
                    joy_config = {}
                    with open(os.path.join(rtk.path_autoconfig, cfg_file.name), 'r') as file:
                        config_string = '[autoconfig]\n' + file.read()
                        config = configparser.ConfigParser(strict=False)
                        config.read_string(config_string)
                        mapping = config['autoconfig']
                        # Info
                        input_device = mapping.get('input_device','Unknown Joystick').replace('"','')
                        input_vendor_id = mapping.get('input_vendor_id','0000').replace('"','')
                        input_product_id = mapping.get('input_product_id','0000').replace('"','')
                        input_btn_style = mapping.get('input_btn_style','None').replace('"','')
                        # Mappings
                        input_up_btn = mapping.get('input_up_btn','None').replace('"','')
                        input_down_btn = mapping.get('input_down_btn','None').replace('"','')
                        input_left_btn = mapping.get('input_left_btn','None').replace('"','')
                        input_right_btn = mapping.get('input_right_btn','None').replace('"','')
                        input_up_axis = mapping.get('input_up_axis','None').replace('"','')
                        input_down_axis = mapping.get('input_down_axis','None').replace('"','')
                        input_left_axis = mapping.get('input_left_axis','None').replace('"','')
                        input_right_axis = mapping.get('input_right_axis','None').replace('"','')
                        if input_device == 'Namco GunCon 2':
                            input_a_btn = mapping.get('ui_input_a_btn','None').replace('"','')
                            input_b_btn = mapping.get('ui_input_b_btn','None').replace('"','')
                            input_start_btn = mapping.get('ui_input_start_btn','None').replace('"','')
                            input_select_btn = mapping.get('ui_input_select_btn','None').replace('"','')
                            input_x_btn = 'None'
                            input_y_btn = 'None'
                            input_l_btn = 'None'
                            input_r_btn = 'None'
                            input_menu_toggle_btn = 'None'
                        else:
                            input_a_btn = mapping.get('input_a_btn','None').replace('"','')
                            input_b_btn = mapping.get('input_b_btn','None').replace('"','')
                            input_start_btn = mapping.get('input_start_btn','None').replace('"','')
                            input_x_btn = mapping.get('input_x_btn','None').replace('"','')
                            input_y_btn = mapping.get('input_y_btn','None').replace('"','')
                            input_select_btn = mapping.get('input_select_btn','None').replace('"','')
                            input_l_btn = mapping.get('input_l_btn','None').replace('"','')
                            input_r_btn = mapping.get('input_r_btn','None').replace('"','')
                            input_l2_btn = mapping.get('input_l2_btn','None').replace('"','')
                            input_r2_btn = mapping.get('input_r2_btn','None').replace('"','')
                            input_l2_axis = mapping.get('input_l2_axis','None').replace('"','')
                            input_r2_axis = mapping.get('input_r2_axis','None').replace('"','')
                            input_l_x_minus_axis = mapping.get('input_l_x_minus_axis','None').replace('"','')
                            input_l_y_minus_axis = mapping.get('input_l_y_minus_axis','None').replace('"','')
                            input_r_x_minus_axis = mapping.get('input_r_x_minus_axis','None').replace('"','')
                            input_r_y_minus_axis = mapping.get('input_r_y_minus_axis','None').replace('"','')
                            input_menu_toggle_btn = mapping.get('input_menu_toggle_btn','None').replace('"','')
                        # Parse config
                        joy_config['name'] = input_device
                        joy_config['vid'] = input_vendor_id
                        joy_config['pid'] = input_product_id
                        joy_id = input_device + '_' + input_vendor_id + '_' + input_product_id
                        if input_btn_style in cglobals.button_styles: joy_config['style'] = input_btn_style
                        else: joy_config['style'] = 'snes'
                        if input_device == "TOMMO NEOGEOX Arcade Stick" or input_device == "EXAR USB JOYSTICK PS3":
                            joy_config['D-Pad Up'] = ('is_axis', 1)
                            joy_config['D-Pad Down'] = ('is_axis', 1)
                            joy_config['D-Pad Left'] = ('is_axis', 0)
                            joy_config['D-Pad Right'] = ('is_axis', 0)
                        else:
                            if input_up_btn not in invalid_map:
                                if input_up_btn == 'h0up': # is hat (h0up --> 0 is the hat number)
                                    joy_config['D-Pad Up'] = ('is_hat', int(input_up_btn[1]))
                                else:
                                    joy_config['D-Pad Up'] = ('is_button', int(input_up_btn))
                            if input_down_btn not in invalid_map:
                                if input_down_btn == 'h0down':
                                    joy_config['D-Pad Down'] = ('is_hat', int(input_down_btn[1]))
                                else:
                                    joy_config['D-Pad Down'] = ('is_button', int(input_down_btn))
                            if input_left_btn not in invalid_map:
                                if input_left_btn == 'h0left':
                                    joy_config['D-Pad Left'] = ('is_hat', int(input_left_btn[1]))
                                else:
                                    joy_config['D-Pad Left'] = ('is_button', int(input_left_btn))
                            if input_right_btn not in invalid_map:
                                if input_right_btn == 'h0right':
                                    joy_config['D-Pad Right'] = ('is_hat', int(input_right_btn[1]))
                                else:
                                    joy_config['D-Pad Right'] = ('is_button', int(input_right_btn))
                            if input_up_axis not in invalid_map: joy_config['D-Pad Up'] = ('is_axis', abs(int(input_up_axis)))
                            if input_down_axis not in invalid_map: joy_config['D-Pad Down'] = ('is_axis', abs(int(input_down_axis)))
                            if input_left_axis not in invalid_map: joy_config['D-Pad Left'] = ('is_axis', abs(int(input_left_axis)))
                            if input_right_axis not in invalid_map: joy_config['D-Pad Right'] = ('is_axis', abs(int(input_right_axis)))
                        if input_select_btn not in invalid_map: joy_config['Select'] = ('is_button', int(input_select_btn))
                        if input_start_btn not in invalid_map: joy_config['Start'] = ('is_button', int(input_start_btn))
                        if input_a_btn not in invalid_map: joy_config['A'] = ('is_button', int(input_a_btn))
                        if input_b_btn not in invalid_map: joy_config['B'] = ('is_button', int(input_b_btn))
                        if input_x_btn not in invalid_map: joy_config['X'] = ('is_button', int(input_x_btn))
                        if input_y_btn not in invalid_map: joy_config['Y'] = ('is_button', int(input_y_btn))
                        if input_l_btn not in invalid_map: joy_config['L1/LB'] = ('is_button', int(input_l_btn))
                        if input_r_btn not in invalid_map: joy_config['R1/RB'] = ('is_button', int(input_r_btn))
                        if input_l2_btn not in invalid_map: joy_config['L2/LT Btn'] = ('is_button', int(input_l2_btn))
                        if input_r2_btn not in invalid_map: joy_config['R2/RT Btn'] = ('is_button', int(input_r2_btn))
                        if input_l2_axis not in invalid_map: joy_config['L2/LT Axis'] = ('is_axis', int(input_l2_axis))
                        if input_r2_axis not in invalid_map: joy_config['R2/RT Axis'] = ('is_axis', int(input_r2_axis))
                        try:
                            if input_l_y_minus_axis not in invalid_map: joy_config['Left Analog Up'] = ('is_axis', abs(int(input_l_y_minus_axis)))
                            if input_l_x_minus_axis not in invalid_map: joy_config['Left Analog Left'] = ('is_axis', abs(int(input_l_x_minus_axis)))
                            if input_r_y_minus_axis not in invalid_map: joy_config['Right Analog Up'] = ('is_axis', abs(int(input_r_y_minus_axis)))
                            if input_r_x_minus_axis not in invalid_map: joy_config['Right Analog Left'] = ('is_axis', abs(int(input_r_x_minus_axis)))
                        except:
                            pass # Very weird mappings like G27_Racing_Wheel.cfg
                        if input_menu_toggle_btn not in invalid_map:
                            joy_config['Hotkey'] = ('is_button', int(input_menu_toggle_btn))
                        # Add joy config to dictionary
                        self.joy_configs[joy_id] = joy_config
            except Exception as error:
                rtk.logging.error('Failed to read joy config: %s', error)

    def __key_repeat(self, events, btn_name, pushed, device):
        current_view = utils.get_view_name()
        if current_view != 'joy_cfg_view':
            # Manage Key Repeat
            now = time.time()
            if pushed == pygame.KEYDOWN:
                pushed = 1
            elif pushed == pygame.KEYUP:
                pushed = 0
            if pushed:
                if btn_name == 'D-Pad Up' or btn_name == 'D-Pad Down' or btn_name == 'D-Pad Right' or btn_name == 'D-Pad Left' or \
                    btn_name == cglobals.input_mgr.joy_special_1 or btn_name == 'K_PAGEUP' or \
                    btn_name == cglobals.input_mgr.joy_special_2 or btn_name == 'K_PAGEDOWN':
                    self.key_repeat_button = btn_name
                    if self.key_repeat_pressed_time == 0:
                        self.key_repeat_pressed_time = now
                        self.key_repeat_device = device
            else:
                if btn_name == self.key_repeat_button and not pushed and device == self.key_repeat_device:
                    self.key_repeat_button = None
                    self.key_repeat_last_repetition = 0
                    self.key_repeat_pressed_time = 0
                    self.key_repeat_last_kb_event = None
                    self.key_repeat_last_kb_button = None
                    self.key_repeat_device = None
            if self.key_repeat_button != None:
                elapsed_time = now - self.key_repeat_pressed_time
                if elapsed_time >= self.key_repeat_start_time:
                    if self.key_repeat_last_repetition == 0:
                        self.key_repeat_last_repetition = now
                    if now - self.key_repeat_last_repetition >= self.key_repeat_speed:
                        self.key_repeat_last_repetition = now
                        btn_name = self.key_repeat_button
                        pushed = 1
                        events.append(Input_Event(btn_name, pushed))

    def __set_joy_btn_style_mapping(self):
        self.joy_start = 'Start'
        self.joy_action_1 = 'A'
        self.joy_action_2 = 'B'
        self.joy_action_3 = 'X'
        self.joy_action_4 = 'Y'
        self.joy_special_1 = 'L1/LB' # L
        self.joy_special_2 = 'R1/RB' # R

    def __get_udev_joy_info(self):
        '''
        TEST
        ====
        $ python3
        >>> import pyudev
        >>> context = pyudev.Context()
        >>> joy0 = pyudev.Devices.from_name(context, 'input', 'js0')
        >>> joy1 = pyudev.Devices.from_name(context, 'input', 'js1')
        >>> print(joy0.get('ID_PATH'))
        >>> print(joy1.get('ID_PATH'))
        '''
        joysticks = []
        # Get udev joysticks information
        try:
            devices = pyudev.Context().list_devices(subsystem='input')
        except Exception:
            devices = []
        for device in devices:
            joystick = {}
            is_joystick = '/dev/input/js' in device.get('DEVNAME','None')
            if is_joystick:
                joystick['name'] = device.parent.get('NAME','').replace('"','')
                joystick['dev_name'] = device.get('DEVNAME','')
                joystick['product_id'] = device.get('ID_MODEL_ID','1234')
                joystick['vendor_id'] = device.get('ID_VENDOR_ID','1234')
                joystick['path_id'] = device.get('ID_PATH','')
                if joystick['path_id'] == 'platform-soc': # Workaround to force BT sorting first or last
                    joystick['path_id'] = 'bt-platform-soc'
                joysticks.append(joystick)
        if not joysticks:
            # Lakka fallback: pyudev stub returned nothing, use sysfs to read
            # real VID/PID + pygame.joystick for SDL index. Lets joy_cfg match
            # specific controller maps.
            import glob, os as _os
            pygame.joystick.quit()
            pygame.joystick.init()
            for i in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                try:
                    joy.init()
                    name = joy.get_name()
                except Exception:
                    name = 'Controller %s' % i
                # init_joysticks calls int(vendor_id, 16) and int(product_id, 16),
                # so leave raw hex strings here ('0079', '0126', ...)
                vid = '1234'
                pid = '1234'
                try:
                    # Walk up sysfs until idVendor appears (skips usb interface)
                    js_path = _os.path.realpath('/sys/class/input/js%s' % i)
                    cur = js_path
                    for _ in range(8):
                        if _os.path.isfile(cur + '/idVendor') and _os.path.isfile(cur + '/idProduct'):
                            with open(cur + '/idVendor') as _f:
                                vid = _f.read().strip()
                            with open(cur + '/idProduct') as _f:
                                pid = _f.read().strip()
                            break
                        cur = _os.path.dirname(cur)
                except Exception:
                    for usb in glob.glob('/sys/bus/usb/devices/*/idVendor'):
                        try:
                            with open(usb) as _f:
                                vid = _f.read().strip()
                            with open(_os.path.dirname(usb)+'/idProduct') as _f:
                                pid = _f.read().strip()
                            break
                        except Exception:
                            pass
                joysticks.append({
                    'name': name,
                    'dev_name': '/dev/input/js%s' % i,
                    'product_id': pid,
                    'vendor_id': vid,
                    'path_id': 'pygame',
                    'index': i,
                })
        # Removed sorting used in Retroarch > 1.9.8. Now it uses Linux bus standard ordering (BT at the end and Pi4 USB port numbering)
        joys_sorted_by_name = sorted(joysticks, key=lambda joystick:(joystick['dev_name'], joystick['path_id']), reverse=False)
        for i, joy in enumerate(joys_sorted_by_name):
            joy['index'] = i
        return joysticks

    def init_lgun(self):
        try:
            # Find the first guncon2
            lgun = None
            for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
                if device.name == 'Namco GunCon 2':
                    lgun = device
                    break
            if lgun is None:
                self.lgun = None
                rtk.logging.info('Failed to find any attached GunCon2 devices')
            else:
                with lgun.grab_context():
                    self.lgun = Guncon2(lgun)
        except Exception as error:
            self.lgun = None
            rtk.logging.error('Failed to init gun: %s', error)

    def init_joysticks(self):
        self.joy_0 = {}
        self.joy_1 = {}
        self.joy_2 = {}
        self.joy_3 = {}
        self.joy_4 = {}
        self.joy_5 = {}
        self.joy_6 = {}
        self.joy_7 = {}
        self.joy_cfg_queue = []
        self.joy_id_queue = []
        self.num_lguns = 0
        pygame.joystick.quit()
        pygame.joystick.init()
        cglobals.num_joysticks = pygame.joystick.get_count()
        # Get udev joysticks information
        joy_info = self.__get_udev_joy_info()
        # Get joy objects
        i = 0
        for joy in joy_info:
            joy_name = joy['name']
            joy_index = int(joy['index'])
            joy_vendor_id = str(int(joy['vendor_id'],16))
            joy_product_id = str(int(joy['product_id'],16))
            joy_id = joy_name + '_' + joy_vendor_id + '_' + joy_product_id
            joy_obj = pygame.joystick.Joystick(joy_index)
            joy_obj.init()
            if joy_name == 'Namco GunCon 2':
                self.num_lguns += 1
            rtk.logging.info('Init Joy %s:', i)
            rtk.logging.info('Joy Udev Name: %s, Index: %s, Vendor: %s, Product: %s, Path Id: %s', joy_name, joy_index, joy_vendor_id, joy_product_id, joy['path_id'])
            rtk.logging.info('Joy SDL Name: %s', joy_obj.get_name())
            # Create joy dictionary
            eval('self.joy_' + str(i))['name'] = joy_name
            eval('self.joy_' + str(i))['vid'] = joy_vendor_id
            eval('self.joy_' + str(i))['pid'] = joy_product_id
            eval('self.joy_' + str(i))['object'] = joy_obj
            # Check joys that need mapping configuration
            if not self.get_joy_config(joy_index=i):
                if joy_id not in self.joy_id_queue: # this avoid configuring twice usb adapters with 2 players
                    self.joy_id_queue.append(joy_id)
                    self.joy_cfg_queue.append(i)
            i += 1
        rtk.logging.info('Num LGuns: %s', self.num_lguns)
        # Set joy style and UI helpers 
        self.load_joy_btn_style()
        # Check if controller has Select button
        cglobals.has_select = False
        try:
            if self.joy_0:
                if self.get_joy_config(joy_index=0).get('Select','None') != 'None':
                    cglobals.has_select = True
        except Exception as error:
            rtk.logging.error('Failed to get Select button: %s', error)
    # This will pump the pygame events. If this is not called every frame, then pygame will start to lock up
    # This is basically a proxy method for pygame's event pump and will likewise return a list of event proxies
    def get_events(self):
        events = []
        threshold = 0.7
        # Get custom events
        joy_id = self.get_joy_id(joy_index=0)
        if joy_id:
            joy_obj = self.joy_0['object']
            # And this is where each configured button is checked... 
            for btn_name in self.buttons_layout:
                try:
                    # Determine what something like "Y" actually means in terms of the joystick
                    if joy_id in self.joy_configs:
                        joy_btn = self.joy_configs[joy_id].get(btn_name, None)
                        if joy_btn:
                            if joy_btn[0] == 'is_button':
                                rtk.logging.debug('Joy Btn: %s --> %s', btn_name, joy_btn)
                                is_pushed = joy_obj.get_button(joy_btn[1])
                                if is_pushed != self.btn_status[btn_name]:
                                    events.append(Input_Event(btn_name, is_pushed))
                                    self.btn_status[btn_name] = is_pushed
                            elif joy_btn[0] == 'is_hat':
                                status = joy_obj.get_hat(joy_btn[1])
                                x = status[0] # -1=Left 0=Center 1=Right
                                y = status[1] # -1=Down 0=Center 1=Up
                                if 'Up' in btn_name: is_pushed = y == 1
                                elif 'Down' in btn_name: is_pushed = y == -1
                                elif 'Left' in btn_name: is_pushed = x == -1
                                elif 'Right' in btn_name: is_pushed = x == 1
                                if is_pushed != self.btn_status[btn_name]:
                                    events.append(Input_Event(btn_name, is_pushed))
                                    self.btn_status[btn_name] = is_pushed
                            elif joy_btn[0] == 'is_axis':
                                status = joy_obj.get_axis(joy_btn[1])
                                if 'Up' in btn_name: is_pushed = status < -threshold
                                elif 'Down' in btn_name: is_pushed = status > threshold
                                elif 'Left' in btn_name: is_pushed = status < -threshold
                                elif 'Right' in btn_name: is_pushed = status > threshold
                                if is_pushed != self.btn_status[btn_name]:
                                    events.append(Input_Event(btn_name, is_pushed))
                                    self.btn_status[btn_name] = is_pushed
                            # Manage Joystick Key Repeat
                            self.__key_repeat(events=events, btn_name=btn_name, pushed=is_pushed, device='joy')
                except Exception as error:
                    pass
                    #rtk.logging.error('get_events error: %s (%s) --> Button: %s', error, joy_obj.get_name(), btn_name)
        # Get lgun events
        if self.lgun:
            try:
                if utils.get_view_name() == 'lgun_cfg_view':
                    move_aim = False
                    cx, cy = self.lgun.pos_normalised.x, self.lgun.pos_normalised.y
                    trigger = False
                    for button, value in self.lgun.update():
                        if button == ecodes.BTN_LEFT and value == 1:
                            trigger = True
                    for btn_name in self.lgun_buttons_layout:
                        if rtk.scr_w > cx >= 0 and rtk.scr_h > cy >= 0:  # on screen
                            if btn_name == 'Trigger':
                                is_pushed = trigger
                                if is_pushed != self.btn_status[btn_name]:
                                    events.append(Input_Event(btn_name, is_pushed))
                                    self.btn_status[btn_name] = is_pushed
                            elif btn_name == 'PosX' and cx != self.lgun_x:
                                move_aim = True
                                self.lgun_x = cx
                                events.append(Input_Event(btn_name, self.lgun_x))
                            elif btn_name == 'PosY' and cy != self.lgun_y:
                                move_aim = True
                                self.lgun_y = cy
                                events.append(Input_Event(btn_name, self.lgun_y))
                    if move_aim and rtk.mouse.is_active:
                        rtk.mouse.set_position((cx,cy))
            except:
                pass # Disconected
        # Get pygame events
        for event in pygame.event.get():
            # Check Quit event
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_F4):
                if rtk.cfg_adv_mode in ('god','suser'):
                    self.quit_attempt = True
            # This is where the keyboard events are checked 
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                key_pushed_down = event.type == pygame.KEYDOWN
                btn_name = self.key_map.get(event.key)
                if btn_name != None:
                    events.append(Input_Event(btn_name, key_pushed_down))
                    self.btn_status[btn_name] = key_pushed_down
                    # Manage Keyboard Key Repeat
                    self.key_repeat_last_kb_button = btn_name
                    self.key_repeat_last_kb_event = event.type
        self.__key_repeat(events=events, btn_name=self.key_repeat_last_kb_button, pushed=self.key_repeat_last_kb_event, device='kb')
        # Allow multiple keypress per loop itereation
        return events
    
    def get_event(self):
        # Use this method instead of get_events to restrict multiple keypress to just one per loop itereation
        events = self.get_events()
        if events:
            return events[0]
        else:
            return None

    def get_joy_config(self, joy_index):
        joy_id = self.get_joy_id(joy_index)
        if joy_id:
            return self.joy_configs.get(joy_id, None)
        else:
            return None

    def get_joy_id(self, joy_index):
        joystick = eval('self.joy_' + str(joy_index))
        if joystick:
            joy_name = eval('self.joy_' + str(joy_index))['name']
            joy_vid = eval('self.joy_' + str(joy_index))['vid']
            joy_pid = eval('self.joy_' + str(joy_index))['pid']
            joy_id = joy_name + '_' + joy_vid + '_' + joy_pid
            return joy_id
        else:
            return None

    def set_joy_btn_style(self, joy_index, style):
        joy_cfg = self.get_joy_config(joy_index)
        # Set style
        if joy_cfg:
            if style == 'auto':
                joy_name = eval('self.joy_' + str(joy_index))['name']
                if 'RGB-Pi' in joy_name or 'JoyPi' in joy_name:
                    has_extra_buttons = joy_cfg['L1/LB'][0] != 'is_skipped'
                    if has_extra_buttons:
                        joy_cfg['style'] = 'jamma6'
                    else:
                        joy_cfg['style'] = 'jamma3'
                else:
                    joy_cfg['style'] = 'snes'
            else:
                joy_cfg['style'] = style

    def load_joy_btn_style(self):
        joy_cfg = self.get_joy_config(0)
        # Set style
        if joy_cfg:
            # Refresh joy style at config level
            rtk.cfg_button_style = joy_cfg['style']
            # Refresh joy style logic and helpers
            self.__set_joy_btn_style_mapping()
            try: cglobals.event_mgr.submit_event('refresh_helpers')
            except: pass
        else:
            self.__set_joy_btn_style_mapping()

# Lgun

class Guncon2(object):
    def __init__(self, device):
        self.device = device
        self.pos = Position(0, 0)
        try:
            self.default_min_x = 150
            self.default_min_y = 5
            self.default_max_x = 712
            self.default_max_y = 245
            rtk.logging.info('System -> Min X %s, Min Y %s, Max X %s, Max Y %s', self.min_x, self.min_y, self.max_x, self.max_y)
            rtk.logging.info('User   -> Min X %s, Min Y %s, Max X %s, Max Y %s', rtk.cfg_lgun_min_x, rtk.cfg_lgun_min_y, rtk.cfg_lgun_max_x, rtk.cfg_lgun_max_y)
            self.load_calibration()
        except Exception as error:
            rtk.logging.error('LGun init error: %s', error)
    @property
    def absinfo(self):
        return [self.device.absinfo(ecodes.ABS_X), self.device.absinfo(ecodes.ABS_Y)]

    @property
    def min_x(self):
        return self.device.absinfo(ecodes.ABS_X).min

    @property
    def max_x(self):
        return self.device.absinfo(ecodes.ABS_X).max

    @property
    def min_y(self):
        return self.device.absinfo(ecodes.ABS_Y).min

    @property
    def max_y(self):
        return self.device.absinfo(ecodes.ABS_Y).max

    @property
    def pos_normalised(self):
        return Position(
                int(self.normalise(self.pos.x, self.min_x, self.max_x) * rtk.scr_w),
                int(self.normalise(self.pos.y, self.min_y, self.max_y) * rtk.scr_h))

    @staticmethod
    def normalise(pos, min_, max_):
        return (pos - min_) / float(max_ - min_)

    def update(self):
        while True:
            ev = self.device.read_one()
            if ev:
                if ev.type == ecodes.EV_ABS:
                    if ev.code == ecodes.ABS_X:
                        self.pos = Position(ev.value, self.pos.y)
                    elif ev.code == ecodes.ABS_Y:
                        self.pos = Position(self.pos.x, ev.value)
                if ev.type == ecodes.EV_KEY:
                    yield ev.code, ev.value
            else:
                break

    def calibrate(self, targets, shots, width=rtk.scr_w, height=rtk.scr_h):
        targets_x = [target[0] for target in targets]
        targets_y = [target[1] for target in targets]
        shots_x = [shot[0] for shot in shots]
        shots_y = [shot[1] for shot in shots]
        rtk.logging.info('Targets X %s, Targets Y %s, Shoots X %s, Shoots Y %s', targets_x, targets_y, shots_x, shots_y)
        # calculate the ratio between on-screen units and gun units for each axes
        try:
            gsratio_x = (max(targets_x) - min(targets_x)) / (max(shots_x) - min(shots_x))
        except ZeroDivisionError:
            rtk.logging.error('Failed to calibrate X axis')
            return
        try:
            gsratio_y = (max(targets_y) - min(targets_y)) / (max(shots_y) - min(shots_y))
        except ZeroDivisionError:
            rtk.logging.error('Failed to calibrate X axis')
            return
        min_x = min(shots_x) - (min(targets_x) * gsratio_x)
        max_x = max(shots_x) + ((width - max(targets_x)) * gsratio_x)
        min_x -= 50
        max_x += 50
        min_y = (min(shots_y) - (min(targets_y) * gsratio_y))
        max_y = (max(shots_y) + ((height - max(targets_y)) * gsratio_y))
        # set the X and Y calibration values
        self.device.set_absinfo(ecodes.ABS_X, min=int(min_x), max=int(max_x))
        self.device.set_absinfo(ecodes.ABS_Y, min=int(min_y), max=int(max_y))
        # Save config
        rtk.cfg_lgun_min_x = int(min_x)
        rtk.cfg_lgun_min_y = int(min_y)
        rtk.cfg_lgun_max_x = int(max_x)
        rtk.cfg_lgun_max_y = int(max_y)
        cglobals.event_mgr.submit_event('save_config')
        rtk.logging.info('Saved Calibration: x=(%s) y=(%s)',self.absinfo[0],self.absinfo[1])

    def load_calibration(self):
        # set the X and Y calibration values
        self.device.set_absinfo(ecodes.ABS_X, min=int(rtk.cfg_lgun_min_x), max=int(rtk.cfg_lgun_max_x))
        self.device.set_absinfo(ecodes.ABS_Y, min=int(rtk.cfg_lgun_min_y), max=int(rtk.cfg_lgun_max_y))
        rtk.logging.info('Loaded Calibration: x=(%s) y=(%s)',self.absinfo[0],self.absinfo[1])

    def load_default_calibration(self):
        # set the X and Y calibration values
        self.device.set_absinfo(ecodes.ABS_X, min=self.default_min_x, max=self.default_max_x)
        self.device.set_absinfo(ecodes.ABS_Y, min=self.default_min_y, max=self.default_max_y)
        rtk.logging.info('Loaded Default Calibration: x=(%s) y=(%s)',self.absinfo[0],self.absinfo[1])
