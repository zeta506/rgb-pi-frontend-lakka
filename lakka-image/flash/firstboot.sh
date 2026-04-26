#!/bin/sh
# Lakka-CRT-RetroTINK first-boot provisioner.
# Copied from /flash/firstboot.sh to /storage/.first-run by the systemd
# oneshot below, then executed ONCE.
#
# Responsibilities:
#   - Enable SSH persistently.
#   - Populate /storage/.config/retroarch/ with CRT presets.
#   - Copy switchres.ini.
#   - Touch /storage/.first-run-done so next boots skip.

set -eu

# Sentinel on /flash so it survives storage wipes and is visible/deletable
# from Windows. Delete /flash/.first-run-done to force re-provision.
SENTINEL=/flash/.first-run-done
[ -f "$SENTINEL" ] && exit 0

echo "[firstboot] running initial CRT/SSH provisioning..."

if [ -f /flash/cmdline.txt ] && ! grep -qw nosplash /flash/cmdline.txt; then
    mount -o remount,rw /flash 2>/dev/null || true
    cp /flash/cmdline.txt /flash/cmdline.txt.before-rgbpi-nosplash 2>/dev/null || true
    sed -i 's/$/ nosplash/' /flash/cmdline.txt
    sync
fi

# -- SSH --
mkdir -p /storage/.cache/services
echo 'SSHD_START=true' > /storage/.cache/services/sshd.conf
systemctl enable sshd 2>/dev/null || true
systemctl start  sshd 2>/dev/null || true

# -- WiFi seed from /flash/wifi-config.txt (legacy retrotink-revival format) --
WIFI_FILE=/flash/wifi-config.txt
[ -f /flash/wifi.conf ] && WIFI_FILE=/flash/wifi.conf
if [ -f "$WIFI_FILE" ]; then
    SSID=$(grep -E '^SSID='    "$WIFI_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "\r")
    PSK=$(grep -E '^PSK='      "$WIFI_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "\r")
    COUNTRY=$(grep -E '^COUNTRY=' "$WIFI_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "\r")
    if [ -n "${SSID:-}" ]; then
        mkdir -p /storage/.cache/connman
        SSID_HEX=$(printf '%s' "$SSID" | od -An -tx1 | tr -d ' \n')
        cat > /storage/.cache/connman/wifi.config <<CM
[global]
Name = wifi
Description = wifi seeded by firstboot.sh

[service_wifi]
Type = wifi
Security = psk
Name = $SSID
SSID = $SSID_HEX
Passphrase = $PSK
IPv4 = dhcp
Nameservers = 1.1.1.1,8.8.8.8
CM
        chmod 600 /storage/.cache/connman/wifi.config
        echo "[firstboot] wifi seeded for SSID=$SSID"
    fi
fi

# -- RetroArch CRT defaults --
RA_DIR=/storage/.config/retroarch
mkdir -p "$RA_DIR"

# switchres.ini (generic 15 kHz range — covers NTSC 240p/480i and PAL 240p/288p)
cat > "$RA_DIR/switchres.ini" <<'INI'
monitor   custom
crt_range0  15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 480, 576
INI

# Global RA tweaks — append only if not present already
RA_CFG="$RA_DIR/retroarch.cfg"
[ -f "$RA_CFG" ] || touch "$RA_CFG"
for kv in \
    'crt_switch_resolution = "1"' \
    'crt_switch_resolution_super = "3840"' \
    'crt_switch_hires_menu = "false"' \
    'crt_switch_porch_adjust = "0"' \
    'crt_switch_center_adjust = "0"' \
    'crt_switch_vertical_adjust = "0"' \
    'video_scale_integer = "false"' \
    'video_smooth = "false"' \
    'aspect_ratio_index = "22"' \
    'video_aspect_ratio_auto = "false"' \
    'video_fullscreen = "true"' \
    'video_fullscreen_x = "0"' \
    'video_fullscreen_y = "0"' \
    'video_viewport_bias_x = "0.500000"' \
    'video_viewport_bias_y = "0.500000"' \
    'custom_viewport_width = "0"' \
    'custom_viewport_height = "0"' \
    'custom_viewport_x = "0"' \
    'custom_viewport_y = "0"' \
    'menu_driver = "rgui"' \
    'joypad_autoconfig_dir = "/storage/rgbpi/data/joyconfig"' \
    'input_driver = "udev"' \
    'input_joypad_driver = "udev"' \
    'all_users_control_menu = "true"' \
    'assets_directory = "/storage/rgbpi/raassets"' \
    'rgui_menu_color_theme = "16"' \
    'menu_dynamic_wallpaper_enable = "false"' \
    'rgui_menu_theme_preset = ""' \
    'config_save_on_exit = "false"' \
    'rgui_aspect_ratio = "0"' \
    'rgui_aspect_ratio_lock = "0"' \
    'kms_connector = "DPI-1"'
do
    key=$(printf '%s' "$kv" | cut -d'=' -f1 | tr -d ' ')
    if grep -q "^${key} *=" "$RA_CFG" 2>/dev/null; then
        sed -i "s|^${key} *=.*|${kv}|" "$RA_CFG"
    else
        echo "$kv" >> "$RA_CFG"
    fi
done

# Per-core overrides — let CRT switchres own the aspect (22 = core-provided
# but with switchres' "Aspect ratio forced by user" override the running
# DRM mode dimensions are used, so 240p games fill 3840x240 and 480i games
# fill 3840x480 without the FE rewriting MAME.cfg per launch).
mkdir -p "$RA_DIR/config/MAME"
cat > "$RA_DIR/config/MAME/MAME.cfg" <<'CFG'
aspect_ratio_index = "22"
video_aspect_ratio_auto = "false"
video_scale_integer = "false"
CFG

mkdir -p "$RA_DIR/config/MAME 2003-Plus"
cp "$RA_DIR/config/MAME/MAME.cfg" "$RA_DIR/config/MAME 2003-Plus/MAME 2003-Plus.cfg"

mkdir -p "$RA_DIR/config/Flycast"
cp "$RA_DIR/config/MAME/MAME.cfg" "$RA_DIR/config/Flycast/Flycast.cfg"

# -- Optional CRT extras from /flash/retrotink (retrotink-revival fork) --
if [ -d /flash/retrotink ]; then
    # SuperResolucion bitmap font for RGUI menu legibility @ 240p
    if [ -f /flash/retrotink/SuperResolucion.ttf ]; then
        mkdir -p /storage/fonts
        cp /flash/retrotink/SuperResolucion.ttf /storage/fonts/
        sed -i 's|^video_font_path = .*|video_font_path = "/storage/fonts/SuperResolucion.ttf"|' "$RA_CFG" 2>/dev/null || true
        grep -q '^video_font_path ' "$RA_CFG" || echo 'video_font_path = "/storage/fonts/SuperResolucion.ttf"' >> "$RA_CFG"
        grep -q '^video_font_size ' "$RA_CFG" || echo 'video_font_size = "12.000000"' >> "$RA_CFG"
    fi
    # Per-core options (overscan OFF for most cores)
    if [ -f /flash/retrotink/core-options.cfg ]; then
        CORE_OPTS=/storage/.config/retroarch/retroarch-core-options.cfg
        touch "$CORE_OPTS"
        while IFS= read -r line; do
            case "$line" in \#*|"") continue ;; esac
            key=$(echo "$line" | cut -d'=' -f1 | tr -d ' ')
            if grep -q "^${key} *=" "$CORE_OPTS" 2>/dev/null; then
                sed -i "s|^${key} *=.*|${line}|" "$CORE_OPTS"
            else
                echo "$line" >> "$CORE_OPTS"
            fi
        done < /flash/retrotink/core-options.cfg
    fi
fi

# -- Auto-detect USB DAC and write audio_device into retroarch.cfg --
AUDIO_DEV=""
for card in 0 1 2 3; do
    name=$(cat /proc/asound/card${card}/id 2>/dev/null)
    if [ -n "$name" ] && [ "$name" != "vc4hdmi" ] && [ "$name" != "vc4hdmi0" ] && [ "$name" != "vc4hdmi1" ]; then
        AUDIO_DEV="hw:${card},0"
        break
    fi
done
[ -z "$AUDIO_DEV" ] && AUDIO_DEV="hw:0,0"
if grep -q '^audio_device ' "$RA_CFG"; then
    sed -i "s|^audio_device = .*|audio_device = \"${AUDIO_DEV}\"|" "$RA_CFG"
else
    echo "audio_device = \"${AUDIO_DEV}\"" >> "$RA_CFG"
fi
# Also alsa default + max volume on detected card
CARD_NUM=$(echo "$AUDIO_DEV" | sed 's|hw:||;s|,.*||')
mkdir -p /storage/.config
cat > /storage/.config/asound.conf <<ASND
defaults.pcm.card $CARD_NUM
defaults.pcm.device 0
defaults.ctl.card $CARD_NUM
ASND
amixer -c "$CARD_NUM" sset Speaker 100% unmute >/dev/null 2>&1 || true

# -- Done --
touch "$SENTINEL"
echo "[firstboot] done. Rebooting for good measure."
systemctl reboot
