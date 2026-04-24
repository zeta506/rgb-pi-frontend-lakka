#!/bin/sh
# Apply Lakka-CRT-RetroTINK overlay onto a freshly-flashed Lakka SD card.
# Usage:
#   ./apply.sh [--preset 240p-ntsc|240p-pal|480i-ntsc|480i-pal] FLASH_MNT STORAGE_MNT
#
# FLASH_MNT   — mount point of the first FAT partition of the SD ( /flash on the Pi)
# STORAGE_MNT — mount point of the second ext4 partition   ( /storage on the Pi)

set -eu

preset=240p-ntsc
if [ "${1:-}" = '--preset' ]; then
    preset=$2
    shift 2
fi

FLASH="${1:?FLASH_MNT required}"
STORAGE="${2:?STORAGE_MNT required}"
SRC="$(cd "$(dirname "$0")" && pwd)"

[ -d "$FLASH" ]   || { echo "FLASH_MNT '$FLASH' not a dir"; exit 1; }
[ -d "$STORAGE" ] || { echo "STORAGE_MNT '$STORAGE' not a dir"; exit 1; }

echo "[apply] preset=$preset"
preset_file="$SRC/presets/$preset.txt"
[ -f "$preset_file" ] || { echo "unknown preset '$preset'"; exit 2; }

echo "[apply] copy flash/* -> $FLASH"
cp "$SRC/flash/config.txt"        "$FLASH/config.txt"
cp "$SRC/flash/firstboot.sh"      "$FLASH/firstboot.sh"
chmod +x "$FLASH/firstboot.sh" 2>/dev/null || true

# Inject preset into distroconfig.txt between the CRT-DPI-BEGIN/END markers
dc="$FLASH/distroconfig.txt"
cp "$SRC/flash/distroconfig.txt" "$dc"
awk -v preset_file="$preset_file" '
    /-------- CRT-DPI-BEGIN --------/ {print; in_block=1; while((getline line < preset_file) > 0) print line; next}
    /-------- CRT-DPI-END --------/   {in_block=0; print; next}
    !in_block                          {print}
' "$dc" > "$dc.tmp" && mv "$dc.tmp" "$dc"

echo "[apply] copy storage overlay -> $STORAGE"
cp -a "$SRC/storage/." "$STORAGE/"

# Enable firstboot systemd unit on target
mkdir -p "$STORAGE/.config/system.d/multi-user.target.wants"
ln -sf ../rgbpi-firstboot.service \
    "$STORAGE/.config/system.d/multi-user.target.wants/rgbpi-firstboot.service"

# Enable SSH right now so even before firstboot runs, sshd will start
mkdir -p "$STORAGE/.cache/services"
echo 'SSHD_START=true' > "$STORAGE/.cache/services/sshd.conf"

echo "[apply] done. Eject SD, boot the Pi, then 'ssh root@<ip>'."
