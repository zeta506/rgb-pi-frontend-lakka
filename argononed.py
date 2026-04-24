# https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
import smbus
import RPi.GPIO as GPIO
import subprocess
import time
import os
import sys
from threading import Thread

try:
	bus = smbus.SMBus(1)
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	shutdown_pin=4
	GPIO.setup(shutdown_pin, GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)
except:
	sys.exit(0) # This supress the onscreen systemd errors

def shutdown_check():
	try:
		while True:
			pulsetime = 1
			GPIO.wait_for_edge(shutdown_pin, GPIO.RISING)
			time.sleep(0.01)
			while GPIO.input(shutdown_pin) == GPIO.HIGH:
				time.sleep(0.01)
				pulsetime += 1
			if pulsetime >=2 and pulsetime <=3:
				reboot()
	except:
		pass
def temp_check():
	fanmin = 0x00
	fanmax = 0x64
	address = 0x1a
	is_fan_active = False
	bus.write_byte(address,fanmin)
	while True:
		try:
			tempfp = open("/sys/class/thermal/thermal_zone0/temp", "r")
			temp = tempfp.readline()
			tempfp.close()
			temp = float(int(temp)/1000)
		except IOError:
			temp = 0
		try:
			if is_fan_active:
				if temp < 45:
					bus.write_byte(address,fanmin)
					is_fan_active = False
			else:
				if temp > 50:
					bus.write_byte(address,fanmax)
					is_fan_active = True
		except IOError:
			pass
		time.sleep(30)
def check_rgbpiui():
    try:
        rgbpiui = str(int(subprocess.check_output(['pgrep', '-f', '-n', 'rgbpiui.pyc'])))
    except:
        rgbpiui = 0
    return rgbpiui
def check_retroarch():
    try:
        retroarch_pids = subprocess.check_output(['pgrep', '-f', 'retroarch([^.]|$)']).splitlines()
        for index, pid in enumerate(retroarch_pids):
            retroarch_pids[index] = str(int(pid))
    except:
        retroarch_pids = []
    return retroarch_pids
def reboot():
    rgbpi_ui = check_rgbpiui()
    retroarch_pids = check_retroarch()
    if rgbpi_ui != 0 and retroarch_pids != []: # Close retroarch and child processes and return to UI
        for pid in retroarch_pids:
            os.system('kill -9 ' + pid)
    else:    
        os.system('shutdown -r now')

try:
	#t1 = Thread(target = shutdown_check)
	t2 = Thread(target = temp_check)
	#t1.start()
	t2.start()
except:
	#t1.stop()
	t2.stop()
	GPIO.cleanup()
