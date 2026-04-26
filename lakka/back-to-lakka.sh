#!/bin/sh
set -eu

mkdir -p /storage/.cache/services
echo "SSHD_START=true" > /storage/.cache/services/sshd.conf
systemctl start sshd 2>/dev/null || true

touch /storage/.cache/rgbpi-lakka-session
systemctl set-default multi-user.target >/dev/null 2>&1 || true
systemctl enable rgbpi-frontend >/dev/null 2>&1 || true
systemctl disable retroarch >/dev/null 2>&1 || true

fe_pid="$(systemctl show -p MainPID --value rgbpi-frontend 2>/dev/null || echo 0)"
systemctl stop rgbpi-frontend --no-block >/dev/null 2>&1 || true
for i in 1 2 3 4 5; do
    if ! kill -0 "$fe_pid" 2>/dev/null; then
        break
    fi
    sleep 1
done

if [ "$fe_pid" != "0" ] && kill -0 "$fe_pid" 2>/dev/null; then
    kill -9 "$fe_pid" >/dev/null 2>&1 || true
    systemctl kill -s KILL rgbpi-frontend >/dev/null 2>&1 || true
    sleep 1
fi

systemctl reset-failed rgbpi-frontend retroarch >/dev/null 2>&1 || true
cat /dev/zero > /dev/fb0 2>/dev/null || true
systemctl start retroarch --no-block
sleep 1
systemctl reset-failed rgbpi-frontend retroarch >/dev/null 2>&1 || true
