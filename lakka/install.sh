#!/bin/sh
# Lakka deploy script for rgb-pi-frontend port.
# Run on target Lakka device (as root):
#   scp -r lakka-port root@LAKKA_IP:/tmp/rgbpi-src && \
#   ssh root@LAKKA_IP 'sh /tmp/rgbpi-src/lakka/install.sh'
#
# Idempotent — safe to re-run.

set -eu

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST=/storage/rgbpi
SYSD=/storage/.config/system.d

echo "[1/7] Create /storage/rgbpi tree"
mkdir -p "$DEST" "$DEST/data" "$DEST/dsp" "$DEST/eq" "$DEST/images" \
         "$DEST/logs" "$DEST/music" "$DEST/remaps" "$DEST/scraper" \
         "$DEST/sfx" "$DEST/sounds" "$DEST/temp" "$DEST/themes" \
         "$DEST/backup" "$DEST/fonts" "$DEST/python-libs"
mkdir -p "$DEST/data/scraper/images" "$DEST/data/scraper/videos" \
         "$DEST/data/scraper/manuals"

echo "[2/7] Copy frontend sources"
# exclude heavy test/dev paths; keep assets
cp -a "$SRC_DIR"/*.py "$DEST/"
cp -a "$SRC_DIR/lakka/smoke-test.sh" "$DEST/"
chmod +x "$DEST/smoke-test.sh"
cp -a "$SRC_DIR/images"   "$DEST/"  2>/dev/null || true
cp -a "$SRC_DIR/sounds"   "$DEST/"  2>/dev/null || true
cp -a "$SRC_DIR/themes"   "$DEST/"  2>/dev/null || true
cp -a "$SRC_DIR/data"     "$DEST/"  2>/dev/null || true
cp -a "$SRC_DIR/raassets" "$DEST/"  2>/dev/null || true
cp -a "$SRC_DIR/config.ini" "$DEST/"
# Seed env.conf only if absent so user edits aren't clobbered on re-install
[ -f "$DEST/env.conf" ] || cp -a "$SRC_DIR/lakka/env.conf" "$DEST/env.conf"

echo "[3/7] Check Python3 + deps"
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not present on Lakka. Install LibreELEC Python3 addon first."
    echo "       See: https://addons.libreelec.tv/"
    exit 2
fi

echo "[4/7] Pip install required libs into $DEST/python-libs"
# Offline-first: if bundled wheels present, install from them; else fallback online
if ls "$SRC_DIR/lakka/wheels"/*.whl >/dev/null 2>&1; then
    echo "      Installing bundled wheels (offline)"
    python3 -m pip install --no-index --target "$DEST/python-libs" \
        --no-warn-script-location "$SRC_DIR/lakka/wheels"/*.whl 2>&1 | tail -3
else
    echo "      No bundled wheels found; attempting online install"
    python3 -m pip install --target "$DEST/python-libs" --no-warn-script-location \
        pygame Pillow 2>&1 | tail -3 || \
        echo "WARN: pip install failed. Re-run with lakka/wheels/*.whl present."
fi

echo "[5/7] Install systemd unit"
mkdir -p "$SYSD"
cp "$SRC_DIR/lakka/rgbpi-frontend.service" "$SYSD/"
[ -f "$SRC_DIR/lakka/rgbpi-boot-logo.service" ] && cp "$SRC_DIR/lakka/rgbpi-boot-logo.service" "$SYSD/"
cp "$SRC_DIR/lakka/rgbpi-switch-to-lakka.service" "$SYSD/"
cp "$SRC_DIR/lakka/back-to-lakka.sh" /storage/back-to-lakka.sh
cp "$SRC_DIR/lakka/return-to-rgbpi.sh" /storage/return-to-rgbpi.sh
chmod +x /storage/back-to-lakka.sh /storage/return-to-rgbpi.sh
mkdir -p /storage/.config/system.d/retroarch.service.d
cp "$SRC_DIR/lakka/retroarch-rgbpi-session-override.conf" \
   /storage/.config/system.d/retroarch.service.d/override.conf
systemctl daemon-reload
if [ "${RGBPI_ENABLE_SERVICE:-0}" = "1" ]; then
    echo "      Enabling rgbpi-frontend.service and disabling retroarch"
    # Disable stock retroarch.service so it doesn't race for fb0.
    systemctl disable retroarch 2>/dev/null || true
    systemctl enable rgbpi-boot-logo.service 2>/dev/null || true
    systemctl enable rgbpi-frontend.service
else
    echo "      Safe mode: service installed but not enabled"
    echo "      Manual test: systemctl stop retroarch; systemctl start rgbpi-frontend"
fi

echo "[6/7] Write switchres.ini default"
cat > "$DEST/data/switchres.ini" <<'INI'
monitor   custom
crt_range0  15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 448, 576
INI
mkdir -p /storage/.config/retroarch
cp "$DEST/data/switchres.ini" /storage/.config/retroarch/switchres.ini

if [ -f /flash/cmdline.txt ] && ! grep -qw nosplash /flash/cmdline.txt; then
    mount -o remount,rw /flash 2>/dev/null || true
    cp /flash/cmdline.txt /flash/cmdline.txt.before-rgbpi-nosplash 2>/dev/null || true
    sed -i 's/$/ nosplash/' /flash/cmdline.txt
    sync
fi

RA_CFG=/storage/.config/retroarch/retroarch.cfg
[ -f "$RA_CFG" ] || touch "$RA_CFG"
for kv in \
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
    'video_font_size = "12.000000"' \
    'menu_show_start_screen = "false"'
do
    key=$(printf '%s' "$kv" | cut -d'=' -f1 | tr -d ' ')
    if grep -q "^${key} *=" "$RA_CFG" 2>/dev/null; then
        sed -i "s|^${key} *=.*|${kv}|" "$RA_CFG"
    else
        echo "$kv" >> "$RA_CFG"
    fi
done

echo "[7/8] Run smoke test"
sh "$SRC_DIR/lakka/smoke-test.sh" || {
    echo "!! Smoke test failed. Inspect output above before enabling service."
    echo "!! Service remains enabled; you can disable with:"
    echo "!!    systemctl disable rgbpi-frontend.service"
    exit 3
}

echo "[8/8] Done."
if [ "${RGBPI_ENABLE_SERVICE:-0}" = "1" ]; then
    echo "Reboot to launch frontend."
else
    echo "RetroArch boot left untouched."
    echo "Manual test: systemctl stop retroarch; systemctl start rgbpi-frontend"
fi
