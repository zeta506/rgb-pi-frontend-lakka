#!/usr/bin/env python3
"""Lakka-port: pull RGB-Pi-style scraper images from libretro-thumbnails.

RGB-Pi OS distributes a proprietary scraper image pack via OTA. We don't
have access to that server, so this script fetches the equivalent media
from the public libretro-thumbnails GitHub repo and renames the files into
RGB-Pi's expected layout:

    /storage/rgbpi/data/scraper/images/<id>_<system>_<type>_<region>.png

`type`   : ingame | title | box
`region` : usa | eur | jap

Usage (run on the Pi, needs internet):
    python3 /tmp/rgbpi-src/lakka/scrap-libretro-thumbs.py

Throttled (1 request / 0.2 s) so GitHub rate-limit stays happy.
"""

from __future__ import annotations

import csv
import os
import re
import sys
import time
import urllib.parse
import urllib.request

GAMES_DAT = '/storage/roms/dats/games.dat'
SCRAPER_DAT = '/storage/rgbpi/data/scraper/scraper.dat'
OUT_DIR = '/storage/rgbpi/data/scraper/images'

# RGB-Pi system slug -> libretro-thumbnails repo name. Arcade is intentionally
# omitted: MAME zip names (e.g. tekken3ja.zip) almost never match the
# libretro-thumbnails Named_* filenames (e.g. "Tekken 3 (Asia, TET2 Ver. A)").
# Stick to console / handheld systems where the rom file stem matches.
LIBRETRO_REPO = {
    'atari2600': 'Atari_-_2600',
    'atari7800': 'Atari_-_7800',
    'pcengine': 'NEC_-_PC_Engine_-_TurboGrafx_16',
    'pcenginecd': 'NEC_-_PC_Engine_CD_-_TurboGrafx-CD',
    'nes': 'Nintendo_-_Nintendo_Entertainment_System',
    'snes': 'Nintendo_-_Super_Nintendo_Entertainment_System',
    'n64': 'Nintendo_-_Nintendo_64',
    'sgb': 'Nintendo_-_Super_Game_Boy',
    'gba': 'Nintendo_-_Game_Boy_Advance',
    'sg1000': 'Sega_-_SG-1000',
    'mastersystem': 'Sega_-_Master_System_-_Mark_III',
    'megadrive': 'Sega_-_Mega_Drive_-_Genesis',
    'segacd': 'Sega_-_Mega-CD_-_Sega_CD',
    'sega32x': 'Sega_-_32X',
    'dreamcast': 'Sega_-_Dreamcast',
    'neogeo': 'SNK_-_Neo_Geo',
    'neocd': 'SNK_-_Neo_Geo_CD',
    'ngp': 'SNK_-_Neo_Geo_Pocket_Color',
    'psx': 'Sony_-_PlayStation',
}

REPO_BASE = 'https://raw.githubusercontent.com/libretro-thumbnails/{repo}/master/{kind}/{name}.png'
KIND_MAP = {
    'ingame': 'Named_Snaps',
    'title':  'Named_Titles',
    'box':    'Named_Boxarts',
}
THROTTLE_S = 0.2


def detect_region(filename: str) -> str:
    f = filename.lower()
    if 'usa' in f or '(u)' in f or '(us)' in f:
        return 'usa'
    if 'europe' in f or '(e)' in f or '(eur)' in f:
        return 'eur'
    if 'japan' in f or '(j)' in f or '(jap)' in f:
        return 'jap'
    return 'usa'


def fetch(url: str, dst: str) -> bool:
    if os.path.exists(dst):
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'rgbpi-lakka/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if not data:
            return False
        with open(dst, 'wb') as fh:
            fh.write(data)
        return True
    except Exception:
        return False


def main() -> int:
    if not os.path.isfile(GAMES_DAT):
        print('games.dat missing — run Settings -> Scan ROMs first', file=sys.stderr)
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)

    fetched = skipped = failed = 0
    with open(GAMES_DAT, encoding='utf-8') as fh:
        reader = csv.DictReader(fh, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            gid = row.get('Id', '').strip()
            system = row.get('System', '').strip()
            filename = os.path.basename(row.get('File', ''))
            if not gid or not system or not filename:
                continue
            repo = LIBRETRO_REPO.get(system)
            if not repo:
                continue
            stem = re.sub(r'\.(zip|7z|bin|gen|md|smd|sfc|smc|nes|fds|iso|cue|chd|gba|gb|gbc|sms|gg|32x|neo|pce|sgx|a26|a78)$',
                          '', filename, flags=re.IGNORECASE)
            region = detect_region(filename)
            for kind, dirname in KIND_MAP.items():
                dst = os.path.join(OUT_DIR, f'{gid}_{system}_{kind}_{region}.png')
                if os.path.exists(dst):
                    skipped += 1
                    continue
                url = REPO_BASE.format(
                    repo=repo,
                    kind=dirname,
                    name=urllib.parse.quote(stem))
                if fetch(url, dst):
                    fetched += 1
                    print(f'+ {os.path.basename(dst)}', flush=True)
                else:
                    failed += 1
                    if failed % 50 == 0:
                        print(f'... {failed} misses, last: {stem[:60]} ({system}/{kind})',
                              flush=True)
                time.sleep(THROTTLE_S)

    print(f'\nDone. fetched={fetched} skipped={skipped} failed={failed}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
