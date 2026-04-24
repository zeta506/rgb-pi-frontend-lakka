#!/bin/sh
# Revert Lakka to stock RetroArch menu.
set -eu
SYSD=/storage/.config/system.d
systemctl stop rgbpi-frontend.service 2>/dev/null || true
systemctl disable rgbpi-frontend.service 2>/dev/null || true
rm -f "$SYSD/rgbpi-frontend.service"
systemctl daemon-reload
systemctl enable retroarch
echo "Stock Lakka restored. /storage/rgbpi kept intact."
