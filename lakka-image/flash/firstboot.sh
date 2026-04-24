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

SENTINEL=/storage/.first-run-done
[ -f "$SENTINEL" ] && exit 0

echo "[firstboot] running initial CRT/SSH provisioning..."

# -- SSH --
mkdir -p /storage/.cache/services
echo 'SSHD_START=true' > /storage/.cache/services/sshd.conf
systemctl enable sshd 2>/dev/null || true
systemctl start  sshd 2>/dev/null || true

# -- RetroArch CRT defaults --
RA_DIR=/storage/.config/retroarch
mkdir -p "$RA_DIR"

# switchres.ini (generic 15 kHz range — covers NTSC 240p/480i and PAL 240p/288p)
cat > "$RA_DIR/switchres.ini" <<'INI'
monitor   custom
crt_range0  15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 448, 576
INI

# Global RA tweaks — append only if not present already
RA_CFG="$RA_DIR/retroarch.cfg"
[ -f "$RA_CFG" ] || touch "$RA_CFG"
for kv in \
    'crt_switch_resolution = "1"' \
    'crt_switch_resolution_super = "2560"' \
    'crt_switch_hires_menu = "false"' \
    'crt_switch_porch_adjust = "0"' \
    'crt_switch_center_adjust = "0"' \
    'crt_switch_vertical_adjust = "0"' \
    'video_scale_integer = "false"' \
    'video_smooth = "false"' \
    'aspect_ratio_index = "20"' \
    'video_aspect_ratio = "1.333333"' \
    'video_fullscreen = "true"' \
    'kms_connector = "DPI-1"'
do
    key=$(printf '%s' "$kv" | cut -d'=' -f1 | tr -d ' ')
    if grep -q "^${key} *=" "$RA_CFG" 2>/dev/null; then
        sed -i "s|^${key} *=.*|${kv}|" "$RA_CFG"
    else
        echo "$kv" >> "$RA_CFG"
    fi
done

# Per-core overrides tuned for 240p mode (2560x240)
mkdir -p "$RA_DIR/config/MAME"
cat > "$RA_DIR/config/MAME/MAME.cfg" <<'CFG'
aspect_ratio_index = "23"
custom_viewport_width = "2560"
custom_viewport_height = "240"
custom_viewport_x = "0"
custom_viewport_y = "0"
video_scale_integer = "false"
CFG

mkdir -p "$RA_DIR/config/MAME 2003-Plus"
cp "$RA_DIR/config/MAME/MAME.cfg" "$RA_DIR/config/MAME 2003-Plus/MAME 2003-Plus.cfg"

mkdir -p "$RA_DIR/config/Flycast"
cp "$RA_DIR/config/MAME/MAME.cfg" "$RA_DIR/config/Flycast/Flycast.cfg"

# -- Done --
touch "$SENTINEL"
echo "[firstboot] done. Rebooting for good measure."
systemctl reboot
