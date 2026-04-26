# Lakka-specific path definitions
# Replaces internal RGB-Pi OS bootstrap paths
# All paths anchored to Lakka's writable /storage overlay + read-only system dirs

import os

# Root install dir (writable, persists across reboot)
path_rgbpi           = '/storage/rgbpi'
path_rgbpi_data      = path_rgbpi + '/data'
path_rgbpi_dsp       = path_rgbpi + '/dsp'
path_rgbpi_eq        = path_rgbpi + '/eq'
path_rgbpi_images    = path_rgbpi + '/images'
path_rgbpi_logs      = path_rgbpi + '/logs'
path_rgbpi_music     = path_rgbpi + '/music'
path_rgbpi_remaps    = path_rgbpi + '/remaps'
path_rgbpi_scraper   = path_rgbpi + '/scraper'
path_rgbpi_sfx       = path_rgbpi + '/sfx'
path_rgbpi_sounds    = path_rgbpi + '/sounds'
path_rgbpi_temp      = path_rgbpi + '/temp'
path_rgbpi_themes    = path_rgbpi + '/themes'
path_rgbpi_backup    = path_rgbpi + '/backup'
path_rgbpi_fonts     = path_rgbpi + '/fonts'

# RetroArch Lakka paths (read-only overlays auto-mounted at /tmp/*)
path_retroarch        = '/usr/bin/retroarch'
path_retroarch_assets = '/tmp/assets'
path_retroarch_fonts  = path_rgbpi_fonts            # frontend controls fonts
path_cores            = '/usr/lib/libretro'
path_autoconfig       = '/tmp/joypads'

# Lakka storage/roms convention
path_media_sd         = '/storage/roms'
path_media_usb        = '/var/media'
path_media_nfsg       = '/storage/nfs-global'
path_media_nfsl       = '/storage/nfs-local'

# Optional
path_kodi             = '/usr/lib/kodi'             # not installed in Lakka; placeholder
path_udev_rules       = '/storage/.config/udev.rules.d'
path_wpa_supplicant   = '/storage/.cache/connman'   # Lakka uses connman not wpa_sup

# Ensure writable dirs exist
def ensure_dirs():
    for d in (path_rgbpi_data, path_rgbpi_dsp, path_rgbpi_eq,
              path_rgbpi_images, path_rgbpi_logs, path_rgbpi_music,
              path_rgbpi_remaps, path_rgbpi_scraper, path_rgbpi_sfx,
              path_rgbpi_sounds, path_rgbpi_temp, path_rgbpi_themes,
              path_rgbpi_backup, path_rgbpi_fonts):
        os.makedirs(d, exist_ok=True)
