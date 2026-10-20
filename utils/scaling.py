# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import ctypes

def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass

def get_dpi_scale():
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        if dpi_x <= 0:
            return 1.0
        scale = dpi_x / 96.0
        return max(0.75, min(3.0, scale))
    except Exception:
        return 1.0

def get_scale_factor():
    return get_dpi_scale()

def get_optimal_scale():
    dpi_scale = get_dpi_scale()

    try:
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)

        base_w, base_h = 1200, 800
        max_scale_w = (screen_w * 0.92) / base_w
        max_scale_h = (screen_h * 0.92) / base_h
        max_scale = min(max_scale_w, max_scale_h)

        scale = min(dpi_scale, max_scale)

        if screen_w >= 2560 and screen_h >= 1440 and scale < 1.0:
            scale = 1.0

        if screen_w >= 3840 and screen_h >= 2160 and dpi_scale <= 1.0:
            scale = max(scale, 1.25)

        scale = max(0.75, min(2.5, scale))
        return scale
    except Exception:
        return dpi_scale if dpi_scale else 1.0

def scale_size(size, scale_factor):
    return int(size * scale_factor)

def scale_value(value, scale_factor):
    return int(round(value * scale_factor))

def scale_font(size, scale_factor, softness=0.6):
    eff = 1.0 + (scale_factor - 1.0) * softness
    return max(1, int(round(size * eff)))
