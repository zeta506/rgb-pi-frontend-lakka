#!/bin/sh
# Smoke test — run on target Lakka to validate install before enabling service.
# Exits 0 on success, non-zero on any check failure.
set -u

DEST=/storage/rgbpi
fail=0

echo "=== rgbpi-frontend Lakka smoke test ==="

# 1. Presence of core files
for f in rgbpiui.py rtk.py launcher.py lakka_paths.py lakka_switchres.py \
         lakka_optional_deps.py config.ini; do
    if [ ! -f "$DEST/$f" ]; then
        echo "  [FAIL] missing $DEST/$f"
        fail=$((fail+1))
    fi
done
[ "$fail" -eq 0 ] && echo "  [ok] core files present"

# 2. Writable dirs
for d in data logs temp themes fonts; do
    if ! touch "$DEST/$d/.probe" 2>/dev/null; then
        echo "  [FAIL] $DEST/$d not writable"
        fail=$((fail+1))
    else
        rm -f "$DEST/$d/.probe"
    fi
done

# 3. Python3 + bundled libs
if ! command -v python3 >/dev/null 2>&1; then
    echo "  [FAIL] python3 not installed"
    fail=$((fail+1))
else
    PY_VER=$(python3 -c 'import sys; print("%d.%d"%sys.version_info[:2])')
    echo "  [ok] python3 = $PY_VER"
fi

# 4. Import smoke test (actually load modules)
export PYTHONPATH="$DEST:$DEST/python-libs"
export SDL_VIDEODRIVER=dummy
export SDL_FBDEV=/dev/fb0
python3 - <<'PY' 2>&1
import sys, os
sys.path.insert(0, '/storage/rgbpi')
sys.path.insert(0, '/storage/rgbpi/python-libs')
os.chdir('/storage/rgbpi')

ok = True
for mod in ('lakka_optional_deps', 'lakka_paths', 'lakka_switchres',
            'pygame', 'PIL.Image'):
    try:
        __import__(mod)
        print('  [ok] import', mod)
    except Exception as e:
        print('  [FAIL] import', mod, '->', e)
        ok = False

try:
    import rtk
    print('  [ok] rtk loaded; path_rgbpi =', rtk.path_rgbpi)
    print('       cfg_crt_type =', getattr(rtk, 'cfg_crt_type', '(missing)'))
    print('       cfg_dynares  =', getattr(rtk, 'cfg_dynares',  '(missing)'))
except Exception as e:
    import traceback
    traceback.print_exc()
    ok = False

sys.exit(0 if ok else 1)
PY
rc=$?
[ $rc -ne 0 ] && fail=$((fail+1))

# 5. DRM framebuffer accessible
if [ ! -w /dev/fb0 ]; then
    echo "  [FAIL] /dev/fb0 not writable"
    fail=$((fail+1))
else
    echo "  [ok] /dev/fb0 writable"
fi

# 6. RetroArch binary
if [ -x /usr/bin/retroarch ]; then
    echo "  [ok] retroarch binary"
else
    echo "  [FAIL] /usr/bin/retroarch missing"
    fail=$((fail+1))
fi

echo "=== $fail failures ==="
exit $fail
