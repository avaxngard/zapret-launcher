# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
import threading
import subprocess
import ctypes
import time
from gui.widgets import RoundedButton
from utils.languages import tr
from utils.scaling import scale_size
from config import ZAPRET_CORE_DIR

class ServicePage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_sub = scale_size(14, self.scale_factor)
        btn_width = scale_size(200, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('service_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('service_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)
        
        functions = [
            (tr('service_filters'), [
                (tr('service_game_filter'), "game_filter"),
                (tr('service_ipset_filter'), "ipset_filter"),
            ]),
        ]
        
        for title, items in functions:
            card = tk.Frame(self.frame, bg=self.colors['bg_light'])
            card.pack(fill=tk.X, padx=padx, pady=pady, ipadx=scale_size(20, self.scale_factor), ipady=scale_size(10, self.scale_factor))
            
            tk.Label(card, text=title, font=("Inter", font_size_sub, "bold"),
                    fg=self.colors['text_primary'], bg=self.colors['bg_light']).pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=(scale_size(10, self.scale_factor), 5))
            
            for btn_text, cmd in items:
                btn = RoundedButton(card, text=btn_text, 
                                command=lambda c=cmd: self.app.run_service_command(c),
                                width=btn_width, height=btn_height, bg=self.colors['button_bg'],
                                font=self.font_primary, corner_radius=btn_radius,
                                hover_color=self.colors['accent'], theme_name=self.app.current_theme)
                btn.pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=2)

        card = tk.Frame(self.frame, bg=self.colors['bg_light'])
        card.pack(fill=tk.X, padx=padx, pady=pady, ipadx=scale_size(20, self.scale_factor), ipady=scale_size(10, self.scale_factor))
        
        tk.Label(
            card, 
            text=tr('service_tools'), 
            font=("Inter", font_size_sub, "bold"),
            fg=self.colors['text_primary'], 
            bg=self.colors['bg_light']
        ).pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=(scale_size(10, self.scale_factor), 5))
        
        diag_btn = RoundedButton(
            card,
            text=tr('service_run_diagnostic'),
            command=self.run_diagnostics,
            width=btn_width, height=btn_height,
            bg=self.colors['button_bg'],
            font=self.font_primary,
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        diag_btn.pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=2)
        
        test_btn = RoundedButton(
            card,
            text=tr('service_run_tests'),
            command=self.run_tests,
            width=btn_width, height=btn_height,
            bg=self.colors['button_bg'],
            font=self.font_primary,
            corner_radius=btn_radius,
            hover_color=self.colors['accent'],
            theme_name=self.app.current_theme
        )
        test_btn.pack(anchor='w', padx=scale_size(15, self.scale_factor), pady=2)
        
        self.game_filter_btn = None
        self.ipset_filter_btn = None

    def run_diagnostics(self):
        def run():
            try:
                service_bat = ZAPRET_CORE_DIR / "service.bat"
                subprocess.Popen([str(service_bat)], cwd=str(ZAPRET_CORE_DIR), shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                time.sleep(2)
                
                ctypes.windll.user32.keybd_event(0x36, 0, 0, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x36, 0, 2, 0)
                time.sleep(0.2)
                
                ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)
                
            except Exception as e:
                self.app.log_event("info", f"Diagnostics error: {e}")
        
        threading.Thread(target=run, daemon=True).start()

    def run_tests(self):
        def run():
            try:
                service_bat = ZAPRET_CORE_DIR / "service.bat"
                subprocess.Popen([str(service_bat)], cwd=str(ZAPRET_CORE_DIR), shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                time.sleep(2)
                
                ctypes.windll.user32.keybd_event(0x37, 0, 0, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x37, 0, 2, 0)
                time.sleep(0.2)
                
                ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)
                
            except Exception as e:
                self.app.log_event("info", f"Diagnostics error: {e}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def get_frame(self):
        return self.frame