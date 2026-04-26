# rgb-pi-frontend-lakka

> **English** · [Español](README.es.md)

Port of [rtomasa/rgb-pi-frontend](https://github.com/rtomasa/rgb-pi-frontend) to **Lakka** (LibreELEC base) for **Raspberry Pi 5 + RetroTINK Ultimate** on a **15 kHz CRT**.

The upstream frontend ships with RGB-Pi OS and depends on a custom `dynares_*` patched RetroArch that has not been released. This fork swaps every `dynares_*` write for stock `crt_switch_*` keys + a `switchres.ini` so the UI runs on **vanilla Lakka RetroArch** with full CRT super-resolution.

## Repository layout

```
lakka-port/                       # Frontend (Python) running on top of Lakka
├── lakka_paths.py                #   /storage/rgbpi/* path injection into rtk
├── lakka_optional_deps.py        #   stubs for missing native libs (smbus, dbus, evdev…)
├── lakka_switchres.py            #   dynares_* → crt_switch_* translator
├── lakka_fbdisplay.py            #   pygame Surface → /dev/fb0 mirroring
├── framebuffer_write.py          #   pure PIL/ioctl replacement for FBpyGIF
├── rtk.py / rgbpiui.py / …       #   patched upstream sources
├── lakka/
│   ├── rgbpi-frontend.service    #   systemd unit (Conflicts=retroarch.service)
│   ├── install.sh / uninstall.sh
│   ├── smoke-test.sh             #   post-install self-check
│   └── wheels/                   #   pygame + Pillow aarch64 wheels (offline)
└── lakka-image/                  # First-boot SD overlay (FAT-only)
    ├── flash/                    #   copied to /flash partition
    │   ├── config.txt + distroconfig.txt
    │   ├── firstboot.sh          #   auto-run by Lakka fs-resize on first boot
    │   ├── wifi-config.txt       #   SSID/PSK template (placeholders)
    │   └── retrotink/            #   SuperResolucion font, core-options, setup.sh
    ├── presets/                  #   240p-ntsc-superx (default), 480i-ntsc, …
    └── apply-windows.ps1 / apply.sh
```

## Hardware tested

| Component | Notes |
|-----------|-------|
| Raspberry Pi 5 (8 GB) | Kernel 6.12.66/6.12.77, interlace via RP1 PIO |
| RetroTINK Ultimate HAT | RGB888 24-bit DPI → component YPbPr to CRT |
| 15 kHz CRT | NTSC 240p + 480i superres |
| C-Media USB DAC | Card 1 once `nohdmi` removes vc4-hdmi |
| USB gamepad | Detected via sysfs (evdev not required) |

## Quick start

### 1. Flash Lakka nightly

```
https://nightly.builds.lakka.tv/latest/RPi5.aarch64/Lakka-RPi5.aarch64-6.1-*.img.gz
```

Use Raspberry Pi Imager or balenaEtcher.

### 2. Provision the SD (Windows)

```powershell
cd lakka-image
.\apply-windows.ps1 -Preset 240p-ntsc-superx -Flash F:
notepad F:\wifi-config.txt   # set SSID + PSK
```

`apply-windows.ps1` is FAT-only — Lakka's `fs-resize` runs `/flash/firstboot.sh`
on first boot, which seeds:

- SSH (`/storage/.cache/services/sshd.conf SSHD_START=true`)
- Wi-Fi via ConnMan (`/storage/.cache/connman/wifi.config`)
- `switchres.ini` for 15 kHz CRT range
- RetroArch CRT keys + RGUI menu @ 240p
- MAME / MAME 2003-Plus / Flycast viewport overrides
- Auto-detected USB DAC as `audio_device`
- SuperResolucion font + RetroPie core options (overscan OFF)

### 3. Boot the Pi5

`firstboot.sh` runs once, then the Pi reboots into Lakka with everything
configured. Stock Lakka XMB still appears on screen — RGB-Pi frontend is
**not** auto-launched (so a broken FE never locks you out).

### 4. Install the frontend (optional)

```
ssh root@<pi-ip>           # password: root  (CHANGE IT)
mkdir -p /tmp/rgbpi-src
scp -r lakka-port/* root@<pi-ip>:/tmp/rgbpi-src/
ssh root@<pi-ip> 'sh /tmp/rgbpi-src/lakka/install.sh'
ssh root@<pi-ip> 'systemctl stop retroarch; systemctl start rgbpi-frontend'
```

Set `RGBPI_ENABLE_SERVICE=1` before `install.sh` to make the frontend
launch automatically on every boot.  By default `retroarch.service` stays
enabled, so a `reboot` is the recovery path if anything in the FE breaks.

The frontend's **Shutdown** menu also has a `Return to Lakka` entry.
Picking it drops the FE, re-enables `retroarch.service`, and starts XMB —
no reboot required, no SD edits.  Sentinel: `/storage/.cache/rgbpi-return-to-lakka`.

## Recent changes (post-checkpoint)

- **SNES core** swapped to `bsnes-jg` (more accurate than `snes9x`).
- **NeoGeo `.neo`** files routed to `geolith_libretro`; everything else
  still uses `fbneo`.
- **scan_games** searches both `/storage/roms/<system>` AND
  `/storage/roms/roms/<system>` so it works whether you keep Lakka's
  flat layout or RGB-Pi's nested one.
- **mount_usb** reuses the udisks auto-mount (`/storage/roms/sdaN-usb-LABEL`)
  instead of forcing the disk into `/var/media`.
- **Standalone scanner** at `lakka/scan-lakka-roms.py` so you can
  populate `games.dat` from a shell without booting the FE.
- **Lakka return** menu entry + ExecStopPost service hook.
- **`crt_switch_hires_menu = false`** in the launcher template so the
  RetroArch RGUI menu stays at the CRT-friendly 240p when launched.

## Why this port exists

- RGB-Pi OS bundles a fork of RetroArch with `dynares_*` keys that handle
  per-game CRT mode switching. Those patches are not public.
- Stock Lakka RetroArch already has the same capability behind the
  documented `crt_switch_resolution`/`switchres.ini` API.
- The Python frontend itself is open source. Translate the keys → it runs
  on plain Lakka.
- Lakka's `nohdmi` overlay + 3840×240 super-resolution (81 MHz pixel clock)
  smears DAC mismatches in the RetroTINK Ultimate VGA888 stage, masking
  the green/blue speckle you see at lower clocks.

## What is NOT auto-configured

- Pairing controllers (use Lakka XMB → Settings → Input first).
- Bluetooth audio (USB DAC is preferred).
- 480i superx (default preset is 240p; switch with another preset file).
- ROMs / BIOS / scraper data — copy to `/storage/roms` over SSH or USB.

## Development

The folder is a self-contained Git repository. The two halves (`lakka-port/`
and `lakka-image/`) are independent — you can install only the SD overlay
and keep stock XMB if you don't want the Python frontend yet.

## License

GPLv3, inherited from upstream rgb-pi-frontend. RGB-Pi OS itself is © Rubén
Tomás (rtomasa); this port is © 2026 Pablo Puente.
