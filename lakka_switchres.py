# Dynares -> Lakka CRT switchres translation layer
# Replaces RGB-Pi OS's custom `dynares_*` RetroArch keys with stock
# `crt_switch_*` keys that vanilla RA + switchres.ini understand.
#
# dynares semantics  ->  stock RA equivalent
# ----------------------------------------------------------------------
# dynares_mode=custom     video_aspect_ratio_index=23 + custom viewport
# dynares_mode=native     crt_switch_resolution=1  (native per-game)
# dynares_mode=superx     crt_switch_resolution=3  (3840 super)
# dynares_crt_type=X      switchres.ini crt_range0 (written by frontend)
# dynares_overscan=N      crt_switch_porch_adjust=-N (negative crops)
# dynares_flicker_reduc   video_black_frame_insertion=1
# dynares_video_info=X    video_fps_show=X + video_statistics_show=X
# dynares_handheld_full   custom viewport stretch to full when handheld

# CRT type -> switchres.ini crt_range values
# (hfreq_min-max, vfreq_min-max, hfp, hsync, hbp, vfp_lo, vsync, vbp_lo, hfp_hi, vfp_hi, line_min, line_240, line_480, line_576)
CRT_RANGES = {
    'generic_15': '15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 448, 576',
    'ntsc_15':    '15734-15734, 59.94-59.94, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 240, 480,   0',
    'pal_15':     '15625-15625, 50.00-50.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288,   0, 576',
    'arcade_15':  '15625-15750, 49.50-65.00, 3.900, 4.700, 6.100, 0.064, 0.192, 1.024, 0, 0, 192, 288, 448, 576',
    'arcade_25':  '24960-25080, 49.50-65.00, 1.000, 3.500, 2.000, 0.064, 0.192, 1.024, 0, 0, 384, 400, 512, 0',
    'arcade_31':  '31400-31600, 49.50-65.00, 0.940, 3.770, 1.890, 0.349, 0.064, 1.017, 0, 0, 400, 480, 600, 0',
    'vga_31':     '31400-31600, 49.50-65.00, 0.940, 3.770, 1.890, 0.349, 0.064, 1.017, 0, 0, 400, 480, 600, 0',
}

SUPER_WIDTH = {
    'native':     '0',       # 0 = native per-game, no super
    'superx':     '3840',    # 3840 superres horizontal
    'super2x':    '2560',
    'super4x':    '3840',
}

def write_switchres_ini(path, crt_type='generic_15', super_width='3840'):
    """Emit stock switchres.ini consumed by RA when crt_switch_resolution>=1"""
    with open(path, 'w') as f:
        f.write('monitor   custom\n')
        f.write('crt_range0  ' + CRT_RANGES.get(crt_type, CRT_RANGES['generic_15']) + '\n')

def apply_crt_settings(config, cfg_crt_type, cfg_dynares, cfg_overscan,
                       cfg_video_info, cfg_flicker_reduction):
    """Append stock RA CRT switchres keys to config list (drop-in replacement
    for the RGB-Pi dynares_* block in launcher.make_common)."""
    super_w = SUPER_WIDTH.get(cfg_dynares, '3840')
    # CRT switchres
    config.append('crt_switch_resolution = "1"\n')               # 1 = native, frontend sets super
    config.append('crt_switch_resolution_super = "%s"\n' % super_w)
    config.append('crt_switch_hires_menu = "true"\n')
    config.append('crt_switch_center_adjust = "0"\n')
    config.append('crt_switch_vertical_adjust = "0"\n')
    # Overscan (RGB-Pi dynares_overscan=8 => trim 8 lines)
    porch = '-' + str(cfg_overscan) if str(cfg_overscan).isdigit() and int(cfg_overscan) > 0 else '0'
    if cfg_overscan == 'on':
        porch = '-8'
    elif cfg_overscan == 'off':
        porch = '0'
    config.append('crt_switch_porch_adjust = "%s"\n' % porch)
    # Flicker reduction -> BFI
    if cfg_flicker_reduction == 'on':
        config.append('video_black_frame_insertion = "1"\n')
    else:
        config.append('video_black_frame_insertion = "0"\n')
    # Video info overlay
    if cfg_video_info == 'on':
        config.append('video_fps_show = "true"\n')
        config.append('video_statistics_show = "true"\n')
    else:
        config.append('video_fps_show = "false"\n')
        config.append('video_statistics_show = "false"\n')

def apply_dynares_mode(config, dynares_mode):
    """Replace dynares_mode= with stock aspect/viewport keys."""
    if dynares_mode == 'superx':
        config.append('aspect_ratio_index = "21"\n')      # full
        config.append('video_scale_integer = "false"\n')
    elif dynares_mode == 'native':
        config.append('aspect_ratio_index = "21"\n')      # core-provided
        config.append('video_scale_integer = "true"\n')
    elif dynares_mode == 'custom':
        config.append('aspect_ratio_index = "23"\n')      # custom viewport
        config.append('video_scale_integer = "false"\n')
