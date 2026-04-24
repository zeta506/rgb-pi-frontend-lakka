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
systemctl daemon-reload
if [ "${RGBPI_ENABLE_SERVICE:-0}" = "1" ]; then
    echo "      Enabling rgbpi-frontend.service and disabling retroarch"
    # Disable stock retroarch.service so it doesn't race for fb0.
    systemctl disable retroarch 2>/dev/null || true
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
