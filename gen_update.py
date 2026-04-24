import os
import zipfile
import datetime

rgbpi       = '/opt/rgbpi/ui'
temp        = '/opt/rgbpi/ui/temp'
# System folders
data        = '/opt/rgbpi/ui/data'
bck         = '/opt/rgbpi/ui/data/backup'
bck_joy     = '/opt/rgbpi/ui/data/backup/joyconfig'
joy_cfg     = '/opt/rgbpi/ui/data/joyconfig'
remaps      = '/opt/rgbpi/ui/data/remaps'
scraper     = '/opt/rgbpi/ui/data/scraper'
scr_img     = '/opt/rgbpi/ui/data/scraper/images'
fonts       = '/opt/rgbpi/ui/fonts'
images      = '/opt/rgbpi/ui/images'
sounds      = '/opt/rgbpi/ui/sounds'
fx          = '/opt/rgbpi/ui/sounds/fx'
music       = '/opt/rgbpi/ui/sounds/music'
system      = '/opt/rgbpi/ui/system'
themes      = '/opt/rgbpi/ui/themes'
other       = '/opt/rgbpi/ui/other'
retroarch   = '/opt/retroarch'
cores       = '/opt/retroarch/cores'
# Update folders
tmp_data    = '/opt/rgbpi/ui/temp/data'
tmp_bck     = '/opt/rgbpi/ui/temp/data/backup'
tmp_bck_joy = '/opt/rgbpi/ui/temp/data/backup/joyconfig'
tmp_joy_cfg = '/opt/rgbpi/ui/temp/data/joyconfig'
tmp_remaps  = '/opt/rgbpi/ui/temp/data/remaps'
tmp_scraper = '/opt/rgbpi/ui/temp/data/scraper'
tmp_scr_img = '/opt/rgbpi/ui/temp/data/scraper/images'
tmp_fonts   = '/opt/rgbpi/ui/temp/fonts'
tmp_images  = '/opt/rgbpi/ui/temp/images'
tmp_sounds  = '/opt/rgbpi/ui/temp/sounds'
tmp_fx      = '/opt/rgbpi/ui/temp/sounds/fx'
tmp_music   = '/opt/rgbpi/ui/temp/sounds/music'
tmp_system  = '/opt/rgbpi/ui/temp/system'
tmp_themes  = '/opt/rgbpi/ui/temp/themes'
tmp_rarch   = '/opt/rgbpi/ui/temp/retroarch'

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
os.chdir('/opt/rgbpi/ui/temp')
os.system('zip -r ' + file_name + ' .')