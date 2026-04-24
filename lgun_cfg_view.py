import rtk
import utils
import cglobals

class Lgun_Cfg_View(object):
    def __init__(self, is_active=False):
        self.gen_menu(is_active)

    def gen_menu(self, is_active, is_refresh=False):
        if is_refresh:
            for widget in self.container_view.widgets:
                try: self.container_view.remove(widget=widget,opid=rtk.get_random_id())
                except: pass
        # Init Vars
        self.STATE_START = 0
        self.STATE_TARGET = 1
        self.STATE_DONE = 3
        self.state = self.STATE_START
        self.target_i = 0
        self.targets = [(50, 50), (rtk.scr_w - 50, 50), (rtk.scr_w - 50, rtk.scr_h - 50), (50, rtk.scr_h - 50)]
        self.target_shots = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # Title
        self.title = rtk.RtkText(
            name      = 'lgun_cfg_title',
            text      = 'lgun_cfg_title',
            is_active = is_active,
            color     = rtk.orange,
            font      = 'title',
            is_upper  = True,
            is_tate   = utils.is_tate(),
            position  = ('center',rtk.lgun_title_y),
            colorkey  = rtk.color_key)
        # Info
        self.info = rtk.RtkText(
            name      = 'lgun_cfg_info',
            text      = 'lgun_cfg_info',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            color     = rtk.lgun_info_color,
            position  = ('center',rtk.lgun_info_y),
            colorkey  = rtk.color_key)
        self.info_2 = rtk.RtkText(
            name      = 'lgun_cfg_info_2',
            text      = 'lgun_cfg_info_2',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            color     = rtk.lgun_info_color,
            position  = ('center',rtk.lgun_info_y),
            colorkey  = rtk.color_key)
        # Warning
        self.warning = rtk.RtkText(
            name      = 'lgun_cfg_warn',
            text      = 'lgun_cfg_warn',
            is_active = is_active,
            font      = 'list',
            is_upper  = False,
            color     = rtk.lgun_warn_color,
            position  = ('center',rtk.lgun_warn_y),
            colorkey  = rtk.color_key)
        # Lgun images
        self.target = rtk.RtkImage(name='lgun_target', image='lgun_target.bmp', is_active=is_active, colorkey=rtk.color_key)
        self.bg = rtk.RtkRect(name='color_bg_lgun', color=rtk.blue, w=rtk.scr_w, h=rtk.scr_h, is_active=is_active)
        self.brightness = rtk.RtkImage(name='gun_brightness', image='gun_brightness.bmp', is_active=is_active, position=('center','center'), colorkey=rtk.color_key)
        # Add objects to containers
        if not is_refresh:
            self.container_view = rtk.ContainerMgr.create(name='lgun_cfg_view')
        rtk.ContainerMgr.append(parent=rtk.container_bg, child=self.container_view)
        rtk.ContainerMgr.append(parent=self.container_view, child=(
            self.bg,
            self.title,
            self.info,
            self.info_2,
            self.warning,
            self.target,
            self.brightness))

    def refresh_view(self):
        pass

    def activate(self):
        self.container_view.activate()
        self.state = self.STATE_START
        rtk.mouse.activate()
        self.target.deactivate()
        self.warning.deactivate()
        self.info_2.deactivate()

    def deactivate(self):
        self.container_view.deactivate()
        self.state = self.STATE_START
        rtk.mouse.deactivate()

    def exit(self):
        utils.goto_view('last_view')

    def update(self, event):
        if event.down:
            if not cglobals.stop_action:
                cglobals.stop_action = True
                if event.key == cglobals.input_mgr.joy_action_2 or event.key == 'K_BACKSPACE' or event.key == 'K_ESCAPE':
                    self.exit()
                if self.state == self.STATE_START:
                    if event.key == 'Trigger':
                        self.state = self.STATE_TARGET
                        self.target_i = 0
                        cglobals.input_mgr.lgun.load_default_calibration()
                        self.info.deactivate()
                        self.info_2.activate()
                        self.title.deactivate()
                        self.target.set_position(self.targets[self.target_i], use_center=True)
                        rtk.mouse.deactivate()
                        rtk.logging.info('Set target at: (%s, %s)',self.targets[self.target_i][0],self.targets[self.target_i][1])
                        self.target.activate()
                elif self.state == self.STATE_TARGET:
                    #if self.raw_x > 5 and event.key == 'Trigger':
                    if event.key == 'Trigger':
                        self.target_shots[self.target_i] = (self.raw_x, self.raw_y)
                        rtk.logging.info('Shoot at: (%s, %s)',self.raw_x, self.raw_y)
                        self.target_i += 1
                        if self.target_i == len(self.targets):
                            self.state = self.STATE_DONE
                        else:
                            self.target.set_position(self.targets[self.target_i], use_center=True)
                            rtk.logging.info('Set target at: (%s, %s)',self.targets[self.target_i][0],self.targets[self.target_i][1])
                elif self.state == self.STATE_DONE:
                    cglobals.input_mgr.lgun.calibrate(self.targets, self.target_shots)
                    self.state = self.STATE_START
                    self.exit()

    def draw(self, time_step):
        self.raw_x, self.raw_y = cglobals.input_mgr.lgun.pos
        if self.state != self.STATE_START:
            if self.raw_x < 5:
                self.warning.activate()
            elif self.raw_x > 5:
                self.warning.deactivate()