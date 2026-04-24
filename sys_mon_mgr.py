'''
19:'soft_temperature_limit_has_occurred',
18:'throttling_has_occurred',
17:'arm_frequency_capped_has_occurred',
16:'under_voltage_has_occurred',
3:'soft_temperature_limit_active',
2:'currently_throttled',
1:'arm_frequency_capped',
0:'under_voltage'

'0x80000':'soft_temperature_limit_has_occurred',
'0x40000':'throttling_has_occurred',
'0x20000':'arm_frequency_capped_has_occurred',
'0x10000':'under_voltage_has_occurred',
'0x8':'soft_temperature_limit_active',
'0x4':'currently_throttled',
'0x2':'arm_frequency_capped',
'0x1':'under_voltage'

01110000000000000010
||||            ||||_ Under-voltage detected
||||            |||_ Arm frequency capped
||||            ||_ Currently throttled
||||            |_ Soft temperature limit active
||||_ Under-voltage has occurred since last reboot
|||_ Arm frequency capped has occurred
||_ Throttling has occurred
|_ Soft temperature limit has occurred
'''
# https://elinux.org/RPI_vcgencmd_usage
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/frequency-management.md
# https://www.raspberrypi.org/documentation/configuration/config-txt/overclocking.md
# Throttling from 80-85º
# Soft limit set to 60º only in 3A+ and 3B+ can be extended to 70º by temp_soft_limit in config.txt

import rtk
import subprocess
import utils

class Sys_Mon_Mgr(object):
    def __init__(self):
        self.warnings = {
            2:'currently_throttled',
            1:'arm_frequency_capped',
            0:'under_voltage'
        }

    def get_throttled(self):
        p = subprocess.Popen('vcgencmd get_throttled | cut -f2 -d=', stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p.wait()
        throttled = output.decode("utf-8").replace('\n','')
        #throttled = '0x0000F'
        throttled_binary = bin(int(throttled, 0))
        return throttled_binary

    def check(self):
        sensor_info = utils.get_sensor_info()
        temp = sensor_info.temp
        throttle = self.get_throttled()
        # Throttle
        if throttle != '0x0':
            for position, warning in self.warnings.items():
                # Check for the binary digits to be "on" for each warning message
                if len(throttle) > position and throttle[0 - position - 1] == '1':
                    rtk.notif_msg.display(text='volt_warning', l_icon='volt')
        # Temp
        if int(temp.split('.')[0]) >= 60:
            rtk.notif_msg.display(text='temp_warning', l_icon='temp')
