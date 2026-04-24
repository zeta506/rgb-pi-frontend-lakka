# RGB-Pi Frontend — Lakka Port

Fork of [rtomasa/rgb-pi-frontend](https://github.com/rtomasa/rgb-pi-frontend)
adapted to run on **Lakka** (LibreELEC base) instead of RGB-Pi OS.

## Motivation

RGB-Pi OS ships a patched RetroArch with custom `dynares_*` keys handling
dynamic CRT resolution switching. Those patches are not public yet. Lakka's
stock RetroArch does have the same functionality behind different key names
(`crt_switch_resolution*`) plus `switchres.ini`.

This port translates all dynares semantics to stock keys so the frontend
works on unmodified Lakka.

## Architecture changes vs upstream

| Upstream (RGB-Pi OS)           | Lakka port                                                 |
|--------------------------------|------------------------------------------------------------|
| `/opt/rgbpi/ui` install dir    | `/storage/rgbpi`                                           |
| `/media/sd` roms root          | `/storage/roms`                                            |
| `FBpyGIF` native lib           | Pure PIL + /dev/fb0 ioctl (`framebuffer_write.py` rewritten)|
| `dynares_crt_type`             | `switchres.ini crt_range0`                                 |
| `dynares_mode=native`          | `crt_switch_resolution=1`, `..._super=0`                   |
| `dynares_mode=superx`          | `crt_switch_resolution=1`, `..._super=3840`                |
| `dynares_mode=custom`          | `aspect_ratio_index=23` + custom viewport                  |
| `dynares_overscan=8`           | `crt_switch_porch_adjust=-8`                               |
| `dynares_flicker_reduction`    | `video_black_frame_insertion=1`                            |
| `dynares_video_info`           | `video_fps_show` + `video_statistics_show`                 |
| `dynares_handheld_full`        | Dropped (no stock equivalent)                              |
| `retroarch.service` (stock)    | `rgbpi-frontend.service` (conflict with retroarch)         |

## Files added

- `lakka_paths.py` — injects `path_*` constants into `rtk` namespace.
- `lakka_switchres.py` — dynares→switchres translation helpers.
- `lakka/rgbpi-frontend.service` — systemd unit replacing `retroarch.service`.
- `lakka/install.sh` — idempotent deploy to /storage.
- `lakka/uninstall.sh` — revert to stock Lakka menu.

## Files modified

- `rtk.py` — `from lakka_paths import *; ensure_dirs()` at top.
- `launcher.py` — all `dynares_*` writes replaced with stock `crt_switch_*` +
  `switchres.ini` emitted per-game; `framebuffer_write.py` rewritten without
  FBpyGIF dep.

## Install on Lakka target

```sh
# From development host (this repo):
scp -r lakka-port root@LAKKA_IP:/tmp/rgbpi-src
ssh root@LAKKA_IP 'sh /tmp/rgbpi-src/lakka/install.sh'
ssh root@LAKKA_IP reboot
```

Prerequisites on Lakka:
- Python3 (install via LibreELEC addon if missing)
- Writable `/storage`
- `dtparam=interlaced` + DPI timings already configured in `/flash/config.txt`
- HAT: RetroTINK Ultimate / VGA666 / VGA888 connected
- CRT 15kHz via component/RGBS/VGA

## Uninstall

```sh
ssh root@LAKKA_IP 'sh /tmp/rgbpi-src/lakka/uninstall.sh'
```

## Known limitations

- dynares flicker-reduction uses generic BFI, not RGB-Pi's field-blending.
- Some frontend menu items tied to RGB-Pi HW (`native_csync`, JAMMA probe)
  remain visible but no-op; clean in `sys_opt_display_view.py` as TODO.
- OTA update (`gen_update.py`) still points to RGB-Pi servers; disable via
  menu or patch `rtk.cfg_update = off`.

## TODO

- [ ] Lakka-specific theme (XMB-like) so the UI feels native.
- [ ] Hook `rtk.cfg_dynares=native` + per-game modeline to match Lakka's
      switchres dynamic mode creation (requires RA 1.20+, verify support).
- [ ] Ship pygame/Pillow wheels under `install/wheels/` so `install.sh`
      works offline.
- [ ] Audit all `rtk.path_*` references for remaining absolute paths
      (currently 27 resolved; JAMMA/NFS paths may still be stale).
