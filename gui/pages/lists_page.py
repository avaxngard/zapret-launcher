# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import messagebox
from gui.widgets import RoundedButton
from utils.languages import tr
from utils.scaling import scale_size
from utils.list_editor import ListEditor
import os
from config import APPDATA_DIR, LISTS_DIR

def check_zapret_folder():
    zapret_core_dir = APPDATA_DIR / "zapret_core"
    if not zapret_core_dir.exists():
        messagebox.showerror(
            tr('error_zapret_folder'), 
            f"{tr('error_zapret_folder')}\n\n"
            f"Expected folder: {zapret_core_dir}\n\n"
            "Restart the program to extract resources."
        )
        return False
    return True

def open_lists_folder():
    try:
        os.startfile(LISTS_DIR)
    except Exception as e:
        messagebox.showerror(tr('error_occurred'), f"Failed to open folder: {str(e)}")

class ListsPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_name = scale_size(14, self.scale_factor)
        font_size_filename = scale_size(11, self.scale_factor)
        font_size_btn = scale_size(10, self.scale_factor)
        btn_width = scale_size(100, self.scale_factor)
        btn_height = scale_size(35, self.scale_factor)
        btn_radius = scale_size(8, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        btn_width_folder = scale_size(300, self.scale_factor)
        btn_height_folder = scale_size(40, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('lists_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('lists_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, scale_size(20, self.scale_factor)), padx=padx)
        
        lists_content = tk.Frame(self.frame, bg=self.colors['bg_light'])
        lists_content.pack(fill=tk.X, padx=padx, pady=pady)
        
        for label, filename in [
            (tr('lists_custom'), "list-custom.txt"),
            (tr('lists_ipset'), "ipset-all.txt"),
            (tr('lists_ipset_white'), "ipset-white.txt"),
            (tr('lists_white'), "list-white.txt"),
            (tr('lists_google'), "list-google.txt"),
            (tr('lists_general'), "list-general.txt")
        ]:
            
            frame = tk.Frame(lists_content, bg=self.colors['bg_light'])
            frame.pack(fill=tk.X, pady=scale_size(15, self.scale_factor), padx=scale_size(20, self.scale_factor))
            
            text_frame = tk.Frame(frame, bg=self.colors['bg_light'])
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(text_frame, text=label, font=("Inter", font_size_name, "bold"), 
                    fg=self.colors['text_primary'], bg=self.colors['bg_light'], anchor='w').pack(anchor='w')
            tk.Label(text_frame, text=filename, font=("Inter", font_size_filename), 
                    fg=self.colors['text_secondary'], bg=self.colors['bg_light'], anchor='w').pack(anchor='w', pady=(scale_size(5, self.scale_factor), 0))
            
            btn_frame = tk.Frame(frame, bg=self.colors['bg_light'])
            btn_frame.pack(side=tk.RIGHT, padx=(scale_size(10, self.scale_factor), 0))
            
            edit_btn = RoundedButton(btn_frame, text=tr('lists_edit'), 
                                    command=lambda f=filename: self.edit_list_file(f),
                                    width=btn_width, height=btn_height, bg=self.colors['button_bg'], 
                                    font=("Inter", font_size_btn), corner_radius=btn_radius,
                                    hover_color=self.colors['accent'], 
                                    theme_name=self.app.current_theme)
            edit_btn.pack()
        
        folder_frame = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        folder_frame.pack(fill=tk.X, padx=padx, pady=(scale_size(20, self.scale_factor), scale_size(10, self.scale_factor)))
        
        open_folder_btn = RoundedButton(folder_frame, text=tr('lists_open_folder'), 
                                    command=open_lists_folder,
                                    width=btn_width_folder, height=btn_height_folder, bg=self.colors['button_bg'], 
                                    font=("Inter", scale_size(11, self.scale_factor), "bold"), corner_radius=scale_size(10, self.scale_factor),
                                    hover_color=self.colors['accent'], 
                                    theme_name=self.app.current_theme)
        open_folder_btn.pack()
    
    def edit_list_file(self, filename):
        if not check_zapret_folder():
            return
        
        lists_path = os.path.join(self.app.zapret.zapret_dir, "lists")
        file_path = os.path.join(lists_path, filename)
        ListEditor(self.app.root, file_path, filename, app=self.app)
    
    def get_frame(self):
        return self.frame