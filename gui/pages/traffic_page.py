# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import tkinter as tk
from tkinter import ttk
from utils.languages import tr
from utils.scaling import scale_size

class TrafficPage:
    def __init__(self, parent, app):
        self.app = app
        self.colors = app.colors
        self.font_primary = app.font_primary
        self.font_medium = app.font_medium
        self.font_bold = app.font_bold
        self.scale_factor = getattr(app, 'scale_factor', 1.0)
        
        font_size_title = scale_size(20, self.scale_factor)
        font_size_desc = scale_size(10, self.scale_factor)
        font_size_warning = scale_size(8, self.scale_factor)
        font_size_tree = scale_size(9, self.scale_factor)
        font_size_heading = scale_size(10, self.scale_factor)
        row_height = scale_size(25, self.scale_factor)
        padx = scale_size(30, self.scale_factor)
        pady = scale_size(10, self.scale_factor)
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        title_label = tk.Label(
            self.frame,
            text=tr('traffic_title'),
            font=("Inter", font_size_title, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(anchor='w', pady=(scale_size(30, self.scale_factor), 5), padx=padx)
        
        desc_label = tk.Label(
            self.frame,
            text=tr('traffic_desc'),
            font=("Inter", font_size_desc),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark']
        )
        desc_label.pack(anchor='w', pady=(0, 5), padx=padx)

        warning_label = tk.Label(
            self.frame,
            text=tr('traffic_warning'),
            font=("Inter", font_size_warning),
            fg=self.colors['accent'],
            bg=self.colors['bg_dark']
        )
        warning_label.pack(anchor='w', pady=(0, 5), padx=padx)
        
        table_frame = tk.Frame(self.frame, bg=self.colors['bg_light'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)

        columns = (tr('traffic_process'), tr('traffic_speed'), tr('traffic_vpn'), tr('traffic_direct'), tr('traffic_connections'), tr('traffic_host'), tr('traffic_total'))

        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("Treeview.Heading",
                        background=self.colors['bg_medium'],
                        foreground=self.colors['text_primary'],
                        font=("Inter", font_size_heading, "bold"),
                        relief="flat")
        
        style.map("Treeview.Heading",
            background=[('active', self.colors['bg_medium'])],
            foreground=[('active', self.colors['text_primary'])])
        
        style.configure("Treeview",
            background=self.colors['bg_light'],
            foreground=self.colors['text_primary'],
            rowheight=row_height,
            fieldbackground=self.colors['bg_light'],
            font=("Inter", font_size_tree))
        
        style.map("Treeview", background=[('selected', self.colors['accent'])], foreground=[('selected', 'white')])
        
        self.traffic_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20, style="Treeview")
        
        col_widths = {
            tr('traffic_process'): scale_size(200, self.scale_factor),
            tr('traffic_speed'): scale_size(100, self.scale_factor),
            tr('traffic_vpn'): scale_size(100, self.scale_factor),
            tr('traffic_direct'): scale_size(100, self.scale_factor),
            tr('traffic_connections'): scale_size(70, self.scale_factor),
            tr('traffic_host'): scale_size(180, self.scale_factor),
            tr('traffic_total'): scale_size(100, self.scale_factor)
        }
        
        for col in columns:
            self.traffic_tree.column(col, width=col_widths.get(col, scale_size(100, self.scale_factor)), anchor="w" if col in [tr('traffic_process'), tr('traffic_host')] else "e")
            self.traffic_tree.heading(col, text=col)
        
        for col in [tr('traffic_connections')]:
            self.traffic_tree.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.traffic_tree.yview, style="Custom.Vertical.TScrollbar")
        self.traffic_tree.configure(yscrollcommand=scrollbar.set)
        self.traffic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def get_frame(self):
        return self.frame