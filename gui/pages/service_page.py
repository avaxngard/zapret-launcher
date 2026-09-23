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
        font_size_card_name = scale_size(14, self.scale_factor)
        font_size_card_desc = scale_size(9, self.scale_factor)
        card_padx = scale_size(15, self.scale_factor)
        card_pady = scale_size(12, self.scale_factor)
        grid_gap = scale_size(10, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('service_title'),
            font=("Segoe UI Variable", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('service_desc'),
            font=("Segoe UI Variable", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)
        
        grid_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        grid_frame.columnconfigure(0, weight=1, uniform="cards")
        grid_frame.columnconfigure(1, weight=1, uniform="cards")
        grid_frame.rowconfigure(0, weight=0)
        grid_frame.rowconfigure(1, weight=0)
                
        self._create_card(
            grid_frame, row=0, col=0,
            name=tr('service_game_filter'),
            desc=tr('service_game_filter_desc'),
            command=lambda: self.app.run_service_command("game_filter"),
            padx=(0, grid_gap // 2), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )
        
        self._create_card(
            grid_frame, row=0, col=1,
            name=tr('service_ipset_filter'),
            desc=tr('service_ipset_filter_desc'),
            command=lambda: self.app.run_service_command("ipset_filter"),
            padx=(grid_gap // 2, 0), pady=(0, grid_gap // 2),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )
        
        self._create_card(
            grid_frame, row=1, col=0,
            name=tr('service_run_diagnostic'),
            desc=tr('service_run_diagnostic_desc'),
            command=self.run_diagnostics,
            padx=(0, grid_gap // 2), pady=(grid_gap // 2, 0),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )
        
        self._create_card(
            grid_frame, row=1, col=1,
            name=tr('service_run_tests'),
            desc=tr('service_run_tests_desc'),
            command=self.run_tests,
            padx=(grid_gap // 2, 0), pady=(grid_gap // 2, 0),
            font_size_name=font_size_card_name,
            font_size_desc=font_size_card_desc,
            card_padx=card_padx, card_pady=card_pady
        )
    
    def _create_card(self, parent, row, col, name, desc, command,
                     padx, pady, font_size_name, font_size_desc,
                     card_padx, card_pady):
        card = tk.Frame(parent, bg=self.colors['bg_light'], cursor="hand2", height=scale_size(80, self.scale_factor))
        card.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
        card.pack_propagate(False)
        card.grid_propagate(False)
        
        inner = tk.Frame(card, bg=self.colors['bg_light'])
        inner.pack(fill=tk.BOTH, expand=True, padx=card_padx, pady=card_pady)
        
        name_label = tk.Label(
            inner,
            text=name,
            font=("Segoe UI Variable", font_size_name, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_light'],
            anchor='w',
            justify=tk.LEFT
        )
        name_label.pack(anchor='w', fill=tk.X)
        
        desc_label = tk.Label(
            inner,
            text=desc,
            font=("Segoe UI Variable", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            anchor='w',
            justify=tk.LEFT,
            wraplength=scale_size(300, self.scale_factor)
        )
        desc_label.pack(anchor='w', fill=tk.X, pady=(scale_size(6, self.scale_factor), 0))
        
        def on_enter(e):
            card.configure(bg=self.colors['bg_light_hover'])
            inner.configure(bg=self.colors['bg_light_hover'])
            name_label.configure(bg=self.colors['bg_light_hover'])
            desc_label.configure(bg=self.colors['bg_light_hover'])
        
        def on_leave(e):
            card.configure(bg=self.colors['bg_light'])
            inner.configure(bg=self.colors['bg_light'])
            name_label.configure(bg=self.colors['bg_light'])
            desc_label.configure(bg=self.colors['bg_light'])
        
        def on_click(e):
            command()
        
        for widget in (card, inner, name_label, desc_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
    
    def run_diagnostics(self):
        def run():
            try:
                service_bat = ZAPRET_CORE_DIR / "service.bat"
                subprocess.Popen(
                    [str(service_bat)],
                    cwd=str(ZAPRET_CORE_DIR),
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
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
                subprocess.Popen(
                    [str(service_bat)],
                    cwd=str(ZAPRET_CORE_DIR),
                    shell=False,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                time.sleep(2)
                
                ctypes.windll.user32.keybd_event(0x37, 0, 0, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x37, 0, 2, 0)
                time.sleep(0.2)
                ctypes.windll.user32.keybd_event(0x0D, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.keybd_event(0x0D, 0, 2, 0)
                
            except Exception as e:
                self.app.log_event("info", f"Tests error: {e}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def get_frame(self):
        return self.frame
