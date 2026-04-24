#!/bin/sh
# FAT-only provisioner for Lakka-CRT-RetroTINK.
# Lakka's fs-resize auto-executes /flash/firstboot.sh on first boot, so we
# only need to drop files on the FAT partition — ext4 access is optional.
#
# Usage:
#   ./apply.sh [--preset NAME] FLASH_MNT
#
# Presets (presets/*.txt):
#   240p-ntsc           — 2560x240  @ 52.33 MHz
#   240p-ntsc-superx    — 3840x240  @ 81    MHz   (recommended)
#   240p-pal            — 2560x288  @ 43.75 MHz
#   480i-ntsc           — 3840x480i @ 81    MHz
#   480i-pal            — 3840x576i @ 81    MHz

set -eu

preset=240p-ntsc-superx
if [ "${1:-}" = '--preset' ]; then
    preset=$2
    shift 2
fi

FLASH="${1:?FLASH_MNT required}"
SRC="$(cd "$(dirname "$0")" && pwd)"

[ -d "$FLASH" ] || { echo "FLASH_MNT '$FLASH' not a dir"; exit 1; }

echo "[apply] preset=$preset  flash=$FLASH"
preset_file="$SRC/presets/$preset.txt"
[ -f "$preset_file" ] || { echo "unknown preset '$preset'"; exit 2; }

echo "[apply] copy flash/* -> $FLASH"
cp "$SRC/flash/config.txt"   "$FLASH/config.txt"
cp "$SRC/flash/firstboot.sh" "$FLASH/firstboot.sh"
chmod +x "$FLASH/firstboot.sh" 2>/dev/null || true

# Inject preset into distroconfig.txt between CRT-DPI-BEGIN/END markers
dc="$FLASH/distroconfig.txt"
cp "$SRC/flash/distroconfig.txt" "$dc"
awk -v preset_file="$preset_file" '
    /-------- CRT-DPI-BEGIN --------/ {print; in_block=1; while((getline line < preset_file) > 0) print line; next}
    /-------- CRT-DPI-END --------/   {in_block=0; print; next}
    !in_block                          {print}
' "$dc" > "$dc.tmp" && mv "$dc.tmp" "$dc"

echo "[apply] done. Eject SD, boot Pi5. /flash/firstboot.sh runs on first boot:"
echo "         - enables sshd persistently (SSHD_START=true)"
echo "         - writes switchres.ini + RA CRT keys + per-core overrides"
echo "        After reboot: ssh root@<pi-ip>  (pwd: root — change it!)"
