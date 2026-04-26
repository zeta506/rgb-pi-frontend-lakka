#!/bin/sh
set -eu

mkdir -p /storage/.cache/services
echo "SSHD_START=true" > /storage/.cache/services/sshd.conf
systemctl start sshd 2>/dev/null || true

if [ ! -f /storage/.cache/rgbpi-lakka-session ]; then
    /bin/sh -c '(sleep 1; systemctl reset-failed retroarch >/dev/null 2>&1 || true; systemctl start retroarch --no-block >/dev/null 2>&1 || true) &' >/dev/null 2>&1 || true
    exit 0
fi

rm -f /storage/.cache/rgbpi-lakka-session
systemctl set-default multi-user.target >/dev/null 2>&1 || true
systemctl disable retroarch >/dev/null 2>&1 || true
systemctl enable rgbpi-frontend >/dev/null 2>&1 || true
systemctl reset-failed rgbpi-frontend retroarch >/dev/null 2>&1 || true

/bin/sh -c '(sleep 2; cat /dev/zero > /dev/fb0 2>/dev/null || true; systemctl start rgbpi-frontend --no-block >/dev/null 2>&1 || true) &' >/dev/null 2>&1 || true
