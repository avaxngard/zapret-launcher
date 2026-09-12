# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

def get_theme(theme_name='Default'):
    themes = {
        'Default': {
            'accent': '#6c5579',
            'accent_hover': '#e8ccf7',
            'accent_green': '#4ade80',
            'accent_darkgreen': '#348f55',
            'accent_red': '#EF4444',
            
            'bg_dark': '#0F0F12',
            'bg_medium': '#1A1A1F',
            'bg_light': '#25252B',
            'bg_light_hover': '#3a3a44',
            
            'text_primary': '#FFFFFF',
            'text_secondary': '#A1A1AA',
            
            'button_bg': '#2D2D35',
            'button_hover': '#3D3D45',
            
            'separator': "#2D2D35",
        },
        'Pink': {
            'accent': "#D4438C",
            'accent_hover': "#DD72A9",
            'accent_green': '#4ade80',
            'accent_darkgreen': '#348f55',
            'accent_red': '#EF4444',
            
            'bg_dark': '#1E1B2E',
            'bg_medium': '#2D2A3F',
            'bg_light': '#3D3A55',
            'bg_light_hover': '#4D4A6B',
            
            'text_primary': '#FFFFFF',
            'text_secondary': "#B0B0C9",
            
            'button_bg': '#4D4A6B',
            'button_hover': '#5D5A7B',
            
            'separator': "#46435A",
        },
        'Old': {
            'accent': "#3B82F6",
            'accent_hover': "#60A5FA",
            'accent_green': '#4ade80',
            'accent_darkgreen': '#348f55',
            'accent_red': '#EF4444',
            
            'bg_dark': '#0F172A',
            'bg_medium': '#1E293B',
            'bg_light': '#334155',
            'bg_light_hover': '#475569',
            
            'text_primary': '#FFFFFF',
            'text_secondary': "#94A3B8",
            
            'button_bg': '#475569',
            'button_hover': '#64748B',
            
            'separator': "#3E4C63",
        }
    }
    return themes.get(theme_name, themes['Default'])

def get_theme_names():
    return ['Default', 'Pink']#, 'Old']
