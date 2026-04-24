import os
import zipfile
import datetime

# Lakka-port: anchored to /storage/rgbpi
RGBPI_ROOT  = '/storage/rgbpi'
rgbpi       = RGBPI_ROOT
temp        = RGBPI_ROOT + '/temp'
# System folders
data        = RGBPI_ROOT + '/data'
bck         = RGBPI_ROOT + '/data/backup'
bck_joy     = RGBPI_ROOT + '/data/backup/joyconfig'
joy_cfg     = RGBPI_ROOT + '/data/joyconfig'
remaps      = RGBPI_ROOT + '/data/remaps'
scraper     = RGBPI_ROOT + '/data/scraper'
scr_img     = RGBPI_ROOT + '/data/scraper/images'
fonts       = RGBPI_ROOT + '/fonts'
images      = RGBPI_ROOT + '/images'
sounds      = RGBPI_ROOT + '/sounds'
fx          = RGBPI_ROOT + '/sounds/fx'
music       = RGBPI_ROOT + '/sounds/music'
system      = RGBPI_ROOT + '/system'
themes      = RGBPI_ROOT + '/themes'
other       = RGBPI_ROOT + '/other'
# Lakka retroarch paths: binary + cores come from overlay mounts
retroarch   = '/usr/bin/retroarch'
cores       = '/tmp/cores'
# Update folders
tmp_data    = RGBPI_ROOT + '/temp/data'
tmp_bck     = RGBPI_ROOT + '/temp/data/backup'
tmp_bck_joy = RGBPI_ROOT + '/temp/data/backup/joyconfig'
tmp_joy_cfg = RGBPI_ROOT + '/temp/data/joyconfig'
tmp_remaps  = RGBPI_ROOT + '/temp/data/remaps'
tmp_scraper = RGBPI_ROOT + '/temp/data/scraper'
tmp_scr_img = RGBPI_ROOT + '/temp/data/scraper/images'
tmp_fonts   = RGBPI_ROOT + '/temp/fonts'
tmp_images  = RGBPI_ROOT + '/temp/images'
tmp_sounds  = RGBPI_ROOT + '/temp/sounds'
tmp_fx      = RGBPI_ROOT + '/temp/sounds/fx'
tmp_music   = RGBPI_ROOT + '/temp/sounds/music'
tmp_system  = RGBPI_ROOT + '/temp/system'
tmp_themes  = RGBPI_ROOT + '/temp/themes'
tmp_rarch   = RGBPI_ROOT + '/temp/retroarch'

# Clean temp folder
os.system('rm -rf ' + temp)
# Create update folders
os.system('mkdir ' + temp)
os.system('mkdir ' + tmp_data)
os.system('mkdir ' + tmp_bck)
os.system('mkdir ' + tmp_bck_joy)
os.system('mkdir ' + tmp_joy_cfg)
os.system('mkdir ' + tmp_remaps)
os.system('mkdir ' + tmp_scraper)
os.system('mkdir ' + tmp_scr_img)
os.system('mkdir ' + tmp_fonts)
os.system('mkdir ' + tmp_images)
os.system('mkdir ' + tmp_sounds)
os.system('mkdir ' + tmp_fx)
os.system('mkdir ' + tmp_music)
os.system('mkdir ' + tmp_system)
os.system('mkdir ' + tmp_themes)
os.system('mkdir ' + tmp_rarch)
# Copy files
os.system('cp ' + rgbpi + '/*.pyc ' + tmp_system)
os.system('cp ' + data + '/bios.dat ' + tmp_data)
os.system('cp ' + data + '/cores.cfg ' + tmp_data)
os.system('cp ' + data + '/systems.dat ' + tmp_data)
os.system('cp ' + data + '/tate_games.dat ' + tmp_data)
os.system('cp ' + data + '/translations.dat ' + tmp_data)
os.system('cp ' + bck + '/config.ini ' + tmp_bck)
os.system('cp ' + bck + '/cores.cfg ' + tmp_bck)
os.system('cp ' + retroarch + '/retroarch ' + tmp_rarch)
os.system('cp ' + cores + '/lr-mgba/mgba_libretro.so ' + tmp_rarch)
# Create Pre/Post update scripts
with open(temp + '/pre-update.py', 'w', encoding='utf-8') as file:
    file.write('import os\n')
    file.write('print("Pre-Update in progress...")\n')
    file.write('print("Pre-Update finished!")\n')
with open(temp + '/post-update.py', 'w', encoding='utf-8') as file:
    file.write('import os\n')
    file.write('print("Post-Update in progress...")\n')
    file.write('os.system("apt install zip")\n')
    file.write('os.system("cp ' + tmp_rarch + '/retroarch ' + retroarch + '")\n')
    file.write('os.system("cp ' + tmp_rarch + '/mgba_libretro.so ' + cores + '/lr-mgba")\n')
    file.write('print("Post-Update finished!")\n')
# Create zip file
os_ver = str(4)
os_int_ver = str(7)
now = datetime.datetime.now()
year = str(now.year)
month = str(now.month).zfill(2)
day = str(now.day).zfill(2)
file_name = os_ver + '_' + os_int_ver + '_' + year + month + day + '.zip'
os.chdir('/storage/rgbpi/temp')
os.system('zip -r ' + file_name + ' .')