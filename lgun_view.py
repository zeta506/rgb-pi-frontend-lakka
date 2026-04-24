import rtk
import cglobals
from games_view import Games_View

class Lgun_View(Games_View):
    def gen_menu(self, system, is_active, is_refresh=False):
        self.lgun_p1_sys = ('mastersystem','psx','fbneo','dreamcast','naomi')
        self.lgun_p2_sys = ('nes','snes','megadrive','segacd')
        super().gen_menu(system, is_active, is_refresh)

    def __get_joy_name(self, joy_index):
        joystick = eval('cglobals.input_mgr.joy_' + str(joy_index))
        if joystick:
            return joystick['name'].lower()
        else:
            return '-'

    def launch_content(self):
        joy_0_name = self.__get_joy_name(joy_index=0)
        joy_1_name = self.__get_joy_name(joy_index=1)
        system = self.items[self.item_index]['Subsystem']
        rtk.logging.info('joy_0_name %s, joy_1_name %s, system %s', joy_0_name, joy_1_name, system)
        if system in self.lgun_p1_sys and joy_0_name != 'namco guncon 2':
            rtk.notif_msg.display(text='lgun_p1_error', l_icon='forbidden')
        elif system in self.lgun_p2_sys and joy_1_name != 'namco guncon 2':
            rtk.notif_msg.display(text='lgun_p2_error', l_icon='forbidden')
        else:
            cglobals.launcher['lgun_mode'] = True
            super().launch_content(system)