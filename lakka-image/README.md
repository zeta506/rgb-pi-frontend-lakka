# Lakka CRT-RetroTINK preset

Turns a stock Lakka nightly SD card into a CRT-ready image on first boot:

- SSH enabled persistently (root login, warn user to change pwd).
- DPI superres timings for RetroTINK Ultimate + generic 15 kHz CRT.
- switchres.ini written with `crt_range0` for NTSC+PAL.
- RetroArch global tweaks (`crt_switch_resolution=1`, `_super=3840`).
- Per-core overrides for MAME / Flycast / Genesis Plus GX tuned for 15 kHz.
- Optional integration point for [rgb-pi-frontend-lakka](../lakka-port/).

## Layout

```
lakka-image/
├── flash/         # copied verbatim to /flash (FAT) partition of the SD
│   ├── distroconfig.txt        # DPI overlay + nohdmi + KMS
│   ├── config.txt              # boots distroconfig.txt include
│   └── firstboot.sh            # one-shot provisioner (runs before RA)
├── storage/       # copied to /storage (ext4) on first boot via firstboot.sh
│   ├── .cache/services/sshd.conf
│   └── .config/retroarch/
│       ├── retroarch.cfg.d/    # snippets merged into global cfg
│       ├── switchres.ini
│       └── config/<Core>/<Core>.cfg
├── presets/       # interchangeable CRT profiles
│   ├── 240p-ntsc.txt
│   ├── 240p-pal.txt
│   ├── 480i-ntsc.txt
│   └── 480i-pal.txt
└── apply.sh       # runs on dev-host to sync files onto a mounted SD
```

## Apply to an existing Lakka SD

1. Flash Lakka nightly image normally (Pi Imager / balenaEtcher).
2. Plug SD into your dev machine.
3. From this folder: `./apply.sh /path/to/mounted/FLASH_PARTITION /path/to/storage`.
4. Boot the Pi once — `firstboot.sh` runs, SSH comes up, CRT config lands.
5. SSH in: `ssh root@<ip>`. Default password is `root` — change it.

## Choosing a preset

```sh
./apply.sh --preset 240p-ntsc  /mnt/FLASH /mnt/STORAGE
./apply.sh --preset 480i-ntsc  /mnt/FLASH /mnt/STORAGE
```

Preset files live in `presets/`. Each is a drop-in replacement for the DPI
section of `flash/distroconfig.txt`.
