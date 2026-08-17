# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from utils.scaling import scale_size

class BasePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors['bg_dark'])
        self.app = app
        self.colors = app.colors
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        self.create_header()
        self.create_content()
    
    def create_header(self):
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady_top = scale_size(30, self.scale_factor)
        pady_bottom = scale_size(20, self.scale_factor)
        
        title = tk.Label(
            self,
            text=self.get_title(),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title.pack(anchor='w', pady=(pady_top, 5), padx=padx)
        
        desc = tk.Label(
            self,
            text=self.get_description(),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc.pack(anchor='w', pady=(0, pady_bottom), padx=padx)
    
    def get_title(self) -> str:
        return ""
    
    def get_description(self) -> str:
        return ""
    
    def create_content(self):
        pass