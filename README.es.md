# rgb-pi-frontend-lakka

> [English](README.md) · **Español**

Port de [rtomasa/rgb-pi-frontend](https://github.com/rtomasa/rgb-pi-frontend) a **Lakka** (base LibreELEC) para **Raspberry Pi 5 + RetroTINK Ultimate** sobre **CRT 15 kHz**.

El frontend original viene con RGB-Pi OS y depende de un RetroArch con parches `dynares_*` que aún no se publicaron. Este fork reemplaza cada `dynares_*` por las keys estándar `crt_switch_*` + un `switchres.ini`, así la UI corre sobre **Lakka RetroArch sin modificar** con super-resolución CRT completa.

## Estructura del repositorio

```
lakka-port/                       # Frontend (Python) corriendo sobre Lakka
├── lakka_paths.py                #   inyección de paths /storage/rgbpi/* en rtk
├── lakka_optional_deps.py        #   stubs de libs nativas faltantes (smbus, dbus, evdev…)
├── lakka_switchres.py            #   traductor dynares_* → crt_switch_*
├── lakka_fbdisplay.py            #   espejo pygame Surface → /dev/fb0
├── framebuffer_write.py          #   reemplazo PIL/ioctl puro de FBpyGIF
├── rtk.py / rgbpiui.py / …       #   fuentes upstream parchadas
├── lakka/
│   ├── rgbpi-frontend.service    #   unidad systemd (Conflicts=retroarch.service)
│   ├── install.sh / uninstall.sh
│   ├── smoke-test.sh             #   self-check post-instalación
│   └── wheels/                   #   wheels aarch64 pygame + Pillow (offline)
└── lakka-image/                  # Overlay SD primer-arranque (solo FAT)
    ├── flash/                    #   copiado a la partición /flash
    │   ├── config.txt + distroconfig.txt
    │   ├── firstboot.sh          #   auto-ejecutado por fs-resize de Lakka
    │   ├── wifi-config.txt       #   plantilla SSID/PSK (placeholders)
    │   └── retrotink/            #   fuente SuperResolucion, core-options, setup.sh
    ├── presets/                  #   240p-ntsc-superx (default), 480i-ntsc, …
    └── apply-windows.ps1 / apply.sh
```

## Hardware probado

| Componente | Notas |
|-----------|-------|
| Raspberry Pi 5 (8 GB) | Kernel 6.12.66/6.12.77, interlace vía RP1 PIO |
| RetroTINK Ultimate HAT | DPI RGB888 24-bit → componente YPbPr al CRT |
| Sony Trinitron Wega CRT | 15 kHz NTSC + interlace 480i para arcade |
| DAC USB C-Media | Card 1 cuando `nohdmi` quita vc4-hdmi |
| Mando USB DragonRise | Detectado vía sysfs (evdev no requerido) |

## Inicio rápido

### 1. Flashear Lakka nightly

```
https://nightly.builds.lakka.tv/latest/RPi5.aarch64/Lakka-RPi5.aarch64-6.1-*.img.gz
```

Usar Raspberry Pi Imager o balenaEtcher.

### 2. Provisionar la SD (Windows)

```powershell
cd lakka-image
.\apply-windows.ps1 -Preset 240p-ntsc-superx -Flash F:
notepad F:\wifi-config.txt   # poner SSID + PSK
```

`apply-windows.ps1` es FAT-only — `fs-resize` de Lakka ejecuta
`/flash/firstboot.sh` en el primer arranque, que prepara:

- SSH (`/storage/.cache/services/sshd.conf SSHD_START=true`)
- Wi-Fi vía ConnMan (`/storage/.cache/connman/wifi.config`)
- `switchres.ini` con el rango CRT 15 kHz
- Keys CRT de RetroArch + menú RGUI a 240p
- Overrides de viewport para MAME / MAME 2003-Plus / Flycast
- DAC USB autodetectado como `audio_device`
- Fuente SuperResolucion + core options (overscan OFF)

### 3. Bootear el Pi5

`firstboot.sh` corre una sola vez y reboot. Lakka arranca con todo
configurado. El XMB nativo de Lakka sigue apareciendo — el frontend
RGB-Pi **no** se lanza solo (así nunca se rompe el arranque si la FE falla).

### 4. Instalar el frontend (opcional)

```
ssh root@<pi-ip>           # contraseña: root  (CAMBIALA)
mkdir -p /tmp/rgbpi-src
scp -r lakka-port/* root@<pi-ip>:/tmp/rgbpi-src/
ssh root@<pi-ip> 'sh /tmp/rgbpi-src/lakka/install.sh'
ssh root@<pi-ip> 'systemctl stop retroarch; systemctl start rgbpi-frontend'
```

Setear `RGBPI_ENABLE_SERVICE=1` antes de `install.sh` para que la FE
arranque sola en cada boot. Por defecto `retroarch.service` queda
activo → un `reboot` siempre te devuelve a Lakka stock si la FE rompe.

## Por qué existe este port

- RGB-Pi OS trae un fork de RetroArch con keys `dynares_*` que manejan
  el cambio de modo CRT por juego. Esos parches no son públicos.
- El RetroArch nativo de Lakka ya tiene la misma capacidad detrás del
  API documentado `crt_switch_resolution`/`switchres.ini`.
- El frontend Python sí es open source. Traduciendo las keys → corre en
  Lakka sin modificar.
- El overlay `nohdmi` de Lakka + super-resolución 3840×240 (pixel clock
  81 MHz) difumina los desajustes del DAC en la etapa VGA888 del
  RetroTINK Ultimate y enmascara los puntos verdes/azules que aparecen
  con clocks más bajos.

## Lo que NO se autoconfigura

- Emparejar controles (entrar al XMB → Settings → Input la primera vez).
- Audio Bluetooth (preferimos DAC USB).
- 480i superx (preset por defecto es 240p; cambiar con otro archivo de preset).
- ROMs / BIOS / scraper — copiar a `/storage/roms` por SSH o USB.

## Desarrollo

La carpeta es un repositorio Git autocontenido. Las dos mitades
(`lakka-port/` y `lakka-image/`) son independientes — podés instalar
solo el overlay de SD y quedarte con el XMB nativo si no querés todavía
el frontend Python.

## Licencia

GPLv3, heredada del rgb-pi-frontend upstream. RGB-Pi OS es © Rubén Tomás
(rtomasa); este port es © 2026 Pablo Bridge.
