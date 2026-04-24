# FAT-only Windows provisioner for Lakka-CRT-RetroTINK.
# Lakka's fs-resize auto-executes /flash/firstboot.sh on first boot, so
# everything we need to seed lives on the FAT partition only - no need for
# ext4 access from Windows.
#
# Usage:
#   .\apply-windows.ps1 -Preset 240p-ntsc -Flash E:
#
# Presets (preset/*.txt):
#   240p-ntsc          - 2560x240 @ 52.33 MHz
#   240p-ntsc-superx   - 3840x240 @ 81   MHz  (recommended for HAT glitch mask)
#   240p-pal           - 2560x288 @ 43.75 MHz
#   480i-ntsc          - 3840x480i @ 81 MHz
#   480i-pal           - 3840x576i @ 81 MHz
param(
    [string]$Preset  = "240p-ntsc-superx",
    [Parameter(Mandatory)][string]$Flash
)

$ErrorActionPreference = "Stop"
$src = Split-Path -Parent $MyInvocation.MyCommand.Definition

$presetFile = Join-Path $src "presets/$Preset.txt"
if (!(Test-Path $presetFile)) { throw "Unknown preset '$Preset'" }
if (!(Test-Path $Flash))       { throw "Flash path '$Flash' not found"   }

Write-Host "[apply] preset=$Preset  flash=$Flash"
Copy-Item (Join-Path $src "flash/config.txt")   (Join-Path $Flash "config.txt")   -Force
Copy-Item (Join-Path $src "flash/firstboot.sh") (Join-Path $Flash "firstboot.sh") -Force
# Only overwrite wifi.conf if target doesn't exist (preserve user's SSID/PSK edits)
if (!(Test-Path (Join-Path $Flash "wifi.conf"))) {
    Copy-Item (Join-Path $src "flash/wifi.conf") (Join-Path $Flash "wifi.conf") -Force
}
# Clear sentinel so firstboot runs again
Remove-Item (Join-Path $Flash ".first-run-done") -ErrorAction SilentlyContinue

# Inject preset into distroconfig.txt between CRT-DPI-BEGIN / END markers
$dc = Get-Content (Join-Path $src "flash/distroconfig.txt") -Raw
$block = Get-Content $presetFile -Raw
$dc = [regex]::Replace(
    $dc,
    '(?s)(-------- CRT-DPI-BEGIN --------\r?\n)(.*?)(# -------- CRT-DPI-END --------)',
    "`$1${block}`$3")
[IO.File]::WriteAllText((Join-Path $Flash "distroconfig.txt"), $dc)

Write-Host "[apply] done."
Write-Host "[apply] Eject SD, boot Pi5. On first boot Lakka runs /flash/firstboot.sh:"
Write-Host "          - enables sshd (SSHD_START=true)"
Write-Host "          - writes switchres.ini + RA CRT keys + per-core overrides"
Write-Host "        After reboot: ssh root@<pi-ip>  (pwd: root - change it!)"
