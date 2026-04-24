import os
import pygame
import rtk
import utils
import cglobals
import alsaaudio
import math

class Sound_Manager(object):
    def __init__(self):
        self.init_mixer()
        self.playlist_index = 0
        self.status = 'Stopped'
        self.volumes = ('0','10','20','30','40','50','60','70','80','90','100')
        self.alsa_freqs = ('00. 31 Hz','01. 63 Hz','02. 125 Hz','03. 250 Hz','04. 500 Hz','05. 1 kHz','06. 2 kHz','07. 4 kHz','08. 8 kHz','09. 16 kHz')
        self.eq_freqs = ('31hz','63hz','125hz','250hz','500hz','1khz','2khz','4khz','8khz','16khz')
        self.load_sound_fx()
        self.set_playlist()
        self.set_bg_music_volume()
        self.set_menu_sounds_volume()

    def load_sound_fx(self):
        if cglobals.has_audio:
            try:
                fx_path = rtk.path_rgbpi_themes + '/' + rtk.cfg_theme + '/sounds/fx'
                self.fx_text_advance = pygame.mixer.Sound(fx_path + '/text_advance.ogg')
                self.fx_menu_confirm = pygame.mixer.Sound(fx_path + '/menu_confirm.ogg')
                self.fx_menu_open = pygame.mixer.Sound(fx_path + '/menu_open.ogg')
                self.fx_menu_deny = pygame.mixer.Sound(fx_path + '/menu_deny.ogg')
                self.fx_system_error = pygame.mixer.Sound(fx_path + '/system_error.ogg')
                self.fx_screenshot = pygame.mixer.Sound(fx_path + '/screenshot.ogg')
                self.fx_shoot = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/shoot.ogg')
            except:
                self.fx_text_advance = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/text_advance.ogg')
                self.fx_menu_confirm = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/menu_confirm.ogg')
                self.fx_menu_open = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/menu_open.ogg')
                self.fx_menu_deny = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/menu_deny.ogg')
                self.fx_system_error = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/system_error.ogg')
                self.fx_screenshot = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/screenshot.ogg')
                self.fx_shoot = pygame.mixer.Sound(rtk.path_rgbpi_sfx + '/shoot.ogg')

    def init_mixer(self):
        # Lakka-port: pygame.mixer first (must succeed) then alsaaudio mixers
        # are best-effort. Card 1 = first USB audio device on Lakka with nohdmi.
        self.mixer_range = [0, 100]
        self.dynamic_range = 50
        # Pi5 Lakka: bind ALSA to card 1 (USB DAC) explicitly via SDL env.
        os.environ.setdefault('SDL_AUDIODRIVER', 'alsa')
        os.environ.setdefault('AUDIODEV', 'hw:1,0')
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            rtk.logging.info('pygame.mixer init: %s', pygame.mixer.get_init())
        except Exception as e:
            rtk.logging.error('pygame.mixer init failed: %s', e)
            cglobals.has_audio = False
            return
        # alsaaudio Mixers are nice-to-have; on Lakka many of these controls
        # don't exist (no Headphone/equal cards). Stay silent if missing so
        # the FE doesn't disable audio entirely.
        try:
            utils.cmd('amixer -c 1 sset Speaker 100% unmute >/dev/null 2>&1')
        except Exception:
            pass
        for attr, ctrl, kwargs in (
            ('headphone_mixer', 'Speaker', {'cardindex': 1}),
            ('eq_mixer_0', '00. 31 Hz', {'device': 'equal'}),
            ('eq_mixer_1', '01. 63 Hz', {'device': 'equal'}),
            ('eq_mixer_2', '02. 125 Hz', {'device': 'equal'}),
            ('eq_mixer_3', '03. 250 Hz', {'device': 'equal'}),
            ('eq_mixer_4', '04. 500 Hz', {'device': 'equal'}),
            ('eq_mixer_5', '05. 1 kHz', {'device': 'equal'}),
            ('eq_mixer_6', '06. 2 kHz', {'device': 'equal'}),
            ('eq_mixer_7', '07. 4 kHz', {'device': 'equal'}),
            ('eq_mixer_8', '08. 8 kHz', {'device': 'equal'}),
            ('eq_mixer_9', '09. 16 kHz', {'device': 'equal'}),
        ):
            try:
                setattr(self, attr, alsaaudio.Mixer(control=ctrl, **kwargs))
            except Exception:
                setattr(self, attr, None)
        try:
            self.set_volume(percent=rtk.cfg_system_vol, mixer='headphone', control=0)
        except Exception:
            pass

    def set_playlist(self):
        self.playlist = utils.get_songs(name=rtk.cfg_playlist)

    def set_preset(self, preset=None):
        if cglobals.has_audio:
            # Get preset values from dictionary
            if preset:
                preset_values = cglobals.presets[preset]
            else:
                preset_values = cglobals.presets[rtk.cfg_preset]
            # Set preset values
            for index in range (0,10):
                rtk.__dict__['cfg_'+self.eq_freqs[index]] = preset_values[index]
            # Apply preset to system ALSA
            # Frequencies
            for index in range (0,10):
                if index == 10:
                    self.set_volume(percent=preset_values[index], control=index)
                else:
                    self.set_volume(percent=preset_values[index], mixer='equal', control=index)
            # Clipping
            self.set_clipping(clipping=preset_values[10])

    def equalize(self, band):
        if cglobals.has_audio:
            index = self.eq_freqs.index(band)
            cglobals.presets[rtk.cfg_preset][index] = eval('rtk.cfg_'+band)
            volume = eval('rtk.cfg_'+band)
            self.set_volume(percent=volume, mixer='equal', control=index)
            cglobals.event_mgr.submit_event('save_preset')

    def set_clipping(self, clipping):
        if cglobals.has_audio:
            rtk.cfg_clipping = clipping
            rtk.cfg_system_vol = clipping
            cglobals.presets[rtk.cfg_preset][-1] = rtk.cfg_clipping
            self.set_volume(clipping)
            cglobals.event_mgr.submit_event('save_preset')

    def play_music(self, music_file):
        if cglobals.has_audio:
            self.status = 'Playing'
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play() # pass int number to play n-1 times. Pass -1 for loop
            self.set_bg_music_volume()

    def play_bg_music(self):
        if cglobals.has_audio:
            try:
                if rtk.cfg_system_music == 'on':
                    if self.status == 'Playing' and pygame.mixer.music.get_busy():
                        pass
                    elif self.status == 'Playing' and not pygame.mixer.music.get_busy():
                        self.status = 'Stopped'
                    elif self.status == 'Paused':               
                        self.status = 'Playing'
                        pygame.mixer.music.unpause()
                    elif self.status == 'Stopped':
                        try:
                            if self.playlist:
                                self.status = 'Playing'
                                if self.playlist_index < len(self.playlist)-1:
                                    self.playlist_index += 1
                                else:
                                    self.playlist_index = 0
                                pygame.mixer.music.load(self.playlist[self.playlist_index])
                                pygame.mixer.music.play() # pass int number to play n-1 times. Pass -1 for loop
                                self.set_bg_music_volume()
                                # Display song info
                                if rtk.cfg_music_title == 'on':
                                    song_name = self.playlist[self.playlist_index].split('/')[-1].rsplit('.',1)[0]
                                    rtk.notif_msg.display(text='<music> ' + song_name)
                        except Exception as error:
                            rtk.logging.error('Error Playing Music: %s', error)
                elif rtk.cfg_system_music == 'off':
                    if self.status != 'Stopped':
                        self.stop_music()
            except:
                pass

    def stop_music(self):
        if cglobals.has_audio:
            self.status = 'Stopped'
            pygame.mixer.music.stop()
    
    def pause_music(self):
        if cglobals.has_audio:
            if rtk.cfg_system_music == 'on' and self.playlist:
                self.status = 'Paused'
                pygame.mixer.music.pause()

    def set_bg_music_volume(self):
        if cglobals.has_audio:
            pygame.mixer.music.set_volume(float(rtk.cfg_system_music_vol)/100) # optional volume 0 to 1.0

    def set_menu_sounds_volume(self):
        if cglobals.has_audio:
            volume = str(rtk.cfg_system_sounds_vol)
            self.fx_text_advance.set_volume(float(volume)/100)
            self.fx_menu_confirm.set_volume(float(volume)/100)
            self.fx_menu_deny.set_volume(float(volume)/100)
            self.fx_system_error.set_volume(float(volume)/100)
            self.fx_screenshot.set_volume(float(volume)/100)
            self.fx_menu_open.set_volume(float(volume)/100)

    def set_volume(self, percent, mixer='headphone', control=0):
        if cglobals.has_audio:
            dB = lambda x: 2*math.log10(x)
            vol = lambda d,x: dB((1-x)/d+x)/dB(d)+1
            p = int(percent)/100
            v = vol(self.dynamic_range, p)
            a,b = self.mixer_range
            volume = int(a*(1-v)+b*v)
            try:
                if mixer == 'headphone':
                    if self.headphone_mixer:
                        self.headphone_mixer.setvolume(volume)
                elif mixer == 'equal':
                    eq_mixer = getattr(self, 'eq_mixer_%s' % control, None)
                    if eq_mixer:
                        eq_mixer.setvolume(int(percent))
            except Exception as e:
                rtk.logging.debug('set_volume(%s,%s,%s) ignored: %s', percent, mixer, control, e)

    def vol_down(self):
        if cglobals.has_audio:
            if rtk.cfg_preset == 'Flat':
                index = self.volumes.index(str(rtk.cfg_system_vol))
                if index > 0:
                    index -= 1
                    rtk.cfg_system_vol = self.volumes[index]
                    rtk.notif_msg.display(text='<speaker> ' + str(rtk.cfg_system_vol))
                    self.set_volume(rtk.cfg_system_vol)
                    cglobals.event_mgr.submit_event('save_config')
                else:
                    rtk.notif_msg.display(text='<speaker> ' + str(rtk.cfg_system_vol))
            else:
                rtk.notif_msg.display(text='volume_locked')

    def vol_up(self):
        if cglobals.has_audio:
            if rtk.cfg_preset == 'Flat':
                index = self.volumes.index(str(rtk.cfg_system_vol))
                if index < len(self.volumes)-1:
                    index += 1
                    rtk.cfg_system_vol = self.volumes[index]
                    rtk.notif_msg.display(text='<speaker> ' + str(rtk.cfg_system_vol))
                    self.set_volume(rtk.cfg_system_vol)
                    cglobals.event_mgr.submit_event('save_config')
                else:
                    rtk.notif_msg.display(text='<speaker> ' + str(rtk.cfg_system_vol))
            else:
                rtk.notif_msg.display(text='volume_locked')

    def play_advance(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_text_advance)

    def play_confirm(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_menu_confirm)

    def play_open(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_menu_open)

    def play_deny(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_menu_deny)

    def play_screenshot(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_screenshot)

    def play_shoot(self):
        if cglobals.has_audio:
            pygame.mixer.Sound.play(self.fx_shoot)

    def play_error(self):
        if cglobals.has_audio:
            self.stop_music()
            pygame.mixer.Sound.play(self.fx_system_error)

    def update(self, event):
        if event.down:
            if rtk.cfg_system_sounds == 'on':
                current_view = utils.get_view_name()
                if current_view == 'lgun_cfg_view':
                    if event.key == 'Trigger':
                        self.play_shoot()
                    elif event.key == cglobals.input_mgr.joy_action_2\
                        or event.key == 'K_ESCAPE' or event.key == 'K_BACKSPACE':
                        self.play_deny()
                    elif event.key == 'K_PRINT':
                        self.play_screenshot()
                elif current_view != 'joy_cfg_view':
                    if event.key == 'D-Pad Up' or event.key == 'D-Pad Down' or event.key == 'D-Pad Right' or event.key == 'D-Pad Left'\
                        or event.key == cglobals.input_mgr.joy_special_1\
                        or event.key == cglobals.input_mgr.joy_special_2\
                        or event.key == 'K_-' or event.key == 'K_+':
                        self.play_advance()
                    elif event.key == cglobals.input_mgr.joy_action_1\
                        or event.key == cglobals.input_mgr.joy_action_3\
                        or event.key == cglobals.input_mgr.joy_action_4\
                        or event.key == 'K_RETURN' or event.key == 'K_X' or event.key == 'K_Y':
                        self.play_confirm()
                    elif event.key == cglobals.input_mgr.joy_start or event.key == 'K_F1':
                        self.play_open()
                    elif event.key == cglobals.input_mgr.joy_action_2\
                        or event.key == 'K_ESCAPE' or event.key == 'K_BACKSPACE':
                        self.play_deny()
                    elif event.key == 'K_PRINT':
                        self.play_screenshot()