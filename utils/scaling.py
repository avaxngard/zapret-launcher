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

def get_scale_factor():
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        
        base_dpi = 96
        scale = dpi_x / base_dpi
        scale = max(0.8, min(2.0, scale))
        return scale
    except Exception:
        return 1.0

def get_optimal_scale():
    try:
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        base_width = 1920
        base_height = 1080
        
        scale_w = screen_width / base_width
        scale_h = screen_height / base_height
        scale = min(scale_w, scale_h)
        scale = max(0.8, min(1.5, scale))
        
        if screen_width >= 3840 and screen_height >= 2160:
            scale = 1.25
        elif screen_width >= 2560 and screen_height >= 1440:
            scale = 1.0
        elif screen_width <= 1920 and screen_height <= 1080:
            scale = 1.0
        
        return scale
    except Exception:
        return 1.0

def scale_size(size, scale_factor):
    return int(size * scale_factor)

def scale_value(value, scale_factor):
    return int(round(value * scale_factor))