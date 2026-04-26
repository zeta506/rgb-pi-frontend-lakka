#!/bin/sh
#############################################
# RetroTINK Ultimate - Setup automatico Pi 5
# Correr despues del primer boot:
#   sh /flash/retrotink/setup.sh
# NO toca configuracion de video/RetroArch
#############################################

echo "=== RetroTINK Ultimate Setup (Pi 5) ==="

# 1. Desactivar HDMI en distroconfig (nohdmi para que RetroArch use DPI)
echo "[1/7] Desactivando HDMI en distroconfig..."
mount -o remount,rw /flash 2>/dev/null
if grep -q 'vc4-kms-v3d,cma' /flash/distroconfig.txt && ! grep -q 'nohdmi' /flash/distroconfig.txt; then
    sed -i 's/dtoverlay=vc4-kms-v3d,cma-/dtoverlay=vc4-kms-v3d,nohdmi,cma-/' /flash/distroconfig.txt
    echo "      OK (nohdmi agregado, requiere reboot)"
else
    echo "      OK (ya configurado)"
fi

# 2. Copiar fuente SuperResolucion
echo "[2/7] Copiando fuente SuperResolucion..."
mkdir -p /storage/fonts
cp /flash/retrotink/SuperResolucion.ttf /storage/fonts/
echo "      OK"

# 3. Activar SSH permanentemente
echo "[3/7] Activando SSH..."
mkdir -p /storage/.cache/services
echo "SSHD_START=true" > /storage/.cache/services/sshd.conf
systemctl start sshd 2>/dev/null
echo "      OK"

# 4. Detectar dispositivo de audio (DAC USB)
echo "[4/7] Detectando audio..."
echo "      Dispositivos encontrados:"
aplay -l 2>/dev/null | grep "^card"

AUDIO_DEV=""
for card in 0 1 2 3; do
    name=$(cat /proc/asound/card${card}/id 2>/dev/null)
    if [ -n "$name" ] && [ "$name" != "vc4hdmi" ] && [ "$name" != "vc4hdmi0" ] && [ "$name" != "vc4hdmi1" ]; then
        AUDIO_DEV="hw:${card},0"
        echo "      DAC detectado: $name en $AUDIO_DEV"
        break
    fi
done

if [ -z "$AUDIO_DEV" ]; then
    AUDIO_DEV="hw:0,0"
    echo "      AVISO: No se detecto DAC USB, usando $AUDIO_DEV"
fi

# 5. Core options - overscan OFF en todos los cores
echo "[5/7] Configurando core options (overscan OFF)..."
CORE_OPTS="/storage/.config/retroarch/retroarch-core-options.cfg"
if [ -f /flash/retrotink/core-options.cfg ]; then
    if [ -f "$CORE_OPTS" ]; then
        while IFS= read -r line; do
            case "$line" in \#*|"") continue ;; esac
            key=$(echo "$line" | cut -d'=' -f1 | tr -d ' ')
            if ! grep -q "^${key} " "$CORE_OPTS" 2>/dev/null; then
                echo "$line" >> "$CORE_OPTS"
            else
                sed -i "s|^${key} = .*|${line}|" "$CORE_OPTS"
            fi
        done < /flash/retrotink/core-options.cfg
    else
        cp /flash/retrotink/core-options.cfg "$CORE_OPTS"
    fi
    echo "      OK"
else
    echo "      AVISO: No se encontro core-options.cfg"
fi

# 6. Overrides por core para 480i (aspect_ratio_index=22 + viewport correcto)
echo "[6/7] Creando overrides para 480i (MAME, MAME 2003-Plus, Flycast)..."

mkdir -p /storage/.config/retroarch/config/MAME
cat > /storage/.config/retroarch/config/MAME/MAME.cfg << 'EOF'
aspect_ratio_index = "22"
custom_viewport_width = "1920"
custom_viewport_height = "480"
custom_viewport_x = "160"
custom_viewport_y = "0"
EOF

mkdir -p "/storage/.config/retroarch/config/MAME 2003-Plus"
cat > "/storage/.config/retroarch/config/MAME 2003-Plus/MAME 2003-Plus.cfg" << 'EOF'
aspect_ratio_index = "22"
custom_viewport_width = "1920"
custom_viewport_height = "480"
custom_viewport_x = "160"
custom_viewport_y = "0"
EOF

mkdir -p /storage/.config/retroarch/config/Flycast
cat > /storage/.config/retroarch/config/Flycast/Flycast.cfg << 'EOF'
aspect_ratio_index = "22"
custom_viewport_width = "1920"
custom_viewport_height = "480"
custom_viewport_x = "320"
custom_viewport_y = "0"
EOF
echo "      OK"

# 7. switchres.ini con porches centrados
echo "[7/7] Creando switchres.ini..."
cat > /storage/.config/retroarch/switchres.ini << 'EOF'
monitor   custom
crt_range0  15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 448, 576
EOF
echo "      OK"

# Aplicar audio, fuente y kms_connector
systemctl stop retroarch
sleep 2
CFG="/storage/.config/retroarch/retroarch.cfg"
sed -i "s|audio_device = \".*\"|audio_device = \"${AUDIO_DEV}\"|" "$CFG"
sed -i 's|video_font_path = \".*\"|video_font_path = \"/storage/fonts/SuperResolucion.ttf\"|' "$CFG"
sed -i 's|video_font_size = \".*\"|video_font_size = \"12.000000\"|' "$CFG"

# Forzar DPI como conector KMS
if grep -q "kms_connector" "$CFG"; then
    sed -i 's|kms_connector = \".*\"|kms_connector = \"DPI-1\"|' "$CFG"
else
    echo 'kms_connector = "DPI-1"' >> "$CFG"
fi

systemctl start retroarch

echo ""
echo "=== Setup completado! ==="
echo "Audio: $AUDIO_DEV"
echo "SSH: Activado"
echo "Core options: Overscan OFF"
echo "HDMI: Desactivado (nohdmi)"
echo "KMS: DPI-1"
echo "Fuente: SuperResolucion 8pt"
echo "Overrides 480i: MAME, MAME 2003-Plus, Flycast"
echo "switchres.ini: Porches centrados"
echo ""
echo "IMPORTANTE: Si es la primera vez, reiniciar para aplicar nohdmi:"
echo "  reboot"
