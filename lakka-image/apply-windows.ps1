# Windows PowerShell equivalent of apply.sh for flashing on Windows dev hosts.
# Usage:
#   .\apply-windows.ps1 -Preset 480i-ntsc -Flash E: -Storage F:
param(
    [string]$Preset  = "480i-ntsc",
    [Parameter(Mandatory)][string]$Flash,
    [Parameter(Mandatory)][string]$Storage
)

$ErrorActionPreference = "Stop"
$src = Split-Path -Parent $MyInvocation.MyCommand.Definition

$presetFile = Join-Path $src "presets/$Preset.txt"
if (!(Test-Path $presetFile)) { throw "Unknown preset '$Preset'" }
if (!(Test-Path $Flash))       { throw "Flash path '$Flash' not found"   }
if (!(Test-Path $Storage))     { throw "Storage path '$Storage' not found" }

Write-Host "[apply] preset=$Preset"
Copy-Item (Join-Path $src "flash/config.txt")       (Join-Path $Flash "config.txt")       -Force
Copy-Item (Join-Path $src "flash/firstboot.sh")     (Join-Path $Flash "firstboot.sh")     -Force

# Inject preset into distroconfig.txt between CRT-DPI-BEGIN / END markers
$dc = Get-Content (Join-Path $src "flash/distroconfig.txt") -Raw
$block = Get-Content $presetFile -Raw
$dc = [regex]::Replace(
    $dc,
    '(?s)(-------- CRT-DPI-BEGIN --------\r?\n)(.*?)(# -------- CRT-DPI-END --------)',
    "`$1${block}`$3")
[IO.File]::WriteAllText((Join-Path $Flash "distroconfig.txt"), $dc)

# Copy /storage overlay (FAT can't represent hidden/symlinks — acceptable for our files)
Copy-Item (Join-Path $src "storage") $Storage -Recurse -Force

# Enable firstboot systemd unit
$wants = Join-Path $Storage ".config\system.d\multi-user.target.wants"
New-Item -ItemType Directory -Force -Path $wants | Out-Null
# Systemd reads the unit via the WantedBy=multi-user.target line; wants symlink
# isn't strictly required on first boot since rgbpi-firstboot.service already
# declares [Install]. Copy a stub for redundancy:
Copy-Item (Join-Path $Storage ".config\system.d\rgbpi-firstboot.service") `
          (Join-Path $wants     "rgbpi-firstboot.service") -Force

Write-Host "[apply] done. Eject SD, boot the Pi, ssh root@<ip>."
